from PIL import Image
from urllib import request
import pic2pic,random,qrcode
from hashlib import md5
from smms import smms
import os,sys,getopt,myhash,threading

lck=threading.Lock()
boxsiz=20
def int2c(i):
	return (int(i/256/256),int(i/256)%256,i%256)
def getoptions(arg):
	temp=''
	ret={}
	for i in arg:
		if(i[0]=='-'):
			temp=i
			ret[i]=[]
		else:
			ret[temp].append(i)		
	return ret
blx=int2c(0xFFA3F8)
whx=int2c(0x0053C1)
#tilec=[0x403150,0x803A9E,0xF95E71,0x70F0F4,0xDB67AE]
tilec_red=[0xFF3ABA,0xFF6D9E,0xFFA5A5]
tilec_pink=[0xFFA3F8,0xEAA0FF,0xFFA3C6]
tilec_blue=[0x357CFF,0x467FC4,0x0053C1]
tilec_orange=[0xFF6500,0xE05900]
tilec_bw=[0x0,0xffffff]
tilec_cyan=[0x0053C1,0x77DAFF,0x70B0FF]
tilec_miku=[0x39C5BB,0x66ffcc,0x33cccc,0x00ffcc]
tilec_flesh=[0xFFF8ED,0xFEE9D4]
tilec_brown=[0x824621,0xA53C00,0xB70000]
tilec_lightsalmon=[0xFCA96F,0xF9CCAE,0xF4B17A]
tilec_gold=[0xFBFF99,0xFFEDCC,0xF2FF7F]
tilec_lightpurple=[0xE2CEE5,0xCDA4D8,0xD7A3E0]
tilec_purple=[0x77458f,0x682B87,0x5700EF]

tilec=tilec_pink+tilec_miku

tilea=0.6
gridsize=1
mosaic=False


thx=8
#print(tilec)
#exit()
if(pic2pic.cBrightness(blx)>thx):
	tbr=pic2pic.cBrightness(blx)
	blx=tuple([int(blx[i]/tbr*thx) for i in [0,1,2]])
if(pic2pic.cBrightness(whx)<(100-thx)):
	tbr=100-pic2pic.cBrightness(whx)
	whx=tuple([int(255-(255-whx[i])/tbr*thx) for i in [0,1,2]])



