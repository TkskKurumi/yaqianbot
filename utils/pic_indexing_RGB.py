from glob import glob
from os import path
import numpy as np
import mybio,random,myio
import os,time,pic2pic
from PIL import Image
from annoy import AnnoyIndex
from threading import Lock
from pic_indexing_RGB_img2vecs import *
def vec_euclidean_dist(a,b):
	return np.linalg.norm(np.array(a)-np.array(b))
eps=1e-12
def vec_cos_dist(a,b):
	npa=np.array(a,np.float64)
	npb=np.array(b,np.float64)
	nma=np.linalg.norm(npa)
	nmb=np.linalg.norm(npb)
	if(nma<eps and nmb<eps):
		return 1
	if(nma < eps):
		return 0
	if(nmb < eps):
		return 0
	return np.dot(npa,npb)/np.linalg.norm(npa)/np.linalg.norm(npb)
def vec_angular_dist(u,v):
	temp=1.0-vec_cos_dist(u,v)
	if(temp<eps):
		return 0
	return np.sqrt(2*(temp))
dist_func={'euclidean':vec_euclidean_dist,'angular':vec_angular_dist}
im2vectim=0
im2vecnum=0
nnstim=0
nnsnum=0



def load_vec(file):
	f=mybio.bread(file)
	vec=[]
	le=f.read_uint32()
	for i in range(le):
		vec.append(f.read_uint8())
	f.close()
	return vec
def save_vec(file,vec):
	le=len(vec)
	f=mybio.bwrite(file)
	f.write_uint32(le)
	for i in vec:
		f.write_uint8(i)
	f.close()
