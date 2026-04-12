import math
import random

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ObstacleStop(Node):
    def __init__(self):
        super().__init__('obstacle_stop')

        self.declare_parameter('front_stop_distance', 0.45)
        self.declare_parameter('side_clear_distance', 0.35)
        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('turn_angular_speed', 0.8)
        self.declare_parameter('backup_speed', -0.08)
        self.declare_parameter('control_rate', 10.0)
        self.declare_parameter('backup_duration', 1.0)
        self.declare_parameter('turn_duration', 1.8)
        self.declare_parameter('stuck_timeout', 4.0)
        self.declare_parameter('stuck_distance_epsilon', 0.05)

        self.front_stop_dist = self.get_parameter('front_stop_distance').value
        self.side_clear_dist = self.get_parameter('side_clear_distance').value
        self.linear_spd = self.get_parameter('linear_speed').value
        self.turn_angular_spd = self.get_parameter('turn_angular_speed').value
        self.backup_spd = self.get_parameter('backup_speed').value
        self.control_rate = self.get_parameter('control_rate').value
        self.backup_duration = self.get_parameter('backup_duration').value
        self.turn_duration = self.get_parameter('turn_duration').value
        self.stuck_timeout = self.get_parameter('stuck_timeout').value
        self.stuck_distance_epsilon = self.get_parameter('stuck_distance_epsilon').value

        self.latest_scan = None
        self.latest_pose = None
        self.last_progress_pose = None
        self.last_progress_time = self.get_clock().now()
        self.state = 'FORWARD'
        self.state_until = None
        self.turn_direction = 1.0

        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.cmd_pub = self.create_publisher(
            TwistStamped, '/cmd_vel', 10)
        self.control_timer = self.create_timer(
            1.0 / self.control_rate, self.control_loop)

        self.get_logger().info(
            'ObstacleStop running with reactive mapping behavior')

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def odom_callback(self, msg: Odometry):
        self.latest_pose = msg.pose.pose.position
        if self.last_progress_pose is None:
            self.last_progress_pose = msg.pose.pose.position

    def valid_ranges(self, ranges, range_min, range_max):
        valid = [r for r in ranges if math.isfinite(r) and range_min < r < range_max]
        return valid if valid else [range_max]

    def scan_sectors(self, msg: LaserScan):
        front = self.valid_ranges(msg.ranges[:25] + msg.ranges[-25:], msg.range_min, msg.range_max)
        left = self.valid_ranges(msg.ranges[25:90], msg.range_min, msg.range_max)
        right = self.valid_ranges(msg.ranges[-90:-25], msg.range_min, msg.range_max)
        return {
            'front_min': min(front),
            'left_min': min(left),
            'right_min': min(right),
            'left_avg': sum(left) / len(left),
            'right_avg': sum(right) / len(right),
        }

    def distance_since_progress(self):
        if self.latest_pose is None or self.last_progress_pose is None:
            return 0.0
        dx = self.latest_pose.x - self.last_progress_pose.x
        dy = self.latest_pose.y - self.last_progress_pose.y
        return math.hypot(dx, dy)

    def set_state(self, state, duration=None, turn_direction=None):
        self.state = state
        self.state_until = None
        if duration is not None:
            self.state_until = self.get_clock().now() + Duration(seconds=duration)
        if turn_direction is not None:
            self.turn_direction = turn_direction

    def choose_turn_direction(self, sectors):
        if sectors['left_avg'] > sectors['right_avg'] + 0.05:
            return 1.0
        if sectors['right_avg'] > sectors['left_avg'] + 0.05:
            return -1.0
        return random.choice([-1.0, 1.0])

    def make_twist(self, linear_x=0.0, angular_z=0.0):
        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        twist.header.frame_id = 'base_footprint'
        twist.twist.linear.x = linear_x
        twist.twist.angular.z = angular_z
        return twist

    def control_loop(self):
        if self.latest_scan is None:
            return

        now = self.get_clock().now()
        sectors = self.scan_sectors(self.latest_scan)

        if self.state == 'FORWARD' and self.latest_pose is not None:
            if self.distance_since_progress() > self.stuck_distance_epsilon:
                self.last_progress_pose = self.latest_pose
                self.last_progress_time = now
            elif now - self.last_progress_time > Duration(seconds=self.stuck_timeout):
                self.get_logger().warn(
                    'Robot appears stuck, starting escape recovery',
                    throttle_duration_sec=2.0
                )
                self.set_state(
                    'BACKUP',
                    duration=self.backup_duration,
                    turn_direction=random.choice([-1.0, 1.0]),
                )

        if self.state_until is not None and now >= self.state_until:
            if self.state == 'BACKUP':
                self.set_state('TURN', duration=self.turn_duration, turn_direction=self.turn_direction)
            elif self.state == 'TURN':
                self.set_state('FORWARD')

        if self.state == 'FORWARD':
            if sectors['front_min'] < self.front_stop_dist:
                self.get_logger().info(
                    f'Obstacle ahead at {sectors["front_min"]:.2f}m, backing up to turn',
                    throttle_duration_sec=1.0
                )
                self.set_state(
                    'BACKUP',
                    duration=self.backup_duration,
                    turn_direction=self.choose_turn_direction(sectors),
                )
                cmd = self.make_twist(self.backup_spd, 0.0)
            else:
                angular = 0.0
                if sectors['left_min'] < self.side_clear_dist:
                    angular = -0.25
                elif sectors['right_min'] < self.side_clear_dist:
                    angular = 0.25
                cmd = self.make_twist(self.linear_spd, angular)
        elif self.state == 'BACKUP':
            cmd = self.make_twist(self.backup_spd, 0.0)
        else:
            cmd = self.make_twist(0.0, self.turn_direction * self.turn_angular_spd)

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
