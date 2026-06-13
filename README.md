# Storagy Practice Workspace (Docker)

Storagy 로봇 ROS 2 시뮬레이션에서 **Cartographer 로 지도를 만들고(SLAM)**, 그 지도로
**Nav2 자율주행**을 실습하는 환경을 **Docker 하나로** 패키징한 레포입니다.

- **GPU 불필요** — 소프트웨어 렌더링으로 동작
- **Windows / macOS(Apple Silicon 포함) / Ubuntu** 어디서나 동일하게 실행
- Gazebo / RViz 화면은 **웹 브라우저(noVNC)** 로 표시 — 호스트에 X 서버 설정 불필요
- `src/` 폴더가 **볼륨 마운트**되어 있어 코드를 직접 수정·실험 가능

## 구성

| 구성요소 | 내용 |
|---|---|
| 베이스 이미지 | `tiryoh/ros2-desktop-vnc:humble` (ROS 2 Humble + MATE 데스크탑 + noVNC) |
| 시뮬레이터 | Gazebo Harmonic (gz-sim8) + ros_gz |
| 매핑(SLAM) | Cartographer |
| 자율주행 | Nav2 |
| 수동 조작 | teleop_twist_keyboard |

## 사전 준비

[Docker Desktop](https://www.docker.com/products/docker-desktop/)(Windows / macOS) 또는
Docker Engine + compose 플러그인(Ubuntu)을 설치합니다. 메모리는 **6GB 이상** 권장합니다.

## 빠른 시작

```bash
git clone https://github.com/bluephysi01/storayg_practice_ws.git
cd storayg_practice_ws

# Docker Hub 이미지를 받아서 실행 (이미지가 없으면 docker compose build 로 로컬 빌드)
docker compose up -d
```

브라우저에서 **http://localhost:6080** 으로 접속하면 리눅스 데스크탑이 열립니다.
Gazebo / RViz 창이 이 데스크탑 안에 표시됩니다.

접속하면 **"Storagy Practice"** 안내 터미널이 자동으로 떠 있습니다. 이 터미널과 새로 여는
모든 터미널은 ROS / 워크스페이스가 이미 `source` 되어 있습니다. 추가 터미널은
`Ctrl+Shift+T` 로 엽니다.

종료:

```bash
docker compose down
```

---

## 실습

아래 명령은 모두 **noVNC 데스크탑(http://localhost:6080) 안의 터미널**에서 실행합니다.

### 1. 시뮬레이션 실행

먼저 Gazebo 시뮬레이션(창고 월드 + 로봇 + RViz)을 띄웁니다. 매핑·자율주행 모두 이 단계가
먼저 켜져 있어야 합니다. 첫 실행은 모델 로딩 때문에 1~2분 걸릴 수 있습니다.

```bash
ros2 launch storagy sim.launch.py
```

### 2. 지도 만들기 (Cartographer SLAM)

시뮬레이션이 켜진 상태에서 **새 터미널 A** 에 Cartographer 를 실행합니다.

```bash
ros2 launch storagy mapping.launch.py
```

**새 터미널 B** 에 키보드 조작 노드를 실행하고, 안내에 따라 로봇을 운전하며 공간을 한 바퀴
돕니다. RViz 에 지도가 실시간으로 그려집니다.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

> 지도가 깔끔하게 만들어지려면 **천천히** 운전합니다. 직진 약 0.2~0.3 m/s, 회전은 더 느리게.

공간을 다 돌았으면 지도를 저장합니다 (`warehouse.yaml` + `warehouse.pgm` 생성).

```bash
ros2 run nav2_map_server map_saver_cli -f src/storagy/map/warehouse
```

저장이 끝나면 매핑 터미널(A)과 teleop 터미널(B)을 `Ctrl+C` 로 종료합니다.

### 3. 자율주행 (Nav2)

자율주행 단계에서는 Nav2 가 자체 RViz 를 띄우므로, 시뮬레이션은 RViz **없이** 실행합니다.
실행 중이던 시뮬레이션을 `Ctrl+C` 로 끄고 다시 실행합니다.

```bash
ros2 launch storagy sim.launch.py use_rviz:=false
```

**새 터미널** 에 2단계에서 저장한 지도로 Nav2 를 실행합니다.

```bash
ros2 launch storagy navigation.launch.py
```

RViz 가 뜨면:

1. 상단 **"2D Pose Estimate"** 버튼을 누르고, 지도에서 로봇의 실제 위치·방향을 클릭·드래그해
   초기 위치를 잡습니다.
2. 상단 **"Nav2 Goal"** 버튼을 누르고 목적지를 클릭하면, 로봇이 경로를 계획해 장애물을
   피하며 이동합니다.

---

## 코드 수정하기

호스트의 `./src` 폴더가 컨테이너 안 `/opt/storayg_practice_ws/src` 에 마운트되어 있어,
**호스트에서 파일을 수정하면 컨테이너에 반영**됩니다.

- 런치 파일 / 월드 / 맵 / URDF / Cartographer·Nav2 설정 등을 수정한 뒤에는 컨테이너 안에서
  워크스페이스를 재빌드합니다:

```bash
docker compose exec storagy-practice rebuild_ws.sh
```

재빌드 후 실행 중이던 launch 를 `Ctrl+C` 로 끄고 다시 실행하면 변경이 반영됩니다.
noVNC 데스크탑 터미널에서 `rebuild_ws.sh` 를 직접 실행해도 됩니다.

## 직접 빌드 / 이미지 배포 (메인테이너용)

```bash
# 소스에서 이미지 빌드
docker compose build

# Docker Hub 로그인 후 푸시
docker login
docker compose push   # bluephysi01/storayg_practice_ws:latest
```

Docker Hub 저장소가 **Public** 이어야 다른 사람이 로그인 없이 `docker compose up` 만으로
이미지를 받을 수 있습니다.

## 폴더 구조

```
├── Dockerfile              # 이미지 정의 (Gazebo/Cartographer/Nav2 의존성 + colcon build)
├── docker-compose.yml      # 포트, 볼륨 마운트
├── docker/
│   ├── run_sim.sh          # 시뮬레이션 실행 헬퍼
│   ├── rebuild_ws.sh       # src 수정 후 컨테이너 안에서 colcon 재빌드
│   └── welcome.sh          # 접속 시 뜨는 실습 안내 터미널
└── src/
    └── storagy/            # 로봇 모델(URDF), 창고 월드, 런치, Cartographer/Nav2 설정, 맵
```

## 트러블슈팅

- **Gazebo 화면이 안 뜸 / 검은 화면**: 첫 로딩이 느립니다. 1~2분 기다리세요. 메모리가 부족하면
  Docker Desktop 리소스(메모리 6GB 이상)를 늘립니다.
- **지도가 진행 방향으로 길게 늘어짐**: 너무 빨리 운전하면 발생합니다. 더 천천히 운전하세요.
- **자율주행 시 RViz 가 두 개 뜸**: 시뮬레이션을 `use_rviz:=false` 로 실행했는지 확인하세요.
- **포트 충돌**: `docker-compose.yml` 의 `6080` 을 다른 포트로 바꾸세요.
- **`navigation.launch.py` 가 맵을 못 찾음**: 2단계에서 `src/storagy/map/warehouse` 로 지도를
  저장했는지 확인하세요. 기본 맵 경로는 `map/warehouse.yaml` 입니다.