class indexing:
	def __init__(self,workpth,wsiz=20,mode='euclidean',color='grey',annsize2capacity=lambda x:x*2-1):
		color=color.lower()
		self.color=color.lower()
		self.workpth=workpth
		self.img2v=color2img2vec(color)
		self.annsize2capacity=annsize2capacity
		if(not(path.exists(path.join(workpth,'vecs')))):
			os.makedirs(path.join(workpth,'vecs'))
		if(not(path.exists(path.join(workpth,'imgs')))):
			os.makedirs(path.join(workpth,'imgs'))
		self.Lock=Lock()
		self.size=len(glob(path.join(workpth,'vecs','*.vec')))
		self.wsiz=wsiz
		f=color2f(color,wsiz)
		self.f=f
		self.mode=mode
		self.item_img={}
		self.ann=AnnoyIndex(f,mode)
		self.dist_func=dist_func[mode]
		if(path.exists(path.join(workpth,'annoy.ann'))):
			self.ann.load(path.join(workpth,'annoy.ann'))
			#self.lazy=np.zeros(self.annsize,np.int32)
			self.next=np.zeros(self.annsize2capacity(self.annsize),np.int32)-1
			self.vecs=np.zeros((self.annsize2capacity(self.annsize)-self.annsize,f),np.uint8)
			for i in range(self.annsize,self.size):
				self.vecs[i-self.annsize]=np.array(load_vec(path.join(workpth,'vecs','%d.vec'%i)),np.uint8)
				u=self.ann.get_nns_by_vector(self.vecs[i-self.annsize],1)[0]
				self.next[i]=self.next[u]
				self.next[u]=i
		else:
			#self.lazy=np.array(20,np.uint32)
			self.vecs=np.zeros((19,f),np.uint8)
			self.next=np.zeros(19,np.int32)-1
			for i in range(self.size):
				self.vecs[i]=np.array(load_vec(path.join(workpth,'vecs','%d.vec'%i)),np.uint8)
	@property
	def annsize(self):
		return self.ann.get_n_items()
	def get_item_vector(self,idx):
		
		if(idx<self.annsize):
			
			return self.ann.get_item_vector(idx)
		else:
			
			return self.vecs[idx-self.annsize]
	def get_nns_by_vector(self,vec,n,include_distances=False,multi=2):
		
		if(self.annsize):
			temp=self.ann.get_nns_by_vector(vec,int(n*multi))
			temp1=[]
			for i in temp:
				u=i
				while(u!=-1):
					temp1.append(u)
					#print(u)
					u=self.next[u]
					
		else:
			temp1=list(range(self.size))
		#print(len(temp1))
		if(include_distances):
			
			return sorted([(self.dist_func(self.get_item_vector(x),vec),x) for x in temp1])[:n]
		else:
			temp=sorted(temp1,key=lambda x:self.dist_func(self.get_item_vector(x),vec))
			
			return temp[:n]
	def add_vector(self,vec,debug=False):
		if(self.size and self.get_nns_by_vector(vec,1,True)[0][0]<eps):
			
			#print('added,skip')
			return None
		if(debug):
			print('???',self.get_nns_by_vector(vec,1,True))
			#print('????',vec_dist(vec,self.get_item_vector(0)))
		self.Lock.acquire()
		save_vec(path.join(self.workpth,'vecs','%d.vec'%self.size),vec)
		
		if(self.size<self.next.shape[0]):
			self.vecs[self.size-self.annsize]=np.array(vec,np.uint8)
			self.size+=1
			if(self.annsize):
				i=self.ann.get_nns_by_vector(vec,1)[0]
				if(debug):
					print('line136',i,self.size-1)
				self.next[self.size-1]=self.next[i]
				self.next[i]=self.size-1
				
		else:
			if(debug):
				print('new')
			print('new',self.size+1)
			ann_new=AnnoyIndex(self.f,self.mode)
			
			for i in range(self.size):
				ann_new.add_item(i,self.get_item_vector(i))
			ann_new.add_item(self.size,vec)
			ann_new.build(5)
			if(debug):
				print(ann_new.get_nns_by_item(self.size,n=1))
			#print(path.join(self.workpth,'annoy.ann'))
			self.ann.unload()
			ann_new.save(path.join(self.workpth,'annoy.ann'))
			self.ann=ann_new
			
			#self.lazy=np.zeros(self.annsize,np.int32)
			self.next=np.zeros(self.annsize2capacity(self.annsize),np.int32)-1
			self.vecs=np.zeros((self.annsize2capacity(self.annsize)-self.annsize,self.f),np.uint8)
			self.size+=1
		self.Lock.release()
		return self.size-1
	def add_image(self,im):
		vec=self.img2v(im,self.wsiz)
		ret=self.add_vector(vec)
		if(ret is not None):
			pic2pic.im_sizeSquareSize(im,90000).save(path.join(self.workpth,'imgs','%d.png'%ret),'PNG')
		return ret
	def get_nns_by_image(self,img,n,include_distances=False):
		if(not(self.size)):
			return None
		vec=self.img2v(img,self.wsiz)
		return self.get_nns_by_vector(vec,n,include_distances)
	def get_image_index(self,img):
		if(not(self.size)):
			return None
		nns=self.get_nns_by_image(img,1,include_distances=True)
		if(nns[0][0]):
			return None
		else:
			return nns[0][1]
	def get_vec_index(self,vec):
		nns=self.get_nns_by_vector(vec,1,include_distances=True)
		if(nns[0][0] > eps):
			return None
		else:
			return nns[0][1]
	def __getitem__(self,key):
		if(isinstance(key,int) or isinstance(key,np.int32)):
			if(path.exists(path.join(self.workpth,'info','%d.json'%key))):
				return myio.loadjson(path.join(self.workpth,'info','%d.json'%key))
			else:
				raise KeyError(key)
		elif(isinstance(key,Image.Image)):
			idx=self.get_image_index(key)
			if(idx is None):
				raise KeyError(key)
			else:
				return self.__getitem__(idx)
		elif(isinstance(key,list) or isinstance(key,np.ndarray)):
			idx=self.get_vec_index(key)
			if(idx is None):
				raise KeyError(key)
			else:
				return self.__getitem__(idx)
		else:
			raise TypeError('key must be int, list or PIL.Image.Image, not %s'%type(key))
	def __contain__(self,key):
		if(isinstance(key,int) or isinstance(key,np.int32)):
			idx=key
		elif(isinstance(key,Image.Image)):
			idx=self.get_image_index(key)
			if(idx is None):
				return False
		elif(isinstance(key,list) or isinstance(key,np.ndarray)):
			idx=self.get_vec_index(key)
			if(idx is None):
				return False
		else:
			raise TypeError('key must be int, list or PIL.Image.Image, not %s'%type(key))
		return path.exists(path.join(self.workpth,'info','%d.json'%idx))
	def get(self,key,*args,**kwargs):
		if(self.__contain__(key)):
			return self[key]
		elif(args or kwargs):
			if(args):
				return args[0]
			else:
				for i in kwargs:
					return kwargs[i]
		else:
			raise KeyError(key)
	def __setitem__(self,key,value):
		if(isinstance(key,Image.Image)):
			idx=self.get_image_index(key)
			if(idx is None):
				idx=self.add_image(key)
		elif(isinstance(key,list) or isinstance(key,np.ndarray)):
			idx=self.get_vec_index(key)
			if(idx is None):
				idx=self.add_vector(key)
		elif(isinstance(key,int) or isinstance(key,np.int32)):
			idx=key
			
		else:
			raise TypeError('key must be int, list or PIL.Image.Image,not %s'%type(key))
		myio.dumpjson(path.join(self.workpth,'info','%d.json'%idx),value)
	def get_item_img(self,n):
		if(n not in self.item_img):
			self.item_img[n]=Image.open(path.join(self.workpth,'imgs','%d.png'%n))
		return self.item_img[n].copy()

def vec_similarity(a,b):
	temp=vec_cos_dist(a,b)
	temp=(temp+1)/2
	return temp**(np.sqrt(len(a)))
def glob_exts(pth,exts):
	ret=[]
	for i in exts:
		ret+=list(glob(pth+'\\*.'+i))
	return ret
if(__name__=='__main__'):
	idx=indexing(r'G:\temp_indexing',mode='euclidean',color='RGB',wsiz=8,annsize2capacity=lambda x:int(x*1.2+20))
	idx1=indexing(r'G:\setubot\ahegao\indexing',mode='euclidean',color='RGB',wsiz=8)
	for i in glob_exts(r'G:\setubot\ahegao',['jpg','png']):
		idx.add_image(Image.open(i))
	import pic2pic2
	im=Image.open(r"G:\setubot\20200717\34920454_p0.jpg")
	img_=pic2pic2.p2p(idx,im,grid_num=2000,pixel_num=2000000).convert("RGB")
	img_.save(r'G:\temp.jpg','JPEG')
	img_=pic2pic2.p2p(idx1,im,grid_num=2000,pixel_num=2000000).convert("RGB")
	img_.save(r'G:\temp1.jpg','JPEG')
	