from esys.lsm import *
from esys.lsm.util import Vec3, BoundingBox
from esys.lsm.geometry import *

sim = LsmMpi(numWorkerProcesses=2, mpiDimList=[2,1,1])
sim.initNeighbourSearch( particleType="RotSphere", gridSpacing=38, verletDist=0.7 )
sim.setSpatialDomain( BoundingBox(Vec3(0,0,0), Vec3(64,240,64)), circDimList = [False, False, False])
sim.setTimeStepSize(1)
sim.setNumTimeSteps(10000)
sim.createInteractionGroup(	RemoteForcePrms(name="tclb", remote_name="TCLB", max_rad=10) )
output_prefix="output/3D/pipe_dem_ESYS"
def output_path(x):
	return output_prefix + x

sim.readMesh(
    fileName = "my/ParticlePipe/pipe.msh",
    meshName = "floor_mesh_wall"
)

geoRandomBlock = RandomBoxPacker(
    minRadius = 4.0000,
    maxRadius = 15.0000,
    cubicPackRadius = 11.0000,
    maxInsertFails = 1000,
    bBox = BoundingBox(
    Vec3(9.0000, 2.0000, 9.0000),
    Vec3(51.0000, 60.0000, 51.0000)
    ),
    circDimList = [False, False, False],
    tolerance = 1.0000e-05
    )
geoRandomBlock.generate()
geoRandomBlock_particles = geoRandomBlock.getSimpleSphereCollection()
sim.createParticles(geoRandomBlock_particles)
sim.setParticleDensity (   tag = 0,   mask = -1,   Density = 2.0)

normalK = 3;

sim.createInteractionGroup (
    RotFrictionPrms (
        name = "friction",
        normalK = normalK,
        dynamicMu = 0.6,
        shearK = normalK/10.0,
        staticMu = 0.6,
        scaling = True
        )
    )

sim.createInteractionGroup (
    NRotElasticTriMeshPrms (
        name = "floorWall_repell",
        meshName = "floor_mesh_wall",
        normalK = normalK
        )
    )

sim.createInteractionGroup (
    GravityPrms (
        name = "gravity",
        acceleration = Vec3(0.0000, 1e-5, 0.0000)
        )
    )

sim.createCheckPointer (
    CheckPointPrms (
        fileNamePrefix = "flow_data",
        beginTimeStep = 0,
        endTimeStep = 20000,
        timeStepIncr = 100
        )
    )
        
sim.run()
