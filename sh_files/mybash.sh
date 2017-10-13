#!/bin/bash
alias mycd='cd ~/jackal_navigation/src/my_pkg/maps/'
mycd
pwd
mapname=$1
echo $mapname
mapname1=$mapname.png
mapname2=$mapname.pgm
mapname3=$mapname.txt
#terminator -e "rostopic echo -n 1 /gazebo/model_states > $mapname.txt"& ## big mistake!!!
mkdir -p $mapname
cd $mapname
terminator -e "rostopic echo -n 1 /gazebo/link_states > $mapname.txt"&
sleep 2s
#terminator -e "rosrun my_pkg ground_truth2b.py $mapname1 $mapname2 $mapname3"&
#terminator -e "rosrun my_pkg ground_truth3.py $mapname1 $mapname2 $mapname3"&
#terminator -e "rosrun my_pkg ground_truth5.py $mapname1 $mapname2 $mapname3"&
terminator -e "rosrun my_pkg ground_truth6.py $mapname1 $mapname2 $mapname3"&

sleep 10s
cp -n /home/liron/jackal_navigation/src/jackal_simulator/jackal_gazebo/launch/$mapname.launch $mapname.launch 
cp -n /home/liron/jackal_navigation/src/jackal_simulator/jackal_gazebo/launch/jackal.launch jackal.launch 
cp -n /home/liron/jackal_navigation/src/jackal_simulator/jackal_gazebo/worlds/$mapname.world $mapname.world 
cp -n /home/liron/jackal_navigation/src/my_pkg/scripts/cone_world1.yaml $mapname.yaml 

#yaml_text="image: $mapname.png\n
#		   resolution: 0.025688073\n
#		   origin: [-56.000000, -56.000000, 0.000000]\n
#		   negate: 0\n
#		   occupied_thresh: 0.65\n
#		   free_thresh: 0.196\n "


#yaml_text="image: $mapname.png\n
#		   resolution: 0.02564102564\n
#		   origin: [-40.000000, -40.000000, 0.000000]\n
#		   negate: 0\n
#		   occupied_thresh: 0.65\n
#		   free_thresh: 0.196\n "
		   

#yaml_text="image: $mapname.png\n
#		   resolution: 0.02565597668\n
#		   origin: [-44.000000, -44.000000, 0.000000]\n
#		   negate: 0\n
#		   occupied_thresh: 0.65\n
#		   free_thresh: 0.196\n "


yaml_text="image: $mapname.png\nresolution: 0.0255863539\norigin: [-30.000000, -30.000000, 0.000000]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n"		   



echo $yaml_text > $mapname.yaml 

sleep 10s
