import myMesh,pic2pic,random,time
from PIL import Image
from myGeometry import point
import numpy as np
from math import floor,ceil
from array import array

def npa2color(nda):
	return tuple([int(i) for i in nda])
_debug_info={}
class mesh_deform:
	def __init__(self,img,ss=None,mesh_cnt=100,qdpoints=None,ensure_corner=True):
		if(ss is not None):
			img=pic2pic.squareSize(img,ss)
		self.img=img.convert("RGBA")
		self.arr=np.asarray(self.img).swapaxes(0,1).astype(np.float32)
		temp=[]
		w,h=img.size
		for i in range(w):
			temp.append(self.arr[i,0])
			temp.append(self.arr[i,h-1])
		for j in range(h):
			temp.append(self.arr[0,j])
			temp.append(self.arr[w-1,j])
		self.bgcolor=sum(temp)/len(temp)
		self.bgcolor=npa2color(self.bgcolor)
		self.w=w
		self.h=h
		points=[]
		if(mesh_cnt):
			for i in range(mesh_cnt*5):
				points.append((random.randrange(w),random.randrange(h)))
			points=pic2pic.kmeans(points,mesh_cnt)[0]
		if(qdpoints):
			points+=qdpoints
		if(ensure_corner):
			for x in [0,w-1]:
				for y in [0,h-1]:
					points.append((x,y))
		points=[point(x,y) for x,y in points]
		self.mesh=myMesh.mesh.generate_mesh_by_points1(points)
		self.mesh.point_info=[_ for _ in self.mesh.points]
	
	def getp(self,x,y):
		w,h=self.w,self.h
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
		
		
		ps=[self.arr[i[0],j[0]]*i[1]*j[1] for i in xx for j in yy  if(i[1]and j[1])]
		
		return sum(ps)
	
	def getp_nn(self,x,y):
		
		return self.arr[int(x),int(y)]
	'''def render(self,bg=None):
		if(bg is None):
			bg=self.bgcolor
		w,h=self.w,self.h
		ret=Image.new("RGBA",(w,h),bg)
		for i in range(w):
			for j in range(h):
				msh=self.mesh.get_mesh_by_xy(i,j,include_weights=True)
				if(msh is None):
					#print(i,j,'is None')
					continue
				p=sum([self.mesh.point_info[idx]*w for idx,w in msh])
				x,y=p.xy
				if(x<0 or y<0 or x>=w or y>=h):
					continue
				ret.putpixel((i,j),npa2color(self.getp(x,y)))
		return ret'''
	def get_tri_integral_point(self):
		return self.mesh.get_tri_integral_point()
	def render1(self,bg=None,mode='img',resampling='nearest'):
		points=self.points
		if(bg is None):
			bg=self.bgcolor
		w,h=self.w,self.h
		if(resampling=='bilinear'):
			getp=self.getp
		else:
			getp=self.getp_nn
		mode_img=mode=='img'
		mode_arr=mode=='arr'
		if(mode_img):
			ret=Image.new("RGBA",(w,h),bg)
		elif(mode=='xyrgb'):
			ret=[]
		elif(mode=='arr'):
			retx=array()
		'''elif(mode=='eximg'):
			tmtm=time.time()
			temp=self.render1(mode='xyrgb',resampling=resampling)
			
			le=min(temp,key=lambda p:p[0])[0]
			ri=max(temp,key=lambda p:p[0])[0]
			up=min(temp,key=lambda p:p[1])[1]
			lo=max(temp,key=lambda p:p[1])[1]
			w=ri-le+1
			h=lo-up+1
			#print(le,ri,up,lo)
			#print(temp[:10])
			ret=np.zeros((h,w,4),np.float32)
			#ret=Image.new('RGBA',(w,h),(0,0,0,0))
			for i in temp:
				x,y,x1,y1=i
				#ret.putpixel((x-le,y-up),(r,g,b,a))
				ret[y-up,x-le]=getp(x1,y1)
			#print(time.time()-tmtm,end='\r')
			#print('lentemp=%d,time=%.3fms'%(len(temp),(time.time()-tmtm)*1000),end='\r')
			global _debug_info
			_debug_info['time']=time.time()-tmtm
			_debug_info['len_temp']=len(temp)
			return Image.fromarray(ret.astype(np.uint8)),le,up'''
		fkey1=lambda p:p.x
		fkey2=lambda UV:((x-UV[0].x)*(x-UV[1].x),UV[0].x-UV[1].x)
		func=lambda A,B,x:((B.x-x)*A.y+(x-A.x)*B.y)/(B.x-A.x)
		funcr=lambda x,y,L,R:(max(x,L),min(y,R))
		
		def calc_weights(a,b,c,P):
			A=points[a]
			B=points[b]
			C=points[c]
			#SABC=abs((A-B)**(A-C))
			SA=abs((P-B)**(P-C))/SABC
			SB=abs((P-A)**(P-C))/SABC
			SC=abs((P-A)**(P-B))/SABC
			return ((a,SA),(b,SB),(c,SC))
		if(mode_img):
			for a,b,c in self.mesh.tris:
				A,B,C=self.points[a],self.points[b],self.points[c]
				A,B,C=sorted([A,B,C],key=fkey1)
				SABC=abs((A-B)**(A-C))
				L=A.x
				R=C.x
				
				L,R=funcr(L,R,0,w-1)
				edgs=[(A,B),(B,C),(A,C)]
				for x in range(ceil(L),floor(R)+1):
					
					edgs.sort(key=fkey2)
					e1=edgs[0]
					e2=edgs[1]
					y1=func(*e1,x)
					y2=func(*e2,x)
					UP=ceil(min(y1,y2))
					LO=floor(max(y1,y2))
					
					UP,LO=funcr(UP,LO,0,h-1)
					for y in range(UP,LO+1):
						P=point(x,y)

						idx_weights=calc_weights(a,b,c,P)
						p=sum([self.mesh.point_info[idx]*w for idx,w in idx_weights])
						x1,y1=p.xy
						if(x1<0 or y1<0 or x1>=w or y1>=h):
							continue
						ret.putpixel((x,y),npa2color(self.getp(x1,y1)))
						
		elif(mode=='xyrgb'):
			for a,b,c in self.mesh.tris:
				A,B,C=self.points[a],self.points[b],self.points[c]
				A,B,C=sorted([A,B,C],key=fkey1)
				SABC=abs((A-B)**(A-C))
				L=A.x
				R=C.x
				edgs=[(A,B),(B,C),(A,C)]
				
				ct=(A+B+C)/3
				ep=0.02
				PC=sum([self.mesh.point_info[idx]*w for idx,w in calc_weights(a,b,c,ct)])
				P10=(sum([self.mesh.point_info[idx]*w for idx,w in calc_weights(a,b,c,ct+point(ep,0))])-PC)/ep
				P01=(sum([self.mesh.point_info[idx]*w for idx,w in calc_weights(a,b,c,ct+point(0,ep))])-PC)/ep
				P00=PC-P01*ct.y-P10*ct.x
				k_x1_x,k_y1_x=P10.xy
				k_x1_y,k_y1_y=P01.xy
				b_x1,b_y1=P00.xy
				
				for x in range(ceil(L),floor(R)+1):
					
					edgs.sort(key=fkey2)
					e1=edgs[0]
					e2=edgs[1]
					y1=func(*e1,x)
					y2=func(*e2,x)
					UP=ceil(min(y1,y2))
					LO=floor(max(y1,y2))
					x1=x*k_x1_x+(UP-1)*k_x1_y+b_x1
					y1=x*k_y1_x+(UP-1)*k_y1_y+b_y1
					for y in range(UP,LO+1):
						x1+=k_x1_y
						y1+=k_y1_y
						if(x1<0 or y1<0 or x1>w-1 or y1>h-1):
							continue
						ret.append((x,y,x1,y1))
		elif(mode=='eximg'):
			_debug_info['time']=-time.time()
			len_temp=0
			pinfo=self.mesh.point_info
			
			le=ceil(min(points,key=lambda p:p.x).x)
			ri=floor(max(points,key=lambda p:p.x).x)
			up=ceil(min(points,key=lambda p:p.y).y)
			lo=floor(max(points,key=lambda p:p.y).y)
			ww=ri-le+1
			hh=lo-up+1
			ret=np.zeros((hh,ww,4),np.float32)
			for a,b,c in self.mesh.tris:
				A,B,C=points[a],points[b],points[c]
				A,B,C=sorted([A,B,C],key=fkey1)
				SABC=abs((A-B)**(A-C))
				if(SABC==0):
					continue
				L=A.x
				R=C.x
				edgs=[(A,C),(A,B),(B,C)]
				
				ct=(A+B+C)/3
				ep=0.02
				PC=sum([pinfo[idx]*w for idx,w in calc_weights(a,b,c,ct)])
				P10=(sum([pinfo[idx]*w for idx,w in calc_weights(a,b,c,ct+point(ep,0))])-PC)/ep
				P01=(sum([pinfo[idx]*w for idx,w in calc_weights(a,b,c,ct+point(0,ep))])-PC)/ep
				P00=PC-P01*ct.y-P10*ct.x
				k_x1_x,k_y1_x=P10.xy
				k_x1_y,k_y1_y=P01.xy
				b_x1,b_y1=P00.xy
				
				for x in range(ceil(L),floor(R)+1):
					e1,e2=[_ for _ in edgs if(_[0].x!=_[1].x and _[0].x<= x and x<=_[1].x)][:2]
					
					y1=func(*e1,x)
					y2=func(*e2,x)
					UP=ceil(min(y1,y2))
					LO=floor(max(y1,y2))
					x1=x*k_x1_x+(UP-1)*k_x1_y+b_x1
					y1=x*k_y1_x+(UP-1)*k_y1_y+b_y1
					#print(x,UP,LO)
					for y in range(UP,LO+1):
						x1+=k_x1_y
						y1+=k_y1_y
						if(x1<0 or y1<0 or x1>w-1 or y1>h-1):
							continue
						p=getp(x1,y1)
						if(p[3]>5):
							ret[y-up,x-le]=getp(x1,y1)
						len_temp+=1
			_debug_info['time']+=time.time()
			_debug_info['len_temp']=len_temp
			ret=Image.fromarray(ret.astype(np.uint8)),le,up
		return ret
	render=render1
	@property
	def npoints(self):
		return len(self.mesh.points)
	@property
	def size(self):
		return self.w,self.h
	@property
	def points(self):
		return self.mesh.points
	@property
	def npoints(self):
		return self.mesh.npoints
	@property
	def point_info(self):
		return self.mesh.point_info
