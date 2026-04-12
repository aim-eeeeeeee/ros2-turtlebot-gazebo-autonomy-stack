import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped


class ObstacleStop(Node):
    def __init__(self):
        super().__init__('obstacle_stop')

        self.declare_parameter('stop_distance', 0.35)   # metres
        self.declare_parameter('linear_speed', 0.15)    # m/s
        self.declare_parameter('angular_speed', 0.5)    # rad/s

        self.stop_dist = self.get_parameter('stop_distance').value
        self.linear_spd = self.get_parameter('linear_speed').value
        self.angular_spd = self.get_parameter('angular_speed').value

        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(
            TwistStamped, '/cmd_vel', 10)

        self.get_logger().info(
            f'ObstacleStop running — stop distance: {self.stop_dist}m')

    def scan_callback(self, msg: LaserScan):
        # Front arc: last 30 + first 30 readings (centre = index 0)
        front_ranges = msg.ranges[:30] + msg.ranges[-30:]
        valid = [r for r in front_ranges if msg.range_min < r < msg.range_max]

        if not valid:
            return

        min_dist = min(valid)
        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        twist.header.frame_id = 'base_footprint'

        if min_dist < self.stop_dist:
            # Obstacle ahead — stop and turn
            twist.twist.linear.x = 0.0
            twist.twist.angular.z = self.angular_spd
            self.get_logger().info(
                f'Obstacle at {min_dist:.2f}m — turning', throttle_duration_sec=1.0)
        else:
            # Clear — drive forward
            twist.twist.linear.x = self.linear_spd
            twist.twist.angular.z = 0.0

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
