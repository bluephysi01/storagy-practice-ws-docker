#!/usr/bin/env python3
# URDF 를 읽어 robot_description 토픽과 로봇 링크 TF(base_link, 바퀴, 라이다 등)를
# 퍼블리시한다. sim/mapping/navigation 런치에서 공통으로 include 한다.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    urdf = os.path.join(
        get_package_share_directory('storagy'), 'urdf', 'storagy.urdf')
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc},
                    {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='Gazebo 시뮬레이션 시계를 사용하려면 true'),
        robot_state_publisher,
    ])
