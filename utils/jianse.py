import myio
from PIL import Image
import numpy as np
from annoy import AnnoyIndex
from glob import glob
def rouse(p,color,siz=8,thr=10):
	color=np.array(color)
	def dist(a):
		return np.linalg.norm(np.array(a)-color)
	a=[]
	#b=[]
	p=p.resize((siz,siz),Image.LANCZOS).convert("RGB")
	for x in range(siz):
		for y in range(siz):
			d=dist(p.getpixel((x,y)))
			#a.append(max(1,d-thr)**0.8)
			a.append(d)
	return np.std(a),np.mean(a)
class jianse:
	def __init__(self,points,color):
		self.ann=AnnoyIndex(3,'euclidean')
		for idx,i in enumerate(points):
			self.ann.add_item(idx,i)
		self.ann.build(2)
		self.color=color
	def jian(self,im):
		std,mean=rouse(im,self.color)
		nn=self.ann.get_nns_by_vector([std,mean,0],1)[0]
		nn=self.ann.get_item_vector(nn)
		return nn[-1]
	def from_json(pth):
		j=myio.loadjson(pth)
		return jianse(j['points'],j['color'])
	def default():
		from os import path
		pth=path.join(path.dirname(__file__),'jianse.json')
		return jianse.from_json(pth)
if(__name__=='__main__'):
	j=jianse.from_json(r"M:\pic\colornsfw\results\70_69_72.json")
	poss=glob(r"M:\pic\colornsfw\pos\*")
	negs=glob(r"M:\pic\colornsfw\neg\*")
	pos=[]
	neg=[]
	for i in list(poss)+list(negs):
		im=Image.open(i)
		w,h=im.size
		w,h=100,int(h*100/w)
		im.resize((w,h))
		result=j.jian(im)
		if(result):
			pos.append(im)
		else:
			neg.append(im)
	for i in negs:
		im=Image.open(i)
		w,h=im.size
		w,h=100,int(h*100/w)
		im.resize((w,h))
		result=j.jian(im)
		if(result):
			pos.append(im)
		else:
			neg.append(im)
		
	from pic2pic import pinterest
	pinterest(pos,int(len(pos)**0.5)).show()
	pinterest(neg,int(len(neg)**0.5)).show()
