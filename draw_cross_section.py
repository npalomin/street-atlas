'''----------------------------------------------------------------------------------
 Tool Name:   Transect Sampling cs
 Source Name: 
 Author:      
 Required Arguments:
              Input line feature class
              Width of transect lines
              
 Optional Argument:
              Create transect line feature class
 Description: Generate transect lines (CS) of specific width through Cross Points
 Date:        
----------------------------------------------------------------------------------'''

import arcpy
import os
import math

# workspace for temporary fc
from arcpy import env
env.workspace = "C:/temp"
#env.workspace = arcpy.GetSystemEnvironment("TEMP")
env.overwriteOutput = True

#####################################################################################
# Parameters
#####################################################################################

# Input feature class containing linear features
infc = "N:\\GIS\\ex_04\\cS geodatabase.gdb\\Haringey_TQ_Road"

# Input feature class containing point features
# crPts = "N:\\GIS\\ex_04\\cS geodatabase.gdb\\Haringey_TQ_Road_midPoint"

# Output feature class to store fc
sampfc = "N:\\GIS\\ex_04\\cS geodatabase.gdb\\Haringey_cS_130917"
dirfc = os.path.dirname(sampfc)
filefc = os.path.basename(sampfc)

# Width of transect lines
fwi = 50

# Get spatial reference of input feature class
desc = arcpy.Describe(infc) 
sr = desc.spatialReference
  
############################### Create transect lines ###############################
crLines = [] # list of cross lines along the road
# Split road at vertices to get individual line segments
segments = arcpy.SplitLine_management(infc, arcpy.Geometry())

################################ Create cross points ################################
# Create cursor to search road features
cur = arcpy.da.SearchCursor(infc, (["SHAPE@"]))

crPts = [] # list of cross points along the road

for row in cur:
  # Get road geometry from cursor
  road = row[0] # Polyline

# Create cross points along the road at midpoint
  if road.length > 0:
      d = road.length / 2
      # Get position of a point at distance d
      cross = road.positionAlongLine(d) # PointGeometry
      crPts.append(cross) # add cross point into the list

del cur # delete cursor

# Process: Feature Vertices To Points
# arcpy.FeatureVerticesToPoints_management(infc, crPts, "MID")

# Loop through cross points
for cross in crPts:
  # Get Point class of cross point
  pt = cross.firstPoint # Point
  
  # Get X,Y coord of cross point
  xC = pt.X
  yC = pt.Y
  
  # Find line segment overlapping with cross point
  for seg in segments:
    if seg.contains(pt) or seg.touches(pt):
      # Get the start and end points of line segment
      fr = seg.firstPoint
      to = seg.lastPoint
      
      # Calculate the slope of line segment
      rise = to.Y - fr.Y
      run = to.X - fr.X + 0.0000000000000000001
      slope = rise/run
      
      # Calculate the slope angle
      a = math.atan(slope) # in radian
      
      # Find dx and dy to get vector wi at angle a
      wi = fwi/2 # half width of cross line
      dx = wi * math.cos(a)
      dy = wi * math.sin(a)
      
      # Rotate vector wi +90 deg around cross point
      xOri = xC + dy
      yOri = yC - dx
      
      # Rotate vector wi -90 deg around cross point
      xDes = xC - dy
      yDes = yC + dx
      
      # Determine origin and destination points of cross line
      ori = arcpy.Point(xOri,yOri)
      des = arcpy.Point(xDes,yDes)
      
      # Add origin and destination points into an array object
      arr = arcpy.Array()
      arr.add(ori)
      arr.add(des)
      
      # Contruct a cross line from the array object
      line = arcpy.Polyline(arr, sr)
      
      # Add the cross line into the list
      crLines.append(line)
      
      break # no need to check the remaining line segments

# Create transect lines fc
if any(crLines):
  f = os.path.splitext(filefc) # split into file and extension
  trannm = f[0] + "_transects" + f[1] # transect basename
  tranfc = os.path.join(dirfc, trannm)
  arcpy.CopyFeatures_management(crLines, tranfc)
  arcpy.SetParameterAsText(7, tranfc)
