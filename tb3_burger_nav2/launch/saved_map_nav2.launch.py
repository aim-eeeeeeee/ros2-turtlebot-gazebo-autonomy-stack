import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_file = LaunchConfiguration('map')

    nav2_params_file = os.path.join(
        get_package_share_directory('tb3_burger_nav2'),
        'config', 'nav2_params.yaml'
    )
    localization_params_file = os.path.join(
        get_package_share_directory('tb3_burger_nav2'),
        'config', 'localization_params.yaml'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('tb3_burger_bringup'),
                'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'open_rviz': 'false',
            'obstacle_stop': 'false',
            'use_nav2': 'false',
            'use_slam': 'false',
        }.items()
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'localization_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_file,
            'params_file': localization_params_file,
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'navigation_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(
            get_package_share_directory('nav2_bringup'),
            'rviz', 'nav2_default_view.rviz'
        )],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'map',
            description='Absolute path to the saved map YAML file.'
        ),
        gazebo,
        localization,
        navigation,
        rviz,
    ])
