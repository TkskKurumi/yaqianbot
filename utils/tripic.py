import numpy as np
import myMesh
from random import random as rnd
from random import shuffle
from myGeometry import point
from PIL import Image
def get(width=514,height=114,az=100,colors=[(255,0,0),(0,0,255),(255,0,255)],mode='RGB'):

	ls=[np.array(_,'float64') for _ in colors]
	
	smls=sum(ls)/len(ls)
	points=[(x,y) for x in [0,width-1] for y in [0,height-1]]
	for i in range(az):
		points.append((rnd()*(width-1),rnd()*(height-1)))
	mesh=myMesh.mesh.generate_mesh_by_points1([point(x,y) for x,y in points])
	#print('build mesh',tmr.gettime())
	ret=Image.new(mode,(width,height))
	for abc,xys in mesh.get_tri_integral_point().items():
		_r=rnd()
		if(rnd()<0.5):
			_r=_r**5
		else:
			_r=1-_r**5
		shuffle(ls)
		c1,c2=ls[0],ls[1]
		color=c1+_r*(c2-c1)
		color=(color*3+smls)/4
		color=tuple([int(x) for x in color])
		for x,y in xys:
			ret.putpixel((x,y),color)
	return ret
if(__name__=='__main__'):
	get().show()