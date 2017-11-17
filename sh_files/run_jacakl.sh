#!/bin/bash
killall gzserver
killall -9 gazebo
sleep 8s

#mapname=cone_orcahrd4_single_cone_dz2
#mapname=cone_orcahrd4_single_cone_dy
#mapname=cone_orcahrd5a
#mapname=cone_orcahrd4_interleaving_dy3
#mapname=cone_orcahrd4_unique_pattern_cones_dy
#mapname=cone_orchard4_one_rect
#mapname=cone_orcahrd5b #Two Cones missing
#mapname=cone_orcahrd5e #3 Cones missing
#mapname=cone_orcahrd5c #Half row missing
#mapname=cone_orcahrd5d #single cone missing
#mapname=cone_orcahrd6a #two cone 1 m ahead
#mapname=cone_orcahrd6b #half row ahead
#mapname=cone_orcahrd6c #single cylinder 
#mapname=cone_orcahrd6d #3 cylinders near axis 
#mapname=cone_orcahrd6e #3 Cones 1m ahead
#mapname=cone_orcahrd6f #3 Cones 1m ahead
#mapname=cone_orcahrd6g #3 Cones 1m ahead
#mapname=cone_orcahrd7a # random positioning 1 rows
#mapname=cone_orcahrd7b # random positioning 2 rows
#mapname=cone_orcahrd8 #perfect population of cylinders
#mapname=cone_orcahrd8a #perfect population of cylinders
#mapname=cone_orcahrd8b #random cylinders
#mapname=cone_orcahrd8c #random cylinders 20%
#mapname=cone_orcahrd8d #random cylinders 20%
#mapname=cone_orcahrd8e #random cylinders 20%
#mapname=cone_orcahrd8f #random cylinders 20%
#mapname=cone_orcahrd8g #random cylinders 20%

#mapname=cone_orcahrd8bx #random cylinders 20% with +-20cm movement
#mapname=cone_orcahrd8by #random cylinders 20% with +-20cm movement
#mapname=cone_orcahrd8ga #random cylinders 20% with +-20cm movement
mapname=cone_orcahrd8gb #random cylinders 20% with +-20cm movement

export JACKAL_LASER=1
export JACKAL_LASER_SCAN_TOPIC=front/scan



##create bag
###################################
create_bag=false
#create_bag=false


##create map
###################################
create_map=true 
#create_map=false 

#headless
###################################
###see http://gazebosim.org/tutorials?tut=ros_roslaunch
##see  http://gazebosim.org/tutorials?tut=quick_start
#headless=true
headless=false


#inject pose
###################################
inject_initial_pose=True
#inject_initial_pose=False
xinitial=8.0 #initial x for AMCL
yinitial=8.0 #initial y for AMCL

######################################
##launching
######################################
##########################################################################

if $headless; then
terminator -e "roslaunch jackal_gazebo $mapname.launch gui:=false headless:=true"&
sleep 10s
terminator -e "roslaunch jackal_gazebo jackal.launch gui:=false headless:=true"&
sleep 10s
terminator -e "roslaunch jackal_navigation odom_navigation_demo.launch"&
sleep 5s

if $create_map; then
	sleep 60s
	sh mybash.sh $mapname
fi


terminator -e "roslaunch jackal_navigation amcl_demo.launch map_file:=/home/liron/jackal_navigation/src/my_pkg/maps/$mapname/$mapname.yaml"&
sleep 3s
#terminator -e "roslaunch jackal_viz view_robot.launch config:=localization"&



else
#gnome-terminal -e "roslaunch gazebo_ros empty_world.launch"&

gnome-terminal -e "roslaunch jackal_gazebo $mapname.launch gui:=true headless:=false"&
sleep 20s
#gnome-terminal -e "roslaunch jackal_gazebo jackal.launch gui:=true headless:=false"&
#gnome-terminal  -e "roslaunch jackal_navigation odom_navigation_demo.launch"&
sleep 5s

if $create_map; then
	sleep 60s
	sh mybash.sh $mapname
fi

gnome-terminal  -e "rosrun map_server map_server /home/liron/jackal_navigation/src/my_pkg/maps/$mapname/$mapname.yaml respawn=true"&
sleep 10s
gnome-terminal  -e "roslaunch jackal_navigation amcl_demo.launch map_file:=/home/liron/jackal_navigation/src/my_pkg/maps/$mapname/$mapname.yaml use_map_topic:=true"&
sleep 6s
gnome-terminal  -e "roslaunch jackal_viz view_robot.launch config:=localization"&

fi

##########################################################################



##ruunning scripts
#####################################

cd /home/liron/jackal_navigation/src/my_pkg/maps/$mapname


sleep 5s


gnome-terminal  -e "rosrun my_pkg doitall_node2.py $xinitial $yinitial $inject_initial_pose"&

sleep 6s



if $create_bag; then
gnome-terminal -e "rosrun teleop_twist_keyboard teleop_twist_keyboard.py"&
gnome-terminal -e "roslaunch jackal_gazebo bag_record.launch"&

#rosbag reindex $mapname.bag
fi

sleep 5s

terminator -e "rosrun my_pkg cmd_vel_based_patrol5.py"&
sleep 2s
terminator -e  "rosservice call --wait /global_localization"&
#gnome-terminal -e "roslaunch jackal_gazebo bag_play.launch"&

#terminator -e "rqt_graph"&
#terminator -e "rqt_plot /amcl_pose/pose/pose/position/x"& 
#terminator -e "rqt_plot /amcl_pose/pose/pose/covariance[1]"& 
#rqt_plot /amcl_pose/pose/pose/covariance[3]& 
#terminator -e "rostopic echo -n 20 /gazebo/link_states > link_states.txt"&







