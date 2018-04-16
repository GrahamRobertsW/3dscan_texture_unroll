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

def find_phi(xy_coords):
   phi = np.zeros(xy_coords.shape[0])
   norms = find_norms(xy_coords)
   norm_coords = xy_coords/np.sqrt(norms)
   x = norm_coords[:,0]
   y = norm_coords[:,1]
   x_angles = np.arccos(x)
   y_angles = np.arcsin(y)
   for i in range(xy_coords.shape[0]):
      if y_angles[i] > 0:
         phi[i] = x_angles[i]
      else:
         phi[i] = -1 * x_angles[i]
   return(phi)

def shift_to_origin(bm):
   coords = find_coordinates(bm)
   minc = coords.min(axis=0)
   maxc = coords.max(axis=0)
   midc = (maxc+minc)/2.
   bmesh.ops.translate(bm, verts = bm.verts, vec = -1*midc[:3])
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
# RETURN matrix of coordinates in the shape [x,z,y,phi,r]
def find_coordinates(bm):
   verts = bm.verts
   coords = np.zeros((len(verts),5))
   for i in range(len(verts)):
      coords[i,0] = verts[i].co[0]
      coords[i,1] = verts[i].co[1]
      coords[i,2] = verts[i].co[2]
      coords[i,3] = np.arctan2(verts[i].co[0],verts[i].co[2])
      coords[i,4] = np.sqrt(verts[i].co[0]**2+verts[i].co[2]**2)
   return(coords)

#find_angle_between
def find_angle_between(vec1, vec2):
   v1 = vec1/np.linalg.norm(vec1)
   v2 = vec2/np.linalg.norm(vec2)
   return(np.arccos(np.clip(np.inner(v1,v2),-1,1)))

#find_xy_intercepts
# a bit of a misnomer
# just finds point close to the xy-plane
# namely points with a z-coordinate less than threshold
#ARGS:
#  coords: an array of coordinates [x,z,y] or [x,z,y,phi,r] work
#  thresh: the threshold of z-values only ones within this range are returned
#RETURN:
#  close_coords: an array of the coordinates of points approximately lying on xy-plane
def find_xy_intercepts(coords, thresh = 0.01):
   close_inds = np.less(np.abs(coords[:,1]),thresh)
   close_coords = coords[close_inds]
   return(close_coords)

#rough_align_to_z
def rough_align_to_z(bm, num_points = 10000):
   z_ax = np.array([0,1,0])
   shift_to_origin(bm)
   coords = find_coordinates(bm)
   sample_coords = coords[np.random.choice(coords.shape[0],num_points,replace=False),:3]
   best_line = find_best_line(sample_coords)
   best_line = best_line/np.linalg.norm(best_line)
   print(best_line)
   angle = np.arccos(np.clip(np.inner(best_line,z_ax),-1,1))
   perp_ax = np.cross(z_ax, best_line)
   perp_ax[1] = perp_ax[2]
   perp_ax[2] = 0
   print(perp_ax)
   bpy.ops.transform.rotate(value=-angle,axis=perp_ax)
   return
   
def update_pointers(scene, name):
   scene.update()
   obj = scene.objects[name]
   me = obj.data
   bm = bmesh.from_edit_mesh(me)
   return(obj, me, bm)

# find_coords_and_uv
# function returns array of coordinates and correesponding UV values
# note only finds first uv vector
# in the future rewrite to access RGBA values from UV image and average over all locales
# example online just averages vectors which opens up a pretty dirty opportunity for bugs
# ARGS: "obj" the active object in edit mode
#              This might be accessible from globally scoped context maybe should be argumentless
def find_coords_and_UV(bm):
   uv_layer = bm.loops.layers.uv.active
   verts = bm.verts
   data=np.zeros((len(verts),7))
   for i in range(len(verts)):
      v = verts[i]
      coord = v.co
      data[i,0] = coord[0]
      data[i,1] = coord[1]
      data[i,2] = coord[2]
      data[i,3] = v.link_loops[0][uv_layer].uv[0]
      data[i,4] = v.link_loops[0][uv_layer].uv[1]
      data[i,5] = np.arctan2(coord[0], coord[2])
      data[i,6] = np.sqrt(coord[0]**2+coord[2]**2)
   return(data)
      
