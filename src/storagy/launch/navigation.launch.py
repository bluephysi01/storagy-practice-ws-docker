#!/usr/bin/env python3
# 3단계: 자율주행 (Nav2)
#   sim.launch.py 가 켜져 있는 상태에서, 2단계에서 저장한 지도로 Nav2 를 띄운다.
#   RViz 의 "2D Pose Estimate" 로 초기 위치를 잡고 "Nav2 Goal" 로 목적지를 찍으면
#   로봇이 경로를 계획해서 장애물을 피하며 이동한다.
#
#   사용 예:
#     ros2 launch storagy navigation.launch.py \
#         map:=$HOME/storagy-practice-ws-docker/src/storagy/map/warehouse.yaml

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_storagy = get_package_share_directory('storagy')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    default_map = os.path.join(pkg_storagy, 'map', 'warehouse.yaml')
    default_params = os.path.join(pkg_storagy, 'param', 'nav2_params.yaml')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    # Nav2 전체 스택(map_server, amcl, planner, controller, bt_navigator ...)
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': 'true',
        }.items(),
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_storagy, 'launch', 'rviz.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time, 'use_rviz': use_rviz}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='불러올 지도 yaml 경로(2단계에서 저장한 파일)'),
        DeclareLaunchArgument('params_file', default_value=default_params,
                              description='Nav2 파라미터 파일'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Gazebo 시계 사용 여부 (시뮬레이션은 true)'),
        DeclareLaunchArgument('use_rviz', default_value='true',
                              description='RViz 를 함께 띄울지 여부'),
        nav2,
        rviz,
    ])
