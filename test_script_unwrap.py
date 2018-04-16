import numpy as np
from PIL import Image

def uv_coord(u, v, inh, inw):
   wcoord = int(u*inw)
   hcoord = int(v*inw)
   return(wcoord, hcoord)

def phiz_im_coord(phi, z, outw, outh, zrange):
   wcoord = int(phi/(np.pi)*outw/2.+outw/2.)
#   print('{0} {1} {2}'.format(phi/np.pi, outw/2., wcoord))
   hcoord = int(np.clip(z/zrange*outh,0,outh-1))
   print('{0} {1}'.format(z/float(zrange), outh))
   return(wcoord, hcoord)

file_loc = './model with UV.jpg'
inim = Image.open(file_loc)
inpix = inim.load()
indat = np.loadtxt('test_coordinates.txt')
leng = indat.shape[0]
width, height = inim.size
print('{0} {1}'.format(width, height))
out_w = 240
xmin = np.min(indat[:,0])
xmax = np.max(indat[:,0])
d = xmax-xmin
circ = d*np.pi
zmin = np.min(indat[:,1])
zmax = np.max(indat[:,1])
z_range = zmax-zmin
print(z_range)
ratio = z_range/circ
out_h = int(ratio*out_w)
print(out_h)
outim = Image.new('RGB',(out_w, out_h))
outpix = outim.load()
for i in range(leng):
   row = indat[i]
   uvw, uvh = uv_coord(row[3], row[4], height, width)
   rgb = inpix[uvw,uvh]
   outw, outh = phiz_im_coord(row[5], row[1], out_w, out_h, z_range)
#   print('({0},{1}) {2}'.format(outw, outh, rgb))
   outpix[outw, outh] = rgb
outim.save('testim.png')
