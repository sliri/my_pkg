#!/usr/bin/env python

import rospy
import roslib
roslib.load_manifest('hw2')
import sys
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import math
import tf
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

## MAIN EXAMPLE FROM 
#https://github.com/markwsilliman/turtlebot/blob/master/goforward.py
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
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
#    
        #subscribing to the depth image topic. The callback methos updates each image       
        # Create the cv_bridge object       
        self.bridge = CvBridge()
         
        # Subscribe to the depth topic and set
        # the appropriate callbacks  
        self.depth_image_sub = rospy.Subscriber("/camera/depth/image_raw",Image,self.depth_image_callback)
         
        # Subscribe to the odom topic and set
        # the appropriate callbacks
        self.odom_sub = rospy.Subscriber('/jackal_velocity_controller/odom', Odometry, self.odom_callback)
        self.tf_listener = tf.TransformListener()
        #self.tf_listener.waitForTransform('/odom', '/base_footprint', rospy.Time(), rospy.Duration(1.0))         
        #initilize  odometry_on and depth_image_on  FLAG      
        self.odometry_on=False
        self.depth_image_on = False 
        self.middle_row=[]     
        #Name of  frames  
        self.frame_id = '/odom'
        self.child_id = '/base_footprint' 
         
        #Velocities,tolerances
        self.angular_velocity = math.radians(5) #rad/sec
        self.linear_velocity =0.1#0.1  #m/sec
        self.linear_tol = 0.2     
        self.angular_tol = 1
        self.xtarget=6
        self.ytarget=0
        self.states=['st_idle','edge_focusing']
        self.current_state= 'stay_still'
        self.edge_focus_finished=False
        self.surround_started = False
        self.surround_finished = False
        #Writing on screen..     
        rospy.loginfo("Waiting for image topics...")
         
        # Publishing rate = 100 Hz       
        self.rate = rospy.Rate(10)
        rospy.loginfo('Waiting for depth image and odometry to become available..')
        while (not self.depth_image_on or not self.odometry_on):
            rospy.loginfo('.')
            rospy.sleep(1)
          
          
 
    def navigate(self): #sampling rising_edge? 
        self.move_cmd = Twist()
        #self.odom_based_rotate_by_angle(5)   
        #self.cmd_vel.publish(self.move_cmd)
        if self.odometry_on and self.depth_image_on:
         self.find_angle_to_target()
         print self.target_angle
         self.odom_based_rotate_by_angle(self.target_angle)
         self.rate.sleep()
         while not self.reached_target():
          self.rate.sleep() 
          if self.current_state=='linear_move':
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0
              self.find_angle_to_target()
              while (self.target_angle-self.rotation)%180>2 and (self.target_angle-self.rotation)%180<178:
		self.rate.sleep() 
		self.find_angle_to_target()
		print (self.target_angle-self.rotation)%180,self.x,self.y,self.xtarget,self.ytarget
		if (self.target_angle-self.rotation)%180>90  and (self.target_angle-self.rotation)%180<178:
		  self.odom_based_rotate_by_angle(-2)
		  rospy.sleep(1)
		  print (self.target_angle-self.rotation)%180
		if (self.target_angle-self.rotation)%180>2 and(self.target_angle-self.rotation)%180<90:
		  self.odom_based_rotate_by_angle(2)
		  rospy.sleep(1)
		  print (self.target_angle-self.rotation)%180
	      self.odom_based_linear_move(0.3)
	      print (self.target_angle-self.rotation)%180,self.x,self.y,self.xtarget,self.ytarget
          elif self.current_state=='edge_focusing':
              self.edge_finder()
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0                      
          elif self.current_state=='surrounding':
              self.surround_obstacle()
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0
          elif self.current_state=='stay_still':
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0
          elif self.current_state=='obstacle_stay_still':
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0
              #rospy.sleep(1)
              self.rate.sleep()
	  elif self.current_state=='finding_closest_point':
	      self.find_angle_to_target()
	      #while abs(self.target_angle%180)>1:
		#self.rate.sleep()
	      self.find_angle_to_target()
              #while (self.target_angle-self.rotation)%180>3 or (self.target_angle-self.rotation)%180<-3:
		#self.rate.sleep() 
		#self.find_angle_to_target()
		#print (self.target_angle-self.rotation)%180,self.x,self.y,self.xtarget,self.ytarget
		#if (self.target_angle-self.rotation)%180<-2:
		  #self.odom_based_rotate_by_angle(-5)
		  #rospy.sleep(1)
		  #print (self.target_angle-self.rotation)%180+10000,self.target_angle,self.rotation
		#if (self.target_angle-self.rotation)%180>2:
		  #self.odom_based_rotate_by_angle(5)
		  #rospy.sleep(1)
		  #print (self.target_angle-self.rotation)%180-10000,self.target_angle,self.rotation
	      self.goto_target_closest_point()
          self.cmd_vel.publish(self.move_cmd)
          print(self.current_state,np.argmin(self.middle_row), self.surround_finished)
          self.state_machine()
   
   
    def state_machine(self):          
      if self.current_state=='stay_still':
          if self.reached_target():
              self.current_state='target_reached'        
          elif not self.obstacle_found():
               self.current_state='linear_move'
          elif self.obstacle_found():
               self.current_state='obstacle_stay_still'     
      elif self.current_state=='obstacle_stay_still':           
           if not self.edge_focus_finished:
              self.current_state='edge_focusing'
           elif self.edge_focus_finished and not self.surround_finished:
               self.current_state='surrounding'
           elif self.edge_focus_finished  and self.surround_finished :
               self.current_state='obstacle_stay_still'
           else:
               self.current_state='stay_still'
                    
      elif self.current_state=='linear_move':
           if self.reached_target():
              self.current_state='stay_still'
           elif self.obstacle_found():
              self.current_state='obstacle_stay_still'
           else:
              self.current_state='linear_move'             
      elif self.current_state=='edge_focusing':
           if self.edge_focus_finished:
              self.current_state='obstacle_stay_still'
           else:
              self.current_state='edge_focusing'             
      elif self.current_state=='surrounding':
           if self.surround_finished:
              self.current_state='finding_closest_point'
              self.reached_point = False
           else:
              self.current_state='surrounding'
      elif self.current_state=='finding_closest_point':
	    print self.reached_point,self.closest_x,self.closest_y
	    if self.reached_point:
	      self.current_state='stay_still'
     

 
    def  edge_finder(self):
        self.edge_focus_finished = False
        #In the begining stop the robot
        self.move_cmd.linear.x = 0
        self.move_cmd.angular.z = 0
        #Intilizing.. 
        #Flag for signaling that the rotation has finished
        #surround_started = False
        #sampling      
        #The closest pixel that caused us to stop           
        index_middle_row = np.argmin(self.middle_row)
        #Difference vector, for detecting edges of the objetct
        vec_diff = abs(np.diff(self.middle_row))       
        #Suspected edges- a list of all pixels (indexes!) which are suspected to be an edge (diff>1meter)                         
        index_vec_deff = np.where(vec_diff>1)[0]
        left_index_vec_deff = [val for val in index_vec_deff if val <= index_middle_row]
        #the obstacle is huge and there are no edges
        #since the obstacle covers the entire frame
        #The best thing is probably to rotate by 5Deg till you find one
        while not(left_index_vec_deff):
              self.rate.sleep()
              print left_index_vec_deff
              self.odom_based_rotate_by_angle(2)
              self.move_cmd.linear.x = 0
              self.move_cmd.angular.z = 0
              #Updating....
              #Difference vector, for detecting edges of the objetct
              index_middle_row = np.argmin(self.middle_row)
              vec_diff = abs(np.diff(self.middle_row))            
              #Suspected edges- a list of all pixels (indexes!) which are suspected to be an edge (diff>1meter)                         
              index_vec_deff = np.where(vec_diff>1)[0]
              left_index_vec_deff =[val for val in index_vec_deff if val <= index_middle_row]
              
        self.move_cmd.linear.x = 0
        self.move_cmd.angular.z = 0
        self.edge_focus_finished = True
        #rospy.sleep(4)
         
        
         
         
       
 
    def surround_obstacle(self):
        self.surround_started = False
        self.surround_finished = False 
        #In the begining stop the robot
        self.move_cmd.linear.x = 0
        self.move_cmd.angular.z = 0
        self.min_distanse_to_target = np.inf
        #Intilizing.. 
        #sampling    
        starting_position_x = self.x
        starting_position_y = self.y      
       # bounds      
        lower_bound= 500
        upper_bound= 640    
        way_to_close = False
        print(starting_position_x,starting_position_y)
        self.angle_rotated = 0
