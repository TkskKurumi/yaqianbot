import numpy as np
from mymath import *
import math

#计算几何

class point:
	def __init__(self,x=0,y=0):
		self.x=float(x)
		self.y=float(y)
	def __mul__(self,other):
		if(isinstance(other,point)):
			return self.x*other.x+self.y*other.y
		elif(isinstance(other,int) or isinstance(other,float)):
			return point(self.x*other,self.y*other)
	def comp(self):
		return self.x+self.y*1j
	def __neg__(self):
		return point(-self.x,-self.y)
	def __add__(self,other):
		return point(self.x+other.x,self.y+other.y)
	def __radd__(self,other):
		if(other==0):
			return self
		else:
			return NotImplemented
	def __sub__(self,other):
		return point(self.x-other.x,self.y-other.y)
	def __pow__(self,other):
		return self.x*other.y-self.y*other.x
	def __str__(self):
		return "(%.3f,%.3f)"%(self.x,self.y)
	def is_zero(self):
		return asgn(self.x)==0 and asgn(self.y)==0
	def distO(self):
		return (self.x*self.x+self.y*self.y)**0.5
	
	def dist_segment(self,A,B):
		AB=B-A
		AP=self-A
		
		if(AP.is_zero()):
			
			return 0
		AH=(AB*AP)/AB.distO()
		H=A+AB.unit()*AH
		AH=H-A
		HB=B-H
		if(AH*HB<0):
			return min(self.dist(A),self.dist(B))
		else:
			return self.dist(H)
	def on_segment(self,A,B):
		x=(A-self)**(B-self)
		if(asgn(x)!=0):
			return False
		x=(A-self)*(B-self)
		return asgn(x)<=0
	def in_triangle(self,A,B,C):
		
		if(self.on_segment(A,B) or self.on_segment(B,C) or self.on_segment(A,C)):
			return True
		
		PA=A-self
		PB=B-self
		PC=C-self
		
		xAB=PA**PB
		xBC=PB**PC
		xCA=PC**PA
		
		temp=sorted([asgn(xAB),asgn(xBC),asgn(xCA)])
		if(temp[0]==1 and temp[2]==1):
			return True
		elif(temp[0]==-1 and temp[2]==-1):
			return True
		else:
			return False
		
	def __truediv__(self,n):
		return point(self.x/n,self.y/n)
	def unit(self):
		return self/self.distO()
		
	def dist(self,other):
		if(isinstance(other,point)):
			return (self-other).distO()
	@property
	def xy(self):
		return self.x,self.y
	@property
	def arg(self):
		return math.atan2(self.y,self.x)
	@property
	def r(self):
		return self.distO()
	def __str__(self):
		return "point(%.4f,%.4f)"%self.xy
	def __repr__(self):
		return "point(%.4f,%.4f)"%self.xy
	def __equal__(self,other):
		return (self-other).is_zero
	def rarg(r,arg):
		return point(math.cos(arg)*r,math.sin(arg)*r)
class line:
	
	def __init__(self,A=0,B=0,C=0):
		self.A=A
		self.B=B
		self.C=C
	
	def from_points(A:point,B:point):
		return line(A.y-B.y,B.x-A.x,A**B)
	
	@property
	def AB(self):
		return self.A,self.B
	
	def intersection(self,other):
		a=np.array([list(self.AB),list(other.AB)],np.float64)
		b=np.array([-self.C,-other.C],np.float64)
		return np.linalg.solve(a,b)
class circle:
	def __init__(self,x=0,y=0,r=10):
		self.x=x
		self.y=y
		self.r=r
	@property
	def xyr(self):
		return self.x,self.y,self.r
	def point_on(self,p):
		d=p.dist(point(self.x,self.y))
		return aequal(d,self.r)
	def intersection(self,other):
		if(isinstance(other,circle)):
			#https://www.cnblogs.com/AOQNRMGYXLMV/p/5098304.html
			x1,y1,r1=self.xyr
			x2,y2,r2=other.xyr
			a=2*r1*(x1-x2)
			b=2*r1*(y1-y2)
			c=r2*r2-r1*r1-(x1-x2)*(x1-x2)-(y1-y2)*(y1-y2)
			A=a*a+b*b
			B=-2*a*c
			C=c*c-b*b
			cos1,cos2=solve_quadratic_equation(A,B,C)
			if(asgn(cos1.imag)!=0):
				return None
			def foo(_cos):
				_sin=(1-_cos*_cos)**0.5
				x=x1+r1*_cos
				y=y1+r1*_sin
				d=point(x,y).dist(point(x2,y2))
				if(aequal(d,r2)):
					return point(x,y)
				else:
					return point(x,y1-r1*_sin)
			return (foo(cos1),foo(cos2))
def arbquadmapping(p1,p2,p3,p4):
	if(isinstance(p1,list)):
		p1=point(*p1)
		p2=point(*p2)
		p3=point(*p3)
		p4=point(*p4)
	def ret(x,y):
		x=float(x)
		y=float(y)
		O1=p1*(1-x)+p2*x
		O2=p3*(1-x)+p4*x
		L1=line.from_points(O1,O2)
		
		O3=p1*(1-y)+p3*y
		O4=p2*(1-y)+p4*y
		L2=line.from_points(O3,O4)
		
		return L1.intersection(L2)
	return ret
def segment_intersection(A,B,C,D,strict=True):
	if(not strict):
		if(A.on_segment(C,D) or B.on_segment(C,D) or C.on_segment(A,B) or D.on_segment(A,B)):
			return True
	AC=C-A
	AD=D-A
	AB=B-A
	temp1=asgn(AC**AB)*asgn(AB**AD)
	
	CA=A-C
	CB=B-C
	CD=D-C
	temp2=asgn(CA**CD)*asgn(CD**CB)
	
	return temp1>0 and temp2>0
def normalize_arg(arg,rad=3.14159):
	arg=arg%(rad*2)
	return min([arg,arg-2*rad],key=lambda a:abs(a))
	
quad_map=arbquadmapping


def judge_P_in_Cirle_ABC(A,B,C,P):
	#tmp=lambda a:a if isinstance(a,tuple) else a.xy
	tmp=lambda a:a.xy
	x0,y0=tmp(A)
	x1,y1=tmp(B)
	x2,y2=tmp(C)
	xp,yp=tmp(P)
	denominator=[[x0,y0,2],[x1,y1,2],[x2,y2,2]]
	denominator=np.linalg.det(np.array(denominator,np.float64))
	tmp=lambda a,b:a*a+b*b
	l0=tmp(x0,y0)
	l1=tmp(x1,y1)
	l2=tmp(x2,y2)
	
	x=[[l0,y0,1],[l1,y1,1],[l2,y2,1]]
	x=np.linalg.det(np.array(x,np.float64))/denominator
	
	y=[[x0,l0,1],[x1,l1,1],[x2,l2,1]]
	y=np.linalg.det(np.array(y,np.float64))/denominator
	
	O=point(x,y)
	
	R=O.dist(A)
	
	OP=P.dist(O)
	
	enmiao=OP-R
	return asgn(enmiao)