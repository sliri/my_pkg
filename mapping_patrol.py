#!/usr/bin/env python

import rospy
import roslib
roslib.load_manifest('my_pkg')
import sys
from std_srvs.srv import Empty, Trigger, TriggerResponse
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import String
from std_msgs.msg import Float32
import tf
import math
import numpy as np
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion





class GoToPose():
    def __init__(self):
    # constants, states, flags    
     self.goal_sent = False  #flag
     self.orchard_dx=1.5     #meter
     self.orchard_dy=1.5     #meter
     self.orchard_rows =8   #num of rows in the orchard 
     self.orchard_columns=8 #num of cols in the orchard      
     self.states=['st_idle','st_going_south','st_mapping_patrol','st_end'] #state machine states
     self.current_state='st_idle'     
  
 
        
     # What to do if shut down (e.g. Ctrl-C or failure)
     rospy.on_shutdown(self.shutdown)
        	
     # Tell the action client that we want to spin a thread by default
     self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
     rospy.loginfo("Wait for the action server to come up")
     
     # Allow up to 5 seconds for the action server to come up
     self.move_base.wait_for_server(rospy.Duration(5))
     self.current_state='st_going_south'
     rospy.loginfo("%s" % self.current_state)
         
            	
   




    def navigate(self):
        if(self.goto_southwest()):
            self.patrol()
        
        

                                                                                        
#This function takes the 
#jackal to the south west point of the orchard    
###########################################################
    def goto_southwest(self): 
#       Publishing rate = 100 Hz       
      self.rate = rospy.Rate(10) 
      while not self.current_state=='st_patrol':   
           
          if self.current_state=='st_idle':
              rospy.loginfo("%s" % self.current_state)
              self.rate.sleep() #Do nothing
              if self.move_base.wait_for_server():
                 self.current_state='st_going_south'
                 
                 
          elif self.current_state=='st_going_south':
              # Customize the following values so they are appropriate for your location
              position = {'x':  self.orchard_dx*(self.orchard_rows+1)/2, 'y' : 0}
              quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
              ###########################################################################
              rospy.loginfo("%s" % self.current_state)
              success = self.goto(position, quaternion)
              if success:
                  self.current_state='st_going_west'
                  
                     
          elif self.current_state=='st_going_west':
              # Customize the following values so they are appropriate for your location
              position = {'x':  self.orchard_dx*(self.orchard_rows+1)/2, 'y' : -self.orchard_dx*(self.orchard_columns+1)/2}
              quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.5, 'r4' : 0.4}
              ###########################################################################
              rospy.loginfo("%s" % self.current_state)
              success = self.goto(position, quaternion)
              if success:
                  self.current_state='st_patrol'       
                  
      return  success               
               
                  
                  







   
#This function makes the jackal patrol all over the orchard 
###########################################################
    def patrol(self): 
#       Publishing rate = 100 Hz       
      self.rate = rospy.Rate(10)
      
      if self.current_state=='st_patrol': 
       i=0   
       while i < self.orchard_columns:
           
              self.patrol_state='st_go up'
                 
              if  self.patrol_state=='st_go up':
                  #go up
                  # Customize the following values so they are appropriate for your location                  
                  position = {'x':  -self.orchard_dx*(self.orchard_rows+1)/2, 'y' : -self.orchard_dx*(self.orchard_columns+1)/2+(i)*self.orchard_dy}
                  quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
                  ###########################################################################
                  rospy.loginfo("%s" % self.patrol_state)
                  success = self.goto(position, quaternion)
                  if success:
                      self.patrol_state='st_go_right'
              
              if  self.patrol_state=='st_go_right':
                  #go right
                  # Customize the following values so they are appropriate for your location                  
                  position = {'x':  -self.orchard_dx*(self.orchard_rows+1)/2, 'y' : -self.orchard_dx*(self.orchard_columns+1)/2+(i+1)*self.orchard_dy}
                  quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
                  ###########################################################################
                  rospy.loginfo("%s" % self.patrol_state)
                  success = self.goto(position, quaternion)
                  if success:
                      self.patrol_state='st_go_down' 
                      
                      
              if  self.patrol_state=='st_go_down':
                  #go right
                  # Customize the following values so they are appropriate for your location                  
                  position = {'x':  self.orchard_dx*(self.orchard_rows+1)/2, 'y' : -self.orchard_dx*(self.orchard_columns+1)/2+(i+1)*self.orchard_dy}
                  quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
                  ###########################################################################
                  rospy.loginfo("%s" % self.patrol_state)
                  success = self.goto(position, quaternion)
                  if success:
                      self.patrol_state='st_go_next_column' 
                      
                       
              if  self.patrol_state=='st_go_next_column':
                  #go right
                  # Customize the following values so they are appropriate for your location                  
                  position = {'x':   self.orchard_dx*(self.orchard_rows+1)/2, 'y' : -self.orchard_dx*(self.orchard_columns+1)/2+(i+2)*self.orchard_dy}
                  quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
                  ###########################################################################
                  rospy.loginfo("%s" % self.patrol_state)
                  success = self.goto(position, quaternion)
                  if success:
                      i=i+1       
                                        
                  
       self.current_state=='st_end_patrol'      
       rospy.loginfo("%s" % self.current_state)  
                  

#This function makes the jackal go to a specific location 
###########################################################   
   
    def goto(self, pos, quat):

        # Send a goal
        self.goal_sent = True
	goal = MoveBaseGoal()
	goal.target_pose.header.frame_id = 'odom'
	goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

	# Start moving
        #rospy.loginfo("Go to (%s, %s) pose", pos['x'], quat['y'])
        rospy.loginfo("Go to (%s, %s) pose", pos['x'], pos['y'])
        self.move_base.send_goal(goal)

	# Allow TurtleBot up to 120 seconds to complete task
	success = self.move_base.wait_for_result(rospy.Duration(120)) 

        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False

        if result:
            rospy.loginfo("Hooray, reached the desired pose")
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)       
        
        return result
        
        

    def shutdown(self):
        if  self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)

if __name__ == '__main__':
    try:
        rospy.init_node('nav_test', anonymous=False)
        GoToPose()
        GoToPose().navigate() 
       
       
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")