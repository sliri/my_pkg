#!/usr/bin/env python

import rospy
import roslib
roslib.load_manifest('my_pkg')
import sys
from std_srvs.srv import Empty, Trigger, TriggerResponse
from geometry_msgs.msg import Twist ,PoseWithCovarianceStamped
from std_msgs.msg import String
from std_msgs.msg import Float32
import tf
import math
import numpy as np
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from math import radians
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.msg import LinkStates, ModelStates
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
import operator
import time
import os

########################################################################
#MAIN EXAMPLE TAKEN FORM
#https://github.com/markwsilliman/turtlebot/blob/master/goforward.py
#########################################################################
class doitall_node():
    def __init__(self):
    
        # Initialize the node
        # rospy.init_node('my_node_name', anonymous=True)#
        # The anonymous keyword argument is mainly used for nodes where
        # you normally expect many of them to be running and
        # don't care about their names (e.g. tools, GUIs)
        #see  http://wiki.ros.org/rospy/Overview/Initialization%20and%20Shutdown       
        rospy.init_node('doitall_node',anonymous=False)
                
        # tell user how to stop TurtleBot and print on Terminal
        rospy.loginfo("To stop Jakcal CTRL + C")
        
        # What function to call when you ctrl + c
        #rospy.on_shutdown(h)
        #Register handler to be called when rospy process begins shutdown.
        #h is a function that takes no arguments. 
        #see http://wiki.ros.org/rospy/Overview/Initialization%20and%20Shutdown
        rospy.on_shutdown(self.shutdown)     
                             
       
                                 
             
        self.f1 = open('jackal_ground_truth_coordinates.txt', 'w+')
        self.f2 = open('jackal_amcl_coordinates.txt', 'w+')         
        
        #with open('jackal_ground_truth_coordinates.txt', 'r+') as self.f1: pass 
        #with open('jackal_amcl_coordinates.txt', 'r+') as self.f2: pass  
       
        
        # Subscribe to the amcl_pose topic and set 
        # the appropriate callbacks 
        # see http://answers.ros.org/question/49282/amcl-and-laser_scan_matcher/
        # see http://answers.ros.org/question/185907/help-with-some-code-send-a-navigation-goal/
        #self.link_states = rospy.Subscriber('/gazebo/link_states',  LinkStates, self.link_stateCallback)
        
        # Subscribe to the amcl_pose topic and set 
        # the appropriate callbacks 
        # see http://answers.ros.org/question/49282/amcl-and-laser_scan_matcher/
        # see http://answers.ros.org/question/185907/help-with-some-code-send-a-navigation-goal/
        self.model_states = rospy.Subscriber('/gazebo/model_states',  ModelStates, self.model_stateCallback)
        
        
         
        
       
        
        # Subscribe to the amcl_pose topic and set 
        # the appropriate callbacks 
        # see http://answers.ros.org/question/49282/amcl-and-laser_scan_matcher/
        # see http://answers.ros.org/question/185907/help-with-some-code-send-a-navigation-goal/
        self.amcl_sub = rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.amclPoseCallback)
       
        
        # Create publisher for cmd_vel topic
        # cmd_vel publisher can "talk" to Jackal and tell it to move             
        self.cmd_vel = rospy.Publisher('/jackal_velocity_controller/cmd_vel', Twist, queue_size=10)
        
        # Create publisher for amcl initial pose
        # set the initial pose and covariance    
        self.amcl_initialpose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=10)
       
        #initialize coordinates list
        self.jackal_amcl_coordinates=[]
        self.jackal_amcl_timestamps=[]
       
        #initialize coordinates list
        self.jackal_coordinates=[]
        self.jackal_timestamps=[]
       
           
        #injecing initial pose
        try:
            self.inject_initial_pose=sys.argv[3]            
        except:
            self.inject_initial_pose='False' 
        
        
       
        # Publishing rate = 100 Hz look for odometry
        #for sleeping and rate see
        #http://wiki.ros.org/rospy/Overview/Time         
        self.rate = rospy.Rate(20)
       
      
              
        
       
    #setting initial pose for AMCL 
    #http://answers.ros.org/question/205308/publishing-to-initialpose-programmatically-on-turtlebot-navigation/
    def set_initial_pose(self):
        
     
      if self.inject_initial_pose=='True':
          try:
          
               pose = PoseWithCovarianceStamped()
               pose.header.frame_id = "map"
               #pose.header.stamp = rospy.get_rostime() #-Time now- did not work properley
               pose.header.stamp.secs = 0
               pose.header.stamp.nsecs = 0
               xinitial = float(sys.argv[1])
               yinitial = float(sys.argv[2])          
               pose.pose.pose.position.x=xinitial
               pose.pose.pose.position.y=yinitial
               pose.pose.pose.position.z=0
               pose.pose.covariance=[0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942]
               pose.pose.pose.orientation.z=0.0267568523876
               pose.pose.pose.orientation.w=0.999641971333
              
              
           #publishing the initial pose over the topic 
               #while not  rospy.is_shutdown(): 
               #if  self.amcl_run_flag==True:
               i = 1
               while i<=5:
                       #pose.header.stamp = rospy.get_rostime() #-Time now- did not work properley                       
                       rospy.loginfo(pose)                
                       self.amcl_initialpose_pub.publish((pose))
                       i+=1  
                       self.rate.sleep()         
                                       
          except:
               pass
            
    
    def grapher(self):

