#!/usr/bin/env python


import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from collections import Counter
#import rospy
#import roslib
import numpy
from numpy import array
from PIL import Image, ImageDraw
import sys
from pylab import *
import re
import rospy
import roslib
roslib.load_manifest('my_pkg')


##opening the world position file for reading
#world_file = open("world_positions.txt", "r")

#look for the specific objects:
#coounting the number of cloned cones
#see http://stackoverflow.com/questions/38401099/how-to-count-one-specific-word-in-python/38401167
#with open("world_positions.txt") as world_file:
#    contents = world_file.read()
#    cones = contents.count("clone")
#print ("There are %s cones in the world"%cones)

#CONSTANTS

cone_radius=0.1
orchard_length=80   #size of the image in inches. The real size is 40 meter=157.48 inch
orchard_width=80    #size of the image in inches. The real size is 36 meter=141.8732 inch 



try:
    mapname3 = sys.argv[3]
except:
    mapname3 = "jackal_cone_world.txt"






#Splitting the test file and put in list
#http://stackoverflow.com/questions/11870399/python-regex-find-numbers-with-comma-in-string
#http://stackoverflow.com/questions/21744804/python-read-comma-separated-values-from-a-text-file-then-output-result-to-tex
#http://www.pythonforbeginners.com/dictionary/python-split
with open(mapname3, "r") as f: 
            data=f.read()     
            k=data.split(']') 
            k=k[0].split('[') 
            k=k[1].split(',') 
         

indices = [i for i, s in enumerate(k) if 'cone1_clone' in s]



#Reading the file and extracting coordinates of the
#objects in the world
coordinates = []                                             #initialize list          
#opening the world position file for reading
with open(mapname3,"r") as f:   
    for line in f:
        line = line.split() # to deal with blank        
        if "position:" in line:
          xline=next(f)                                       #next line is "x"         
          [int(s) for s in xline.split() if s.isdigit()]      #extract the numerical value of the coordinate out of rthe text
          x=s
          yline=next(f)                                       #next line is "y"         
          [int(s) for s in yline.split() if s.isdigit()]      #extract the numerical value of the coordinate out of rthe text
          y=s
          coordinates.append((x, y))                          #enter ney coordinate to list       
          

       


 




  
    


plt.close("all")
fig = plt.figure( dpi=100,figsize=(40,40),frameon=True) #set image size and DPI are optional
for i in xrange(0,len(coordinates)): #ignoring first 2 coordinates as they are the origin and the jackal locations!
    if i in indices:
#for i in xrange(6,len(coordinates)-1): #ignoring first and 6 coordinates as they are the origin and the jackal locations!
        circlex = plt.Circle(coordinates[i],cone_radius, color='black', linewidth=2,fill=False)
        plt.axis([-orchard_length/2, orchard_length/2, -orchard_width/2, orchard_width/2])
        #fig = plt.gcf()
        ax = fig.gca()
        ax.add_artist(circlex)
        ax.set_axis_bgcolor('white')
        ##removing axis and frame
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_aspect('equal')
        
       
       






try:
    mapname1 = sys.argv[1]
    mapname2 = sys.argv[2]  
except:
    mapname1 = "cone_world.png"
    mapname2 = "cone_world.pgm"
    
#http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
plt.savefig(mapname1,bbox_inches='tight')
#plt.show()

#converting to pgm see http://code.activestate.com/recipes/577591-conversion-of-pil-image-and-numpy-array/
img = Image.open(mapname1)
arr = array(img)
img = Image.fromarray(arr)
img.save(mapname2)

