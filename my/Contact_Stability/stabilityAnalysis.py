"""
stabilityAnalysis.py
====================

A Python script to test the contact stability of plaque particles.

Plaque particles are placed inside a box with both gravity and bouyancy acting. 
The solution timestep can be altered to determine the largest stable time step.
A larger time step is better suited to a coupled simulation with TCLB.

Lightbody, D. 2018.
"""

#Import ESyS-Particle modules
from esys.lsm import *
from esys.lsm.util import *
from math import sqrt

#Define particle parameters
Rmin = 0.125
Rmax = 0.5

bondModulus = 1.0e9 # (MPa)
bondPoissonRatio = 0.25
bondCohesion = 12.5 # lipid parameters
bondTanAngle = 10.5
frictionCoeff= 0.6
density = 1.22e-3 # (g/mm^3)

#Simulation container size
minPoint = Vec3 (-5,-5,-5)
maxPoint = Vec3 (5,5,5)

#Create the simulation container
sim = LsmMpi (1, [1,1,1])

#Initialise neighbour search
sim.initNeighbourSearch (
    particleType = "RotSphere",
    gridSpacing = 2.5*Rmax,
    verletDist = 0.2*Rmin
)

#Set time step parameters
startT = 0
endT = 100000
deltaT = 10000
dt = 1.0e-3  

sim.setNumTimeSteps (endT)
#dt = 0.1*sqrt(4.*density*Rmin**3./3./bondModulus/Rmax)
#print("Calculated minimum stable time step is ", dt)
sim.setTimeStepSize (dt)

#Read the gengeo particle packing
sim.readGeometry("particlesbox.geo")

sim.setParticleDensity (tag = 1, mask = -1, Density = density)

#Create walls of the box
sim.createWall("bottom_wall",minPoint,Vec3(0,0,1))
sim.createWall("left_wall",minPoint,Vec3(0,1,0))
sim.createWall("back_wall",minPoint,Vec3(1,0,0))
sim.createWall("top_wall",maxPoint,Vec3(0,0,-1))
sim.createWall("right_wall",maxPoint,Vec3(0,-1,0))
sim.createWall("front_wall",maxPoint,Vec3(-1,0,0))

#Add an elastic interaction between the particles
sim.createInteractionGroup ( 
    NRotFrictionPrms (
        name = "friction",
        normalK = bondModulus,
        dynamicMu = frictionCoeff,
        shearK = bondModulus,
        scaling = True
    )
)

#Add elastic interaction between particles and the walls
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_bottom","bottom_wall",bondModulus))
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_left","left_wall",bondModulus))
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_back","back_wall",bondModulus))
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_top","top_wall",bondModulus))
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_right","right_wall",bondModulus))
sim.createInteractionGroup ( NRotElasticWallPrms ("pw_front","front_wall",bondModulus))

#Add gravity
sim.createInteractionGroup (
    GravityPrms (name = "gravity", acceleration = Vec3(0,-0.73154e-3,0))
)

#Add a checkpointer for VTK visualisaiton
sim.createCheckPointer (
    CheckPointPrms (
        fileNamePrefix = "snapshot",
        beginTimeStep = startT,
        endTimeStep = endT,
        timeStepIncr = deltaT,
    )
)

#Run the simulation
sim.run()

print("simulation complete")
