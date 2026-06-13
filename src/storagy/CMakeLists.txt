cmake_minimum_required(VERSION 3.8)
project(storagy)

find_package(ament_cmake REQUIRED)

# 실습에 필요한 리소스를 share/storagy 아래로 설치한다.
install(
  DIRECTORY
    launch
    urdf
    meshes
    worlds
    models
    config
    param
    rviz
    map
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
