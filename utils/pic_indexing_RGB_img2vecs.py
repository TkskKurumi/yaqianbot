from glob import glob
from os import path
import numpy as np
import mybio,random,myio
import os,time,pic2pic
from PIL import Image
from annoy import AnnoyIndex
from threading import Lock

def img2vec(im,wsiz):
	#global im2vecnum,im2vectim
	#im2vectim-=time.time()
	if(isinstance(im,np.ndarray)):
		if(im.shape==(wsiz,wsiz)):
			return im.reshape(wsiz*wsiz)
		else:
			raise Exception('arr shape %s does not match wsiz %d'%(arr.shape,wsiz))
	
	vec=[]
	grey=im.resize((wsiz,wsiz),Image.BICUBIC).convert('L')
	for i in range(wsiz):
		for j in range(wsiz):
			vec.append(grey.getpixel((i,j)))
	#im2vectim+=time.time()
	#im2vecnum+=1
	return vec
def img2vec_rgb(im,wsiz):
	#global im2vecnum,im2vectim
	#im2vectim-=time.time()
	if(isinstance(im,np.ndarray)):
		if(im.shape==(wsiz,wsiz,3)):
			return im.reshape(wsiz*wsiz*3)
		else:
			raise Exception('arr shape %s does not match wsiz %d'%(arr.shape,wsiz))
	
	vec=[]
	im_=im.resize((wsiz,wsiz),Image.BICUBIC).convert('RGB')
	for i in range(wsiz):
		for j in range(wsiz):
			r,g,b=im_.getpixel((i,j))
			vec+=[r,g,b]
	return vec
	