#       The main loop- loop until the complete round has finished ... 
        shipua=math.atan2(self.ytarget,self.xtargetx)     
        while (not (abs(self.y-shipua*self.x)<(self.linear_tol) or (not self.surround_started)): 
            
            #print abs(self.y-starting_position_y),abs(self.x-starting_position_x)
            #UPDATE
            # The closest pixel that caused us to stop
            self.find_colosest_pos_to_target()
            index_middle_row = np.argmin(self.middle_row)
           #Difference vector, for detecting edges of the objetct
            vec_diff = abs(np.diff(self.middle_row))
            #Suspected edges- a list of all pixels (indexes!) which are suspected to be an edge (diff>1meter)                         
            index_vec_deff = np.where(vec_diff>1)[0]
            left_index_vec_deff=[val for val in index_vec_deff if val <= index_middle_row]
            #finding the differnce between the suspected edges index and the closet point index:       
            #No Edge?           
            if not any(index_vec_deff):                      
                 #print("No Edge",left_index_vec_deff,index_middle_row)
                                  
                 self.move_cmd.linear.x = 0
                 self.move_cmd.angular.z = 0        
                 if not way_to_close:		# if there is no edge and we are to close 
		   self.odom_based_rotate_by_angle(-2)
		   self.angle_rotated += 2
                 else:				# there is no adge and we're not to close
		   self.odom_based_linear_move(0.5)
		   self.surround_started=True
		   way_to_close = False
                 #self.odom_based_linear_move(0.2)
                 #rospy.sleep(1)
                 self.move_cmd.linear.x = 0
                 self.move_cmd.angular.z = 0
                 self.rate.sleep()		  
                 #index_middle_row = np.argmin(self.middle_row)
                 #Difference vector, for detecting edges of the objetct
                 #vec_diff = abs(np.diff(self.middle_row))
                 #Suspected edges- a list of all pixels (indexes!) which are suspected to be an edge (diff>1meter)                         
                 #index_vec_deff = np.where(vec_diff>1)[0]
                 #left_index_vec_deff=[val for val in index_vec_deff if val <= index_middle_row]
                 #print(left_index_vec_deff)
                  
 
             
            #there is an edge                                  
            else:   
                #for ind in left_index_vec_deff:
		self.move_cmd.linear.x = 0
		self.move_cmd.angular.z = 0
		arguments=(abs(left_index_vec_deff-index_middle_row))
		  #The closest edge to the minimal point (pixel index in index_vec_deff)
		closest_gap_index = np.argmin(arguments)               
		  #finally, the closest edge pixel (from the left)...
		closest_edge=left_index_vec_deff[closest_gap_index]
		#print arguments,closest_gap_index,closest_edge
		dep = self.middle_row[closest_edge+1]
		#print dep 
		#rospy.sleep(1)
		#if len(self.index_vec_deff)>1:
		    #self.argument = abs(self.index_vec_deff-self.index_middle_row)
		    #self.closest_gap_index = np.argmin(self.argument)
		#else:
		    #self.closest_gap_index = 0
		self.rate.sleep()             
            #keep track of the edge on the right side of the frame. between
            #uspper and lower bounds..
             
            #Too close!
		if self.too_close():                                            
                     self.move_cmd.linear.x = 0
                     self.move_cmd.angular.z = 0                    
                     #print("Way Too Close!")
                     if (self.angle_rotated==0):   			# first time we saw obstacle
		       self.odom_based_rotate_by_angle(2)
                     else:
		       self.odom_based_rotate_by_angle(self.angle_rotated)
                     self.angle_rotated = 0
                     way_to_close = True
		else:
                  if (closest_edge<=lower_bound):
                      print("Quite Close!",arguments,closest_gap_index,closest_edge)
#                      #Manuver to avoid colision
                                           
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0                      
                      self.odom_based_rotate_by_angle(2)
                                    
                      
           #Too Far!         
                  elif (closest_edge>=upper_bound):
                      print("Quite Far",arguments,closest_gap_index,closest_edge)
                      #Manuver to avoid colision                     
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0                      
                      self.odom_based_rotate_by_angle(-2)
                      
                      
#            #Bounds o.k-go farward         
                  else:         
                      print("bingo",arguments,closest_gap_index,closest_edge)                     
                      if self.surround_started:
			self.odom_based_linear_move(0.05)
                      else:
			self.odom_based_linear_move(0.5)		      
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0
                      self.surround_started=True
                      self.rate.sleep()
                      #rospy.sleep(4)
                       #corner!!!!!!!!!!!!!!!!!!!!!!!!!!!!! in that case- no edge at all
#                     
                 
        self.move_cmd.linear.x = 0
        self.move_cmd.angular.z = 0              
        self.surround_finished = True
                  
    def goto_target_closest_point(self):
        self.surround_finished = False 
        In the begining stop the robot
        # self.move_cmd.linear.x = 0
        # self.move_cmd.angular.z = 0
        self.min_distanse_to_target = np.inf
        #Intilizing.. 
        #sampling    
       # bounds      
        lower_bound= 500
        upper_bound= 640    
        way_to_close = False
        self.angle_rotated = 0
        print self.closest_x,self.closest_y,self.x,self.y
#       The main loop- loop until the complete round has finished ...      
        while (not (abs(self.x-self.closest_x)<(self.linear_tol) and abs(self.y-self.closest_y)<(self.linear_tol))):
            
            print abs(self.y-self.closest_y),abs(self.x-self.closest_x)
            #UPDATE
            index_middle_row = np.argmin(self.middle_row)
            vec_diff = abs(np.diff(self.middle_row))
            #Suspected edges- a list of all pixels (indexes!) which are suspected to be an edge (diff>1meter)                         
            index_vec_deff = np.where(vec_diff>1)[0]
            left_index_vec_deff=[val for val in index_vec_deff if val <= index_middle_row]
            #finding the differnce between the suspected edges index and the closet point index:       
            #No Edge?           
            if not any(index_vec_deff):                      
                 self.move_cmd.linear.x = 0
                 self.move_cmd.angular.z = 0        
                 if not way_to_close:		# if there is no edge and we are to close 
		   self.odom_based_rotate_by_angle(-2)
		   self.angle_rotated += 2
                 else:				# there is no adge and we're not to close
		   self.odom_based_linear_move(0.5)
		   way_to_close = False
                 self.move_cmd.linear.x = 0
                 self.move_cmd.angular.z = 0
                 self.rate.sleep()		  
            #there is an edge                                  
            else:   
		self.move_cmd.linear.x = 0
		self.move_cmd.angular.z = 0
		arguments=(abs(left_index_vec_deff-index_middle_row))
		closest_gap_index = np.argmin(arguments)               
		closest_edge=left_index_vec_deff[closest_gap_index]
		print arguments,closest_gap_index,closest_edge
		dep = self.middle_row[closest_edge+1]
		print dep 
		self.rate.sleep()             
		#Too close!
		if self.too_close():                                            
                     self.move_cmd.linear.x = 0
                     self.move_cmd.angular.z = 0                    
                     print("Way Too Close!")
                     if (self.angle_rotated==0):   			# first time we saw obstacle
		       self.odom_based_rotate_by_angle(2)
                     else:
		       self.odom_based_rotate_by_angle(self.angle_rotated)
                     self.angle_rotated = 0
                     way_to_close = True
		else:
                  if (closest_edge<=lower_bound):
                      print("Quite Close!",arguments,closest_gap_index,closest_edge)
#                      #Manuver to avoid colision
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0                      
                      self.odom_based_rotate_by_angle(2)
		  #Too Far!         
                  elif (closest_edge>=upper_bound):
                      print("Quite Far",arguments,closest_gap_index,closest_edge)
                      #Manuver to avoid colision                     
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0                      
                      self.odom_based_rotate_by_angle(-2)
		  #Bounds o.k-go farward         
                  else:         
                      print("bingo",arguments,closest_gap_index,closest_edge)                     
                      self.odom_based_linear_move(0.1)
                      self.move_cmd.linear.x = 0
                      self.move_cmd.angular.z = 0
                      self.rate.sleep()
        self.move_cmd.linear.x = 0
        self.move_cmd.angular.z = 0              
        # self.reached_point = True
                       
    def depth_image_callback(self,ros_depth_image):
    #using http://wiki.ros.org/cv_bridge/Tutorials/ConvertingBetweenROSImagesAndOpenCVImagesPython
    #using http://ros-by-example.googlecode.com/svn/trunk/rbx_vol_1/rbx1_vision/nodes/cv_bridge_demo.py   
    # Use cv_bridge() to convert the ROS image to OpenCV format          
        try:
          # The depth image is a single-channel float32 image
          cv_depth_image = self.bridge.imgmsg_to_cv(ros_depth_image,"32FC1")
        except CvBridgeError, e:
          print e              
        # Convert the depth image to a Numpy array since most cv2 functions
        # require Numpy arrays.
        numpy_depth_image = np.array(cv_depth_image,dtype=np.float32)
        #(self.rows,self.cols,self.channels) = numpy_depth_image.shape
        self.rows=cv_depth_image.height
        self.cols=cv_depth_image.width         
        #get middle row , and replace the nan values
        #which are not comperable to inf
        #http://stackoverflow.com/questions/944700/how-to-check-for-nan-in-python
        self.middle_row=numpy_depth_image[(self.rows)/2]
        for i,value in enumerate(self.middle_row):
            if math.isnan(value):
             self.middle_row[i] = 100#np.inf           
        self.depth_image_on = True
        #print(self.middle_row)
  
    def odom_callback(self,ros_odom):
    #using http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29
    #using http://wiki.ros.org/navigation/Tutorials/RobotSetup/Odom
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space:  
    #in order to get navigation working you need to publish 2 types of messages. a TF message and an Odomety message.
    #The nav_msgs/Odometry message stores an estimate of the position and velocity of a robot in free space
       
        #Here, we create a tf.TransformListener object.Once the listener is created, it starts receiving tf transformations
        #over the wire, and buffers them for up to 10 seconds.
        #self.listener = tf.TransformListener()     
        try:
          #We want the transform from a "odom" coordinate frame to a "base_link" coordinate frame over tf.
          (trans,rot) = self.tf_listener.lookupTransform(self.frame_id,self.child_id,rospy.Time(0))
          angles = euler_from_quaternion(rot)
	  self.position=(trans[0],trans[1])
	  self.x=trans[0]
	  self.y=trans[1]
	  self.rotation = math.degrees(angles[2])
	  self.odometry_on=True
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
              self.odometry_on=False
              rospy.loginfo('waiting for odometery...')
         
         
    def odom_based_linear_move(self,distance):
    #Distance In meters
        #Stop all angular move,set linear velocity       
        self.move_cmd.angular.z = 0
        self.move_cmd.linear.x = self.linear_velocity if distance > 0 else -self.linear_velocity
        #initial positions sampled
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
       #print('Robot Moved %s. meters.' % (actual_distance))
       #print('Current Position is (%s,%s) .' % (self.x,self.y))
         
         
         
    def odom_based_rotate_by_angle(self, rotate_by_angle):
        # all angles are in degrees
        actual_turn_angle = 0
        last_rotation = self.rotation
        #Stop all linear move,set angular velocity 
        self.move_cmd.angular.z = self.angular_velocity if rotate_by_angle > 0 else -self.angular_velocity            
        self.move_cmd.linear.x = 0
        while abs(rotate_by_angle) - actual_turn_angle > self.angular_tol:
            #print('In');
            if self.odometry_on: 
             self.cmd_vel.publish(self.move_cmd) 
             self.rate.sleep()
             #Update
             delta_theta = abs(last_rotation - self.rotation)
             actual_turn_angle += delta_theta
             #print last_rotation
             #last_rotation = self.rotation
             #print rotate_by_angle,actual_turn_angle,delta_theta
             #rospy.sleep(1)
    
        self.move_cmd.angular.z=0
         
     
    def obstacle_found (self):
        if not self.depth_image_on:
            return False
        else:
         min_depth = np.inf
         for pixel in self.middle_row:
            min_depth = min(min_depth, pixel)           
         if min_depth < 0.45: # less than 1 meter
           return True
         else:
           return False
            
            
    def too_close (self):
        if not self.depth_image_on:
            return False
        else:
         min_depth = np.inf
         for pixel in self.middle_row:
            min_depth = min(min_depth, pixel)           
         if min_depth < 2: # less than 2 meter
           return True
         else:
           return False
         
    def reached_target(self):
         if not self.odometry_on:
             return False
         else:
	    if (abs(self.x-self.xtarget)<self.linear_tol and abs(self.y-self.ytarget)<self.linear_tol):
	      print("Robot Reached the target!!")
	      print('Current Position is (%s,%s) .' % (self.x,self.y))
	      self.shutdown()
	      return True
	    else:
	      return False
	    print self.x,self.y,self.xtarget,self.ytarget
	    
          

    def find_colosest_pos_to_target (self):
	if self.odometry_on and self.surround_started:
	  min_dis = math.sqrt(math.pow(self.xtarget-self.x,2)+math.pow(self.ytarget-self.y,2))
	  if min_dis < self.min_distanse_to_target:
	    self.min_distanse_to_target = min_dis
	    self.closest_x = self.x
	    self.closest_y = self.y
	    #print min_dis
	    #self.rate.sleep()
	    print self.min_distanse_to_target,self.closest_x,self.closest_y
      
    def find_angle_to_target (self):
	deltax = self.xtarget - self.x
	deltay = self.ytarget - self.y
	self.target_angle = math.degrees(math.atan2(deltay,deltax))
          
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