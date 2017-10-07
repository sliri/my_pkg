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

########################################################################
#MAIN EXAMPLE TAKEN FORM
#https://github.com/markwsilliman/turtlebot/blob/master/goforward.py
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
       
        
        
        # Publishing rate = 100 Hz look for odometry
        #for sleeping and rate see
        #http://wiki.ros.org/rospy/Overview/Time         
        self.rate = rospy.Rate(10)
        rospy.loginfo('Waiting for odometry to become available..')
        while (not self.odometry_on):
            rospy.loginfo("Odometry on is %s !" %self.odometry_on)
            rospy.sleep(1)
        
        rospy.loginfo("Odometry on is %s !" %self.odometry_on) 
        
    
    
    
    
        
    #The main navigation function    
    def navigate(self):
         # Twist is a datatype for velocity
         self.move_cmd = Twist()
         # let's go forward at 0.2 m/s 
         self.move_cmd.linear.x = 0.2
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
          print(trans,rot)
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
     navigation()     
     rospy.init_node('navigation', anonymous=False)
     navigation().navigate()
     try:
         rospy.spin()
     except KeyboardInterrupt:
          rospy.loginfo("navigation node terminated")
  
if __name__ == '__main__':
    main(sys.argv)


