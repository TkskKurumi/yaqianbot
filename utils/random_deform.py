from annoy import AnnoyIndex
from PIL import Image
import myGeometry,random,math,pic2pic
import numpy as np
rr=random.randrange
rnd=random.random
def random_deform(im,cnt=500,neibour_cnt=3,fix_corner=True,fix_border=False,x_range=0.0,y_range=0.0,method=2,qd=None,border_method=0):
	if(method==2):
		neibour_cnt=3

	im=im.convert("RGBA")
	width,height=im.size
	w,h=width,height
	arr=np.asarray(im).swapaxes(0,1)
	#imnew=Image.new("RGBA",(w,h))
	arrnew=np.zeros(arr.shape)
	mp={}
	if(qd):
		mp.update(qd)
	rndw=lambda w=width:rr(w)
	rndh=lambda h=height:rr(h)
	npa=lambda _:np.array(_,np.float64)
	if(fix_corner):
		for x in [0,width-1]:
			for y in [0,height-1]:
				mp[(x,y)]=np.array((x,y),np.float64)
	if(fix_border):
		for x in range(width):
			mp[(x,0)]=npa((x,0))
			mp[(x,h-1)]=npa((x,h-1))
		for y in range(height):
			mp[(0,y)]=npa((0,y))
			mp[(w-1,y)]=npa((w-1,y))
	for i in range(cnt):
		x0,y0=rndw(),rndh()
		x1=x0+(rnd()-rnd())*x_range*width
		y1=y0+(rnd()-rnd())*y_range*height
		mp[(x0,y0)]=np.array((x1,y1),np.float64)
		
	mpl=list(mp)
	mpl_p=[myGeometry.point(x,y) for x,y in mpl]
	mpl1=npa([mp[i] for i in mp])
	
	ann=AnnoyIndex(2,'euclidean')
	for idx,i in enumerate(mpl):
		ann.add_item(idx,i)
	ann.build(2)
	
	def getp(x,y):
		if(x<0.5):
			xx=[(0,0.5),(0,0.5)]
		elif(x>w-1.5):
			xx=[(w-1,0.5),(w-1,0.5)]
		else:
			xx=[(int(x),int(x)+1-x),(int(x)+1,x-int(x))]
		
		if(y<0.5):
			yy=[(0,0.5),(0,0.5)]
		elif(y>h-1.5):
			yy=[(h-1,0.5),(h-1,0.5)]
		else:
			yy=[(int(y),int(y)+1-y),(int(y)+1,y-int(y))]
		
		ps=[arr[i[0],j[0]]*i[1]*j[1] for i in xx for j in yy  if(i[1]and j[1])]
		
		return sum(ps)
	
	'''def getp(x,y):
		xx=[(int(x),int(x)+1-x),(int(x)+1,x-int(x))]
		
		yy=[(int(y),int(y)+1-y),(int(y)+1,y-int(y))]
		
		ps=[arr[i[0],j[0]]*i[1]*j[1] for i in xx for j in yy if(i[1]and j[1])]
		
		return sum(ps)'''
	def weight_method1(point,neibours,dists,debug=False):
		point=myGeometry.point(*point)
		nbc=len(neibours)
		w=np.zeros(nbc,np.float64)
		sm=0
		for idx,i in enumerate(neibours):
			for jdx,j in enumerate(neibours):
				if(mpl_p[i]==mpl_p[j]):
					continue
				
				ab=mpl_p[j]-mpl_p[i]
				ap=point-mpl_p[i]
				abd=ab.distO()
				
				d=(abs(ab**ap)/2)/abd if abd>1e-6 else 0
				if(debug):
					print(idx,jdx,d)
				w[idx]-=d
				w[jdx]-=d
				sm+=d
		if(debug):
			print([mpl_p[i] for i in neibours])
			print(w,sm,point)
		smsm=sum(w)+sm*nbc
		
		for i in range(nbc):
			w[i]=(w[i]+sm)/smsm
		
		return w
	def weight_method2(point,neibours,dists,debug=False):
		P=myGeometry.point(*point)
		nbc=3
		w=np.zeros(3)
		sm=0
		ABC=abs((mpl_p[neibours[0]]-mpl_p[neibours[1]])**(mpl_p[neibours[0]]-mpl_p[neibours[2]]))
		if(ABC<1e-6):
			adx,bdx=max([(0,1),(1,2),(2,0)],key=lambda t:mpl_p[neibours[t[0]]].dist(mpl_p[neibours[t[1]]]))
			
			A=mpl_p[neibours[adx]]
			B=mpl_p[neibours[bdx]]
			AB=A.dist(B)
			AP=A.dist(P)
			BP=B.dist(P)
			w[adx]=BP/AB
			w[bdx]=AP/AB
			return w
		for adx in range(3):
			bdx=(adx+1)%3
			cdx=(adx+2)%3
			A=mpl_p[neibours[adx]]
			B=mpl_p[neibours[bdx]]
			C=mpl_p[neibours[cdx]]
			#print(A,B,C,adx,bdx,cdx)
			try:
				_=abs(((P-C)**(P-B))/ABC)
			except Exception as e:
				print(A,B,C)
				raise e
			w[adx]=_
			sm+=_
		return w/sm
	for i in range(width):
		#print(i/width)
		for j in range(height):
			
			neibours=list(ann.get_nns_by_vector((i,j),neibour_cnt,include_distances=True))
			nbc=len(neibours[0])
			if(method==0):
				
				neibours[1]=[1/_ if _>1e-6 else 1e7 for _ in neibours[1]]
			elif(method==1):
				neibours[1]=weight_method1((i,j),neibours[0],neibours[1],debug=(i==0 and j==0))
				# if(i==j and i==0 and debug):
					# print(neibours[1])
			elif(method==2):
				neibours[1]=weight_method2((i,j),neibours[0],neibours[1],debug=(i==width//2 and j==height//2))
				# if(i==width//2 and j==height//2 and debug):
					# print(neibours[1])
			sum_dist=sum(neibours[1])
			sum_p=sum([mpl1[neibours[0][_]]*neibours[1][_] for _ in range(nbc)])
						
			
			
			x,y=tuple(sum_p/sum_dist)
			if(i==50 and j==50):
				#print(x,y,neibours)
				#print([mpl1[_] for _ in neibours[0]])
				pass
			if(x<0 or x>w-1 or y<0 or y>h-1):
				if(border_method==0):
					x=min(max(0,x),w-1)
					y=min(max(0,y),h-1)
					arrnew[i,j]=getp(x,y)
				
			else:
				arrnew[i,j]=getp(x,y)
	#print(mp)
	return Image.fromarray(arrnew.astype(np.uint8).swapaxes(0,1))
if(__name__=='__main__'):
	img=Image.open(r"M:\pic\timg1.jpg")
	img=pic2pic.im_sizeSquareSize(img,20000)
	w,h=img.size
	random_deform(img,cnt=0,neibour_cnt=3,method=2).show()
	
	npa=lambda _:np.array(_,np.float64)
	
	import time
	tmtm=time.time()
	imgs=[]
	
	for t in range(-1,5):
		qd={}
		p=myGeometry.point(-w*(2**t),h*0.7)
		for i in range(w):
			for j in range(h):
				pp=myGeometry.point(i,j)
				pp=p+(pp-p).unit()*abs((pp-p).x)
				qd[pp.xy]=npa((i,j))
		imgs.append(random_deform(img,cnt=0,neibour_cnt=4,qd=qd,method=0))
	for t in range(4,-2,-1):
		qd={}
		p=myGeometry.point(w+w*(2**t),h*0.7)
		for i in range(w):
			for j in range(h):
				pp=myGeometry.point(i,j)
				pp=p+(pp-p).unit()*abs((pp-p).x)
				qd[pp.xy]=npa((i,j))
		imgs.append(random_deform(img,cnt=0,neibour_cnt=4,qd=qd,method=0))
	
	import make_gif
	print(make_gif.make_gif(imgs+imgs[::-1],fps=18,ss=20000))
	print(time.time()-tmtm)
	#random_deform(img,cnt=0,neibour_cnt=3).show()
	#random_deform(img,cnt=0,neibour_cnt=3,method=0).show()
	
	exit()
			