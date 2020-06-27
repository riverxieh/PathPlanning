import numpy as np
import pyrr

def getRay(x, y):
    direc = [y[0] - x[0], y[1] - x[1], y[2] - x[2]]
    return np.array([x, direc])

def getAABB(blocks):
    AABB = []
    for i in blocks:
        AABB.append(np.array([np.add(i[0:3], -0), np.add(i[3:6], 0)]))  # make AABBs alittle bit of larger
    return AABB

def getDist(pos1, pos2):
    return np.sqrt(sum([(pos1[0] - pos2[0]) ** 2, (pos1[1] - pos2[1]) ** 2, (pos1[2] - pos2[2]) ** 2]))

def getNearest(Space,pt):
    '''get the nearest point on the grid'''
    mindis,minpt = 1000,None
    for strpts in Space.keys(): 
        pts = dehash(strpts)
        dis = getDist(pts,pt)
        if dis < mindis:
            mindis,minpt = dis,pts
    return minpt

def Heuristic(Space,t):
    '''Max norm distance'''
    h = {}
    for k in Space.keys():
        h[k] = max(abs(t-dehash(k)))
    return h

def hash3D(x):
    return str(x[0])+' '+str(x[1])+' '+str(x[2])

def dehash(x):
    return np.array([float(i) for i in x.split(' ')])

def isinbound(i, x):
    if i[0] <= x[0] < i[3] and i[1] <= x[1] < i[4] and i[2] <= x[2] < i[5]:
        return True
    return False

def StateSpace(initparams,factor=0):
    '''This function is used to get nodes and discretize the space.
       State space is by x*y*z,3 where each 3 is a point in 3D.'''
    boundary = initparams.env.boundary
    resolution = initparams.env.resolution
    xmin,xmax = boundary[0]+factor*resolution,boundary[3]-factor*resolution
    ymin,ymax = boundary[1]+factor*resolution,boundary[4]-factor*resolution
    zmin,zmax = boundary[2]+factor*resolution,boundary[5]-factor*resolution
    xarr = np.arange(xmin,xmax,resolution).astype(float)
    yarr = np.arange(ymin,ymax,resolution).astype(float)
    zarr = np.arange(zmin,zmax,resolution).astype(float)
    V = np.meshgrid(xarr,yarr,zarr)
    VV = np.reshape(V,[3,len(xarr)*len(yarr)*len(zarr)]) # all points in 3D
    Space = {}
    for v in VV.T:
        Space[hash3D(v)] = np.inf # this hashmap initialize all g values at inf
    return Space

def isCollide(initparams, x, direc):
    '''see if line intersects obstacle'''
    resolution = initparams.env.resolution
    child = np.array(list(map(np.add,x,np.multiply(direc,resolution))))
    ray = getRay(x, direc)
    dist = getDist(x, child)
    if not isinbound(initparams.env.boundary,child):
        return True, child
    for i in getAABB(initparams.env.blocks):
        shot = pyrr.geometric_tests.ray_intersect_aabb(ray, i)
        if shot is not None:
            dist_wall = getDist(x, shot)
            if dist_wall <= dist:  # collide
                return True, child
    for i in initparams.env.balls:
        shot = pyrr.geometric_tests.ray_intersect_sphere(ray, i)
        if shot != []:
            dists_ball = [getDist(x, j) for j in shot]
            if all(dists_ball <= dist):  # collide
                return True, child
    return False, child

def cost(i,j):
    return getDist(i,j)
    

if __name__ == "__main__":
    from env3D import env