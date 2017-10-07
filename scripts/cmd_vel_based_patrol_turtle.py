#!/usr/bin/env python


#importing everithing...why not to
import rospy
import roslib
roslib.load_manifest('my_pkg')
import sys
from std_srvs.srv import Empty, Trigger, TriggerResponse
from geometry_msgs.msg import Twist, Point, Quaternion,Pose
from std_msgs.msg import String
from std_msgs.msg import Float32
import tf
import math
import numpy as np
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from math import radians
from transform_utils import quat_to_angle, normalize_angle
from math import radians, copysign, sqrt, pow, pi
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from gazebo_msgs.msg import LinkStates, ModelStates














########################################################################
#MAIN EXAMPLE TAKEN FORM
#https://github.com/markwsilliman/turtlebot/blob/master/goforward.py
#https://github.com/pirobot/ros-by-example/blob/master/rbx_vol_1/rbx1_nav/nodes/nav_square.py
#########################################################################
class navigation():
    def __init__(self):
    
        # Initialize the node
        # rospy.init_node('my_node_name', anonymous=True)#
        # The anonymous keyword argument is mainly used for nodes where
        # you normally expect many of them to be running and
        # don't care about their names (e.g. tools, GUIs)
        #see  http://wiki.ros.org/rospy/Overview/Initialization%20and%20Shutdown       
        rospy.init_node('navigation',anonymous=False)
                
        # tell user how to stop TurtleBot and print on Terminal
        rospy.loginfo("To stop Jakcal CTRL + C")
        
        # What function to call when you ctrl + c
        #rospy.on_shutdown(h)
        #Register handler to be called when rospy process begins shutdown.
        #h is a function that takes no arguments. 
        #see http://wiki.ros.org/rospy/Overview/Initialization%20and%20Shutdown
        rospy.on_shutdown(self.shutdown)
             

               
        #Here, we create a tf.TransformListener object. Once the listener is created,
        #it starts receiving tf transformations over the wire, and buffers them for up to 10 seconds. 
        # see http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29       
        self.tf_listener = tf.TransformListener()
        
        # Create publisher for cmd_vel topic
        # cmd_vel publisher can "talk" to Jackal and tell it to move             
        self.cmd_vel = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)
        
#       
        self.model_states = rospy.Subscriber('/gazebo/model_states',  ModelStates, self.model_stateCallback) 
        self.Downsample_rate=100                                      #Thtopic rate is 1000Hz, needs to be downsample by factor of 100!
        self.model_states_msg_cnt=0                                 #msg counter              

        # The base frame is base_footprint for the TurtleBot but base_link for Pi Robot
        self.base_frame = rospy.get_param('~base_frame', '/base_link')
        # The odom frame is usually just /odom
        self.odom_frame = rospy.get_param('~odom_frame', '/odom')
       # Set the odom frame
        self.odom_frame = '/odom'

 
        # Find out if the robot uses /base_link or /base_footprint
        try:
            self.tf_listener.waitForTransform(self.odom_frame, '/base_footprint', rospy.Time(), rospy.Duration(1.0))
            self.base_frame = '/base_footprint'
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            try:
                self.tf_listener.waitForTransform(self.odom_frame, '/base_link', rospy.Time(), rospy.Duration(1.0))
                self.base_frame = '/base_link'
            except (tf.Exception, tf.ConnectivityException, tf.LookupException):
                rospy.loginfo("Cannot find transform between /odom and /base_link or /base_footprint")
                rospy.signal_shutdown("tf Exception")  
                
        # Initialize the position variable as a Point type
        self.position = Point()
        self.rotation =Quaternion()

       
        # Publishing rate = 20 Hz look for odometry
        self.rate = rospy.Rate(20)     
        #Velocities,tolerances
        self.angular_speed = rospy.get_param("~angular_speed", 0.4) # radians per second
        self.angular_tolerance = rospy.get_param("~angular_tolerance", radians(0.01)) # degrees to radians  
        self.linear_speed = rospy.get_param("~linear_speed", 0.5) # meters per second 
        self.linear_tolerance = rospy.get_param("~linear_tolerance",0.01) # degrees to radians
        #initilize  odometry_on  FLAG       
        self.odometry_on=False      
   
        #orchard constants        
        self.orchard_dx=2     #meter
        self.orchard_dy=4     #meter
        self.orchard_rows =20   #num of rows in the orchard 
        self.orchard_columns=10 #num of cols in the orchard    
        
        # Tell the action client that we want to spin a thread by default
        #self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Wait for the action server to come up")
     
        
        
        #Publishing rate = 200 Hz look for odometry
        #for sleeping and rate see
        #http://wiki.ros.org/rospy/Overview/Time         
        rospy.loginfo('Waiting for odometry to become available..')
        while (not self.odometry_on):
            rospy.loginfo("Odometry on is %s !" %self.odometry_on)
            (position, rotation) = self.get_odom()
            rospy.sleep(1)        
        rospy.loginfo("Odometry on is %s !" %self.odometry_on) 
        
    
  
    #main navigation function  
    def navigate(self): 
     xskew= (21.3899080874-20)
     angleskew=abs(-116.890458431+90)
     #Go south 
     self.model_state_based_linear_move(6) 
     #     self.model_state_based_rotate_by_angle(-90)  
     #self.model_state_based_linear_move(self.orchard_dx*self.orchard_rows/2)

