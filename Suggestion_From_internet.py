# https://www.blender.org/forum/viewtopic.php?t=12069
# copy UVs to make a flat mesh for displacement editing
# select object run script 
# the selected object is flattend !
#

import Blender

objs = Blender.Object.GetSelected()
if len(objs) == 1 and objs[0].getType()=="Mesh":
   print "UV-->Verts"
   obj = objs[0]
   
   
   odata = obj.getData()
   
   scale = 20.0
   for f in odata.faces:
      i = 0
      for v in f.v:
         # copy the vert
         v.co[0] = f.uv[i][0] * scale - scale/2.0
         v.co[1] = 0.0
         v.co[2] = f.uv[i][1] * scale - scale/2.0
         i += 1
         print v.co[0],v.co[1],v.co[2] 
   odata.update()
   
   
   
   print "######## SUCCESS ########"

