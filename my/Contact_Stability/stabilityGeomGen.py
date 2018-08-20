"""
A Python script to generate a box and particles for contact stability analysis.

Lightbody, D. 2018.
"""

from gengeo import *

minPoint = Vector3 (-5,-5,-5)
maxPoint = Vector3 (5,5,5)
Rmax = 0.5
Rmin = 0.125
bmin = Vector3 (-2.5,-2.5,-2.5)
bmax = Vector3 (2.5,2.5,2.5)

#Define the box to fill with particles
box = BoxWithPlanes3D (
    minPoint = bmin,
    maxPoint = bmax
)

#Initialise the neighbour table
ntable = MNTable3D (
    minPoint = minPoint,
    maxPoint = maxPoint,
    gridSize = 2.5 * Rmax,
    numGroups = 1
)

#Create a packer
packer = InsertGenerator3D ( 
    minRadius = Rmin, 
    maxRadius = Rmax,
    insertFails = 10000,
    maxIterations = 100,
    tolerance = 1.0e-6,
    seed = True
)

#Pack the box with particles
packer.generatePacking (
    volume = box,
    ntable = ntable,
    groupID = 0,
    tag = 1
)

print("done packing")

#Creeate ESyS-Particle geometry file
ntable.write("particlesbox.geo",1)

print("done .geo file")

#Create VTK file to visuallise packing
ntable.write("particlesbox.vtu",2)

print("done .VTK file")

print("simulation complete")
