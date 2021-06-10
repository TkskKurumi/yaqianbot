import PIL,os,math,random,re,copy,emoji2pic,mymath
from PIL import Image,ImageFile,ImageFont,ImageDraw,ImageColor
from os import path
from functools import cmp_to_key
from glob import glob
from PIL import ImageFilter
from mytimer import *
import numpy as np
import cv2
#一坨乱七八糟的图片处理的东西，写不动注释了
__file__pth=path.dirname(__file__)
default_font=(list(glob(path.join(__file__pth,'*.ttf')))+list(glob(path.join(__file__pth,'*.otf'))))
if(not default_font):
	default_font='simhei.ttf'
else:
	default_font=default_font[0]
def resize_by_ratio(img,size_ratio,resampling=Image.LANCZOS):
	w,h=img.size
	w,h=int(w*size_ratio),int(h*size_ratio)
	return img.resize((w,h),resampling)
def open_gif(gif_file):
	g=Image.open(gif_file)
	ret=[]
	frame=Image.new("RGBA",g.size)
	plt=g.getpalette()
	nmsl=0
	while(True):
		try:
			if(not(g.getpalette)):
				g.putpalette(plt)
			print(g.mode)
			frame.paste(g,(0,0),g.convert("RGBA"))
			nmsl+=1
			g.convert("RGBA").save(r'C:\temp\temp%04d.png'%nmsl,"PNG")
			ret.append(frame.copy())
			g.seek(g.tell()+1)
		except EOFError:
			break
	return ret

def cv2_masked_paste(img1,img2,mask,box,mask_inv=None):
	_height,_width,_=img2.shape
	height,width,_=img1.shape
	le,up=box
	ri,lo=le+_width,up+_height
	offset_le,offset_ri,offset_up,offset_lo=0,0,0,0
	if(ri<=0):
		return None
	elif(le<0):
		offset_le=-le
		le=0
	
	if(le>=width):
		return None
	elif(ri>width):
		offset_ri=width-ri
		ri=width
	
	if(lo<=0):
		return None
	elif(up<0):
		offset_up=-up
		up=0
	
	if(up>=height):
		return None
	elif(lo>height):
		offset_lo=height-lo
		lo=height
		
	img_o=img1[up:lo,le:ri,:]
	
	
	
	im=img2[offset_up:offset_up+lo-up,offset_le:offset_le+ri-le,:]
	mask_=cv2.cvtColor(mask[offset_up:offset_up+lo-up,offset_le:offset_le+ri-le],cv2.COLOR_GRAY2BGR)
	if(mask_inv is None):
		mask_inv_=cv2.cvtColor(cv2.bitwise_not(mask[offset_up:offset_up+lo-up,offset_le:offset_le+ri-le]),cv2.COLOR_GRAY2BGR)
	else:
		mask_inv_=cv2.cvtColor(mask_inv[offset_up:offset_up+lo-up,offset_le:offset_le+ri-le],cv2.COLOR_GRAY2BGR)

	#print('\n',img_o.shape,im.shape,le,up,ri,lo)
	
	img_o=cv2.bitwise_and(img_o,mask_inv_)
	im=cv2.bitwise_and(im,mask_)
	
	img1[up:lo,le:ri,:]=cv2.add(img_o,im)