###########################GROUND TRUTH ####################################################################
        #http://stackoverflow.com/questions/28859266/how-to-split-list-of-x-y-coordinates-of-path-into-seperate-list-of-x-and-y-coo
        #rospy.sleep(1)
        self.f1.close  
        self.f2.close 
        self.f1 = open('jackal_ground_truth_coordinates.txt', 'r')
        self.f2 = open('jackal_amcl_coordinates.txt', 'r')   
               
        for count,line in enumerate( self.f1.read().splitlines(), start=1):
           if count%2 == 0 :                
               #see http://stackoverflow.com/questions/40515661/cannot-convert-string-to-float
               strdata=line
               k=strdata.split(')') 
               k=k[0].split('(') 
               k=k[1].split(',')
               k0=k[0].split()                  
               x1=float(k0[0][1:-1]) #extract the numerical value of the coordinate out of rthe text              
               k1=k[1].split()
               y1=float(k1[0][1:-1]) #extract the numerical value of the coordinate out of rthe text
               
               
               
               self.jackal_coordinates.append((x1,y1))                               
                 
            
           else:  
               timestamp=(float(line)) 
               self.jackal_timestamps.append(timestamp)
          
        #rospy.loginfo(self.jackal_timestamps)
        #rospy.loginfo(self.jackal_coordinates)
         
          
        for count,line in enumerate(self.f2.read().splitlines(), start=1):
           if count%2 == 0 :                
               #see http://stackoverflow.com/questions/40515661/cannot-convert-string-to-float
               strdata=line
               k=strdata.split(']') 
               k=k[0].split('[') 
               k=k[1].split(',')
               k0=k[0].split()                  
               x2=float(k0[0][:-1]) #extract the numerical value of the coordinate out of rthe text              
               k1=k[1].split()
               y2=float(k1[0][:-1]) #extract the numerical value of the coordinate out of rthe text               
               
                         

               self.jackal_amcl_coordinates.append((x2,y2))
               
           else:
               timestamp=(float(line)) 
               self.jackal_amcl_timestamps.append(timestamp)   




       
        xcoords1 = np.array([x for x,y in self.jackal_coordinates])
        ycoords1 = np.array([y for x,y in self.jackal_coordinates])
       
       #For some reason, the time skew had to be doubled if I published on /'initialpose'
        if self.inject_initial_pose=='False':           
            time_sqew=1*abs(self.jackal_timestamps[0]-self.jackal_amcl_timestamps[0]) 
        else:    
            time_sqew=2*abs(self.jackal_timestamps[0]-self.jackal_amcl_timestamps[0]) #black magic
            
        self.jackal_timestamps[:] = [x-time_sqew  for x in  self.jackal_timestamps] #because of the gazebo/model_state time error
        timestamps1 =np.array(self.jackal_timestamps) 
        timestamps2 =np.array(self.jackal_amcl_timestamps) 
       

                
     
        
    
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps1,xcoords1, '-', linewidth=2,label='X -  /gazebo/model_states',color='g')              
        ax.legend(loc='lower right',fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal X Coodinate Vs Time -Ground Truth ',fontsize=14,weight='semibold',style='italic',color='g')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('X[meter]') 
        ax.axis('equal')

        graphnamex = 'Jackal X Coodinate Vs Time.png'       
    
       
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamex)
        
        
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps1,ycoords1, '-', linewidth=2,label='Y -  /gazebo/model_states',color='g')              
        ax.legend(loc='lower right',fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal Y Coodinate Vs Time -Ground Truth ',fontsize=14,weight='semibold',style='italic',color='g')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('Y[meter]') 
        ax.axis('equal')

        graphnamey = 'Jackal Y Coodinate Vs Time.png'       
    
       
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamey)
        
        
        
        

