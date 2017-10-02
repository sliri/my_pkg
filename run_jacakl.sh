#!/bin/bash
killall gzserver
sleep 6s
cd ~/jackal_navigation
#source /opt/ros/indigo/setup.bash 
#roscore&
#sleep 10s
roslaunch jackal_gazebo jackal_cone1_world.launch&
sleep 5s
roslaunch jackal_navigation odom_navigation_demo.launch
sleep 5s
roslaunch roslaunch jackal_navigation amcl_demo.launch map_file:=/home/liron/jackal_navigation/src/my_pkg/maps/cone_world.yaml&
sleep 5s
roslaunch jackal_viz view_robot.launch config:=localization
sleep 5s
#rosrun image_view image_view image:=/camera/depth/image_raw&
#gnome-terminal
#cd ~/catkin_ws/src/image_c/src
#chmod +x navigation.py
#cd ~/catkin_ws
#source ./devel/setup.bash
#catkin_make
#rosrun  image_c navigation.py


#catkin_make
#rosrun  image_c image_c_node&
#gnome-terminal
#cd ~/catkin_ws/src/beginner_tutorials/scripts/
#cd ~/hw2/src/ourpack/src
#chmod +x image_converter.pycd ~/catkin_ws/src/image_c/src
#chmod +x image_converter.cpp
#cd ~/catkin_ws
#source ./devel/setup.bash
#catkin_make
#rosrun  image_c navigation.py
#chmod +x image_converter.cpp
#chmod +x main.cpp
#python turtulebot.py
#roscore
#sleep 10s
#gnome-terminal
#cd ~/catkin_ws
#source ./devel/setup.bash
#rosrun beginner_tutorials image_converter.cpp 
#rosrun beginner_tutorials image_converter.py
#rosrun beginner_tutorials main.cpp liron@ubuntu:~$ cd catkin_ws/
#liron@ubuntu:~/catkin_ws$ source devel/setup.bashliron@ubuntu:~$ cd catkin_ws/

#catkin_ws$ source devel/setup.bash
#rosrun hw2 hw2_node
