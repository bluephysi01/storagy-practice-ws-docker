#!/bin/bash
# 데스크탑 로그인 시 자동으로 뜨는 안내 터미널. 실습 순서를 출력하고 환경을 source 한다.
source /opt/ros/humble/setup.bash
source /opt/storayg_practice_ws/install/setup.bash 2>/dev/null
export DISPLAY=:1
export LIBGL_ALWAYS_SOFTWARE=1
cd /opt/storayg_practice_ws

cat <<'EOF'
============================================================
 Storagy 실습 환경 (ROS 2 Humble + Gazebo Harmonic)
============================================================
 이 터미널과 새 터미널은 모두 ROS / 워크스페이스가 source 되어 있습니다.
 추가 터미널은 상단 메뉴 또는 Ctrl+Shift+T 로 엽니다.

 [1] 시뮬레이션 실행 (항상 먼저)
     ros2 launch storagy sim.launch.py

 [2] 지도 만들기 (SLAM)
     # 새 터미널 A
     ros2 launch storagy mapping.launch.py
     # 새 터미널 B — 로봇을 운전하며 공간을 한 바퀴 돈다
     ros2 run teleop_twist_keyboard teleop_twist_keyboard
     # 다 돌면 지도 저장
     ros2 run nav2_map_server map_saver_cli -f src/storagy/map/warehouse

 [3] 자율주행 (Nav2)
     # 시뮬레이션은 RViz 없이 실행
     ros2 launch storagy sim.launch.py use_rviz:=false
     # 새 터미널 — 저장한 지도로 Nav2 실행
     ros2 launch storagy navigation.launch.py
     # RViz 에서 "2D Pose Estimate" 로 초기 위치, "Nav2 Goal" 로 목적지 지정
============================================================
EOF
