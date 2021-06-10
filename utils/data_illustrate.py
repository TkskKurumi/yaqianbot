from PIL import ImageDraw,ImageFont,Image
from pic2pic import txt2im_ml,txt2im,circle_mask_RGBA
#def horizontal_bar():
import random
from myGeometry import point
def circles(circles,sizes,width,height,bg=(255,)*4):
	_=sum([_*_ for _ in sizes])
	rate=width*height/_
	rnd=random.random
	n=len(circles)
	
	def r(idx):
		return sizes[idx]*rate
	mxrate=0
	for i in range(n):
		rate=min(min(rate,width/sizes[i]/2.5),height/sizes[i]/2.5)
	xy=[(rnd()*(width-r(i)*2)+r(i),rnd()*(height-r(i)*2)+r(i)) for i in range(n)]
	mxxy=None
	def render(mxxy,mxrate):
		from PIL import Image
		ret=Image.new("RGBA",(width,height),bg)
		for i in range(n):
			siz=int(r(i)*2)
			if(not siz):
				print('ln64',siz,rate,mxxy[i])
				continue
			x,y=mxxy[i]
			x=int(x-siz/2)
			y=int(y-siz/2)
			im=circles[i].resize((siz,siz)).convert("RGBA")
			#im=circle_mask_RGBA(im)
			ret.paste(im,box=(x,y),mask=im)
			#print(x,y,siz)
		return ret
	T=0
	mxt=2000000//n//n
	#mxt=10
	fuc=True
	idxs=list(range(n))
	while(T<=mxt or (not mxxy)):
		
		T+=1
		flag=1
		rate=rate*1.5
		if(rnd()<0.015):
			xy=[(rnd()*(width-r(i)*2)+r(i),rnd()*(height-r(i)*2)+r(i)) for i in range(n)]
		for i in range(n):
			x,y=xy[i]
			rate=min(min(rate,width/sizes[i]/2),height/sizes[i]/2)
			_r=r(i)
			x=min(max(_r,x),width-_r)
			y=min(max(r(i),y),height-_r)
			xy[i]=x,y
		#render(xy,rate).show()
		random.shuffle(idxs)
		for idx,i in enumerate(idxs):
			for jdx in range(idx):
				j=idxs[jdx]
				pi=point(*xy[i])
				pj=point(*xy[j])
				pij=pj-pi
				if(pi.dist(pj)==0):
					continue
				ri=r(i)
				rj=r(j)
				if(pi.dist(pj)<ri+rj):
					'''if(i==n-1):
						if(j==i-1):
							rd1=render(xy,rate)'''
					PI=pi-pij.unit()*ri
					PJ=pj+pij.unit()*rj
					PIJ=PJ-PI
					_rate=PIJ.distO()/(ri+rj)/2
					#print(_rate)
					rate*=_rate
					xy[i]=(PI+pij.unit()*r(i)).xy
					xy[j]=(PJ-pij.unit()*r(j)).xy
					'''if(i==n-1):
						if(j==i-1):
							rd2=render(xy,rate)'''
						
#		if(flag):#
		if(rate>mxrate):
			mxrate=rate
			mxxy=xy[:]
		'''if(random.random()<0.1):
			render(xy,rate).show()'''
	#print('T',T)
	# rd1.show()
	# rd2.show()
	return render(mxxy,mxrate)
if(__name__=='__main__'):
	im1=Image.open(r"C:\Users\TokisakiKurumi\Pictures\QQ图片20200725200402.jpg")
	rge=10
	c=[im1]*rge
	sizes=range(1,1+rge)
	circles(c,sizes,200,300).show()