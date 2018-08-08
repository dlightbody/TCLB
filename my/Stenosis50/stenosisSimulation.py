#stenosisSimulation.py:
#=================
#
# ESyS-Particle script to run a carotid artery stenosis for coupling with
# fluid flow in TCLB.
#
# Dylan Lightbody, 2018.
#
#Import the relevant modules: 
from esys.lsm import *
from esys.lsm.util import *
from math import sqrt
##from wall_mover import WallMoverRunnable

#Fundamental units of measure:
#	length = millimetres (mm)
#	time = milliseconds (ms)
#	force = Newtons (N)

#Derived units of measure:
#	velocity = metres per second (m/s)
#	stress = megaPascals (MPa)
#	mass = grams (g)
#	density = 1.0e-6 kg/m^3 (g/mm^3)
#	acceleration = 1.0e-3 m/^2 (mm/s^2)

#Model Parameters:
#================
##cylRadius = 20.0 	#radius of the cylindrical specimen
##cylHeight = 20.0	#length of the cylindrical specimen

Rmin = 0.125		#minimum DEM particle radius
Rmax = 0.5		#maximum DEM particle radius

bondModulus = 1.0e5		#elastic modulus of beam interactions
bondPoissonRatio = 0.25		#Poisson's ratio of beam interactions
bondCohesion = 12.5		#cohesive strength of beam interactions
bondTanAngle = 10.5		#tan(friction angle) of beam interactions
frictionCoeff = 0.6		#friction coefficient for frictional contacts

density = 1.05e-3		#density of individual DEM particles
gravity = Vec3(0,-9.81e-3,0)	#acceleration due to gravity

trimeshInteractionType = "glued"	#specifies type of wall interaction
				#(valid types: "elastic" or "glued")

numT = 10	#total number of simulation timesteps

#calculated stable timestep increment:
dt = 0.1*sqrt(4.*density*Rmin**3./3./bondModulus/Rmax)

#Construct a simulation container:
sim = LsmMpi (
   numWorkerProcesses = 1,
   mpiDimList = [1,1,1]
)

#Initialise the neighbour search algorithm (using RotSphere):
sim.initNeighbourSearch (
   particleType = "RotSphere",
   gridSpacing = 2.5*Rmax,
   verletDist = 0.2*Rmin
)

#Specify the number of simulation timesteps and timestep increment:
sim.setNumTimeSteps (numT)
sim.setTimeStepSize (dt)

#Read the initial DEM particle geometry:
sim.readGeometry("Stenosis_50_low_res.geo")

#Set the density of the DEM particles:
sim.setParticleDensity (tag = 1, mask = -1, Density = density)
sim.setParticleDensity (tag = 2, mask = -1, Density = density)

#Import cylindrical artery trimesh
sim.readMesh ("5mm_cylinder.lsm","cylinder")

#construct tag for gluing
meshtag = MeshTagBuildPrms(tag = 2, mask = -1)

#Initialise elastic interactions between DEM particles and the trimesh:
if (trimeshInteractionType=="elastic"):
   sim.createInteractionGroup (
      NRotElasticTriMeshPrms (
         name = "pmesh_repel",
         meshName = "cylinder",
         normalK = bondModulus
      )
   )
elif (trimeshInteractionType == "glued"):
   sim.createInteractionGroup (
      NRotBondedTriMeshPrms (
         name = "pmesh_bond",
         meshName = "cylinder",
         normalK = bondModulus,
         breakDistance = 0.25,
         buildPrms = meshtag
      )
   )

#Specify brittle-elastic beam interactions between bonded particles:
sim.createInteractionGroup (
   BrittleBeamPrms (
      name = "pp_beams",
      youngsModulus = bondModulus,
      poissonsRatio = bondPoissonRatio,
      cohesion = bondCohesion,
      tanAngle = bondTanAngle,
      tag = 1
   )
)

#Specify rotational frictional interactions between unbonded particles:
sim.createInteractionGroup (
   FrictionPrms (
      name = "pp_friction",
      youngsModulus = bondModulus,
      poissonsRatio = bondPoissonRatio,
      dynamicMu = frictionCoeff,
      staticMu = frictionCoeff
   )
)

#Ensure each particle pair only undergoes beam or frictional interactions:
sim.createExclusion ("pp_beams","pp_friction")

#Specify the acceleration due to gravity:
sim.createInteractionGroup (
   GravityPrms (
      name = "gravity",
      acceleration = gravity
   )
)

#Add a checkpointer to record simulation data for visualisation:
sim.createCheckPointer (
   CheckPointPrms (
      fileNamePrefix = "snapshot",
      beginTimeStep = 0,
      endTimeStep = numT,
      timeStepIncr = 1  
   )
)

#Add a FieldSaver to record total particle kinetic energy each timestep:
sim.createFieldSaver (
   ParticleScalarFieldSaverPrms (
      fieldName="e_kin",
      fileName="Ekin.csv",
      fileFormat="SUM",
      beginTimeStep = 0,
      endTimeStep = numT,
      timeStepIncr = 1
   )
)

#Add a FieldSaver to record the number of bonded interactions each timestep:
sim.createFieldSaver (
   InteractionScalarFieldSaverPrms (
      interactionName="pp_beams",
      fieldName="count",
      fileName="Nbonds.csv",
      fileFormat="SUM",
      beginTimeStep = 0,
      endTimeStep = numT,
      timeStepIncr = 1
   )
)

#Add a FieldSaver to record the total stored elastic strain energy:
sim.createFieldSaver (
   InteractionScalarFieldSaverPrms (
      interactionName="pp_beams",
      fieldName="potential_energy",
      fileName="Epot.csv",
      fileFormat="SUM",
      beginTimeStep = 0,
      endTimeStep = numT,
      timeStepIncr = 1
   )
)

#execute the simulation:
sim.run()
