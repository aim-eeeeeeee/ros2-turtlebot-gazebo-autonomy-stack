from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tb3_burger_motion',
            executable='obstacle_stop',
            name='obstacle_stop',
            output='screen',
            parameters=[{
                'stop_distance': 0.35,
                'linear_speed': 0.15,
                'angular_speed': 0.5,
            }],
        )
    ])
