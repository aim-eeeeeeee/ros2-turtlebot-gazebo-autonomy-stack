import math

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ObstacleStop(Node):
    def __init__(self):
        super().__init__('obstacle_stop')

        self.declare_parameter('stop_distance', 0.45)
        self.declare_parameter('front_angle_deg', 25.0)

        self.stop_distance = self.get_parameter('stop_distance').value
        self.front_angle_deg = self.get_parameter('front_angle_deg').value

        self.obstacle_ahead = False

        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)
        self.cmd_sub = self.create_subscription(
            TwistStamped, '/cmd_vel_raw', self.cmd_callback, 10)
        self.cmd_pub = self.create_publisher(
            TwistStamped, '/cmd_vel', 10)

        self.get_logger().info(
            f'ObstacleStop safety filter running '
            f'(stop_distance={self.stop_distance}m, '
            f'front_angle=±{self.front_angle_deg}°)')

    def scan_callback(self, msg: LaserScan):
        n = max(1, round(math.radians(self.front_angle_deg) / msg.angle_increment))
        front = msg.ranges[:n] + msg.ranges[-n:]
        valid = [r for r in front if math.isfinite(r) and msg.range_min < r < msg.range_max]
        self.obstacle_ahead = bool(valid) and min(valid) < self.stop_distance

    def cmd_callback(self, msg: TwistStamped):
        if self.obstacle_ahead and msg.twist.linear.x > 0.0:
            msg.twist.linear.x = 0.0
            self.get_logger().warn(
                'Obstacle ahead — forward motion blocked',
                throttle_duration_sec=1.0)
        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
