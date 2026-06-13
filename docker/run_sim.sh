#!/bin/bash
# 시뮬레이션(Gazebo + 로봇 + RViz)을 실행한다. noVNC 데스크탑의 터미널에서 사용.
#   run_sim.sh                 # RViz 포함 (매핑 실습용 기본값)
#   run_sim.sh use_rviz:=false # RViz 없이 (자율주행 실습 때 navigation 의 RViz 를 쓸 때)
set -e

export DISPLAY=:1
export LIBGL_ALWAYS_SOFTWARE=1

# VNC X 서버(:1)가 뜰 때까지 대기
for _ in $(seq 1 60); do
    [ -e /tmp/.X11-unix/X1 ] && break
    sleep 1
done

source /opt/ros/humble/setup.bash
source /opt/storayg_practice_ws/install/setup.bash

cd /opt/storayg_practice_ws
exec ros2 launch storagy sim.launch.py "$@"
