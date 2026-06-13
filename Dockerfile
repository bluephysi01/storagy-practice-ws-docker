# Storagy ROS 2 실습 환경 — OS(Windows/macOS/Ubuntu) 와 무관하게 동일하게 동작.
# GPU 불필요(소프트웨어 렌더링). 베이스 이미지가 MATE 데스크탑 + noVNC 를 제공하므로
# Gazebo / RViz 창이 웹 브라우저 안에 표시된다. amd64 / arm64(Apple Silicon) 모두 지원.
FROM tiryoh/ros2-desktop-vnc:humble

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# 1. 시스템 의존성
#    - Gazebo Harmonic (gz-sim8) + ros_gz : OSRF apt 저장소
#    - Cartographer(SLAM) / Nav2(자율주행) / 로봇 모델 / 시각화 : ROS apt 저장소
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg lsb-release ca-certificates \
 && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
        -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
        > /etc/apt/sources.list.d/gazebo-stable.list \
 && apt-get update && apt-get install -y --no-install-recommends \
        gz-harmonic \
        ros-humble-ros-gzharmonic \
        ros-humble-cartographer \
        ros-humble-cartographer-ros \
        ros-humble-navigation2 \
        ros-humble-nav2-bringup \
        ros-humble-nav2-map-server \
        ros-humble-robot-state-publisher \
        ros-humble-joint-state-publisher \
        ros-humble-xacro \
        ros-humble-rviz2 \
        ros-humble-teleop-twist-keyboard \
 && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# 2. ROS 2 워크스페이스 빌드
#    Cartographer/Nav2 등은 위 apt 바이너리를 쓰고, 여기서는 storagy 패키지만 빌드.
# ---------------------------------------------------------------------------
ENV WS=/opt/storagy-practice-ws-docker
WORKDIR ${WS}
COPY . ${WS}

RUN source /opt/ros/humble/setup.bash \
 && colcon build --symlink-install --packages-select storagy \
 && chmod -R a+rX ${WS}

# ---------------------------------------------------------------------------
# 3. 헬퍼 스크립트 + 데스크탑 세션 자동 설정
#    - 새로 여는 모든 터미널에서 ROS / 워크스페이스가 자동 source 되도록 설정
#    - 데스크탑 로그인 시 실습 안내 터미널을 한 개 띄움
# ---------------------------------------------------------------------------
RUN install -m 755 ${WS}/docker/run_sim.sh   /usr/local/bin/run_sim.sh \
 && install -m 755 ${WS}/docker/rebuild_ws.sh /usr/local/bin/rebuild_ws.sh \
 && install -m 755 ${WS}/docker/welcome.sh    /usr/local/bin/welcome.sh

# 데스크탑/컨테이너의 어느 사용자로 터미널을 열어도 환경이 잡히도록 .bashrc 에 추가
RUN for HOME_DIR in /root /home/ubuntu; do \
        if [ -d "$HOME_DIR" ]; then \
            { \
              echo '# --- storagy practice ws ---'; \
              echo 'source /opt/ros/humble/setup.bash'; \
              echo "source ${WS}/install/setup.bash 2>/dev/null"; \
              echo 'export LIBGL_ALWAYS_SOFTWARE=1'; \
              echo 'export DISPLAY=:1'; \
            } >> "$HOME_DIR/.bashrc"; \
        fi; \
    done

# 데스크탑 로그인 시 실습 안내 터미널 자동 실행
RUN mkdir -p /etc/xdg/autostart \
 && cat > /etc/xdg/autostart/storagy-practice.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Storagy Practice
Comment=Storagy 실습 안내 터미널
Exec=mate-terminal --maximize --title="Storagy Practice" -- bash -lc "/usr/local/bin/welcome.sh; exec bash"
X-MATE-Autostart-enabled=true
Terminal=false
EOF

EXPOSE 80