if(__name__=='__main__'):
	import timeit,time
	def foo(ss,mesh_cnt,rd=0):
		def ret():
			im=Image.open(r"M:\pic\yjsp.jpg")
			tmtm=time.time()
			md=mesh_deform(im,ss=ss,mesh_cnt=mesh_cnt)
			print(md.mesh.npoints,md.mesh.nedges,md.mesh.ntris)
			print('md time',time.time()-tmtm)
			tmtm=time.time()
			w,h=md.size
			rnd=random.random
			for i in range(md.npoints):
				temp=point((rnd()-rnd())*0.06*w,(rnd()-rnd())*0.06*h)
				md.mesh.points[i]+=temp
			if(rd==0):
				rett=md.render()
			else:
				rett=md.render1()
			print('rendertime',time.time()-tmtm)
			return rett
		return ret
	im=Image.open(r"M:\pic\yjsp.jpg")
	from timer import timer
	tmr=timer()
	md=mesh_deform(im,ss=20000,mesh_cnt=20)
	md.mesh.illust().show()
	tmr.settime()
	im=md.render()
	print('render0time',tmr.gettime())
	im.show()
	tmr.settime()
	im=md.render1()
	print('render1time',tmr.gettime())
	im.show()
	#foo(100000,20,1)().show()
	'''foo(30000,20)().show()
	'''
	