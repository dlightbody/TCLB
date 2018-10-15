#stenosisGeom.py:
#===============
#
# Script to generate a particle packed stl of a stenosis in GenGeo.
#
# Dylan Lightbody, 2018.
#
#import gengeo:
from gengeo import *

#Model Parameters:
Rmin = 0.5		#minimum DEM particle radius
Rmax = 1.5		#maximum DEM particle radius

#specify the spatial domain boundaries:
domainMinPt = Vector3(0.0,0.0,75.0)
domainMaxPt = Vector3(55.0,55.0,180.0)

#define the packing volume

# readfile and add points
with open('Stenosis50_3_lipid_tmm_up_points.txt','r') as f:
    data = f.readlines()
    points = []
    for line in data:
        point = line.split()
        point = map(float,point)
        _point = Vector3(point[1],point[2],point[3])
        points.append(_point)

# Add cells
TriMesh = TriPatchSet()
with open('Stenosis50_3_lipid_tmm_up_cells.txt','r') as c:
    data = c.readlines()
    for line in data:
        cell = line.split()
        cell = map(int,cell)
        p0 = points[cell[5]-1]
        p1 = points[cell[6]-1]
        p2 = points[cell[7]-1]
        TriMesh.addTriangle(p0,p1,p2,2)

# Define the volume of the TriMesh
TriMeshVolume = MeshVolume(Mesh = TriMesh)

#define the tagged/glued volume

# readfile and add points
with open('Stenosis50_3_tag_tmm_up_points.txt','r') as f:
    data = f.readlines()
    points = []
    for line in data:
        point = line.split()
        point = map(float,point)
        _point = Vector3(point[1],point[2],point[3])
        points.append(_point)

# Add cells
TriMeshTag = TriPatchSet()
with open('Stenosis50_3_tag_tmm_up_cells.txt','r') as c:
    data = c.readlines()
    for line in data:
        cell = line.split()
        cell = map(int,cell)
        p0 = points[cell[5]-1]
        p1 = points[cell[6]-1]
        p2 = points[cell[7]-1]
        TriMeshTag.addTriangle(p0,p1,p2,2)

# Define the volume of the TriMesh
TriMeshTagVolume = MeshVolume(Mesh = TriMeshTag)

print("done mesh")

#construct a neighbour table to store particles inserted into the volume:
mntable = MNTable3D (
   minPoint = domainMinPt,
   maxPoint = domainMaxPt,
   gridSize = 2.5*Rmax,
   numGroups = 1
)

#construct a packer for inserting particles into the neighbour table:
packer = InsertGenerator3D (
   minRadius = Rmin,
   maxRadius = Rmax,
   insertFails = 10000, # was 10000
   maxIterations = 100,
   tolerance = 1.0e-6,
   seed = True
)

#generate a packing of spheres (particleTag=1) within the cylindrical volume:
packer.generatePacking (
   volume = TriMeshVolume,
   ntable = mntable,
   groupID = 0,
   tag = 1
)

print("done packing")

#generate bonds (with bondTag = 1) between adjacent particles:
mntable.generateBonds (
   groupID = 0,
   tolerance = 1.0e-5,
   bondID = 1
)

#tag glued layer
mntable.tagParticlesInVolume (
    volume = TriMeshTagVolume,
    tag = 2,
    groupID = 0,
)

print("done generating bonds")

#write the geometry in ESyS-Particle format:
mntable.write("Stenosis50_3_lipid_tmm_up.geo",1)

#write the geometry in VTK format for visualisation purposes:
mntable.write("Stenosis50_3_lipid_tmm_up.vtu",2)

print("done .geo and .vtu files")
print("simulation complete")