############################AMCL ####################################################################

        
        #http://stackoverflow.com/questions/28859266/how-to-split-list-of-x-y-coordinates-of-path-into-seperate-list-of-x-and-y-coo
        xcoords2 = np.array([x for x,y in self.jackal_amcl_coordinates])
        ycoords2 = np.array([y for x,y in self.jackal_amcl_coordinates])
       

    
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps2,xcoords2, '--', linewidth=2,label='X -  /amcl_pose',color='b')              
        ax.legend(loc='lower right',fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal X Coodinate Vs Time -AMCL ',fontsize=14,weight='semibold',style='italic',color='b')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('X[meter]') 
        ax.axis('equal')

        graphnamex = 'Jackal X Coodinate Vs Time AMCL.png'       
    
       
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamex)
        
        
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps2,ycoords2, '--', linewidth=2,label='Y -  /amcl_pose',color='b')              
        ax.legend(loc='lower right',fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal Y Coodinate Vs Time -AMCL ',fontsize=14,weight='semibold',style='italic',color='b')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('Y[meter]') 
        ax.axis('equal')

        graphnamey = 'Jackal Y Coodinate Vs Time AMCL.png'       
    
       
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamey)

########################################COMPARE COMBINE #################################################

    
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps1,xcoords1, '-', linewidth=2,label='X -  /gazebo/model_states',color='g')  
        line2, = ax.plot(timestamps2,xcoords2, '--', linewidth=2,label='X -  /amcl_pose',color='b')   
        xcoords2_interp=np.interp (timestamps1,timestamps2,xcoords2)  
        xcoords1_float=xcoords1.astype(np.float)
        rmse = np.sqrt(np.mean((xcoords2_interp - xcoords1_float) ** 2))
        line3, = ax.plot(timestamps1,abs(xcoords2_interp-xcoords1_float), '-', linewidth=1,label='X - ABS ERROR',color='k')              
        ax.legend(loc='lower right',fontsize=12)
        plt.text(10,0.5, 'RMSE=%s'%rmse,verticalalignment='bottom', horizontalalignment='right',color='k', fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal X Coodinate :AMCL Vs Ground Truth ',fontsize=14,weight='semibold',style='italic',color='r')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('X[meter]') 
        ax.axis('equal')

        graphnamex = 'Jackal X Coodinate AMCL Vs Ground Truth .png'

    
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamex)         

  
 

        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(timestamps1,ycoords1, '-', linewidth=2,label='Y -  /gazebo/model_states',color='g')  
        line2, = ax.plot(timestamps2,ycoords2, '--', linewidth=2,label='Y -  /amcl_pose',color='b') 
        ycoords2_interp=np.interp (timestamps1,timestamps2,ycoords2)   
        ycoords1_float=ycoords1.astype(np.float)   
        rmse = np.sqrt(np.mean((ycoords2_interp - ycoords1_float) ** 2))
        line3, = ax.plot(timestamps1,abs(ycoords2_interp-ycoords1_float), '-', linewidth=1,label='Y - ABS ERROR',color='k')                    
        ax.legend(loc='lower right',fontsize=12)
        plt.text(10,0.5, 'RMSE=%s'%rmse,verticalalignment='bottom', horizontalalignment='right',color='k', fontsize=12)
        # tidy up the figure
        ax.grid()
        ax.set_title('Jackal Y Coodinate :AMCL Vs Ground Truth ',fontsize=14,weight='semibold',style='italic',color='r')
        ax.set_xlabel('Time[sec]')
        ax.set_ylabel('Y[meter]') 
        ax.axis('equal')

        graphnamey = 'Jackal Y Coodinate AMCL Vs Ground Truth .png'

    
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamey)  
        
        
        
        
       ################################ X Y ####################################################  
        
        fig, ax = plt.subplots(figsize=(16, 8))
        line1, = ax.plot(ycoords1,xcoords1, '-', linewidth=2,label='X Y - /gazebo/model_states',color='g')  
        line2, = ax.plot(ycoords2,xcoords2, '--', linewidth=2,label='X Y -/amcl_pose',color='b') 
        
