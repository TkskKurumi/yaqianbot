
import numpy as np
from PIL import Image,ImageFilter
import cv2,pic2pic,math
def gray(im,Image=Image,np=np,cv2=cv2):
  if(isinstance(im,Image.Image)):
    arr=np.asarray(im).astype(np.float32)
    #arr=arr.swapaxes(0,1)
  else:
    arr=im.astype(np.float32)
  if(len(arr.shape)==3):
    ar=np.zeros(arr.shape[:-1],np.float32)
    for i in range(arr.shape[2]):
    	ar+=arr[:,:,i]
    return (ar/arr.shape[2]).astype(np.uint8)
  return arr.astype(np.uint8)
def vec_n(arr,np=np):
  arr=arr.astype(np.float32)
  w,h=arr.shape
  dx=arr[1:,:-1]-arr[:-1,:-1]
  dy=arr[:-1,1:]-arr[:-1,:-1]
  ret=np.zeros((w-1,h-1,3),np.float32)
  ret[:,:,0]=dx
  ret[:,:,1]=dy
  ret[:,:,2]=(np.sum(np.abs(dx))+np.sum(np.abs(dy)))/w/h
  return ret
'''
def vec_n(arr,kernelx=3,kernely=3):
	arr=arr.astype(np.float32)
	def int2kernel(sz):
		ret=np.zeros((sz,sz),np.float32)
		for i in range(sz):
			for j in range(sz):
				ret[i,j]=-1 if(i<sz//2) else (0 if(i==sz//2) else 1)
		return ret
	if(isinstance(kernelx,int)):
		kernelx=int2kernel(kernelx)
	if(isinstance(kernely,int)):
		kernely=int2kernel(kernely)
		kernely=kernely.swapaxes(0,1)
	normx=np.sum(np.abs(kernelx))
	normy=np.sum(np.abs(kernely))
	dx=cv2.filter2D(arr,-1,kernelx/normx,borderType=cv2.BORDER_REPLICATE)
	Image.fromarray(((dx+1)/2*255).astype(np.uint8)).show()
	dy=cv2.filter2D(arr,-1,kernely/normy,borderType=cv2.BORDER_REPLICATE)
	
	w,h=dx.shape
	ret=np.zeros((w,h,3),np.float32)
	ret[:,:,0]=dx
	ret[:,:,1]=dy
	ret[:,:,2]=
	return ret'''
def illust_vecn(vn,np=np,pic2pic=pic2pic,math=math):
	ret=np.zeros(vn.shape,np.uint8)
	w,h,_=vn.shape
	for i in range(w):
		for j in range(h):
			x,y,z=vn[i,j]
			theta=math.atan2(x,y)
			theta=(theta/math.pi*180+360)%360
			c=pic2pic.HSV2RGB(theta,100,100)
			ret[i,j]=c
	return ret
def calc_s(vn,d):
	w,h,_=vn.shape
	vn=vn.astype(np.float32)
	ret=np.zeros((w,h),np.float32)
	d=np.array(d,np.float32)
	d=d/np.linalg.norm(d)
	for i in range(w):
		for j in range(h):
			n=vn[i,j]/np.linalg.norm(vn[i,j])
			s=np.dot(d,n)
			ret[i,j]=(s+1)/2
	return ret
def func_newc(c,ss):
	return c**(1.5-ss)
def illuminate(img,d,gr=None,func_newc=func_newc,vn=None):
	arr=np.asarray(img).astype(np.float32)/255
	if(gr is None):
		gr=gray(img)
	if(vn is None):
		vn=vec_n(gr)
	w,h,_=vn.shape
	d=np.array(d,np.float32)
	d=d/np.linalg.norm(d)
	s=calc_s(vn,d)
	#Image.fromarray((s*255).astype(np.uint8)).show()
	ret=np.zeros((w,h,3),np.uint8)
	for i in range(w):
		for j in range(h):
			ss=s[i,j]
			'''if(i%10==0 and j%10==0):
				print(s[i,j],arr[i,j]*255,vn[i,j])'''
			c=func_newc(arr[i,j],ss)
			
			#print(ss)
			ret[i,j]=(c*255).astype(np.uint8)
	return Image.fromarray(ret)
if(__name__=='__main__'):
	im=Image.open(r"G:\setubot-iot\20200831\49657480_p0.jpg").convert("RGB")
	im=pic2pic.squareSize(im,2e5)
	gr=gray(im.filter(filter=ImageFilter.GaussianBlur(3)))
	vn=vec_n(gr)
	d=(1,0,0.5)
	s=calc_s(vn,d)
	s=(s*255).astype(np.uint8)
	#im.show()
	def func(c,ss):
		if(ss<0.5):
			return c**(10-ss*14)
		else:
			return c**(3.9-ss*3.8)
	def fuc(l_min,l_max,d_min,d_max):
		def func(c,ss):
			if(ss<0.5):
				return c**(d_min-(d_min-d_max)*2*ss)
			else:
				return c**(l_min-(l_min-l_max)*2*(ss-0.5))
		return func
	f=fuc(1.3,0.2,8,2)
	v1=np.array(illuminate(im,(0,1,0),vn=vn,gr=gr,func_newc=f)).astype(np.float32)
	v2=np.array(illuminate(im,(1,3**0.5,0),vn=vn,gr=gr,func_newc=f)).astype(np.float32)
	v3=np.array(illuminate(im,(-1,3**0.5,0),vn=vn,gr=gr,func_newc=f)).astype(np.float32)
	rets=[]
	for i in range(10):
		a=i/10
		v=v1*(1-a)+v2*a
		rets.append(Image.fromarray(v.astype(np.uint8)))
	for i in range(10):
		a=i/10
		v=v2*(1-a)+v3*a
		rets.append(Image.fromarray(v.astype(np.uint8)))
	for i in range(10):
		a=i/10
		v=v3*(1-a)+v1*a
		rets.append(Image.fromarray(v.astype(np.uint8)))
	from make_gif import make_gif
	import os
	gif=make_gif(rets,fps=30)
	print(gif)
	os.system("explorer "+gif)