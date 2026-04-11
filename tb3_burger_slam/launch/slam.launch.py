"""
slam.launch.py
--------------
Launches SLAM Toolbox in online-async mode for the FetchMan / TurtleBot3 Burger.

Usage (standalone):
    ros2 launch tb3_burger_slam slam.launch.py

Arguments:
    use_sim_time  [true]   Set false when running on real hardware.
    slam_params_file      Path to the SLAM params YAML (defaults to this
                          package's config/slam_params.yaml).
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_slam = get_package_share_directory('tb3_burger_slam')

    default_params = os.path.join(pkg_slam, 'config', 'slam_params.yaml')

    use_sim_time    = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')

    return LaunchDescription([

        # ── arguments ─────────────────────────────────────────────────────────
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo sim clock (true) or wall clock (false).',
        ),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_params,
            description='Full path to the SLAM Toolbox parameter file.',
        ),

        # ── slam_toolbox online async node ────────────────────────────────────
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_params_file,
                {'use_sim_time': use_sim_time},
            ],
            # Remap only if your topic names ever differ from the defaults.
            # ObstacleStop already publishes on /scan so no remap needed.
            remappings=[
                # ('/scan', '/scan'),     # already correct
            ],
        ),
    ])
