import myio
import numpy as np
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
def rouse1(p,colors):
	ret=[]
	for i in colors:
		ret.extend(rouse(p,i))
	return ret
def rouse2(p,colors,siz=5):
	ret=[]
	for i in colors:
		ret.extend(rouse(p,i))
	return ret+list(np.asarray(p.convert("RGB").resize((siz,siz),Image.LANCZOS)))
class jianse:
	def __init__(self,points,colors,mode='rouse1'):
		self.ann=AnnoyIndex(len(points[0]),'euclidean')
		for idx,i in enumerate(points):
			self.ann.add_item(idx,i)
		self.ann.build(2)
		self.colors=colors
		if(mode==rouse1):
			self.im2v=rouse1
		else:
			self.im2v=rouse2
	def jian(self,im):
		point=rouse1(im,self.colors)+[0]
		nn=self.ann.get_nns_by_vector(point,1)[0]
		nn=self.ann.get_item_vector(nn)
		return nn[-1]
	def from_json(pth):
		j=myio.loadjson(pth)
		return jianse(j['points'],j['colors'],j.get('mode','rouse1'))
	def default():
		from os import path
		pth=path.join(path.dirname(__file__),'jianse.json')
		return jianse.from_json(pth)
if(__name__=='__main__'):
	j=jianse.from_json(r"M:\pic\colornsfw\results_3colors\82_16_19.json")
	poss=glob(r"M:\pic\colornsfw\pos\*")
	negs=glob(r"M:\pic\colornsfw\neg\*")
	pos=[]
	neg=[]
	from pic2pic import fixWidth
	tot=len(poss)+len(negs)
	P=0
	N=0
	TP=0
	TN=0
	for i in list(poss):
		im=fixWidth(Image.open(i),80).convert("RGB")
		w,h=im.size
		w,h=100,int(h*100/w)
		im.resize((w,h))
		result=j.jian(im)
		if(result):
			P+=1
			TP+=1
			pos.append(im)
		else:
			N+=1
			neg.append(Image.blend(Image.new("RGB",im.size,(255,0,0)),im,0.5))
	for i in list(negs):
		im=fixWidth(Image.open(i),80).convert("RGB")
		w,h=im.size
		w,h=100,int(h*100/w)
		im.resize((w,h))
		result=j.jian(im)
		if(result):
			P+=1
			pos.append(Image.blend(Image.new("RGB",im.size,(255,0,0)),im,0.5))
		else:
			N+=1
			TN+=1
			neg.append(im)
	
	from pic2pic import pinterest
	pinterest(pos,int(len(pos)**0.5)).show()
	pinterest(neg,int(len(neg)**0.5)).show()
	print((P-TP)/(TN+P-TP),(N-TN)/(TP+N-TN))