def img2vec_diff(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.BICUBIC).convert('L')).swapaxes(0,1)
	elif(isinstance(im,np.ndarray)):
		arr=im
		if(arr.shape!=(wsiz,wsiz)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[]
	for i in range(wsiz-1):
		for j in range(wsiz):
			ret.append(arr[i+1,j]-arr[i,j])
	for i in range(wsiz):
		for j in range(wsiz-1):
			ret.append(arr[i,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			ret.append(arr[i+1,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(1,wsiz):
			ret.append(arr[i+1,j-1]-arr[i,j])
	return ret
def img2vec_diffabs(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.BICUBIC).convert('L')).swapaxes(0,1)
	elif(isinstance(im,np.ndarray)):
		arr=im
		if(arr.shape!=(wsiz,wsiz)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[]
	for i in range(wsiz-1):
		for j in range(wsiz):
			ret.append(arr[i+1,j]-arr[i,j])
	for i in range(wsiz):
		for j in range(wsiz-1):
			ret.append(arr[i,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			ret.append(arr[i+1,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(1,wsiz):
			ret.append(arr[i+1,j-1]-arr[i,j])
	return [abs(_) for _ in ret]
def img2vec_diff22abs(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.LANCZOS).convert('L')).swapaxes(0,1).astype(np.int16)
	elif(isinstance(im,np.ndarray)):
		arr=im.astype(np.int16)
		if(arr.shape!=(wsiz,wsiz)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[]
	for i in range(wsiz):
		for j in range(wsiz):
			for x in range(wsiz):
				for y in range(wsiz):
					if((x,y)!=(i,j)):
						ret.append(arr[i,j]-arr[x,y])
					else:
						ret.append(arr[i,j])
	return [abs(_) for _ in ret]
def img2vec_diff22plusrgb(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.BICUBIC).convert('RGB')).swapaxes(0,1)
	elif(isinstance(im,np.ndarray)):
		arr=im
		if(arr.shape!=(wsiz,wsiz,3)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[]
	for i in range(wsiz):
		for j in range(wsiz):
			for x in range(wsiz):
				for y in range(wsiz):
					if((x,y)==(i,j)):
						ret+=list(arr[x,y])
					else:
						s1=sum(arr[x,y])
						s2=sum(arr[i,j])
						ret.append(abs(s1-s2)//3)
	return ret
def img2vec_diff_rgb(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.BICUBIC).convert('RGB')).swapaxes(0,1)
	elif(isinstance(im,np.ndarray)):
		arr=im
		if(arr.shape!=(wsiz,wsiz,3)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[]
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			a=arr[i,j]
			b=arr[i+1,j]
			c=arr[i,j+1]
			d=arr[i+1,j+1]
			ret+=list(a-b)
			ret+=list(a-c)
			ret+=list(a-d)
	return ret
def img2vec_diffcount(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.LANCZOS).convert('L')).swapaxes(0,1).astype(np.int16)
	elif(isinstance(im,np.ndarray)):
		arr=im.astype(np.int16)
		if(arr.shape!=(wsiz,wsiz)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[0]*4
	for i in range(wsiz-1):
		for j in range(wsiz):
			ret[0]+=abs(arr[i+1,j]-arr[i,j])
	for i in range(wsiz):
		for j in range(wsiz-1):
			ret[1]+=abs(arr[i,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			ret[2]+=abs(arr[i+1,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(1,wsiz):
			ret[3]+=abs(arr[i+1,j-1]-arr[i,j])
	return [_//(wsiz*wsiz) for _ in ret]
def img2vec_diffcountplus(im,wsiz):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.LANCZOS).convert('L')).swapaxes(0,1).astype(np.int16)
	elif(isinstance(im,np.ndarray)):
		arr=im.astype(np.int16)
		if(arr.shape!=(wsiz,wsiz)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	ret=[0]*5
	
	for i in range(wsiz):
		for j in range(wsiz):
			ret[4]+=arr[i,j]
	for i in range(wsiz-1):
		for j in range(wsiz):
			ret[0]+=abs(arr[i+1,j]-arr[i,j])
	
	for i in range(wsiz):
		for j in range(wsiz-1):
			ret[1]+=abs(arr[i,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			ret[2]+=abs(arr[i+1,j+1]-arr[i,j])
	for i in range(wsiz-1):
		for j in range(1,wsiz):
			ret[3]+=abs(arr[i+1,j-1]-arr[i,j])
	return [_//(wsiz*wsiz) for _ in ret]
def img2vec_diffcountplusrgb(im,wsiz,diffw=255):
	if(isinstance(im,Image.Image)):
		arr=np.asarray(im.resize((wsiz,wsiz),Image.BICUBIC).convert('RGB')).swapaxes(0,1).astype(np.int32)
	elif(isinstance(im,np.ndarray)):
		arr=im.astype(np.int32)
		if(arr.shape!=(wsiz,wsiz,3)):
			raise Exception('array shape %s does not match wsiz'%arr.shape)
	else:
		raise TypeError('argument im must be PIL.Image.Image or numpy.ndarray, not %s'%type(im))
	#print(arr.shape)
	ret=[0]*4
	ret1=np.zeros(3,np.int32)
	for i in range(wsiz):
		for j in range(wsiz):
			ret1+=arr[i,j]
		#print(ret1)
	for i in range(wsiz-1):
		for j in range(wsiz):
			ret[0]+=sum([_*_ for _ in arr[i+1,j]-arr[i,j]])**0.5
	
	for i in range(wsiz):
		for j in range(wsiz-1):
			ret[1]+=sum([_*_ for _ in arr[i,j+1]-arr[i,j]])**0.5
	for i in range(wsiz-1):
		for j in range(wsiz-1):
			ret[2]+=sum([_*_ for _ in arr[i+1,j+1]-arr[i,j]])**0.5
	for i in range(wsiz-1):
		for j in range(1,wsiz):
			ret[3]+=sum([_*_ for _ in arr[i+1,j-1]-arr[i,j]])**0.5
	temp=wsiz*wsiz*255*(3**0.5)
	for i in range(3):
		ret1[i]=int(ret1[i]/(wsiz*wsiz)*255/max(diffw,255))
	if(temp==0):
		return [0]*4+list(ret1)
	else:
		return [int(_/temp*min(diffw,255)) for _ in ret]+list(ret1)

def color2f(color,wsiz):
	if(color=='grey'):
		return wsiz*wsiz
	elif(color=='rgb'):
		return wsiz*wsiz*3
	elif(color=='diff_rgb'):
		return (wsiz-1)*(wsiz-1)*9
	elif(color in ['diff+_rgb','diffabs+rgb','diffabs+_rgb']):
		return (wsiz-1)*(wsiz-1)*12
	elif(color in ['diff','diffabs']):
		return wsiz*wsiz*4-wsiz*6+2
	elif(color in ['diff+','diffabs+']):
		return (wsiz-1)*(wsiz-1)*4
	elif(color in ['diff22abs']):
		return wsiz*wsiz*wsiz*wsiz
	elif(color=='diff22+rgb'):
		return wsiz*wsiz*wsiz*wsiz+2*wsiz*wsiz
	elif(color=='diffcount'):
		return 4
	elif(color=='diffcount+'):
		return 5
	elif(color in ['diffcount+rgb','0.5diffcount+rgb','2diffcount+rgb','10diffcount+rgb']):
		return 7
def color2img2vec(color):
	if(color=='rgb'):
		return img2vec_rgb
	elif(color=='grey'):
		return img2vec
	elif(color=='diff_rgb'):
		return img2vec_diff_rgb
	elif(color=='diff'):
		return img2vec_diff
	elif(color=='diffabs'):
		return img2vec_diffabs
	elif(color=='diff22abs'):
		return img2vec_diff22abs
	elif(color=='diff22+rgb'):
		return img2vec_diff22plusrgb
	elif(color=='diffcount'):
		return img2vec_diffcount
	elif(color=='diffcount+'):
		return img2vec_diffcountplus
	elif(color=='diffcount+rgb'):
		return img2vec_diffcountplusrgb
	elif(color=='0.5diffcount+rgb'):
		return lambda im,wsiz:img2vec_diffcountplusrgb(im,wsiz,128)
	elif(color=='2diffcount+rgb'):
		return lambda im,wsiz:img2vec_diffcountplusrgb(im,wsiz,1536)
	elif(color=='10diffcount+rgb'):
		return lambda im,wsiz:img2vec_diffcountplusrgb(im,wsiz,7680)