def cv2_rotate_center(img,rotation):
	_height,_width=img.shape[:2]
	mat=cv2.getRotationMatrix2D((_width//2,_height//2),rotation%360,1.0)
	img_rotated=cv2.warpAffine(img,mat,(_width,_height))
	return img_rotated
def pil_rgba_img2cv2img_mask(pil_img):
	img=np.asarray(pil_img.convert("RGBA"))
	mask=cv2.inRange(img,(0,0,0,180),(256,256,256,256))
	img=cv2.cvtColor(np.asarray(pil_img),cv2.COLOR_RGBA2BGR)
	return img,mask
def circle_mask_RGBA(pic,bg=(0,0,0,0)):
  ret=Image.new("RGBA",pic.size,bg)
  mask=Image.new("L",pic.size,0)
  d=ImageDraw.Draw(mask)
  d.pieslice([(0,0),mask.size],0,360,fill=255)
  ret.paste(pic.convert("RGBA"),mask=mask)
  return ret

ImageFile.LOAD_TRUNCATED_IMAGES = True
colorWhite=(255,255,255)
colorBlack=(0,0,0)
colorWhiteA=(255,255,255,255)
colorBlackA=(0,0,0,255)
def HSV2RGB(H,S,V):
	return ImageColor.getrgb('hsv(%d,%d%%,%d%%)'%(H,S,V))
def RGB2HSV(r,g,b):
	MAX=max([r,g,b])
	MIN=min([r,g,b])
	if(MAX==MIN):
		H=0
	elif((MAX==r)and(g>=b)):
		H=60*(g-b)/(MAX-MIN)
	elif((MAX==r)and(g<b)):
		H=360-60*(b-g)/(MAX-MIN)
	elif(MAX==g):
		H=120+60*(b-r)/(MAX-MIN)
	else:
		H=240+60*(r-g)/(MAX-MIN)
	s=1-MIN/MAX if MAX else 0
	v=MAX/255
	return (H,s*100,v*100)
def imageSimilarity(pic1,pic2,res=70):
	pic1=pic1.resize((res,res),Image.LANCZOS).convert('RGB')
	pic2=pic2.resize((res,res),Image.LANCZOS).convert('RGB')
	s=0
	for i in range(res):
		for j in range(res):
			s=s+colorDis(pic1.getpixel((i,j)),pic2.getpixel((i,j)))
	return s
	

	
def colorDis(a,b):
	temp=0
	try:
		for idx,a_ in enumerate(a):
			temp=temp+(abs(a_-b[idx]))**1.5
	except Exception as e:
		print('cd err',a,b)
		#exit()
		return gencd(255)
	return temp
	
def getNearestColor(c,colors,f_colorDis=colorDis):
	bestC=None
	bestD=None
	for i in colors:
		dis=f_colorDis(c,i)
		if((bestC is None) or dis<bestD):
			bestD=dis
			bestC=i
	return bestC,bestD
	
colorDis_30=colorDis( (0,0,0),(30,30,30))
colorDis_10=colorDis( (0,0,0),(10,10,10))
colorDis_5=colorDis( (0,0,0),(5,5,5))
def imageColor(a):
	return a.resize((1,1),Image.BICUBIC).getpixel((0,0))
def cEqual(a,b):
	for i in range(len(a)):
		if(a[i]!=b[i]):
			return False
	return True
colorEqual=cEqual
def zoomin_blur(img,layers=5,dist=0.1):
	ret=img.copy()
	w,h=img.size
	for i in range(1,layers+1):
		_=i/layers*dist
		ww=int(w*_)
		hh=int(h*_)
		__=img.crop((ww,hh,w-ww,h-hh)).resize((w,h))
		
		ret=Image.blend(ret,__,1/(i+1))
		#ret.show()
	return ret
def im_sizeSquareSize(im,siz):
	width,height=im.size
	siz_=width*height			#根据总面积调整图
	siz_=siz/siz_
	siz_=siz_**0.5
	width,height=int(width*siz_),int(height*siz_)
	return im.resize((width,height),Image.LANCZOS)
squareSize=im_sizeSquareSize
def cBrightness(c):
	return int((c[1]+c[0]+c[1])/7.68)

def bsearch(key,lst):
	if(l==r):
		return l
	m=int(len(lst)/2)
	if(key==lst[m]):
		return m
	if(lst[m]>key):
		return bsearch(key,lst[:m])
	else:
		return bsearch(key,lst[m:])
def fixHeight(im,height):
	w,h=im.size
	r=height/h
	w,h=(int(w*r),int(h*r))
	return im.resize((w,h),Image.LANCZOS)
def fixWidth(im,width):
	w,h=im.size
	r=width/w
	w,h=(int(w*r),int(h*r))
	return im.resize((w,h),Image.LANCZOS)

	
def imBanner(im,size):
	ri=im.size[0]/im.size[1]
	rn=size[0]/size[1] 
	if(rn>ri):
		ret=fixWidth(im,size[0])
		#print(ret.size)
		top=(ret.size[1]-size[1])//2
		return ret.crop((0,top,size[0],top+size[1]))
	else:
		ret=fixHeight(im,size[1])
		left=(ret.size[0]-size[0])//2
		
		return ret.crop((left,0,left+size[0],size[1]))
	
class ImageLib():
	
	def __init__(self):
		self.images=[]
		self.imageC=[]
		self.imageURL=[]
		self.ir=[]
		self.charas={}
		self.imageURL2ID={}
		self.size=0
	def iravrg():
		s=0
		for i in self.ir:
			s=s+i
		return s/self.size
	
	'''def allthumb1(self,wid=300):
		ithumb=[]
		h=[]
		for i in range(self.size):
			ti=self.images[i]
			hei=int(ti.size[1]*wid/ti.size[0])
			ithumb.append(ti.resize((300,hei),Image.LANCZOS))
			if(len(h)!=0):
				h.append(h[i-1]+hei)
			else:
				h.append(hei)
		iret=Image.new('RGB',(300,h[-1]))
		for i in range(self.size):
			if(i==0):
				upp=0
			else:
				upp=h[i-1]
			iret.paste(ithumb[i],(0,upp))
		return iret'''
	def allthumb(self,wid=[300]):
		if(len(wid)==0):
			wid=[300]
		hei=[0 for i in wid]
		it=[[] for i in wid]
		hei1=[0 for i in wid]
		col=len(wid)
		for i in range(self.size):
			j=0
			for k in range(col):
				if(hei[k]<hei[j]):
					j=k
			self.getImage(i)
			th=int(self.images[i].size[1]*wid[j]/self.images[i].size[0])
			it[j].append(self.images[i].resize((wid[j],th),Image.LANCZOS))
			hei[j]=hei[j]+th
		rhei=0
		rwid=0
		for i in range(len(wid)):
			if(hei[i]>rhei):
				rhei=hei[i]
			rwid=rwid+wid[i]
		ri=[Image.new('RGB',(wid[i],hei[i])) for i in range(len(wid))]
		iret=Image.new('RGB',(rwid,rhei),(255,255,255))
		tw=0
		for i in range(len(wid)):
			for j in range(len(it[i])):
				ri[i].paste(it[i][j],(0,hei1[i]))
				hei1[i]=hei1[i]+it[i][j].size[1]
			iret.paste(ri[i],(tw,0))
			tw=tw+wid[i]
		return iret
	def allthumb1(self,col=0,wid=None,siz='H',considerr=True):
		avgr=sum(self.ir)/self.size
		rr=[avgr*(math.tanh(i-((col-1)/2))/2*0.45+1) for i in range(col) ]
		
		#神必的一拍脑袋想的弱智的
		#想要每列宽度不同，并且尽量宽的图往宽的列放
		#来保证横屏图竖屏图都能得到足够面积来显示
		#结果效果很垃圾
		
		if(siz=='H'):
			siz=2200
		elif(siz=='Q'):
			siz=1400
		elif(siz=='M'):
			siz=1000
		elif(siz=='L'):
			siz=400
		if(not(wid)):
			wid=[int((siz/col)/(rr[i]**0.6)*(avgr**0.6)) for i in range(col)]
		#for i in range(col):
			#r.append([r1[i],1/r1[-(i+1)]])
		##print(r1)
		#print(rr)
		#print(wid)
			##print(wid)
			#return 'shit'
		f0=lambda x:x if (x>1) else (1/x)
		f1=lambda x,y:-1 if (f0(self.ir[x])>f0(self.ir[y])) else 1
		f2=lambda x,y:0 if (f0(self.ir[x])==f0(self.ir[y])) else f1(x,y)
		c2k=cmp_to_key(f2)
		
		frdif=lambda x,y:(x/y) if (x>y) else (y/x)
		
		dick=range(self.size)
		#return r'shit'
		hei=[0 for i in wid]
		it=[[] for i in wid]
		hei1=[0 for i in wid]
		col=len(wid)
		for i in range(self.size):
			j=None
			tr=self.ir[dick[i]]
			besth=0
			for k in range(col):
				rdif=frdif(tr,rr[k])**0.6		#图片，列应当的，长宽比的差异
				h=(10+hei[k])*rdif				#放的图高度还少并且长宽比差异小综合考虑的评分
				if((h<besth)or(j==None)):
					besth=h
					j=k
			th=int(tr*wid[j])
			it[j].append(self.getImage(dick[i]).resize((wid[j],th),Image.LANCZOS))
			hei[j]=hei[j]+th
		rhei=0
		rwid=0
		for i in range(len(wid)):
			if(hei[i]>rhei):
				rhei=hei[i]
			rwid=rwid+wid[i]
		ri=[Image.new('RGBA',(wid[i],hei[i])) for i in range(len(wid))]
		iret=Image.new('RGBA',(rwid,rhei))
		tw=0
		for i in range(len(wid)):
			for j in range(len(it[i])):
				ri[i].paste(it[i][j],(0,hei1[i]))
				hei1[i]=hei1[i]+it[i][j].size[1]
			iret.paste(ri[i],(tw,0))
			tw=tw+wid[i]
		return iret
		
	'''def getImageByColor1(self,color,temp=None):
		if(self.size==0):
			return None
		tempDis=colorDis(colorBlack,colorWhite)
		if(temp==None):
			temp=[0 for i in range(self.size)]
		ret=-1
		if(len==0):
			return None
		for i in range(self.size):
			if(ret==-1):
				ret=0
			elif(tempDis > (colorDis(color,self.imageC[i])*(temp[i]+1))):
				ret=i
				tempDis=colorDis(color,self.imageC[i])*(temp[i]+1)
		return ret'''
	
	def makeCDic(self):
		dic={}
		for i in range(self.size):
			ic=self.imageC[i]
			R=ic[0]
			G=ic[1]
			B=ic[2]					#建颜色字典，加速根据颜色获取图片（结果没什么用
			if(not(R)in dic):
				dic[R]={}
			if(not(G)in dic[R]):
				dic[R][G]={}
			dic[R][G][B]=i
		#print('mkcdic')
		self.cDic=dic
	def getImageByColor1(self,color,temp=None,dic=None):
		if(not(dic)):
			if(not(self.cDic)):
				self.makeCDic()
			dic=self.cDic
		if(temp==None):
			temp=[0 for i in range(self.size)]
		tempDis=colorDis(color,self.imageC[0])
		ret=0
		sd=sorted(dic)
		for R in sd:
			if(colorDis(color,(R,color[1],color[2]))>tempDis):
				if(R>color[0]):
					break
				continue
			sdr=sorted(dic[R])
			for G in sdr:
				if(colorDis(color,(R,G,color[2]))>tempDis):
					if(G>color[1]):
						break
					continue
				sdrg=sorted(dic[R][G])
				for B in sdrg:
					i=dic[R][G][B]
					if(tempDis > (colorDis(color,self.imageC[i])*(temp[i]+1))):
						ret=i
						tempDis=colorDis(color,self.imageC[i])*(temp[i]+1)
					elif(B>color[2]):
						break
		return ret
	def saveMem(self):
		for i in self.images:
			i=None
	def getImage(self,i):
		if(self.images[i]):
			return self.images[i]
		else:
			self.images[i]=Image.open(self.imageURL[i])
			return self.images[i]
	def getImageByColor(self,color,temp=None):
		
		return self.getImage(self.getImageByColor1(color,temp))
	def openDupSkip(self,a,convert=None,whlimit=None,saveMem=False):	#重复的不加载
		if(a in self.imageURL2ID):
			return None
		i=Image.open(a)#.convert(mode="RGB")
		if(convert):
			i=i.convert(convert)
		if(pcharai(i)in self.charas):
			#print(self.charas[pcharai(i)],a)
			return None
		if(whlimit!=None):
			if((i.size[0]>whlimit)or(i.size[1]>whlimit)):
				if(i.size[0]>i.size[1]):
					i=i.resize((whlimit,int(whlimit*i.size[1]/i.size[0])),Image.LANCZOS)
				else:
					i=i.resize((int(whlimit*i.size[0]/i.size[1]),whlimit),Image.LANCZOS)
		
		self.images.append(i)
		self.imageC.append(imageColor(i))
		self.imageURL.append(a)
		self.imageURL2ID[a]=self.size
		self.charas[pcharai(i)]=a
		self.size=self.size+1
		
		self.ir.append(i.size[1]/i.size[0])
		if(saveMem):
			self.images[self.size-1]=None	#释放空间，之后用到再加载，因为色图bot当时实在图片太多力
		return (self.size-1,self.imageC[self.size-1])
	
	
	
	def open(self,a,convert=None,whlimit=None):
		if(a in self.imageURL):
			return None
		
		i=Image.open(a)#.convert(mode="RGB")
		if(whlimit!=None):
			if((i.size[0]>whlimit)or(i.size[1]>whlimit)):
				if(i.size[0]>i.size[1]):
					i=i.resize((whlimit,int(whlimit*i.size[1]/i.size[0])),Image.LANCZOS)
				else:
					i=i.resize((int(whlimit*i.size[0]/i.size[1]),whlimit),Image.LANCZOS)
		if(convert):
			i=i.convert(convert)
		self.images.append(i)
		self.imageC.append(imageColor(i))
		self.imageURL.append(a)
		self.imageURL2ID[a]=self.size
		self.charas[pcharai(i)]=a
		self.size=self.size+1
		self.ir.append(i.size[1]/i.size[0])
		
		return (self.size-1,self.imageC[self.size-1])
		
	def openImage(self,a,convertmode='RGB'):
		if(convertmode):
			if(a.mode!=convertmode):
				a=a.convert(mode=convertmode)
		self.images.append(a)
		self.imageC.append(imageColor(a))
		self.imageURL.append('none')
		self.charas[pcharai(a)]=a
		self.size=self.size+1
		self.ir.append(a.size[1]/a.size[0])
		return (self.size-1,self.imageC[self.size-1])
	
	def saveall(self,dir,ext='PNG'):
		for i in range(self.size):
			if(ext=='PNG'):
				tsvname="%s\\%d.%d.%d.png" % (dir,self.imageC[i][0],self.imageC[i][1],self.imageC[i][2])
				if(os.path.exists(tsvname)):
					continue
				self.getImage(i).save(tsvname,"PNG")
			else:
				tsvname="%s\\%d.%d.%d.jpg" % (dir,self.imageC[i][0],self.imageC[i][1],self.imageC[i][2])
				if(os.path.exists(tsvname)):
					continue
				self.getImage(i).save(tsvname,"JPEG",quality=97)
	
	def delByURL(self,a):
		if(a not in self.imageURL):
			return none
		i=self.imageURL2ID[a]
		self.images.pop(i)
		self.imageC.pop(i)
		self.imageURL.pop(i)
		self.ir.pop(i)
		self.imageURL2ID.remove(a)
		self.size=self.size-1
		
def pic2pic(pic,ilib,siz=(0,0),gsiz=(0,0),t1=0,t2=1,tc=0.03):
	if((gsiz[0])*(gsiz[1])==0):
		gw=80
		gh=int(pic.size[1] * 80 / pic.size[0])
	else:
		gw=gsiz[0]
		gh=gsiz[1]
	if((siz[0])*(siz[1])==0):
		w=gw*48
		h=int(pic.size[1]/pic.size[0]*w)
	else:
		w=siz[0]
		h=siz[1]
	ilib.makeCDic()
	thumbpic=pic.resize((gw,gh),Image.LANCZOS)
	temps=[0 for i in range(ilib.size)]
	newpic=Image.new('RGB',(w,h))
	for i in range(gw):
		for j in range(gh):
			tLeft=int(w*i/gw)
			tUpper=int(h*j/gh)
			tRight=int(w*(i+1)/gw)-1
			tLower=int(h*(j+1)/gh)-1
			ti=ilib.getImageByColor1(thumbpic.getpixel((i,j)),temps)
			temps[ti]=(temps[ti]+t1)*t2
			tPic=ilib.getImage(ti).resize((tRight-tLeft+1,tLower-tUpper+1))
			newpic.paste(tPic,(tLeft,tUpper))
		for j in range(len(temps)):
			if(temps[j]!=0):
				temps[j]=temps[j]**tc
	##print(temps)
	return newpic	
def ofs_cor_fun1(x):
	return -255*255/(x+255)+255
def ofs_cor_fun2(x):
	#return mymath.tanh1(255,255,limitmax)(x)
	if(x>0):
		return ofs_cor_fun1(x)
	else:
		return -ofs_cor_fun1(-x)
def ofs_cor_fun3(x,limitmax=160):
	return mymath.tanh1(255,255,limitmax)(x)
def kmeans(ps,k,iter=10):
	import numpy as np
	
	ps=[np.array(i,np.float64) for i in ps]
	res=ps[:k]
	dist=lambda x,y:np.linalg.norm(x-y)
	for i in range(iter):
		res=[[_] for _ in res]
		key=lambda _:dist(res[_],p)
		for p in ps:
			temp=min(range(k),key=key)
			res[temp].append(p)
		
		res=[sum(_)/len(_) for _ in res]
	from annoy import AnnoyIndex
	ann=AnnoyIndex(len(res[0]),'euclidean')
	for i in range(k):
		ann.add_item(i,list(res[i]))
	ann.build(2)
	def get_nearest(x):
		return ann.get_item_vector(ann.get_nns_by_vector(x,1)[0])
	return res,get_nearest


def txt2im_emoji(text,font=None,fontsize=0,fill=(0,0,0,255),bg=(255,255,255,0),fixedHeight=None,shadow_fill=None,shadow_delta=None):
	if(fontsize==0):
		fontsize=80
	font_=font
	if(not(font)):
		if(fixedHeight is not None):
			fontSize=32
			font=ImageFont.truetype(default_font,fontSize)
			while(font.getsize("啊")[1]<fixedHeight):
				fontSize=int(1.2*fontSize)
				font=ImageFont.truetype(default_font,fontSize)
				#print(fontSize,font.getsize("啊")[1])
		else:
			font=ImageFont.truetype(default_font,fontsize)
	elif(isinstance(font,str)):
		if(fixedHeight is not None):
			fontSize=32
			fnt=font
			font=ImageFont.truetype(fnt,fontSize)
			
			while(font.getsize("啊")[1]<fixedHeight):
				fontSize=int(1.2*fontSize)
				font=ImageFont.truetype(fnt,fontSize)
		else:
			font=ImageFont.truetype(font,fontsize)
	t=copy.copy(text)
	emojis=[]
	for i in range(0xfe00,0xfe10):
		t.replace(chr(i),'')
	t=list(t)
	for i in range(len(t)):
		o=ord(t[i])
		if(((0x1f000<=o)and(o<=0x1f98b))):
			emojis.append((t[i],font.getsize(''.join(t[:i]))[0]))
			t[i]='　'
	t=''.join(t)
	emoji_size=font.getsize('　')
	im=Image.new('RGBA',font.getsize(t),bg)
	d=ImageDraw.Draw(im)
	d.text((0,0),t,font=font,fill=fill)
	#im.show()
	im_=Image.new('RGBA',im.size,(0,0,0,0))
	for e,left in emojis:
		emoji_im=emoji2pic.get_emoji(e).resize(emoji_size,Image.LANCZOS)
		im_.paste(emoji_im,(left,0))
	ret=Image.alpha_composite(im,im_)
	if(fixedHeight is not None):
		ret=fixHeight(ret,fixedHeight)
	if(shadow_fill):
		ret1=txt2im_emoji(text=text,font=font_,fontsize=fontsize,fill=shadow_fill,bg=bg,fixedHeight=fixedHeight)
		ret2=Image.new("RGBA",ret1.size)
		ret2.paste(ret1,shadow_delta)
		#ret2.show()
		#ret.show()
		ret=Image.alpha_composite(ret2,ret)
	
	#	return fixHeight(ret,fixedHeight)
	return ret
txt2im=txt2im_emoji
def txt2im_(text,font=None,fontsize=0,fill=(0,0,0,255),bg=(255,255,255,0)):	#用img draw获得文字图片，RGBA格式
	if(fontsize==0):
		fontsize=80
	if(not(font)):
		font=ImageFont.truetype(default_font,fontsize)
	elif(isinstance(font,str)):
		font=ImageFont.truetype(font,fontize)
	im=Image.new('RGBA',font.getsize(text),bg)
	d=ImageDraw.Draw(im)
	d.text((0,0),text,font=font,fill=fill)
	return im

def txt2im_ml(text,font=None,fontsize=0,fill=(0,0,0,255),bg=(255,255,255,0),width=320,line_space=0.25,fixedHeight=None,trim_width=False,align=0):	#用img draw获得文字图片，RGBA格式
	'''if(fontsize==0):
		if(fixedHeight):
			font=ImageFont.truetype(default_font,32)
			fontsize=int(fixedHeight*font.getsize("啊")[1]/32)
			font=None
		else:
			fontsize=32
	if(not(font)):
		font=ImageFont.truetype(default_font,fontsize)
	elif(isinstance(font,str)):
		font=ImageFont.truetype(font,fontize)'''

	if(not(font)):
		if(fixedHeight is not None):
			fontSize=12
			font=ImageFont.truetype(default_font,fontSize)
			while(font.getsize("啊")[1]<fixedHeight):
				fontSize=fontSize+1
				font=ImageFont.truetype(default_font,fontSize)
				#print(fontSize,font.getsize("啊")[1])
		else:
			font=ImageFont.truetype(default_font,fontsize)
	elif(isinstance(font,str)):
		if(fixedHeight is not None):
			fontSize=12
			fnt=font
			font=ImageFont.truetype(fnt,fontSize)
			
			while(font.getsize("啊")[1]<fixedHeight):
				fontSize=fontSize+1
				font=ImageFont.truetype(fnt,fontSize)
		else:
			font=ImageFont.truetype(font,fontsize)

	heights=[]
	texts=[]
	emojis=[]
	txt=copy.copy(text)
	totallen=len(txt)
	trimed_width=0
	widths=[]
	while(txt):
		t=''
		emojis_=[]
		#logger.debug(len(txt))
		for i in txt:
			
			if(i in ['\n','\r']):
				break
			o=ord(i)
			##print(i,o)
			if((0xfe00<=o)and(o<=0xfe0f)):
				continue
			if(((0x1f000<=o)and(o<=0x1f98b))):
				emojis_.append((i,font.getsize(t)[0]))
				t+='　'
			else:
				t+=i
			temp_width,temp_height=font.getsize(t)
			
			if(temp_width>width):
				t=t[:-1]
				break
			trimed_width=max(trimed_width,temp_width)
		emojis.append(emojis_)
		heights.append(temp_height*(1+line_space))
		widths.append(temp_width)
		texts.append(t)
		txt=txt[len(t):]
		if(txt):
			o=ord(txt[0])
			while((txt[0] in ['\n','\r'])or((0xfe00<=o)and(o<=0xfe0f))):
				txt=txt[1:]
				if(not(txt)):
					break
				o=ord(txt[0])
			
		if(not(txt)):
			heights[-1]=temp_height
	if(trim_width):
		width=trimed_width
	im=Image.new('RGBA',(width,int(sum(heights))),bg)
	im_emoji=Image.new('RGBA',(width,int(sum(heights))),(0,0,0,0))
	d=ImageDraw.Draw(im)
	nh=0
	emoji_size=font.getsize('　')
	for i in range(len(texts)):
		align_left=int(align*(width-widths[i]))
		d.text((align_left,int(nh)),texts[i],font=font,fill=fill)
		for e,left in emojis[i]:
			p=emoji2pic.get_emoji(e).resize(emoji_size,Image.LANCZOS)
			im_emoji.paste(p,(int(left+align_left),int(nh)))
		nh+=heights[i]
	return Image.alpha_composite(im,im_emoji)
def pic2pic_offsetcorrection(pic,ilib,siz=(0,0),gsiz=(0,0),t1=0,t2=1,tc=0.03,offset_multiplier=0.34):
	if((gsiz[0])*(gsiz[1])==0):
		gw=80
		gh=int(pic.size[1] * 80 / pic.size[0])
	else:
		gw=gsiz[0]
		gh=gsiz[1]
	if((siz[0])*(siz[1])==0):
		w=gw*32
		h=int(pic.size[1]/pic.size[0]*w)
	else:
		w=siz[0]
		h=siz[1]
	ilib.makeCDic()
	thumbpic=pic.resize((gw,gh),Image.LANCZOS)
	temps=[0 for i in range(ilib.size)]
	newpic=Image.new('RGB',(w,h))
	mxoffs=0
	for i in range(gw):
		offset=[0,0,0]
		for j in range(gh):
			tLeft=int(w*i/gw)
			tUpper=int(h*j/gh)
			tRight=int(w*(i+1)/gw)-1
			tLower=int(h*(j+1)/gh)-1
			targetc=list(thumbpic.getpixel((i,j)))
			for k in range(3):
				targetc[k]+=offset[k]
			ti=ilib.getImageByColor1(tuple(targetc),temps)
			unitc=ilib.imageC[ti]
			for k in range(3):
				offset[k]=(targetc[k]-unitc[k])*offset_multiplier
				offset[k]=ofs_cor_fun2(offset[k])
				if(offset[k]>mxoffs):
					mxoffs=offset[k]
			temps[ti]=(temps[ti]+t1)*t2
			tPic=ilib.getImage(ti).resize((tRight-tLeft+1,tLower-tUpper+1))
			newpic.paste(tPic,(tLeft,tUpper))
		for j in range(len(temps)):
			if(temps[j]!=0):
				temps[j]=temps[j]**tc
	##print(temps)
	#print('mxoffs',mxoffs)
	return newpic	
	
def pic2pic_offsetcorrection1(pic,ilib,siz=(0,0),gsiz=(0,0),t1=0,t2=1,tc=0.03):
	if((gsiz[0])*(gsiz[1])==0):
		gw=80
		gh=int(pic.size[1] * 80 / pic.size[0])
	else:
		gw=gsiz[0]
		gh=gsiz[1]
	if((siz[0])*(siz[1])==0):
		w=gw*32
		h=int(pic.size[1]/pic.size[0]*w)
	else:
		w=siz[0]
		h=siz[1]
	ilib.makeCDic()
	thumbpic=pic.resize((gw,gh),Image.LANCZOS)
	temps=[0 for i in range(ilib.size)]
	newpic=Image.new('RGB',(w,h))
	offset=[[[0,0,0]for i in range(gh)]for j in range(gw)]
	mxoffs=0
	for i in range(gw):
		
		for j in range(gh):
			tLeft=int(w*i/gw)
			tUpper=int(h*j/gh)
			tRight=int(w*(i+1)/gw)-1
			tLower=int(h*(j+1)/gh)-1
			targetc=list(thumbpic.getpixel((i,j)))
			for k in range(3):
				targetc[k]+=ofs_cor_fun2(offset[i][j][k])
			ti=ilib.getImageByColor1(tuple(targetc),temps)
			unitc=ilib.imageC[ti]
			if((0<i)and(i<(gw-1))and(0<j)and(j<(gh-1))):
				offset1=[0,0,0]
				
				for k in range(3):
					offset1[k]=(targetc[k]-unitc[k])/6
					if(offset1[k]>mxoffs):
						mxoffs=offset1[k]
					offset[i][j+1][k]+=offset1[k]*2
					offset[i+1][j+1][k]+=offset1[k]
					offset[i+1][j-1][k]+=offset1[k]
					offset[i+1][j][k]+=offset1[k]*2
			temps[ti]=(temps[ti]+t1)*t2
			tPic=ilib.getImage(ti).resize((tRight-tLeft+1,tLower-tUpper+1))
			newpic.paste(tPic,(tLeft,tUpper))
		for j in range(len(temps)):
			if(temps[j]!=0):
				temps[j]=temps[j]**tc
	#print(temps)
	#print('mxoffs',mxoffs)
	return newpic	
	
def pic2pic_offsetcorrection2(pic,ilib,siz=(0,0),gsiz=(0,0),t1=0,t2=1,tc=0.03,corr=4,ofs_cor_fun=ofs_cor_fun2):
	if((gsiz[0])*(gsiz[1])==0):
		gw=80
		gh=int(pic.size[1] * 80 / pic.size[0])
	else:
		gw=gsiz[0]
		gh=gsiz[1]
	if((siz[0])*(siz[1])==0):
		w=gw*32
		h=int(pic.size[1]/pic.size[0]*w)
	else:
		w=siz[0]
		h=siz[1]
	ilib.makeCDic()
	thumbpic=pic.resize((gw,gh),Image.LANCZOS)
	temps=[0 for i in range(ilib.size)]
	newpic=Image.new('RGB',(w,h))
	offset=[[[0,0,0]for i in range(gh)]for j in range(gw)]
	mxoffs=0
	tempcors=0
	for i in range(gw):
		
		for j in range(gh):
			tLeft=int(w*i/gw)
			tUpper=int(h*j/gh)
			tRight=int(w*(i+1)/gw)-1
			tLower=int(h*(j+1)/gh)-1
			targetc=list(thumbpic.getpixel((i,j)))
			for k in range(3):
				targetc[k]+=ofs_cor_fun(offset[i][j][k])
			ti=ilib.getImageByColor1(tuple(targetc),temps)
			unitc=ilib.imageC[ti]
		
			offset1=[0,0,0]
			ws=0
			ijw=[]
			for i1 in range(i,i+corr+1):
				for j1 in range(j-corr,j+corr+1):
					if((i1==i)and(j1<=j)):
						j1=j+1
						continue
					if(((i1-i)**2+(j1-j)**2)>corr*corr):
						continue
					if((j1<0)or(i1>=gw)or(j1>=gh)):
						continue
					wei=(1/((i1-i)**2+(j1-j)**2))
					ws+=wei
					ijw.append((i1,j1,wei))
			if((tempcors==0)and(ijw)):
				#print(ijw)
				pass
			tempcors+=len(ijw)
			if(ws!=0):
				
				for k in range(3):
					offset1[k]=ofs_cor_fun((targetc[k]-unitc[k])/ws)
					if(offset1[k]>mxoffs):
						mxoffs=offset1[k]
						##print(mxoffs)
					for i1,j1,wei in ijw:
						offset[i1][j1][k]+=offset1[k]*wei
			temps[ti]=(temps[ti]+t1)*t2
			
			tPic=ilib.getImage(ti).resize((tRight-tLeft+1,tLower-tUpper+1))
			
			newpic.paste(tPic,(tLeft,tUpper))
		for j in range(len(temps)):
			if(temps[j]!=0):
				temps[j]=temps[j]**tc
	##print(temps)
	#print('cors',tempcors)
	#print('mxoffs',mxoffs)
	return newpic	
def pic2pic_offsetcorrection3(pic,ilib,siz=(0,0),gsiz=(0,0),t1=0,t2=1,tc=0.03,corr=4,ofs_cor_fun=ofs_cor_fun2):
	if((gsiz[0])*(gsiz[1])==0):
		gw=80
		gh=int(pic.size[1] * 80 / pic.size[0])
	else:
		gw=gsiz[0]
		gh=gsiz[1]
	if((siz[0])*(siz[1])==0):
		w=gw*32
		h=int(pic.size[1]/pic.size[0]*w)
	else:
		w=siz[0]
		h=siz[1]
	
	mins=[min([i[j] for i in ilib.imageC]) for j in range(3)]
	#mins=[min(mins_) for i in range(3)]
	maxs=[max([i[j] for i in ilib.imageC]) for j in range(3)]
	#maxs=[max(maxs_) for i in range(3)]
	print(mins,maxs)
	ilib.makeCDic()
	thumbpic=pic.resize((gw,gh),Image.LANCZOS)
	temps=[0 for i in range(ilib.size)]
	newpic=Image.new('RGB',(w,h))
	offset=[[[0,0,0]for i in range(gh)]for j in range(gw)]
	mxoffs=0
	tempcors=0
	for i in range(gw):
		
		for j in range(gh):
			tLeft=int(w*i/gw)
			tUpper=int(h*j/gh)
			tRight=int(w*(i+1)/gw)-1
			tLower=int(h*(j+1)/gh)-1
			targetc=list(thumbpic.getpixel((i,j)))
			targetc=[int(targetc[i]/255*(maxs[i]-mins[i])+mins[i]) for i in range(3)]
			for k in range(3):
				targetc[k]+=ofs_cor_fun(offset[i][j][k])
			ti=ilib.getImageByColor1(tuple(targetc),temps)
			unitc=ilib.imageC[ti]
		
			offset1=[0,0,0]
			ws=0
			ijw=[]
			for i1 in range(i,i+corr+1):
				for j1 in range(j-corr,j+corr+1):
					if((i1==i)and(j1<=j)):
						j1=j+1
						continue
					if(((i1-i)**2+(j1-j)**2)>corr*corr):
						continue
					if((j1<0)or(i1>=gw)or(j1>=gh)):
						continue
					wei=(1/((i1-i)**2+(j1-j)**2))
					ws+=wei
					ijw.append((i1,j1,wei))
			if((tempcors==0)and(ijw)):
				#print(ijw)
				pass
			tempcors+=len(ijw)
			if(ws!=0):
				
				for k in range(3):
					offset1[k]=ofs_cor_fun((targetc[k]-unitc[k])/ws)
					if(offset1[k]>mxoffs):
						mxoffs=offset1[k]
						##print(mxoffs)
					for i1,j1,wei in ijw:
						offset[i1][j1][k]+=offset1[k]*wei
			temps[ti]=(temps[ti]+t1)*t2
			
			tPic=ilib.getImage(ti).resize((tRight-tLeft+1,tLower-tUpper+1))
			
			newpic.paste(tPic,(tLeft,tUpper))
		for j in range(len(temps)):
			if(temps[j]!=0):
				temps[j]=temps[j]**tc
	##print(temps)
	#print('cors',tempcors)
	#print('mxoffs',mxoffs)
	return newpic	

	
def getkb(x1,y1,x2,y2):
	k=(y1-y2)/(x1-x2)
	b=y1-k*x1
	return (k,b)

def changeColor(pic,nc):
	npic=pic.copy()
	minc=[255,255,255]
	maxc=[0,0,0]
	oc=imageColor(npic)
	for i in range(npic.size[0]):
		for j in range(npic.size[1]):
			temppix=npic.getpixel( (i,j) )
			for k in range(3):
				if(temppix[k]<minc[k]):
					minc[k]=temppix[k]
				if(temppix[k]>maxc[k]):
					maxc[k]=temppix[k]
	k=[0,0,0]
	b=[0,0,0]
	for ic in range(3):
		##print("max %d min %d o %d n %d" % (maxc[ic],minc[ic],oc[ic],nc[ic]))
		bestkb=(0,0)
		
		tempkb=getkb(oc[ic],nc[ic] , minc[ic],0)
		##print(tempkb[0]*maxc[ic] + tempkb[1])
		if((tempkb[0]*maxc[ic] + tempkb[1])<=255):
			bestkb=tempkb
		#	#print('ll')
			
		tempkb=getkb(oc[ic],nc[ic] , minc[ic],255)
		##print(tempkb[0]*maxc[ic] + tempkb[1])
		if((tempkb[0]*maxc[ic] + tempkb[1])>=0):
			if(abs(tempkb[0]) > abs(bestkb[0])):
				bestkb=tempkb
		#		#print('lu')
		
		tempkb=getkb(oc[ic],nc[ic] , maxc[ic],0)
		##print(tempkb[0]*minc[ic] + tempkb[1])
		if((tempkb[0]*minc[ic] + tempkb[1])<=255):
			if(abs(tempkb[0]) > abs(bestkb[0])):
				bestkb=tempkb
		#		#print('rl')
		
		tempkb=getkb(oc[ic],nc[ic] , maxc[ic],255)
		##print(tempkb[0]*minc[ic] + tempkb[1])
		if((tempkb[0]*minc[ic] + tempkb[1])>=255):
			if(abs(tempkb[0]) > abs(bestkb[0])):
				bestkb=tempkb
		#		#print('ru')
		
		
		
		k[ic]=bestkb[0]
		b[ic]=bestkb[1]
	
	for i in range(npic.size[0]):
		for j in range(npic.size[1]):
			oc=npic.getpixel((i,j))
			nc=[0,0,0]
			for ic in range(3):
				nc[ic]=int(k[ic]*oc[ic]+b[ic])
				if(nc[ic]>255):
					nc[ic]=255
				if(nc[ic]<0):
					nc[ic]=0
			npic.putpixel((i,j),(nc[0],nc[1],nc[2]))
	
	return npic
#input()
def getXYByColor(pic,c,rg=None):
	
	if(rg==None):
		rgi=range(pic.size[0])
		rgj=range(pic.size[1])
		x=0
		y=0
	else:
		rgi=range(rg[0],rg[2])
		x=rg[0]
		rgj=range(rg[1],rg[3])
		y=rg[1]
	bs=colorDis(c,pic.getpixel((x,y)))
	for i in rgi:
		for j in rgj:
			ts=colorDis(c,pic.getpixel((i,j)))
			if(ts<bs):
				bs=ts
				x=i
				y=j
	return (x,y)
	
def generateLib(oriPic,colors=[]):
	if(len(colors)==0):
		colors=[(25*i,25*j,25*k) for i in range(10) for j in range(10) for k in range(10)]
	
	l=ImageLib()
	for i in colors:
		##print(i)
		l.openImage(changeColor(oriPic,i))
	return l

def generateLib1(originalImageLib,colors=[]):
	if(len(colors)==0):
		colors=[(25*i,25*j,25*k) for i in range(10) for j in range(10) for k in range(10)]
	l=ImageLib()
	for i in colors:
		##print(i)
		p=originalImageLib.getImage(random.randint(0,originalImageLib.size-1))
		l.openImage(changeColor(p,i))
	return l
	
def imageRGBFilter(i,f=lambda x:int((255 + x)/2)):
	iret=i.convert('RGB')
	for i in range(iret.size[0]):
		for j in range(iret.size[1]):
			t=iret.getpixel((i,j))
			t1=[f(i) for i in t]  
			t1=(t1[0],t1[1],t1[2])
			iret.putpixel((i,j),t1)
	return iret
		
def imageBlend1(i1,i2,f=lambda x,y,xy:int((x+y)/2)):
	i1_=i1.copy()
	i2_=i2.resize(i1.size).convert(i1.mode)
	iret=Image.new('RGB',i1.size)
	
	for i in range(i1.size[0]):
		for j in range(i1.size[1]):
			t1=i1_.getpixel((i,j))
			t2=i2_.getpixel((i,j))
			temp=tuple([f(t1[i_],t2[i_],(i,j))for i_ in range(3)])
			iret.putpixel((i,j),temp)
		
	return iret

def __filt1(x,y):
	return tuple([int(x[i]*0.5+y[i]*0.5) for i in range(x)])
	
def imageBlend(i1,i2,f=__filt1,resizefilt=Image.LANCZOS):
	i1_=i1.copy()
	i2_=i2.resize(i1.size,resizefilt).convert(i1.mode)
	iret=Image.new('RGB',i1.size)
	
	for i in range(i1.size[0]):
		for j in range(i1.size[1]):
			t1=i1_.getpixel((i,j))
			t2=i2_.getpixel((i,j))
			temp=f(t1,t2,(i,j))
			iret.putpixel((i,j),temp)
		
	return iret
def picdis(i1,i2):
	i2=i2.resize((64,64),Image.LANCZOS).convert('RGB')
	i1=i1.resize((64,64),Image.LANCZOS).convert('RGB')
	#i2.show()
	#i1.show()
	s=0
	for i in range(64):
		for j in range(64):
			s=s+math.log(colorDis(i1.getpixel((i,j)),i2.getpixel((i,j)))+1)
	return s
def picMatrix(pics,oneSize=None,column_num=None,border=None,bg=(255,255,255)):
	if(oneSize is None):
		wid=0
		hei=0
		for i in pics:
			wid=max(wid,i.size[0])
			hei=max(hei,i.size[1])
		oneSize=wid,hei
	if(border is None):
		border=oneSize[0]//30
	if(column_num is None):
		column_num=int((len(pics)**0.5)*1.2)
	row_num=((len(pics)-1)//column_num)+1
	width=column_num*(oneSize[0]+border*2)
	height=row_num*(oneSize[1]+border*2)
	ret=Image.new(pics[0].mode,(width,height),bg)
	for idx,pic in enumerate(pics):
		column=idx%column_num
		row=idx//column_num
		left=border+(border*2+oneSize[0])*column
		top=border+(border*2+oneSize[1])*row
		if(pic.size!=oneSize):
			pic=im_sizelimitmax(pic,oneSize)
			left+=(oneSize[0]-pic.size[0])//2
			top+=(oneSize[1]-pic.size[1])//2
		ret.paste(pic,(left,top))
	return ret
def im_sizelimitmax(im,sizlimit,rdeltamax=1.05):
	siz=sizelimit(im.size,sizlimitmax=sizlimit,rdeltamax=rdeltamax)
	return im.resize(siz,Image.LANCZOS)
def im_sizelimitmin(im,sizlimit,rdeltamax=1.05):
	siz=sizelimit(im.size,sizlimitmin=sizlimit,rdeltamax=rdeltamax)
	return im.resize(siz,Image.LANCZOS)

def sizelimitmax(siz,limitsiz):
	r=1
	if(limitsiz[0]<siz[0]):
		r1=limitsiz[0]/siz[0]
		if(r1<r):
			r=r1
	if(limitsiz[1]<siz[1]):
		r1=limitsiz[1]/siz[1]
		if(r1<r):
			r=r1
	ret=tuple([int(i*r)for i in siz])
	return ret

	
def pcharai(Img,length=31,offs=2):
	w=20
	img=im_sizelimitmax(Img.convert('RGB'),(w,w))
	l=0
	i1=0
	bitrm=(8-offs)
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			getp=img.getpixel((i,j))
			for j in getp:
				i1=i1^((j>>bitrm) << (l*offs))
				l+=1
				if(l==length):
					l=0
	return i1>>34
	
def pcharai_(img,length=31,offs=2,w=24):
	
	img=im_sizelimitmax(img,(w,w)).convert('L')
	l=0
	i1=0
	bitrm=(9-offs)
	for i in range(img.size[0]-1):
		for j in range(img.size[1]):
			getp=img.getpixel((i,j))
			getp1=img.getpixel((i+1,j))
			k=getp-getp1+256
			##print(k)
			i1=i1^((k>>bitrm) << (l*offs))
			l+=1
			if(l==length):
				l=0
	return i1>>34
	
def pcharai__(img,length=31,offs=2,w=24):
	
	img=im_sizelimitmax(img,(w,w)).convert('L')
	l=0
	i1=0
	bitrm=(10-offs)
	for i in range(img.size[0]-1):
		for j in range(img.size[1]-1):
			getp=img.getpixel((i,j))
			getp1=img.getpixel((i+1,j))
			getp2=img.getpixel((i,j+1))
			getp3=img.getpixel((i+1,j+1))
			k=getp1+getp2-getp3-getp4+512
			##print(k)
			i1=i1^((k>>bitrm) << (l*offs))
			l+=1
			if(l==length):
				l=0
	return i1>>34
def sizelimit(siz,sizlimitmin=None,sizlimitmax=None,rdeltamax=1.05):
	siz=list(siz)
	if(sizlimitmax):
		rlimit=sizlimitmax[0]/sizlimitmax[1]
		rorigin=siz[0]/siz[1]
		if(rlimit<rorigin):
			if(siz[0]>sizlimitmax[0]):
				siz[1]=int(min(sizlimitmax[1],sizlimitmax[0]/rorigin*rdeltamax))
				siz[0]=sizlimitmax[0]
		else:
			if(siz[1]>sizlimitmax[1]):
				siz[0]=int(min(sizlimitmax[0],sizlimitmax[1]*rorigin*rdeltamax))
				siz[1]=sizlimitmax[1]
	if(sizlimitmin):
		rlimit=sizlimitmin[0]/sizlimitmin[1]
		rorigin=siz[0]/siz[1]
		if(rlimit<rorigin):		#限制比较窄
			if(siz[1]<sizlimitmin[1]):
				siz[0]=int(sizlimitmin[1]*rorigin/rdeltamax)
				siz[1]=sizlimitmin[1]
		else:
			if(siz[0]<sizlimitmin[0]):
				siz[1]=int(sizlimitmin[0]/rorigin/rdeltamax)
				siz[0]=sizlimitmin[0]
	return siz
def picLayout(Layouts={},imgs={},res=(),mode={},bgcolor=(0,0,0,0),default_mode='center_border'):
#根据布局，组一个图片出来
	img=Image.new('RGBA',res,bgcolor)
	for i in Layouts:
		if(not(i in imgs)):
			#print('no img',i)
			continue
		
		pos,siz=Layouts[i]
		
		centerpos=[int(pos[j]+siz[j]/2) for j in [0,1]]	#中心位置
		im=imgs[i]
		mode_=mode.get(i,default_mode)
		if(mode_=='center_border'):						
			size=sizelimit(im.size,sizlimitmax=siz)
			im=im.resize(size,Image.LANCZOS)
			pos=[int(centerpos[j]-size[j]/2) for j in [0,1]]
		elif(mode_=='right'):
			size=sizelimit(im.size,sizlimitmax=siz)
			im=im.resize(size,Image.LANCZOS)
			pos=list(pos)
			pos[1]=(centerpos[1]-size[1]/2)
			pos[0]+=siz[0]-im.size[0]
		elif(mode_=='left'):
			size=sizelimit(im.size,sizlimitmax=siz)
			im=im.resize(size,Image.LANCZOS)
			pos=list(pos)
			pos[1]=(centerpos[1]-size[1]/2)
		elif(mode=='fill'):
			if(siz!=im.size):
				im=im.resize(siz,Image.LANCZOS)
			
		else:
			size=sizelimit(im.size,sizlimitmax=siz)
			im=im.resize(size)
			pos=[int(centerpos[j]-size[j]/2) for j in [0,1]]
		pos=[int(i) for i in pos]
		
		#print(pos,size)
		img.paste(im,pos)
	return img
	
def filt_rgb_color_inverse(c):		#反色
	ret=list(c)
	for i in range(3):
		ret[i]=255-ret[i]
	return tuple(ret)
	
def imageFilt(img,convert='RGB',filt=filt_rgb_color_inverse):
	w,h=img.size
	if(img.mode!=convert):
		img.convert(mode=convert)
	d=list(img.getdata())
	for i in range(len(d)):
		d[i]=filt_rgb_color_inverse(d[i])
	img.putdata(d)
	return img
def color2hex(c):
	return c[2]*65536 + c[1]*256 +c[0]
def gencd(th_):
	th=colorDis((0,0,0),(th_,th_,th_))
	return th
def hex2color(h):
	c=[]
	for i in range(3):
		c.append(h%256)			#0xRRGGBB转为(R,G,B)
		h=int(h/256)
	return c
def paletteIm(im,palette=None,paletteSize=67,paletteMinTh=gencd(8),f_colorDis=colorDis):#减少图片的颜色
	t1=timer()
	t1.settime()
	im1=im.copy()
	data=im1.load()
	width=im1.size[0]		
	height=im1.size[1]
	if(palette is None):
		palette=[]
		for t in range(paletteSize*2):
			if(len(palette)>=paletteSize):
				break
			i,j=random.randrange(0,width),random.randrange(0,height)
			c=data[i,j]
			if(palette):
				bc,d=getNearestColor(c,palette,f_colorDis=f_colorDis)
				if(d<paletteMinTh):
					continue
			palette.append(data[i,j])
	palettegetmem={}
	def paletteGet(c):
		h=color2hex(c)
		if(h in palettegetmem):
			return palettegetmem[h]
		bestC,bestD=getNearestColor(c,palette,f_colorDis=f_colorDis)
		palettegetmem[h]=bestC
		return bestC
	
	
	for i in range(width):
		#print(i/width)
		for j in range(height):
			bestC=paletteGet(data[i,j])
			im1.putpixel((i,j),bestC)
	#print('palette image time',t1.gettime())
	#im1age.fromarray(data).show()
	
	# im1.save(r'J:\new\temp\Palette_%s.png'%(int(paletteMinTh)),'PNG')
	return im1

def addTitle(img,txt,fill=(0,0,0),size=0.618,bg=(255,255,255),mode='top'):
	iTxt=fixWidth(txt2im(txt,bg=bg,fill=fill),int(img.size[0]*size))
	ret=Image.new("RGB",(img.size[0],img.size[1]+iTxt.size[1]),bg)
	if(mode=='top'):
		ret.paste(iTxt,((ret.size[0]-iTxt.size[0])//2,0))
		ret.paste(img,(0,iTxt.size[1]))
	else:
		ret.paste(img,(0,0))
		ret.paste(iTxt,((ret.size[0]-iTxt.size[0])//2,img.size[1]))
	return ret
	
def cv2_get_GB(im,sampling=30,add_near=False,border=0.2):
	height,width,_=im.shape
	def rndxy():
		x=random.random()
		x=int(border*width*x*2) if x<0.5 else int(width-border*width*(1-x)*2)
		y=random.random()
		y=int(border*height*y*2) if y<0.5 else int(height-border*height*(1-y)*2)
		return x,y
	cnt={}
	for i in range(sampling):
		x,y=rndxy()
		c=tuple(im[y,x])
		cnt[c]=cnt.get(c,0)+1
	if(add_near):
		temp=colorDis((0,0,0),(10,10,10))
		func=lambda x:0.5**(x/temp)
		for i in cnt:
			for j in cnt:
				cdis=colorDis(i,j)
				cnt[i]+=cnt[j]*func(cdis)
		
	return max(list(cnt),key=lambda x:cnt[x])
	
def get_main_color(p,palette=100,exclude_colors=None,sweight=1.26,vweight=1.05):
	if(exclude_colors is None):
		exclude_colors=[]
	p=fixHeight(p.convert("RGB"),24)
	width,height=p.size
	t1=timer()
	if(palette):
		p=paletteIm(p,paletteSize=palette,paletteMinTh=gencd(2))
	#print("palette_time",t1.gettime())
	#p.show()
	count={}
	count1={}
	ret=[]
	for i in range(width):
		for j in range(height):
			c=p.getpixel((i,j))
			hsv=RGB2HSV(*c)
			t=(hsv[1]**sweight)*(hsv[2]**vweight)
			
			count[c]=count.get(c,0)+t**1.25
			count1[c]=count1.get(c,0)+1
	for i,j in count.items():
		for exc in exclude_colors:
			j*=(mymath.tanh1(1.45,gencd(8),0.7)(colorDis(exc,i))+0.8)**1.25
		ret.append((-j,i))
	ret.sort()
	
	#print("other_time",t1.gettime())
	print(count1[ret[0][-1]])
	return ret[0][-1]
'''def eye_matrix(pth=r'C:\anime-face-detector\detected_eyes'):
	pics=[]
	pics_=[]
	#fl=list(glob(r'C:\anime-eye-detect\posdata\*.jpg'))
	fl=list(glob(pth+r'\*.jpg'))
	fl+=list(glob(pth+r'\*.png'))
	random.shuffle(fl)
	for i in fl:
		pic=Image.open(i)
		pic=fixWidth(pic,120)
		pics.append(pic)
		pics_.append(Image.new("RGB",pic.size,get_main_color(pic.convert("RGB"),sweight=0.2,vweight=0.3,palette=100,exclude_colors=[(250,230,210)]*10+[(0,0,0)]*4+[(245,171,160)]*4+[(240,220,210)]+[(70,30,30)]*2+[(70,10,20)]+[(246,182,182)]*2+[(105,47,22)]+[(46,7,14)]+[(106,53,49)]+[(136,84,55)]+[(137,53,73)]+[(202,159,125)]+[(250,200,165)]+[(231,164,134)]+[(233,200,187)]+[(205,140,140)]*2+[(179,115,93)]+[(223,137,107)]+[(122,72,58)]+[(117,85,74)]+[(83,21,49)]+[(233,202,188)])))
	picMatrix(pics).show()
	picMatrix(pics_).show()'''
def cv22pil(cv2img):
	import cv2
	return Image.fromarray(cv2.cvtColor(cv2img,cv2.COLOR_BGR2RGB))
def pil2cv2(pilimg):
	import cv2,numpy
	return cv2.cvtColor(numpy.asarray(pilimg),cv2.COLOR_RGB2BGR)
def motion_blur(image, degree=12, angle=45):
	image = np.array(image)
	# 这里生成任意角度的运动模糊kernel的矩阵， degree越大，模糊程度越高
	M = cv2.getRotationMatrix2D((degree / 2, degree / 2), angle, 1)
	motion_blur_kernel = np.diag(np.ones(degree))
	motion_blur_kernel = cv2.warpAffine(motion_blur_kernel, M, (degree, degree))
	motion_blur_kernel = motion_blur_kernel / degree
	blurred = cv2.filter2D(image, -1, motion_blur_kernel)
	# convert to uint8
	cv2.normalize(blurred, blurred, 0, 255, cv2.NORM_MINMAX)
	blurred = np.array(blurred, dtype=np.uint8)
	return Image.fromarray(blurred)
def integ(mat):
	h,w=mat.shape
	temp=np.zeros((h+1,w+1),dtype=np.uint8)
	integral=cv2.integral(mat,temp,cv2.CV_64FC1).astype(np.int64)
	def query(x1,y1,x2,y2):
		x1,x2=sorted([x1+1,x2+1])
		y1,y2=sorted([y1+1,y2+1])
		ret=integral[x2,y2]-integral[x2,y1-1]-integral[x1-1,y2]+integral[x1-1,y1-1]
		return ret
	return query
def detect_hair_color(pilimg,dbg=False,exclude_colors=None,fw=250):
	import cv2,numpy
	if(exclude_colors is None):
		exclude_colors=[(250,230,210)]*10+[(0,0,0)]*4+[(245,171,160)]*3+[(240,220,210)]+[(70,30,30)]*2+[(70,10,20)]+[(246,182,182)]+[(105,47,22)]+[(46,7,14)]+[(106,53,49)]+[(136,84,55)]+[(137,53,73)]+[(202,159,125)]+[(250,200,165)]+[(231,164,134)]+[(233,200,187)]+[(205,140,140)]*2+[(179,115,93)]+[(223,137,107)]+[(122,72,58)]+[(117,85,74)]+[(83,21,49)]+[(233,202,188)]+[(254,207,200),(254,243,237)]+[(247,231,231)]+[(246,199,167)]+[(255,255,255)]
	
	rate=fw/pilimg.size[0]
	img=fixWidth(pilimg,fw).convert("RGB")
	img=paletteIm(img,paletteSize=80,paletteMinTh=gencd(2))
	cv2img=pil2cv2(img)
	gray=cv2.cvtColor(cv2img,cv2.COLOR_BGR2GRAY)
	w,h=img.size
	temp=numpy.zeros((h+1,w+1),dtype=numpy.uint8)
	integral=cv2.integral(gray,temp,cv2.CV_64FC1).astype(numpy.int64)
	detect_width=1
	def query_sum(x1,y1,x2,y2):
		x1,x2=sorted([x1+1,x2+1])
		y1,y2=sorted([y1+1,y2+1])
		ret=integral[x2,y2]-integral[x2,y1-1]-integral[x1-1,y2]+integral[x1-1,y1-1]
		return ret
	def query_h_diff(x,y,width=detect_width):
		le=query_sum(x-width,y-width,x-1,y+width)
		ri=query_sum(x+1,y-width,x+width,y+width)
		return le-ri
	def query_w_diff(x,y,width=detect_width):
		up=query_sum(x-width,y-width,x+width,y-1)
		lo=query_sum(x-width,y+1,x+width,y+width)
		return up-lo
	def query_wh_diff(x,y,width=detect_width):
		lu=query_sum(x-width,y-width,x-1,y-1)
		ru=query_sum(x+1,y-width,x+width,y-1)
		ll=query_sum(x-width,y+1,x-1,y+width)
		rl=query_sum(x+1,y+1,x+width,y+width)
		return lu+rl-ru-ll
	weights=np.zeros((h,w),dtype=np.float32)
	for detect_width in [2,5]:
		for i in range(detect_width,h-detect_width):
			for j in range(detect_width,w-detect_width):
				#weight=[]
				wd=float(abs(query_h_diff(i,j,width=detect_width)))
				hd=float(abs(query_w_diff(i,j,width=detect_width)))
				whd=abs(query_wh_diff(i,j,width=detect_width))
				#fun=lambda x,y:(x/y if x>y else y/x) if(x and y) else 0
				#weights[i,j]+=fun(wd,hd)
				weights[i,j]+=max([wd,hd,whd])/detect_width/detect_width
	
	cv2.normalize(weights,weights,0,255,cv2.NORM_MINMAX)
	diff_score={}
	count_score={}
	appear_pos={}
	for i in range(h):
		for j in range(w):
			c=img.getpixel((j,i))
			score=weights[i,j]
			diff_score[c]=diff_score.get(c,0)+score**0.8
			count_score[c]=count_score.get(c,0)+1
			
			if(c not in appear_pos):
				appear_pos[c]=[]
			appear_pos[c].append((j,i))
	ret=[]
	palette=set(diff_score)
	count_score1={}
	for color in count_score:
		palette.remove(color)
		nearest=getNearestColor(color,palette)[0]
		count_score1[color]=count_score[color]+count_score[nearest]
		palette.add(color)
	
	for color in diff_score:
		score=(diff_score[color])*(count_score1[color]**0.8)
		for exc in exclude_colors:
			score*=(mymath.tanh1(1.45,gencd(8),0.7)(colorDis(exc,color))+0.8)**1.25
		H,S,V=RGB2HSV(*color)
		#score*=(S**0.45)*(V**0.3)
		ret.append((-score,color,count_score[color],appear_pos[color]))
	ret.sort()
	if(dbg):
		img.show()
		
		temp=cv22pil(cv2.cvtColor(weights.astype(np.uint8),cv2.COLOR_GRAY2BGR))
		temp.show()
		for score,clr,count,apppos in ret[:3]:
			for pos in appear_pos[clr]:
				temp.putpixel(pos,clr)
			temp.show()
	return ret
def eye_pic2pic():
	eye_matrix()
	fl=list(glob(r'C:\anime-eye-detect\posdata\*.jpg'))
	il=ImageLib()
	for i in fl:
		il.open(i,whlimit=45)
	target=Image.open(r"M:\pic\temp\anime_detect\craw\1CxewYxPfyceAeD.jpg")
	w,h=target.size
	siz=(w*5,h*5)
	i1=pic2pic_offsetcorrection2(target,il,siz=siz,gsiz=(siz[0]//32,siz[1]//32),corr=3,ofs_cor_fun=ofs_cor_fun3)
	i2=pic2pic_offsetcorrection2(target,il,siz=siz,gsiz=(siz[0]//32,siz[1]//32),corr=3,ofs_cor_fun=ofs_cor_fun2)
	i3=pic2pic_offsetcorrection3(target,il,siz=siz,gsiz=(siz[0]//32,siz[1]//32),corr=3,ofs_cor_fun=ofs_cor_fun2)
	i1.show()
	i2.show()
	i3.show()
	target.show()
def yjsp_flash_pic(bg,im,pos):
	bg=bg.convert("RGB")
	
	x,y,w,h = pos
	im=im.convert("RGB").resize((w,h))
	for i in range(x,x+w):
		offset=np.zeros(3,np.int32)
		for j in range(y,y+h):
			if((i+j)%2):
				target=im.getpixel((i-x,j-y))
				original=bg.getpixel((i,j))
				offset+=np.array(original)-np.array(target)
				bg.putpixel(target)
			else:
				original=np.array(bg.getpixel((i,j)),int32)
				target=np.array([max(min(i,255),0) for i in tuple(original+offset)])
				offset+=target-original
				bg.putpixel(target)
	return bg
	
def get_main_colors(p,num=2,exclude_colors=None,sweight=1.26,vweight=1.2,debug=False,cnt_weight=0.4,rough=0.085,color_similarity_weight=1.42):
	if(exclude_colors is None):
		exclude_colors=[]
	if(debug):
		p1=fixHeight(p.convert("RGB"),100)
	p=fixHeight(p.convert("RGB"),30)
	
	width,height=p.size
	pp=np.zeros(shape=(width,height,3),dtype=np.int32)
	
	t1=timer()
	plt=int(max(width*height*0.2,min(num*20,width*height*0.6)))
	plts=[p.getpixel((random.randrange(width),random.randrange(height))) for i in range(plt)]
	
	cnt={}
	color_score={}	
	func1=mymath.tanh1(1.45,gencd(8),0.7)
	for i in range(width):
		for j in range(height):
			c=getNearestColor(p.getpixel((i,j)),plts)[0]
			hsv=RGB2HSV(*c)
			t=(hsv[1]**sweight)*(hsv[2]**vweight)
			for exc in exclude_colors:
				t*=(func1(colorDis(exc,c))+0.8)**1.25
			color_score[c]=t
			cnt[c]=cnt.get(c,0)+1
			#print(c,pp[i,j])
			pp[i,j]=c
	th=0
	times=0
	t0=len(plts)
	while(len(plts)>num):
		times+=1
		i=random.randrange(len(plts))
		j=(random.randrange(1,len(plts))+i)%len(plts)
		score=colorDis(plts[i],plts[j])**color_similarity_weight
		score*=(cnt[plts[i]]+cnt[plts[j]])**cnt_weight
		score*=(color_score[plts[i]]+color_score[plts[j]])
		if(score<th):
			temp=plts[-1]
			plts[-1]=plts[i]
			plts[i]=temp
			cnt[plts[j]]+=cnt[plts[i]]
			plts.pop()
		else:
			th=max(th*1.05,(1-rough)*th+rough*score)
	print(times,t0,t1.gettime())
	if(debug):
		'''for i in range(width):
			for j in range(height):
				pp[i,j]=getNearestColor(tuple(pp[i,j]),plts)[0]
		Image.fromarray(pp.transpose(1,0,2).astype(np.uint8)).show()
		p.show()'''
		
		for i in range(p1.size[0]):
			for j in range(p1.size[1]):
				p1.putpixel((i,j),getNearestColor(p1.getpixel((i,j)),plts)[0])
		p1.show()
	return plts
	
def test_main_color(pth):
	im=Image.open(pth)
	import time
	t=time.time()
	c=get_main_color(im,palette=0)
	print("%.3f"%(time.time()-t))
	#Image.new("RGB",(100,100),c).show()
	c1=tuple([i-5 for i in c])
	c2=tuple([i+5 for i in c])
	cv22pil(cv2.inRange(cv2.cvtColor(pil2cv2(im),cv2.COLOR_BGR2RGB),c1,c2)).show()
def test_cv2_get_GB(pth):
  im=cv2.imread(pth)
  import time
  t=time.time()
  c=np.array(cv2_get_GB(im,sampling=20,add_near=False),np.int32)
  
  c1=c-5
  c2=c+5
  print(time.time()-t,c,c1,c2)
  cv22pil(cv2.inRange(im,c1,c2)).show()
def paletteIm1(img,k):
	sample=k*10
	temp=[]
	for i in range(sample):
		x,y=random.randrange(img.size[0]),random.randrange(img.size[1])
		temp.append(img.getpixel((x,y)))
	pal,gn=kmeans(temp,k)
	for i in range(img.size[0]):
		#print(i/img.size[0])
		for j in range(img.size[1]):
			c=[int(i) for i in gn(img.getpixel((i,j)))]
			img.putpixel((i,j),tuple(c))
	return img
def get_border_color(img,n=10):
	w,h=img.size
	ret=0
	for i in range(n):
		if(random.random()<0.5):
			x=random.choice([0,w-1])
			y=random.randrange(h)
		else:
			y=random.choice([0,h-1])
			x=random.randrange(w)
		ret=np.array(img.getpixel((x,y)))+ret
	return tuple([int(_/n) for _ in ret])
def bubble(img,lu,up,le,mi,border_size=None,ru=None,ll=None,rl=None,lo=None,ri=None,mid_border_size=None):
	
	if(border_size is None):
		border_size=int(img.size[1]/2.1)
	if(mid_border_size is None):
		mid_border_size=int(border_size/1.618)
	_,__=img.size
	_-=2*(border_size-mid_border_size)
	__-=2*(border_size-mid_border_size)
	bs=border_size
	w,h=_+border_size*2,__+border_size*2
	ret=Image.new("RGBA",(w,h))
	ret1=Image.new("RGBA",(w,h))
	if(ru is None):
		ru=lu.transpose(Image.FLIP_LEFT_RIGHT)
	if(ri is None):
		ri=le.transpose(Image.FLIP_LEFT_RIGHT)
	if(rl is None):
		rl=lu.transpose(Image.ROTATE_180)
	if(lo is None):
		lo=up.transpose(Image.FLIP_TOP_BOTTOM)
	if(ll is None):
		ll=lu.transpose(Image.FLIP_TOP_BOTTOM)
	
	ret.paste(lu.resize((bs,bs),Image.LANCZOS),(0,0))
	ret.paste(up.resize((_,bs),Image.LANCZOS),(bs,0))
	ret.paste(ru.resize((bs,bs),Image.LANCZOS),(bs+_,0))
	#ret.show()
	
	
	ret.paste(le.resize((bs,__),Image.LANCZOS),(0,bs))
	ret.paste(mi.resize((_,__),Image.LANCZOS),(bs,bs))
	ret.paste(ri.resize((bs,__),Image.LANCZOS),(bs+_,bs))
	#ret.show()
	
	ret.paste(ll.resize((bs,bs),Image.LANCZOS),(0,bs+__))
	ret.paste(lo.resize((_,bs),Image.LANCZOS),(bs,bs+__))
	ret.paste(rl.resize((bs,bs),Image.LANCZOS),(bs+_,bs+__))
	#ret.show()
	
	ret1.paste(img,(mid_border_size,mid_border_size))
	#print(bs,mid_border_size)
	#ret1.show()
	return Image.alpha_composite(ret,ret1)
def load_bubble(pth):
	dic={}
	for i in glob(path.join(pth,'*.png')):
		bn=path.splitext(path.basename(i))[0]
		dic[bn]=Image.open(i)
	return dic
default_bubble=lambda:load_bubble(path.join(path.dirname(__file__),'bubble1'))
def horizontal_layout(imgs,width=512,border=20,bg=(255,)*4,trim_width=False):
	top=border
	left=border
	now_height=0
	lefts=[]
	tops=[]
	trimed_width=0
	for i in imgs:
		if(left+i.size[0]>width-border):
			top+=now_height+border
			left=0
			now_height=0
		now_height=max(now_height,i.size[1])
		lefts.append(left)
		trimed_width=max(trimed_width,left+i.size[0]+border)
		tops.append(top)
		left+=i.size[0]+border
	height=top+now_height+border
	ret=Image.new("RGBA",(trimed_width if trim_width else width,height),bg)
	for idx,i in enumerate(imgs):
		ret.paste(i,(lefts[idx],tops[idx]),i)
	return ret
def pinterest(imgs,column_num,border=None,widths=None,bg=(0,)*4):
	if(border is None):
		border=int((0.01*imgs[0].size[0]*imgs[0].size[1])**0.5)
	if(widths is None):
		widths=[_.size[0] for _ in imgs[:column_num]]
	width=sum(widths)+(column_num+1)*border
	le_to_pi=[]
	left=[border]
	for i in widths[:-1]:
		left.append(left[-1]+i+border)
	top=[border for i in range(column_num)]
	height=0
	for i in imgs:
		min_idx=0
		for j in range(column_num):
			if(top[j]<top[min_idx]):
				min_idx=j
		to=top[min_idx]
		le=left[min_idx]
		pi=fixWidth(i,widths[min_idx])
		top[min_idx]+=pi.size[1]+border
		height=max(height,top[min_idx])
		le_to_pi.append((le,to,pi))
	im=Image.new("RGBA",(width,height),bg)
	for le,to,pi in le_to_pi:
		im.paste(pi.convert("RGBA"),(le,to))
	return im
if(__name__=='__main__'):
	#bb=load_bubble(r'M:\pic\setubot-iot\static_pics\bubble2')
	bb=default_bubble()
	print(bb)
	bubble(txt2im('(｡ŏ﹏ŏ)(っ °Д °;)っ',fixedHeight=50,fill=(255,230,180)),**bb).show()
	
	tmp=[]
	for t in ['tag1','tag2','tag3']:
		tmp.append(bubble(txt2im(t,fixedHeight=30),**bb))
	horizontal_layout(tmp).show()
	horizontal_layout(tmp,trim_width=True).show()