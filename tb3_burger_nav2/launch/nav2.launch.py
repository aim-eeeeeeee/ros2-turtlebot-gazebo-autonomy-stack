import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    nav2_params_file = LaunchConfiguration(
        'nav2_params_file',
        default=os.path.join(
            get_package_share_directory('tb3_burger_nav2'),
            'config', 'nav2_params.yaml'
        )
    )
    slam_params_file = os.path.join(
        get_package_share_directory('tb3_burger_slam'),
        'config', 'slam_params.yaml'
    )

    # Gazebo sim — obstacle_stop disabled & Nav2 owns /cmd_vel
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('tb3_burger_bringup'),
                'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'obstacle_stop': 'false',
            'open_rviz': 'false',
        }.items()
    )

    # SLAM Toolbox — async mode, builds /map from /scan
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch', 'online_async_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items()
    )

    # Nav2 — uses navigation_launch.py (no map_server; SLAM provides /map)
    nav2 = IncludeLaunchDescription(
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

    # RViz with Nav2 default config
    rviz_config = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'rviz', 'nav2_default_view.rviz'
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('nav2_params_file', default_value=nav2_params_file),
        gazebo,
        slam,
        nav2,
        rviz,
    ])
