cmake_minimum_required(VERSION 3.8)
project(tb3_burger_slam)

find_package(ament_cmake REQUIRED)

# Install the launch file and config so they end up in the share directory
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
