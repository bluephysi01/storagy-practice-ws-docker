#!/bin/bash
# 볼륨 마운트된 ./src 의 런치/월드/맵/URDF/설정 파일을 수정한 뒤 워크스페이스를
# 다시 빌드한다. (단순 텍스트 파일 수정도 새 파일을 추가했다면 재빌드가 필요)
#
#   docker compose exec storagy-practice rebuild_ws.sh
#
# 재빌드 후에는 실행 중인 launch 를 Ctrl+C 로 끄고 다시 실행한다.
set -e

source /opt/ros/humble/setup.bash
cd /opt/storagy-practice-ws-docker
colcon build --symlink-install --packages-select storagy

echo
echo "[rebuild_ws] 완료 — 실행 중인 시뮬레이션을 재시작하면 변경이 반영됩니다."