def filt2(x,y,xy,picQR):
	th=50
	tan=1
	brx=pic2pic.cBrightness(x)
	grid=boxsiz*(1+tan)/1.41*gridsize
	
	
	if(brx<50):
		x=blx
	else:
		x=whx
	
	halfdotsiz=int(boxsiz/10)
	if(halfdotsiz==0):
		halfdotsiz=1
	
	tilea_=(1+tilea)/2
	
	for i in range(len(tilec)):
		if(not(isinstance(tilec[i],tuple))):
			tilec[i]=int2c(tilec[i])
	if(	xyinbox(xy,(0,0,boxsiz*8,boxsiz*8))or
	xyinbox(xy,(0,picQR.size[1]-boxsiz*8,boxsiz*8,picQR.size[1]))or
	xyinbox(xy,(picQR.size[0]-boxsiz*8,0,picQR.size[0],boxsiz*8))or
	xyinbox(xy,(picQR.size[0]-boxsiz*9,picQR.size[1]-boxsiz*9,picQR.size[0]-boxsiz*4,picQR.size[1]-boxsiz*4))
	):
		a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*99987) % len(a_)]*0.05
	else:
		temp0=xy[0]%boxsiz
		temp1=xy[1]%boxsiz
		a=a_[(int((xy[0]+tan*xy[1])/grid)*97+int((xy[1]/tan-xy[0]+1000)/grid)*1230) % len(a_)]
		if(xyinbox((temp0,temp1),(boxsiz/2-halfdotsiz ,boxsiz/2-halfdotsiz ,boxsiz/2+halfdotsiz+1 ,boxsiz/2+halfdotsiz+1))and(pic2pic.colorDis(x,y)>pic2pic.colorDis((0,0,0) , (th,th,th)) or (a>0.20))):
			a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*1250) % len(a_)]*0.2
		else:
			
			a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*99987 + int(xy[1]/grid*2)*1007 ) % len(a_)]*(1-tilea)+tilea
			a1=a_[(int((xy[0]+tan*xy[1])/grid)*10007+int((xy[1]/tan-xy[0]+1000)/grid)*100007) % len(a_)]
			a2=a_[(int((xy[0]+tan*xy[1])/grid)*100007+int((xy[1]/tan-xy[0]+1000)/grid)*9987+int(xy[0]/grid*2)*93) % len(a_)]
			a3=a_[(int((xy[0]+tan*xy[1])/grid)*10007+int((xy[1]/tan-xy[0]+1000)/grid)*1007) % len(a_)]
			if(mosaic):
				grid=grid/1.7
				a2=a_[(int((xy[0]+tan*xy[1])/grid)*100007+int((xy[1]/tan-xy[0]+1000)/grid)*9987+int(xy[0]/grid*2)*93) % len(a_)]
				if(pic2pic.colorEqual(y,mosaicc)):
					return tilec[int(a2*len(tilec))]
			t=int(a2*len(tilec))
			if(a1>tilea_):
				return tuple([int(y[i]*a1+tilec[t][i]*(1-a1)) for i in range(len(x))])
			else:
				if(a1<0.7*tilea_):
					
					return tuple([int(tilec[t][i]*(1-a)+y[i]*a) for i in range(len(x))])
				else:
					return tuple([int(y[i]*a+x[i]*(1-a)) for i in range(len(x))])
				
					
	return tuple([int(y[i]*a + x[i]*(1-a)) for i in range(len(x))])


	
	tan=1
	grid=boxsiz*(1+tan)*0.4
	halfdotsiz=boxsiz/7
	if(halfdotsiz<1):
		halfdotsiz=1
	if(	xyinbox(xy,(0,0,boxsiz*8,boxsiz*8))or
	xyinbox(xy,(0,picQR.size[1]-boxsiz*8,boxsiz*8,picQR.size[1]))or
	xyinbox(xy,(picQR.size[0]-boxsiz*8,0,picQR.size[0],boxsiz*8))or
	xyinbox(xy,(picQR.size[0]-boxsiz*9,picQR.size[1]-boxsiz*9,picQR.size[0]-boxsiz*4,picQR.size[1]-boxsiz*4))
	):
		a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*99987) % len(a_)]*0.2
	else:
		temp0=xy[0]%boxsiz
		temp1=xy[1]%boxsiz
		if(xyinbox((temp0,temp1),(boxsiz/2-halfdotsiz ,boxsiz/2-halfdotsiz ,boxsiz/2+halfdotsiz+1 ,boxsiz/2+halfdotsiz+1))):

			a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*99987) % len(a_)]*0.4
		else:
			a=a_[(int((xy[0]+tan*xy[1])/grid)*9987+int((xy[1]/tan-xy[0]+1000)/grid)*99987) % len(a_)]*0.5+0.5
			a1=a_[(int((xy[0]+tan*xy[1])/grid)*10007+int((xy[1]/tan-xy[0]+1000)/grid)*100007) % len(a_)]
			a2=a_[(int((xy[0]+tan*xy[1])/grid)*100007+int((xy[1]/tan-xy[0]+1000)/grid)*9987) % len(a_)]*0.5
			if(a1>0.3):
				if(a<0.5):
					a=a*a*a
				else:
					a=1-(1-a)*(1-a)*(1-a)
				return tuple([int(y[i]*a+a1*x[i]*(1-a)) for i in range(len(x))])
				return 
			else:
				if(a1>0.14):
					return tuple([int(x[i]*a+a2*(255)*(1-a)) for i in range(len(x))])
					
				else:
					return tuple([int(x[i]*a2) for i in range(len(x))])
					
	return tuple([int(y[i]*a + x[i]*(1-a)) for i in range(len(x))])
	

	
	halfdotsiz=boxsiz/7
	if(halfdotsiz<1):
		halfdotsiz=1
	if(	xyinbox(xy,(0,0,boxsiz*8,boxsiz*8))or
	xyinbox(xy,(0,picQR.size[1]-boxsiz*8,boxsiz*8,picQR.size[1]))or
	xyinbox(xy,(picQR.size[0]-boxsiz*8,0,picQR.size[0],boxsiz*8))or
	xyinbox(xy,(picQR.size[0]-boxsiz*9,picQR.size[1]-boxsiz*9,picQR.size[0]-boxsiz*4,picQR.size[1]-boxsiz*4))
	):
		a=0
	else:
		temp0=xy[0]%boxsiz
		temp1=xy[1]%boxsiz
		if(xyinbox((temp0,temp1),(boxsiz/2-halfdotsiz ,boxsiz/2-halfdotsiz ,boxsiz/2+halfdotsiz+1 ,boxsiz/2+halfdotsiz+1))):
			a=0
		else:
			
			a=1
	return int(y*a + x*(1-a))	



a_=[random.random() for i in range(233)]

def xyinbox(xy,box):
	return (box[0]<=xy[0])and(xy[0]<box[2])and(box[1]<=xy[1])and(xy[1]<box[3])

def make(qrlink='https://twitter.com/mea_Love45/with_replies',picPic=None):
	lck.acquire()
	try:
		qr=qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_Q,
			box_size=boxsiz,
			border=0,
		)
		qr.add_data(qrlink)
		picQR=qr.make_image().convert('RGB')
		if(not(picPic)):
			lck.release()
			return picQR
		f=lambda x,y,xy:filt2(x,y,xy,picQR)
	#print(qrsavepath)
		lck.release()
		return pic2pic.imageBlend(picQR,picPic,f=f,resizefilt=Image.LANCZOS)
	except Exception as e:
		try:
			lck.release()
		except Exception:
			pass
if(__name__=='__main__'):
	pp=Image.open(r"C:\pyxyv\tempimgcache\83432135_p1_master1200.jpg")
	import time
	t=time.time()
	im=make(picPic=pp)
	print(time.time()-t)
	im.show()