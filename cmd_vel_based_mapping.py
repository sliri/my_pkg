#!/usr/bin/env python

import rospy
import roslib
roslib.load_manifest('my_pkg')
import sys
from std_srvs.srv import Empty, Trigger, TriggerResponse
from geometry_msgs.msg import Twist
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


########################################################################
#MAIN EXAMPLE TAKEN FORM
#https://github.com/markwsilliman/turtlebot/blob/master/goforward.py
# ros-by-example/rbx_vol_1/rbx1_nav/nodes/nav_square.py 
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
             

        
        # Subscribe to the odom topic and set 
        # the appropriate callbacks 
        # rospy.Subscriber("topic Name", msg type, callback)
        #The acllback is called whenever a new msg comes
        # see http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28python%29
        # see http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29
        self.odom_sub = rospy.Subscriber('/jackal_velocity_controller/odom', Odometry, self.odom_callback)
        
        #Here, we create a tf.TransformListener object. Once the listener is created,
        #it starts receiving tf transformations over the wire, and buffers them for up to 10 seconds. 
        # see http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29       
        self.tf_listener = tf.TransformListener()
       
        
        #initilize  odometry_on  FLAG       
        self.odometry_on=False                  
        #Name of  frames - NOT user defined! best thing to do is runing
        # rostopic echo '/jackal_velocity_controller/odom' and get the names
        # or rostopic type /topic_name | rosmsg show
        self.frame_id = '/odom'
        self.child_id = '/base_link'      
                
        self.linear_velocity =0.3#0.1  #m/sec
        self.angular_velocity =math.radians(100) #rad/sec
        self.angular_speed = rospy.get_param("~angular_speed", 0.7) # radians per second
        self.angular_tolerance = rospy.get_param("~angular_tolerance", radians(0.5)) # degrees to radians
        self.linear_tol = 0.2     
        self.angular_tol = 0.5
   
       # Create publisher for cmd_vel topic
       # cmd_vel publisher can "talk" to Jackal and tell it to move             
        self.cmd_vel = rospy.Publisher('/jackal_velocity_controller/cmd_vel', Twist, queue_size=10)
        
#         #Velocities,tolerances
#        self.angular_velocity = math.radians(5) #rad/sec
#        self.linear_velocity =0.1#0.1  #m/sec
#        self.linear_tol = 0.2     
#        self.angular_tol = 1
#        self.xtarget=6
#        self.ytarget=0
#        
       
        
        
        # Publishing rate = 200 Hz look for odometry
        #for sleeping and rate see
        #http://wiki.ros.org/rospy/Overview/Time         
        self.rate = rospy.Rate(20)
        rospy.loginfo('Waiting for odometry to become available..')
        while (not self.odometry_on):
            rospy.loginfo("Odometry on is %s !" %self.odometry_on)
            rospy.sleep(1)
        
        rospy.loginfo("Odometry on is %s !" %self.odometry_on) 
        
    
    
    
      
    def navigate(self): 
     #self.odom_based_linear_move(1) 
     self.odom_based_rotate_by_angle(90)
     self.rate.sleep()
     #self.shutdown
      
     #self.turn()
           
    def odom_based_linear_move(self,distance):
    #Distance In meters
     # Twist is a datatype for velocity
        self.move_cmd = Twist()
        #Stop all angular move,set linear velocity       
        self.move_cmd.angular.z = 0
        self.move_cmd.linear.x = self.linear_velocity if distance > 0 else -self.linear_velocity
        #initial positions sampled
        rospy.loginfo("%s"%self.x)
        
        x_start = self.x
        y_start = self.y
        #Havn't yet go anyware
        actual_distance= 0        
        while abs(actual_distance -abs(distance)) > self.linear_tol:
            #start moving           
            if self.odometry_on:
             self.cmd_vel.publish(self.move_cmd)
             self.rate.sleep()
             #Update
             actual_distance = math.sqrt((pow((self.x - x_start), 2) + pow((self.y - y_start), 2)))
         #Stop!       
        self.move_cmd.linear.x = 0
        rospy.loginfo('Robot Moved %s. meters.' % (actual_distance))       
        return actual_distance
    
 
  
    
             
