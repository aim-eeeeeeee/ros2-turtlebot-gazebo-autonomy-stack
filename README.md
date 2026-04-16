# TurtleBot3 Burger Gazebo Autonomy Stack
phase 1: build a map with SLAM + teleop
phase 2: navigate autonomously with Nav2

## Phase 1: Build a map (SLAM + teleop)

**Terminal 1 — Gazebo + SLAM:**
ros2 launch tb3_burger_bringup gazebo.launch.py obstacle_stop:=true use_slam:=true open_rviz:=true

**Terminal 2 — Teleop**
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r /cmd_vel:=/cmd_vel_raw

- `-p stamped:=true` — publishes `TwistStamped` instead of `Twist`, matching the type that `obstacle_stop` expects on `/cmd_vel_raw`
- `-r /cmd_vel:=/cmd_vel_raw` — routes commands through the `obstacle_stop` safety filter, which forwards them as `TwistStamped` on `/cmd_vel`

> **WARNING:** Do NOT run plain `teleop_twist_keyboard` (without these flags) when `obstacle_stop:=true`.
> `obstacle_stop` publishes `TwistStamped` to `/cmd_vel`; plain teleop publishes `Twist` to `/cmd_vel`.
> ROS2 will silently drop all commands from the type-mismatched publisher.

If you prefer to run **without** the obstacle safety filter (`obstacle_stop:=false`), use the standard command:
ros2 run teleop_twist_keyboard teleop_twist_keyboard

Drive the robot around until the map looks complete in RViz.

**Terminal 3 — Save the map when done:**
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
    - This writes `~/maps/my_map.pgm` and `~/maps/my_map.yaml`.

## Phase 2: Navigate with saved map (Nav2 + AMCL)

**Terminal 1:**
ros2 launch tb3_burger_nav2 saved_map_nav2.launch.py map:=/absolute/path/to/my_map.yaml
    - Set a navigation goal in RViz using the **2D Goal Pose** tool. Nav2 will plan and execute the path autonomously.
