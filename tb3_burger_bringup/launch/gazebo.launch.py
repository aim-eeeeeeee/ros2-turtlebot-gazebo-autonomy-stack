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

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),

        DeclareLaunchArgument('use_sim_time', default_value = 'true'),
        DeclareLaunchArgument('x_pose', default_value = '0.0'),
        DeclareLaunchArgument('y_pose', default_value = '0.0'),
        DeclareLaunchArgument('open_rviz', default_value = 'true'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(turtlebot3_gazebo, 'launch', 'turtlebot3_world.launch.py')
            ),
            launch_arguments={
                'x_pose': LaunchConfiguration('x_pose'),
                'y_pose': LaunchConfiguration('y_pose'),
            }.items(),
        ),

        Node(
            condition=IfCondition(LaunchConfiguration('open_rviz')),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output= 'screen',
            arguments=['-d', os.path.join(get_package_share_directory('tb3_burger_bringup'), 'rviz', 'sim.rviz')]
        )
    ])