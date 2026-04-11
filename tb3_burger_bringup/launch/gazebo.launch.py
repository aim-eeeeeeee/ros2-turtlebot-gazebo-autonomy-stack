import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    nav2_params_file = os.path.join(
        get_package_share_directory('tb3_burger_nav2'),
        'config', 'nav2_params.yaml'
    )
    slam_params_file = os.path.join(
        get_package_share_directory('tb3_burger_slam'),
        'config', 'slam_params.yaml'
    )

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),

        DeclareLaunchArgument('use_sim_time', default_value = 'true'),
        DeclareLaunchArgument('x_pose', default_value = '0.0'),
        DeclareLaunchArgument('y_pose', default_value = '0.0'),
        DeclareLaunchArgument('open_rviz', default_value = 'false'),
        DeclareLaunchArgument('obstacle_stop', default_value = 'false'),
        DeclareLaunchArgument('use_nav2', default_value = 'false'),
        DeclareLaunchArgument('slam_params_file', default_value = slam_params_file),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(turtlebot3_gazebo, 'launch', 'turtlebot3_world.launch.py')
            ),
            launch_arguments={
                'x_pose': LaunchConfiguration('x_pose'),
                'y_pose': LaunchConfiguration('y_pose'),
            }.items(),
        ),

        # RViz node (use when use_nav2:=true)
        Node(
            condition=IfCondition(LaunchConfiguration('open_rviz')),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(
                get_package_share_directory('tb3_burger_bringup'),
                'rviz', 'sim.rviz'
                )
            ],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        ),

        # Robot motion node (use when use_nav2:=false)
        # Node(
        #     condition=IfCondition(LaunchConfiguration('obstacle_stop')),
        #     package='tb3_burger_motion',
        #     executable='obstacle_stop',
        #     name='obstacle_stop',
        #     output='screen',
        #     parameters=[{'stop_distance': 0.35, 'linear_speed': 0.15, 'angular_speed': 0.5}]
        # )

        # Nav2 node (use when use_nav2:=true)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('nav2_bringup'),
                    'launch', 'navigation_launch.py'
                )
            ),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file':  nav2_params_file,
            }.items(),
            condition=IfCondition(LaunchConfiguration('use_nav2')),
        ),
    
        # SLAM node (use when use_nav2:=true)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('tb3_burger_slam'),
                    'launch', 'slam.launch.py'
                )
            ),
            launch_arguments={
                'use_sim_time':     LaunchConfiguration('use_sim_time'),
                'slam_params_file': LaunchConfiguration('slam_params_file'),
            }.items(),
            condition=IfCondition(LaunchConfiguration('use_nav2')),
        ),
    ])