#     #Go west
     #self.model_state_based_rotate_by_angle(-90)
     #self.model_state_based_linear_move(self.orchard_dy*self.orchard_columns/2)
    
#     
#     
#     # Cycle through the ochard
#     for i in range(12):
#         self.model_state_based_linear_move(self.orchard_dx*self.orchard_rows)
#         self.model_state_based_rotate_by_angle(-90)  
#         self.model_state_based_linear_move(self.orchard_dy)
#         self.model_state_based_rotate_by_angle(-90)
#         self.model_state_based_linear_move(self.orchard_dx*self.orchard_rows)
#         self.model_state_based_rotate_by_angle(90)
#         self.model_state_based_linear_move(self.orchard_dy)
#         self.model_state_based_rotate_by_angle(90)
#     
     
     self.shutdown
    
   
    
    def model_state_based_linear_move(self,distance):
    #Distance In meters
     # Twist is a datatype for velocity
    
        goal_distance = rospy.get_param("~goal_distance",distance) # meters
        self.move_cmd = Twist()
        #Stop all angular move,set linear velocity  
        
        self.move_cmd.angular.z = 0
        # Set the movement command to forward motion
        self.move_cmd.linear.x = self.linear_speed if distance > 0 else -self.linear_speed
        
        # Get the starting position values          
        position = self.position    
        x_start = position.x
        y_start = position.y
        #Havn't yet go anyware
        actual_distance= 0        
        while abs(actual_distance + self.linear_tolerance ) <  abs(goal_distance) and not rospy.is_shutdown():
            # Keep track of the distance traveled       
             position = self.position  
             self.cmd_vel.publish(self.move_cmd)
             self.rate.sleep()
             # Get the current position            
             #Update
             actual_distance = math.sqrt((pow((position.x - x_start), 2) + pow((position.y - y_start), 2)))
                                                 
        ##Stop the robot when we are done       
        move_cmd=Twist()
        self.cmd_vel.publish(move_cmd)
        rospy.sleep(1.0)        
        rospy.loginfo('Robot Moved %s. meters.' % (actual_distance))     
  
       
        
        
          #rotate by a specific angle
    #see https://github.com/pirobot/ros-by-example/blob/master/rbx_vol_1/rbx1_nav/nodes/nav_square.py         
    def model_state_based_rotate_by_angle(self, angle):
        # Stop the robot before rotating
        move_cmd = Twist()
        self.cmd_vel.publish(move_cmd)
        rospy.sleep(1.0)
        
        # Track how far we have turned
        turn_angle = 0
        goal_angle = rospy.get_param("~goal_angle", radians(angle)) # degrees converted to radians  
        rotation = self.rotation 
        # Track the last angle measured
        last_angle = rotation

        # Set the movement command to a rotation
        move_cmd.angular.z = self.angular_speed  if goal_angle > 0 else -self.angular_speed    
        
        # Begin the rotation
        while abs(turn_angle + self.angular_tolerance) < abs(goal_angle) and not rospy.is_shutdown():
            # Publish the Twist message and sleep 1 cycle         
            self.cmd_vel.publish(move_cmd)            
            self.rate.sleep()
            # Get the current rotation
            rotation = self.rotation
            
            # Compute the amount of rotation since the last lopp
            delta_angle = normalize_angle(rotation - last_angle)           
            turn_angle += delta_angle           
            last_angle = rotation
            
       
       #Stop the robot when we are done    
        move_cmd = Twist()
        self.cmd_vel.publish(move_cmd)
        rospy.sleep(1.0)
        rospy.loginfo('Robot Turned %s. degrees.' %(math.degrees(normalize_angle(turn_angle))))  
        
       

        
  
    
    def model_stateCallback(self,data):
    #rostopic echo /gazebo/model_states |grep "x: 5."
    #rostopic echo /gazebo/model_states |grep 'x: 2[.]'
    #see http://answers.ros.org/question/30227/turtlebot-autonomous-navigation-without-rviz/ 
    #see http://answers.ros.org/question/9686/how-to-programatically-set-the-2d-pose-on-a-map/
    #using http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29
    #using http://wiki.ros.org/navigation/Tutorials/RobotSetup/Odom
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space:  
    #in order to get navigation working you need to publish 2 types of messages. a TF message and an Odomety message.
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space
    #######################################################################################################################        
           
        
         
         #Splitting the test file and put in list
         #http://stackoverflow.com/questions/11870399/python-regex-find-numbers-with-comma-in-string
         #http://stackoverflow.com/questions/21744804/python-read-comma-separated-values-from-a-text-file-then-output-result-to-tex
         #http://www.pythonforbeginners.com/dictionary/python-split
          self.model_states_msg_cnt=(self.model_states_msg_cnt+1)%self.Downsample_rate
          
          if self.model_states_msg_cnt == 0: 
              
              strdata=str(data)                    
              k=strdata.split(']') 
              k=k[0].split('[') 
              k=k[1].split(',')          
              indices = [i for i, s in enumerate(k) if 'mobile_base' in s]     #finding the index of the jackal position in the header section
             
                     
              #Reading the file and extracting coordinates of the
              #objects in the world
            
              i=indices[0]
              jackal_pose=data.pose[i]
              trans= [jackal_pose.position.x , jackal_pose.position.y ,jackal_pose.position.z]  
              self.position=Point(*trans)
              rot= [jackal_pose.orientation.x , jackal_pose.orientation.y , jackal_pose.orientation.z , jackal_pose.orientation.w]  
              self.rotation=quat_to_angle(Quaternion(*rot))
              rospy.loginfo(self.position.x)  
              #rospy.loginfo(math.degrees(normalize_angle(self.rotation)))                      
      
          else:
              return
              

        
    def shutdown(self):
        # stop jackal
        rospy.loginfo("Stop Jackal")
        # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop Jackal
        self.cmd_vel.publish(Twist())
        # sleep just makes sure Jackal receives the stop command prior to shutting down the script
        rospy.sleep(1)


       
    # Get the current transform between the odom and base frames
    # see https://github.com/pirobot/ros-by-example/blob/master/rbx_vol_1/rbx1_nav/nodes/nav_square.py
    def get_odom(self):
        # Get the current transform between the odom and base frames
        try:
            (trans, rot)  = self.tf_listener.lookupTransform(self.odom_frame, self.base_frame, rospy.Time(0))
            self.odometry_on=True
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            rospy.loginfo("TF Exception")
            self.odometry_on=False 
        rospy.loginfo('odom')
        rospy.loginfo(trans)
        #rospy.loginfo(rot)
        return (Point(*trans), quat_to_angle(Quaternion(*rot))) 




#I don't undertand the args thing
#Just use it as is        
def main(args):       
     rospy.init_node('navigation', anonymous=False)
     navigation().navigate()
     try:
         rospy.spin()
     except KeyboardInterrupt:
          rospy.loginfo("navigation node terminated")
  
if __name__ == '__main__':
    main(sys.argv)