#    def odom_based_rotate_by_angle(self, rotate_by_angle):
#        
#        # all angles are in degrees
#        # Twist is a datatype for velocity
#        self.move_cmd = Twist()
#        actual_turn_angle = 0
#        last_rotation=self.rotation
#        #Stop all linear move,set angular velocity 
#        self.move_cmd.angular.z = self.angular_velocity if rotate_by_angle > 0 else -self.angular_velocity            
#        self.move_cmd.linear.x = 0
#        while (abs(rotate_by_angle) - abs(actual_turn_angle) > self.angular_tol):            
#           # if self.odometry_on: 
#             self.cmd_vel.publish(self.move_cmd)             
#            # 
#             #Update
#             delta_theta = normalize_angle(last_rotation - self.rotation)
#             actual_turn_angle += delta_theta
#             self.rate.sleep()
#            
#        #Stop! 
#        self.move_cmd.angular.z=0
#        rospy.loginfo('Robot Turned %s. degrees.' % (actual_turn_angle))       
#        return actual_turn_angle
#    
#    
    
    
    
    

    #rotate by a specific angle
    #see https://github.com/pirobot/ros-by-example/blob/master/rbx_vol_1/rbx1_nav/nodes/nav_square.py         
    def odom_based_rotate_by_angle(self, angle):
        # Stop the robot before rotating
        move_cmd = Twist()
        self.cmd_vel.publish(move_cmd)
        rospy.sleep(1.0)
        
        # Track how far we have turned
        turn_angle = 0
        goal_angle = rospy.get_param("~goal_angle", radians(angle)) # degrees converted to radians  
        rotation = self.rotation
        # Track the last angle measured
        last_angle = self.rotation

        # Set the movement command to a rotation
        move_cmd.angular.z = self.angular_speed        
        
        # Begin the rotation
        while abs(turn_angle + self.angular_tolerance) < abs(goal_angle) and not rospy.is_shutdown():
            # Publish the Twist message and sleep 1 cycle         
            self.cmd_vel.publish(move_cmd)            
            self.rate.sleep()
            # Get the current rotation
            rotation =  self.rotation           
            
            # Compute the amount of rotation since the last lopp           
            delta_angle = normalize_angle(rotation - last_angle)
            
            turn_angle += delta_angle
           # rospy.loginfo('Robot Turned %s. degrees.' % (delta_angle))       
            last_angle = rotation

        move_cmd = Twist()
        self.cmd_vel.publish(move_cmd)
        rospy.sleep(1.0)
        
        # Stop the robot when we are done
        self.cmd_vel.publish(Twist())
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    #go farward function    
    def go_farward(self):
         # Twist is a datatype for velocity
         self.move_cmd = Twist()
         # let's go forward at 0.2 m/s 
         self.move_cmd.linear.x = self.linear_velocity
         # let's turn at 0 radians/s
         self.move_cmd.angular.z = 0
         
         
         #Jackal will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
         rate = rospy.Rate(10.0)
         # as long as you haven't ctrl + c keeping doing...
         while not rospy.is_shutdown():
             # publish the velocity
             self.cmd_vel.publish(self.move_cmd) 
            
             # wait for 0.1 seconds (10 HZ) and publish again             
             #for sleeping and rate see
             #http://wiki.ros.org/rospy/Overview/Time
             rate.sleep()  
             
             
    #turn command    
    def turn(self):
         # Twist is a datatype for velocity
         self.move_cmd = Twist()
         # let's go forward at 0.2 m/s 
         self.move_cmd.linear.x = 0
         # let's turn at 0 radians/s
         self.move_cmd.angular.z = 0.2
         
         #Jackal will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
         rate = rospy.Rate(10.0)
         # as long as you haven't ctrl + c keeping doing...
         while not rospy.is_shutdown():
             # publish the velocity
             self.cmd_vel.publish(self.move_cmd) 
             rospy.loginfo("%s"%abs(self.rotation))
             # wait for 0.1 seconds (10 HZ) and publish again             
             #for sleeping and rate see
             #http://wiki.ros.org/rospy/Overview/Time
             rate.sleep()            

        
    def shutdown(self):
        # stop jackal
        rospy.loginfo("Stop Jackal")
        # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop Jackal
        self.cmd_vel.publish(Twist())
        # sleep just makes sure Jackal receives the stop command prior to shutting down the script
        rospy.sleep(1)



    def odom_callback(self,ros_odom):
    #using http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29
    #using http://wiki.ros.org/navigation/Tutorials/RobotSetup/Odom
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space:  
    #in order to get navigation working you need to publish 2 types of messages. a TF message and an Odomety message.
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space
    #######################################################################################################################        
        #Here, we create a tf.TransformListener object.Once the listener is created, it starts receiving tf transformations
        #over the wire, and buffers them for up to 10 seconds.
        #self.listener = tf.TransformListener()     
        try:
          #We want the transform from a "odom" coordinate frame to a "base_link" coordinate frame over tf.
          (trans,rot) = self.tf_listener.lookupTransform(self.frame_id,self.child_id,rospy.Time(0))
          #print(trans,rot)
          #defining and extracting x,y & theta in a nice way for later use..
          angles = euler_from_quaternion(rot)
          self.x=trans[0]
          self.y=trans[1]
          self.rotation = math.degrees(angles[2])
          self.odometry_on=True
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
          self.odometry_on=False
             
         





#I don't undertand the args thing
#Just use it as is        
def main(args):
     #navigation()     
     rospy.init_node('navigation', anonymous=False)
     navigation().navigate()
     try:
         rospy.spin()
     except KeyboardInterrupt:
          rospy.loginfo("navigation node terminated")
  
if __name__ == '__main__':
    main(sys.argv)


