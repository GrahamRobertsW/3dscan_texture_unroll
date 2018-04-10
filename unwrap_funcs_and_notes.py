import bpy
import math
import bmesh
import numpy as np

# reorient_to_origin
# function moves active object to origin and rotates so that the best axis sits along the Z-axis
# this should make translations way easier
# note easy to find mean and reorient origin
# very time consuming to best fit axis maybe use random sampling
# as long as lines are parallell it should work
# maybe average slopes of multiple best fits of slope
# ARGS: "verts" the list of vertices of the object
def reorient_to_origin(obj, sample_size = 20000, sample_count = 20):
   me = obj.data
   bm = bmesh.from_edit_mesh(me)
   verts = bm.verts
   lim = len(verts)
   coords = find_coordinates(bm)
   coords_mean = coords.mean(axis=0)
   mincoords = coords.min(axis=0)
   maxcoords = coords.max(axis=0)
   deltacoords = maxcoords-mincoords
   stdcoords = coords.std(axis=0)
   longestdim = np.argmax(deltacoords)
   axismin = coords_mean[longestdim]-stdcoords[longestdim]
   axismax = coords_mean[longestdim]+stdcoords[longestdim]
   legitcount = 0
   for v in verts:
      cc = v.co[longestdim]
      if cc<=axismax and cc>=axismin:
         legitcount+=1
   midgroup = np.zeros((legitcount,3))
   index = 0
   for v in verts:
      cc = v.co[longestdim]
      coo = v.co
      if cc<=axismax and cc>=axismin:
         midgroup[index,0] = coo[0]
         midgroup[index,1] = coo[1]
         midgroup[index,2] = coo[2]
         index += 1
   vv_runs = np.zeros((sample_count, 3))
   for i in range(sample_count):
      random_sample = midgroup[np.random.choice(midgroup.shape[0], sample_size, replace=False), :]
      uu, dd, vv = np.linalg.svd(random_sample - coords_mean)
      vv_runs[i] = vv[0]
   best_fit = vv_runs.mean(axis=0)
   angles = np.arccos(best_fit)
   bpy.ops.transform.rotate(value = -1*angles[0], axis=(0,0,1))
   bpy.ops.transform.rotate(value = math.pi-angles[2], axis=(0,1,0))
#   bpy.ops.transform.rotate(value = -1*angles[2], axis=(0,0,1))
   bmesh.ops.translate(bm, verts = verts, vec = -1*coords_mean)
#   mincoords = coords.min(axis=0)
#   maxcoords = coords.max(axis=0)
#   deltacoords = maxcoords-mincoords
#   longestdim = np.argmax(deltacoords)
#   print('longestdim = {0}'.format(longestdim))
#   if longestdim == 0:
#       rotval = 0.5*math.pi
#       rotdim = (0,1,0)
#   elif longestdim == 1:
#       rotval = 0
#       rotdim = (1,0,0)
#   else:
#       rotval = 0.5*math.pi
#       rotdim = (1,0,0)
#   bpy.ops.transform.rotate(value = rotval, axis = rotdim)
#   coords = find_coordinates(bm)
#   mincoords = coords.min(axis=0)
#   maxcoords = coords.max(axis=0)
#   deltacoords = maxcoords-mincoords
#   longestdim = np.argmax(deltacoords)
#   print('longestdim = {0}'.format(longestdim))
#   shiftvec = np.zeros(3)
#   shiftvec[longestdim] = -1*mincoords[longestdim]
#   bmesh.ops.translate(bm, verts = bm.verts, vec = shiftvec)
   #not done need to handle dirty dirty runtime
   return

def shift_to_origin(bm):
   coords = find_coordinates(bm)
   minc = coords.min(axis=0)
   maxc = coords.max(axis=0)
   midc = (maxc+minc)/2.
   bmesh.ops.translate(bm, verts = bm.verts, vec = -1*midc)
   return

def find_norms(coords):
   norms = np.zeros((coords.shape[0],1))
   for i in range(coords.shape[0]):
      norms[i] = np.sqrt(np.inner(coords[i,:],coords[i,:]))
   return(norms)

def find_best_line(coords, mid = None):
   if mid == None:
      uu, dd, vv = np.linalg.svd(coords)
   else:
      uu, dd, vv = np.linalg.svd(coords-mid)
   return(vv[0])

def find_center_points(coords):
   norms = find_norms(coords)
   R = norms.min()
   closeinds = np.less(norms,mult*R)
   length = np.sum(closeinds)
   closecoords = np.zeros((length, 3))
   index = 0
   for i in range(len(coords)):
      if closeinds[i]:
         closecoords[index] = coords[i]
         index += 1
   return(closecoords)
 
# activate_edit   
# finds the active object from the automatically generated filename
# sets that to active object and in edit mode
# just do this first its like super important setup for other stuff
# ARGS: "name" the name of the obj file and object
# Tested it works
def activate_edit(name):
   obj = bpy.context.scene.objects[name]
   bpy.context.scene.objects.active = obj
   bpy.ops.object.mode_set(mode='EDIT')
   return(obj)

# find_coordinates
# find the coordinates
# ARGS: "me" a mesh i.e., obj.data
# Tested works
def find_coordinates(bm):
   verts = bm.verts
   coords = np.zeros((len(verts),3))
   for i in range(len(verts)):
      coords[i,0] = verts[i].co[0]
      coords[i,1] = verts[i].co[1]
      coords[i,2] = verts[i].co[2]
   return(coords)
 
# find_coords_and_uv
# function returns array of coordinates and correesponding UV values
# note only finds first uv vector
# in the future rewrite to access RGBA values from UV image and average over all locales
# example online just averages vectors which opens up a pretty dirty opportunity for bugs
# ARGS: "obj" the active object in edit mode
#              This might be accessible from globally scoped context maybe should be argumentless
def find_coords_and_UV(obj):
   bm = bmesh.from_edit_mesh(object)
   uv_layer = bm.loops.layers.uv.active
   verts = bm.verts
   data=np.zeros((len(verts),5))
   for i in range(len(verts)):
      v = verts[i]
      coord = v.co
      data[i,0] = coord[0]
      data[i,1] = coord[1]
      data[i,2] = coord[2]
      data[i,4] = v.link_loops[0][uv_layer].uv[0]
      data[i,5] = v.link_loops[0][uv_layer].uv[1]
   return(data)
      
