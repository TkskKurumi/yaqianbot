from myGeometry import point, segment_intersection, judge_P_in_Cirle_ABC
inCircle=judge_P_in_Cirle_ABC
segInter = segment_intersection
from mymath import asgn
import math,random
from math import ceil,floor
from PIL import Image,ImageDraw,ImageFont
def normalize_edge(u,v):
	return tuple(sorted([u,v]))
class graph:	#undirected unweighted graph
	def __init__(self,neibours=None,edges=None):
		self.neibours=neibours or dict()
		self.edges=edges or set()
	def add_edge(self,u,v):
		self.neibours[u]=self.neibours.get(u,set())
		self.neibours[u].add(v)
		self.neibours[v]=self.neibours.get(v,set())
		self.neibours[v].add(u)
		edg=normalize_edge(u,v)
		self.edges.add(edg)
	def remove_edge(self,u,v):
		if(v in self.neibours[u]):
			self.neibours[u].remove(v)
			self.neibours[v].remove(u)
			self.edges.remove(normalize_edge(u,v))
def edge2mesh2tris(edge2mesh):
	ret=set()
	for edge in edge2mesh:
		for w in edge2mesh[edge]:
			u,v=edge
			ret.add(tuple(sorted([u,v,w])))
	return ret
class mesh:
	def __init__(self,points,edges,neibours,point_info,edge2mesh,tris=None):
		self.points=points
		self.edges=list(edges)
		self.neibours=neibours
		self.point_info=point_info
		self.edge2mesh=edge2mesh
		if(tris is None):
			self.tris=edge2mesh2tris(edge2mesh)
		else:
			self.tris=tris
		pass
	@property
	def npoints(self):
		return len(self.points)
	@property
	def nedges(self):
		return len(self.edges)
	@property
	def ntris(self):
		return len(self.tris)
	def mesh_contain_xy(self,mesh,x,y):
		A,B,C=[self.points[i]for i in mesh]
		P=point(x,y)
		return P.in_triangle(A,B,C)
	def initiate_edg_indexing(self,step=10):
		
		for edx,e in enumerate(self.edges):
			
			U=self.points[U]
			V=self.points[V]
			for i in range(step+1):
				P=(U*i+V*(step-i))/step
				idx=edx*(step+1)+i
				
				
	def illust(self,bg=(255,255,255,255)):
		
		w=math.ceil(max([i.x for i in self.points]))
		h=math.ceil(max([i.y for i in self.points]))
		img=Image.new("RGBA",(w,h),bg)
		dr=ImageDraw.Draw(img)
		fnt=ImageFont.truetype('simhei.ttf')
		fills=[(255,0,0,255),(0,255,0,255),(0,0,255,255),(6,76,168,255),(6,168,111,255)]
		nfills=len(fills)
		for u,v in self.edges:
			pu=self.points[u].xy
			pv=self.points[v].xy
			dr.line(pu+pv,fills[(u*self.npoints+v)%nfills])
		for i in range(self.npoints):
			p=(self.points[i]-point(4,4)).xy
			dr.text(p,str(i),fill=fills[i%nfills])
			
		return img
	def get_mesh_by_xy(self,x,y,include_weights=False,more=True):
		p=point(x,y)

		for tri in self.tris:
			if(self.mesh_contain_xy(tri,x,y)):
				if(include_weights):
					a,b,c=tri
					A=self.points[a]
					B=self.points[b]
					C=self.points[c]
					SABC=abs((A-B)**(C-B))
					
					P=p
					SPAB=abs((B-P)**(A-P))/SABC
					SPBC=abs((B-P)**(C-P))/SABC
					SPAC=abs((A-P)**(C-P))/SABC
					return [(a,SPBC),(b,SPAC),(c,SPAB)]
				
					
				return tri
		
	
		return None
	def generate_mesh_by_points(points,debug=False):
		points=[point(x,y) for x,y in set([i.xy for i in points])]
		if(debug):
			for idx,i in enumerate(points):
				print(idx,i)
		if(debug):
			from PIL import Image,ImageDraw,ImageFont
			import pic2pic
			im=Image.new("RGB",(333,333),(255,255,255))
			dr=ImageDraw.Draw(im)
			fnt=ImageFont.truetype('simhei.ttf')
			def drln(u,v,c=(0,0,0)):
				pu=points[u].xy
				pv=points[v].xy
				dr.line(pu+pv,c)
			def lable(u,text,c=(0,0,0)):
				dr.text(points[u].xy,text,fill=c)
		n=len(points)
		neibours=[set() for i in range(n)]
		center=sum(points)/n
		points.sort(key=lambda p:p.dist(center))
		v=[0,1]
		A=points[0]
		B=points[1]
		
		AB=B-A
		midx=None
		ms=None
		mc=None
		for i in range(2,n):
			C=points[i]
			AC=C-A
			s=abs(AC**AB)
			if(debug):
				print(i,s)
			if(asgn(s)==0):
				continue
			if((midx is None)or(s<ms)):
				midx=i
				ms=s
				mc=C
		
		points[midx]=points[2]
		points[2]=mc
		if(debug):print(points[midx],points[2],midx)
		center=sum(points[:3])/3
		points=points[:3]+sorted(points[3:],key=lambda p:p.dist(center))
		if(debug):
			for idx,i in enumerate(points):
				lable(idx,'%d(%d,%d)'%(idx,*i.xy),(255,0,0))
				print(idx,i)
		to_add=set(range(3,n))
		conv=[0,1,2]
		
		edges=set([(0,1),(1,2),(0,2)])
		edge2mesh={(0,1):{2},(1,2):{3},(0,2):{1}}
		euv=lambda u,v:tuple(sorted([u,v]))
		
		def sort_conv():
			conv.sort(key=lambda idx:(points[idx].y<center.y , (points[idx]-center).unit().x * (1 if points[idx].y>center.y else -1)))
		def add_tri(u,v,w):
			edgw=euv(u,v)
			edgu=euv(w,v)
			edgv=euv(w,u)
			edges.add(edgu)
			edges.add(edgv)
			edges.add(edgw)
			
			edge2mesh[edgw]=edge2mesh.get(edgw,set())
			edge2mesh[edgw].add(w)
			
			edge2mesh[edgu]=edge2mesh.get(edgu,set())
			edge2mesh[edgu].add(u)
			
			edge2mesh[edgv]=edge2mesh.get(edgv,set())
			edge2mesh[edgv].add(v)
			
			if(debug):
				drln(u,v)
				drln(w,v)
				drln(w,u)
				im.show()
		add_tri(0,1,2)
		for i in range(3,n):
			sort_conv()
			nconv=len(conv)
			min_convdx=None
			min_s=None
			min_p=None
			for udx,u in enumerate(conv):
				v=conv[udx-1]
				
				U=points[u]
				V=points[v]
				for p in to_add:
					P=points[p]
					#print('ln98',u,v)
					#print('ln99',U,V)
					s=P.dist_segment(U,V)
					if(asgn((U-P)**(V-P))==0):
						continue
					if(not(segment_intersection(U,V,P,center))):
						continue
					if(min_s is None or s<min_s):
						min_s=s
						min_convdx=udx
						min_p=p
			if(min_convdx is None):
				break
			udx=min_convdx
			vdx=(min_convdx-1)%nconv
			
			sconv=set(conv)
			
			p=min_p
			to_add.remove(p)
			if(debug):
				drln(p,conv[udx],(255,0,0))
				drln(p,conv[vdx],(255,0,0))
				#lable(p,'P(%s)'%(points[p].xy,),(255,0,0))
				for idx,i in enumerate(conv):
					pos=points[i].xy
					drln(i,conv[idx-1],(123,163,211))
					#dr.text(pos,'conv'+str(i),font=fnt,fill=(0,0,0))
				pic2pic.addTitle(im,'p=%d'%p).show()
			add_tri(p,conv[udx],conv[vdx])
			
			P=points[p]
			U=points[conv[udx]]
			V=points[conv[vdx]]
			sgnUV=asgn((U-P)**(V-P))
			sgnVU=-asgn((U-P)**(V-P))
			
			idx=(udx+1)%nconv
			while(idx!=vdx):
				jdx=(idx-1)%nconv
				I=points[conv[idx]]
				J=points[conv[jdx]]
				sgnJI=asgn((J-P)**(I-P))
				if(sgnJI!=sgnVU):
					break
				sconv.remove(conv[jdx])
				add_tri(conv[idx],conv[jdx],p)
				idx=(idx+1)%nconv
			idx=(vdx-1)%nconv
			while(idx!=udx):
				jdx=(idx+1)%nconv
				
				I=points[conv[idx]]
				J=points[conv[jdx]]
				sgnIJ=asgn((I-P)**(J-P))
				if(sgnIJ!=sgnVU):
					break
				
				if(debug):
					drln(p,conv[idx],(0,0,255))
					drln(p,conv[jdx],(0,255,0))
					pic2pic.addTitle(im,'p%s u%s v%s i%s j%s pu%s pv%s pi %s pj%s'%(P.xy,U.xy,V.xy,I.xy,J.xy,(U-P).xy , (V-P).xy,(I-P).xy,(J-P).xy)).show()
				sconv.remove(conv[jdx])
				add_tri(conv[idx],conv[jdx],p)
				idx=(idx-1)%nconv
			conv=list(sconv)+[p]
		#print(edge2mesh)
		for u,v in edges:
			neibours[u].add(v)
			neibours[v].add(u)
		return mesh(points,edges,neibours,{},edge2mesh)
	def delaunay(points,debug=False,prog_cb=None):
		points=sorted(points,key=lambda x:x.xy)
		G=graph()
		def illust():
			edge2mesh={}
			for u,v in G.edges:
				e=normalize_edge(u,v)
				for w in G.neibours[u]:
					if(w==u or w==u):
						continue
					if(normalize_edge(w,v) in G.edges):
						edge2mesh[e]=edge2mesh.get(e,set())
						edge2mesh[e].add(w)
			mesh(points,G.edges,G.neibours,dict(),edge2mesh).illust().show()
		mx_prog=0
		now_prog=0
		def calc_mx_prog(l,r):
			nonlocal mx_prog
			mx_prog+=r-l+1
			if(r-l<=2):
				return
			mid=(l+r)>>1
			calc_mx_prog(l,mid)
			calc_mx_prog(mid+1,r)
			return
		if(prog_cb):
			calc_mx_prog(0,len(points)-1)
		def div(l,r):
			nonlocal points,G,now_prog,mx_prog
			#print(l,r)
			if(r-l<=2):
				for i in range(l,r+1):
					for j in range(i+1,r+1):
						#print("ln367",points[i],points[j])
						G.add_edge(i,j)
				if(prog_cb):
					now_prog+=r-l+1
					prog_cb(now_prog/mx_prog)
				return
			
			mid=(l+r)>>1
			div(l,mid)
			div(mid+1,r)
			nowl=l
			nowr=r
			flag=True
			while(flag):
				flag=False
				pL=points[nowl]
				pR=points[nowr]
				for t in G.neibours[nowl]:
					pT=points[t]
					tmp=(pL-pR)**(pT-pR)
					tmp=asgn(tmp)
					if(tmp>0 or (tmp==0 and pR.dist(pT)<pR.dist(pL))):
						nowl=t
						flag=True
						break
				if(flag):continue
				for t in G.neibours[nowr]:
					pT=points[t]
					tmp=(pR-pL)**(pT-pL)
					tmp=asgn(tmp)
					if(tmp<0 or (tmp==0 and pL.dist(pT)<pL.dist(pR))):
						nowr=t
						flag=True
						break
			if(debug):print('ln399 add',points[nowl],points[nowr])
			G.add_edge(nowl,nowr)
			flag=True
			
			while(True):
				flag=False
				pL=points[nowl]
				pR=points[nowr]
				ch=None
				side=0
				for t in G.neibours[nowl]:
					pT=points[t]
					sgn=asgn((pR-pL)**(pT-pL))
					if(sgn>0 and ((ch is None)or inCircle(pL,pR,points[ch],pT)<0)):
						ch=t
						side=-1
				for t in G.neibours[nowr]:
					pT=points[t]
					sgn=asgn((pT-pR)**(pL-pR))
					if(sgn>0 and ((ch is None)or inCircle(pL,pR,points[ch],pT)<0)):
						
						'''if(nowl==1 and t==8):
							print("              ln431")
						if(ch is not None):
							for tt in G.neibours[nowl]:
								if(tt==nowl or tt==nowr or tt==t):continue
								if(inCircle(pL,pR,points[t],points[tt])<0):
									if(nowl==1 and t==8):
										print("              ln437",pL,pR,points[t],points[tt])
									f=False
						if(nowl==1 and t==8):
							print("              ln437",f)'''
						
						ch=t
						side=1
				if(ch is None):break
				pCH=points[ch]
				
				if(side==-1):
					to_remove=[]
					for t in G.neibours[nowl]:
						pT=points[t]
						if(t==nowl or t==nowr):continue
						if(segInter(pL,pT,pR,pCH)):
							to_remove.append(t)
					for t in to_remove:
						if(debug):print('ln428 rm',points[nowl],points[t])
						G.remove_edge(nowl,t)
					if(debug):illust()
					nowl=ch
					if(debug):print('ln430 add',points[nowl],points[nowr])
					if(debug):illust()
					G.add_edge(nowl,nowr)
				else:
					to_remove=[]
					for t in G.neibours[nowr]:
						pT=points[t]
						if(t==nowl or t==nowr):continue
						if(segInter(pR,pT,pL,pCH)):
							to_remove.append(t)
					for t in to_remove:
						if(debug):print('ln440 rm',points[nowr],points[t])
						G.remove_edge(nowr,t)
					if(debug):illust()
					nowr=ch
					if(debug):print('ln444 add',points[nowl],points[nowr])
					if(debug):illust()
					G.add_edge(nowl,nowr)
			if(prog_cb):
				now_prog+=r-l+1
				prog_cb(now_prog/mx_prog)
		div(0,len(points)-1)
		edge2mesh={}
		for u,v in G.edges:
			e=normalize_edge(u,v)
			for w in G.neibours[u]:
				if(w==u or w==u):
					continue
				if(normalize_edge(w,v) in G.edges):
					edge2mesh[e]=edge2mesh.get(e,set())
					edge2mesh[e].add(w)
		return mesh(points,G.edges,G.neibours,dict(),edge2mesh)
	def generate_mesh_by_points1(points):
		to_add=[]
		
		edgs=set()
		n=len(points)
		neibours=[set() for i in range(n)]

		for i in range(n):
			for j in range(i+1,n):
				to_add.append((i,j))
		to_add.sort(key=lambda e:points[e[1]].dist(points[e[0]]))
		for i in to_add:
			u,v=i
			flag=True
			for e in edgs:
				u1,v1=e
				if((u1 in i)or(v1 in i)):
					if(u1 in i):
						uu=u1
						uv=v1
					else:
						uu=v1
						uv=u1
					if(points[uv].on_segment(points[u],points[v])):
						flag=False
						break
				else:
					if(segment_intersection(points[u],points[v],points[u1],points[v1])):
						flag=False
						break
			if(flag):
				edgs.add(i)
				neibours[u].add(v)
				neibours[v].add(u)
		edge2mesh={}
		for i in edgs:
			u,v=i
			U=points[u]
			V=points[v]
			min_a=None
			min_as=None
			min_b=None
			min_bs=None
			com=neibours[u].intersection(neibours[v])
			for w in com:
				W=points[w]
				SUVW=(W-U)**(W-V)
				if(SUVW>0):
					if(min_a is None or SUVW<min_as):
						min_a=w
						min_as=SUVW
				else:
					if(min_b is None or SUVW>min_bs):
						min_b=w
						min_bs=SUVW
			edge2mesh[i]=[i for i in [min_a,min_b] if i is not None]
		return mesh(points,edgs,neibours,{},edge2mesh)
	def get_tri_integral_point(self):
		ret={}
		fkey1=lambda p:p.x
		func=lambda A,B,x:((B.x-x)*A.y+(x-A.x)*B.y)/(B.x-A.x)
		for a,b,c in self.tris:
			ret_=[]
			A,B,C=self.points[a],self.points[b],self.points[c]
			A,B,C=sorted([A,B,C],key=fkey1)
			SABC=abs((A-B)**(A-C))
			L=A.x
			R=C.x
			edgs=[(A,C),(A,B),(B,C)]
			for x in range(ceil(L),floor(R)+1):
				e1,e2=[_ for _ in edgs if(_[0].x!=_[1].x and _[0].x<= x and x<=_[1].x)][:2]
					
				y1=func(*e1,x)
				y2=func(*e2,x)
				UP=ceil(min(y1,y2))
				LO=floor(max(y1,y2))
				ret_+=[(x,y) for y in range(UP,LO+1)]
			ret[(a,b,c)]=ret_
		return ret
if(__name__=='__main__'):
	ls=[]
	ls.append(point(0,0))
	ls.append(point(100,0))
	ls.append(point(0,100))
	ls.append(point(100,100))
	
	m=mesh.delaunay(ls)
	m.illust().show()
	print(m.neibours)