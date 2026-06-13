#!/usr/bin/env python3
# RViz2 를 storagy 설정으로 띄운다. use_rviz:=false 면 띄우지 않는다.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    rviz_config = os.path.join(
        get_package_share_directory('storagy'), 'rviz', 'storagy.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config, '--ros-args', '--log-level', 'ERROR'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value=use_sim_time,
                              description='Gazebo 시계 사용 여부'),
        DeclareLaunchArgument('use_rviz', default_value=use_rviz,
                              description='RViz 를 띄울지 여부'),
        rviz,
    ])
