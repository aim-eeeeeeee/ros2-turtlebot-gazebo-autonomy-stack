import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('tb3_burger_description')
    urdf_file = os.path.join(pkg_share, 'urdf', 'tb3.urdf.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    use_joint_state_gui = LaunchConfiguration('use_joint_state_gui', default='false')

    robot_description = Command(['xacro ', urdf_file])

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'
        ),
        DeclareLaunchArgument(
            'use_joint_state_gui',
            default_value='false',
            description='Launch joint_state_publisher_gui for manual joint testing.'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description,
            }]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_joint_state_gui),
        ),
    ])
