#!/usr/bin/env python3
# 2단계: 지도 만들기 (Cartographer SLAM)
#   sim.launch.py 가 켜져 있는 상태에서 실행한다. 로봇을 직접 운전해서
#   (teleop_twist_keyboard) 공간을 돌아다니면 /map 토픽으로 점유격자 지도가
#   실시간으로 만들어진다. 다 돌고 나면 map_saver_cli 로 저장한다.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_storagy = get_package_share_directory('storagy')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    cartographer_config_dir = os.path.join(pkg_storagy, 'config', 'cartographer')
    configuration_basename = 'mobile_2d.lua'

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-configuration_directory', cartographer_config_dir,
                   '-configuration_basename', configuration_basename],
    )

    # Cartographer 의 submap 을 표준 /map (OccupancyGrid) 으로 변환 -> map_saver 가
    # 그대로 저장할 수 있다.
    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-resolution', resolution,
                   '-publish_period_sec', publish_period_sec],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value=use_sim_time,
                              description='Gazebo 시계 사용 여부 (시뮬레이션은 true)'),
        DeclareLaunchArgument('resolution', default_value=resolution,
                              description='지도 격자 해상도(m)'),
        DeclareLaunchArgument('publish_period_sec', default_value=publish_period_sec,
                              description='지도 퍼블리시 주기(초)'),
        cartographer_node,
        occupancy_grid_node,
    ])
