#!/usr/bin/env python

import rospy
import sys
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from sensor_msgs.msg import Image
#from cv_bridge import CvBridge, CvBridgeError
#import numpy as np
#import math
#import tf
#from nav_msgs.msg import Odometry
#from tf.transformations import euler_from_quaternion




class navigation():
    def __init__(self):
        # initiliaze
        rospy.init_node('navigation', anonymous=True)
        
        # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")
       
       # What function to call when you ctrl + c    
        rospy.on_shutdown(self.shutdown)

       # Create a publisher which can "talk" to TurtleBot and tell it to move
        # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
        self.cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)            
      
        
        # Publishing rate = 100 Hz        
        self.rate = rospy.Rate(10)              
        rospy.loginfo('Waiting for depth image and odometry to become available')
        

            
   
    def navigate(self): 
	self.move_cmd = Twist()  
        
        while True:
         
          
             
             self.move_cmd.linear.x = 5
             self.move_cmd.angular.z = 8
             self.rate.sleep()      
                            
		     
        
            
        
    #def odom_based_linear_move(self,distance):
    ##Distance In meters
        ##Stop all angular move,set linear velocity        
        #self.move_cmd.angular.z = 0
        #self.move_cmd.linear.x = self.linear_velocity if distance > 0 else -self.linear_velocity
        ##initial positions sampled
        #x_start = self.x
        #y_start = self.y
        ##Havn't yet go anyware
        #actual_distance= 0         
        #while abs(actual_distance -abs(distance)) > self.linear_tol:
            ##start moving            
            #if self.odometry_on:
             #self.cmd_vel.publish(self.move_cmd)
             #self.rate.sleep()
             ##Update
             #actual_distance = math.sqrt((pow((self.x - x_start), 2) + pow((self.y - y_start), 2)))
         ##Stop!        
        #self.move_cmd.linear.x = 0
       ##print('Robot Moved %s. meters.' % (actual_distance))
       ##print('Current Position is (%s,%s) .' % (self.x,self.y))
        
        
        
    #def odom_based_rotate_by_angle(self, rotate_by_angle): 
        ## all angles are in degrees
        #actual_turn_angle = 0
        #last_rotation = self.rotation
        ##Stop all linear move,set angular velocity  
        #self.move_cmd.angular.z = self.move_cmd.angular.z=self.angular_velocity if rotate_by_angle > 0 else -self.angular_velocity             
        #self.move_cmd.linear.x = 0
        #while abs(actual_turn_angle - rotate_by_angle) > self.angular_tol:
            #if self.odometry_on:  
             #self.cmd_vel.publish(self.move_cmd)  
             #self.rate.sleep()
             ##Update
             #delta_theta = (self.rotation - last_rotation)%360
             #actual_turn_angle += delta_theta
             #last_rotation = self.rotation          
   
        #self.move_cmd.angular.z=0
        
 
         
          
      
      
    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop TurtleBot")
  # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
        self.cmd_vel.publish(Twist())
  # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)
 

        
        
        

        
        
def main(args):
     move=navigation()     
     rospy.init_node('navigation', anonymous=True)
     move.navigate()
     try:
         rospy.spin()
     except KeyboardInterrupt:
          rospy.loginfo("navigation node terminated")
  
if __name__ == '__main__':
    main(sys.argv)
