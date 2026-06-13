#!/usr/bin/env python3
# 1단계: 시뮬레이션 띄우기
#   Gazebo(warehouse 월드) + storagy 로봇 스폰 + ROS<->Gazebo 브리지 + RViz.
#   매핑(mapping.launch.py)과 주행(navigation.launch.py) 모두 이 런치를 먼저 켜둔
#   상태에서 실행한다.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_storagy = get_package_share_directory('storagy')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # --- Gazebo 가 메시/모델을 찾을 수 있도록 리소스 경로 등록 ---
    #  - share 경로: URDF 의 package://storagy/meshes/... 해석
    #  - models 경로: warehouse 월드의 model://workcell 해석
    share_path = os.path.dirname(pkg_storagy)
    models_path = os.path.join(pkg_storagy, 'models')
    gz_resource_path = os.pathsep.join([share_path, models_path])
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + os.pathsep + gz_resource_path

    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    use_rviz = LaunchConfiguration('use_rviz')

    world_path = [pkg_storagy, '/worlds/', world]

    # Gazebo 서버 + GUI ( -r: 즉시 시작 )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ', *world_path]}.items(),
    )

    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_storagy, 'launch', 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'storagy', '-topic', 'robot_description',
                   '-x', x_pose, '-y', y_pose, '-z', z_pose],
        output='screen',
    )

    # ROS 2 <-> Gazebo 브리지 (매핑/주행에 필요한 토픽만)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/model/storagy/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/storagy/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[
            ('/model/storagy/odometry', '/odom'),
            ('/model/storagy/tf', '/tf'),
        ],
        output='screen',
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_storagy, 'launch', 'rviz.launch.py')),
        launch_arguments={'use_sim_time': 'true', 'use_rviz': use_rviz}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse.sdf',
                              description='worlds/ 안의 월드 파일 이름'),
        DeclareLaunchArgument('x_pose', default_value='0.0',
                              description='로봇 스폰 X 좌표'),
        DeclareLaunchArgument('y_pose', default_value='0.0',
                              description='로봇 스폰 Y 좌표'),
        DeclareLaunchArgument('z_pose', default_value='0.2',
                              description='로봇 스폰 Z 좌표'),
        DeclareLaunchArgument('use_rviz', default_value='true',
                              description='RViz 를 함께 띄울지 여부'),
        # 일부 노트북(소프트웨어 렌더링)에서 Gazebo 센서 렌더가 깨지는 것 방지
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path),
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        rviz,
    ])