#        xcoords2_interp=np.interp (ycoords1,ycoords2,xcoords2)
#        xcoords1_float=xcoords1.astype(np.float)   
#          
#           
#        ycoords2_interp=np.interp (xcoords1,xcoords2,ycoords2)   
#        ycoords1_float=ycoords1.astype(np.float)       
#
#        rmse = np.sqrt(np.mean(((xcoords2_interp - xcoords1_float) ** 2)+((ycoords2_interp - ycoords1_float) ** 2))) 
#        line3, = ax.plot(ycoords1,np.sqrt(((xcoords2_interp - xcoords1_float) ** 2)+((ycoords2_interp - ycoords1_float) ** 2)) , '-', linewidth=1,label='X-Y - RMS ERROR',color='k')                    
#        line4,=ax.plot(ycoords2_interp,xcoords2_interp,color='r')            
#        ax.legend(loc='lower right',fontsize=12)
#        plt.text(10,0.5, 'RMSE=%s'%rmse,verticalalignment='bottom', horizontalalignment='right',color='k', fontsize=12)
        # tidy up the figure       
        plt.gca().invert_yaxis()   
        ax.grid()
        ax.set_title('Jackal X Y Coodinates :AMCL Vs Ground Truth ',fontsize=14,weight='semibold',style='italic',color='r')
        ax.set_xlabel('Y[meter]')
        ax.set_ylabel('X[meter]') 
        ax.axis('equal')

        graphnamexy = 'Jackal X Y Coodinate AMCL Vs Ground Truth.png'

    
        #http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
        plt.savefig(graphnamexy)   
 
 
    
        
    def rmse(predictions, targets,self):
            return (predictions-targets)
     
             
             
           

        
    def shutdown(self):
        # stop jackal
        rospy.loginfo("Stop Jackal")
        #plot graph
        

        self.cmd_vel.publish(Twist())
        rospy.sleep(0.5)
        # sleep just makes sure Jackal receives the stop command prior to shutting down the script
                
        self.grapher()
        # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop Jackal
        rospy.sleep(1)
        
       


    
  
          
          
          
          
          
    def link_stateCallback(self,data):
    #see http://answers.ros.org/question/30227/turtlebot-autonomous-navigation-without-rviz/ 
    #see http://answers.ros.org/question/9686/how-to-programatically-set-the-2d-pose-on-a-map/
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
          #timestamp=rospy.get_rostime() 
          timestamp=rospy.get_time()
          #rospy.loginfo(timestamp)
         
         #Splitting the test file and put in list
         #http://stackoverflow.com/questions/11870399/python-regex-find-numbers-with-comma-in-string
         #http://stackoverflow.com/questions/21744804/python-read-comma-separated-values-from-a-text-file-then-output-result-to-tex
         #http://www.pythonforbeginners.com/dictionary/python-split
          strdata=str(data)                    
          k=strdata.split(']') 
          k=k[0].split('[') 
          k=k[1].split(',')          
          indices = [i for i, s in enumerate(k) if 'jackal::base_link' in s]
         
                 
          #Reading the file and extracting coordinates of the
          #objects in the world
          coordinates = [] #initialize list 
          lines=strdata.split('\n')
          for i in xrange(0,len(lines)): 
              if "position:" in lines[i]:                   
                   xline=lines[i+1]                                     #next line is "x"         
                   [int(s) for s in xline.split() if s.isdigit()]       #extract the numerical value of the coordinate out of rthe text
                   x=s           
                   yline=lines[i+2]                                     #next line is "y"         
                   [int(s) for s in yline.split() if s.isdigit()]       #extract the numerical value of the coordinate out of rthe text
                   y=s
                   coordinates.append((x, y))                           #enter ney coordinate to list 
                   
                  
          #extracting the jackal's coordinates 
          #calling data saver function for keeping it both in list and text file
          for i in xrange(0,len(coordinates)): 
              if i in indices:
                  #self.data_saver(coordinates[i])
                   #self.jackal_timestamps.append(timestamp)
                   #self.jackal_coordinates.append(coordinates[i])
                   self.f1.write(str(timestamp))
                   self.f1.write('\n')
                   self.f1.write(str(coordinates[i]))
                   self.f1.write('\n')

                  
          
                    
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
          rospy.loginfo("Did not get link_states_subscriber data :(")
          
          
       
    def model_stateCallback(self,data):
    #see http://answers.ros.org/question/30227/turtlebot-autonomous-navigation-without-rviz/ 
    #see http://answers.ros.org/question/9686/how-to-programatically-set-the-2d-pose-on-a-map/
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
          #timestamp=rospy.get_rostime() 
          timestamp=rospy.get_time()
         # rospy.loginfo(timestamp)
         
         
         #Splitting the test file and put in list
         #http://stackoverflow.com/questions/11870399/python-regex-find-numbers-with-comma-in-string
         #http://stackoverflow.com/questions/21744804/python-read-comma-separated-values-from-a-text-file-then-output-result-to-tex
         #http://www.pythonforbeginners.com/dictionary/python-split
          strdata=str(data)                    
          k=strdata.split(']') 
          k=k[0].split('[') 
          k=k[1].split(',')          
          indices = [i for i, s in enumerate(k) if 'jackal' in s]
         
                 
          #Reading the file and extracting coordinates of the
          #objects in the world
          coordinates = [] #initialize list 
          lines=strdata.split('\n')
          for i in xrange(0,len(lines)): 
              if "position:" in lines[i]:                   
                   xline=lines[i+1]                                     #next line is "x"         
                   [int(s) for s in xline.split() if s.isdigit()]       #extract the numerical value of the coordinate out of rthe text
                   x=s           
                   yline=lines[i+2]                                     #next line is "y"         
                   [int(s) for s in yline.split() if s.isdigit()]       #extract the numerical value of the coordinate out of rthe text
                   y=s
                   coordinates.append((x, y))                           #enter ney coordinate to list 
                   
                  
          #extracting the jackal's coordinates 
          #calling data saver function for keeping it both in list and text file
          for i in xrange(0,len(coordinates)): 
              if i in indices:
                  #self.data_saver(coordinates[i])
                   #self.jackal_timestamps.append(timestamp)
                   #self.jackal_coordinates.append(coordinates[i])
               try:
                   self.f1.write(str(timestamp))
                   self.f1.write('\n')
                   self.f1.write(str(coordinates[i]))
                   self.f1.write('\n')
               except:
                   pass
                   
          
                  
          
                            
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
          rospy.loginfo("Did not get link_states_subscriber data :(")
                       
             
             


    def amclPoseCallback(self,data):
    #see http://answers.ros.org/question/30227/turtlebot-autonomous-navigation-without-rviz/ 
    #see http://answers.ros.org/question/9686/how-to-programatically-set-the-2d-pose-on-a-map/
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
         
          #timestamp=rospy.get_rostime() 
          #timestamp=rospy.get_time()
          #rospy.loginfo(timestamp1)  
          self.x = data.pose.pose.position.x
          self.y = data.pose.pose.position.y
          self.roll, self.pitch, self.yaw = euler_from_quaternion([data.pose.pose.orientation.x,
                                                    data.pose.pose.orientation.y,
                                                    data.pose.pose.orientation.z,
                                                    data.pose.pose.orientation.w])
          self.covariance = data.pose.covariance 
          coordinate=([self.x, self.y])  
          timestamp= (int(str(data.header.stamp)))*(10**-9)
          #rospy.loginfo(timestamp)
          #rospy.loginfo(coordinate)
          # rospy.loginfo("Current robot pose: x=" + str(self.x) + "y=" + str(self.y) + " yaw=" + str(math.degrees(self.yaw)) + "Deg")
          # rospy.loginfo("Covarianece is " +str(self.covariance))
       
         #extracting the jackal's coordinates 
         #calling data saver function for keeping it both in list and text file
         # for i in xrange(0,len(coordinates)): 
         #     if i in indices:
                  #self.data_saver(coordinates[i])
          #self.jackal_amcl_timestamps.append((timestamp))
          #self.jackal_amcl_coordinates.append(coordinate)
          try: 
              self.f2.write(str(timestamp))
              self.f2.write('\n')
              self.f2.write(str(coordinate))
              self.f2.write('\n')
          except:
             pass
       
       
       
       
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
          rospy.loginfo("Did not get AMCL data :(")
             
             


        
        
        
   



#I don't undertand the args thing
#Just use it as is        
def main(args):
     doitall_node()     
     rospy.init_node('doitall_node', anonymous=False)
     try:
         if sys.argv[3]=='True':         
             doitall_node().set_initial_pose()            
     except:
        pass

     #amcl_subscriber().run_amcl()
     try:
         rospy.spin()
     except KeyboardInterrupt:
          rospy.loginfo("doitall_node terminated")
  
if __name__ == '__main__':
    main(sys.argv)


