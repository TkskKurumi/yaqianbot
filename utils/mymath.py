import math
def tanh1(max,x1,y1):
	temp=math.atanh(y1/max)/x1
	#print("f(x)=%s*tanh(%s*x)"%(max,temp))
	return lambda x:max*math.tanh(temp*x)
def geometric_mean(l):
	s=1
	for i in l:
		s*=i
	s**=1/len(l)
	return s
def solute_quadratic_equation(a,b,c):
	delta=b*b-4*a*c
	x1=(-b+delta**0.5)/2/a
	x2=(-b-delta**0.5)/2/a
	return (x1,x2)
solve_quadratic_equation=solute_quadratic_equation
def asgn(a,eps=1e-10):
	if(a>eps):
		return 1
	elif(a<-eps):
		return -1
	else:
		return 0
def aequal(a,b,eps=1e-10):
	return asgn(a-b,eps)==asgn(b-a,eps)
def mean(l):
	return sum(l)/len(l)
def quadratic_mean(l):
	l_=[i**2 for i in l]
	temp=sum(l_)/len(l_)
	return temp**0.5

def harmonic_mean(l):
	t=mean([1/i for i in l])
	return 1/t
def calcEnt(l):		#entropy熵
	s=0
	sum_=sum(l)
	for i in l:
		if(i==0):
			continue
		i=i/sum_
		s=s-i*math.log(i)
	return s
def solve_pow(x1,y1,x2,y2):
	dishu=(y2/y1)**(1/(x2-x1))
	changshu=y1/(dishu**x1)
	return (lambda x:changshu*(dishu**x))
def func1(x_l,x_r,y_min,y_max,y_start):
	y_end=y_min+y_max-y_start
	dy=y_end-y_start
	dx=x_r-x_l
	k=dy/dx
	u=k/(y_start-y_min)
	ux_v=math.log(y_start-y_min)
	v=ux_v-u*x_l
	def ret(x):
		if(x_l<=x and x<=x_r):
			return y_start+k*(x-x_l)
		elif(x<x_l):
			return math.e**(u*x+v) + y_min
		else:
			return y_max+y_min-ret(x_l+x_r-x)
	return ret
	
def sanci(a,b,c,d):
  def fuc(x):
    return a*x*x*x+b*x*x+c*x+d
  return fuc
def build_sin(cx,cy,T,A):
  return lambda x:math.sin((x-cx)/T*math.pi*2)*A+cy
def variance(ls):
	myu=mean(ls)
	return sum([(i-myu)**2 for i in ls])/len(ls)
def s_curve(x):
	if(x<0.5):
		y=0.5-(0.25-x**2)**0.5
	else:
		y=0.5+(0.25-(x-1)**2)**0.5
	return y
def motion_curve(points,type='sin'):
	points.sort()
	lex,ley=points[0]
	rix,riy=points[-1]
	funcs=[]
  #_a=[]
  #_c=[]
	def ellipse_(x1,y1,x2,y2):
		def ret(x):
			y=y1+(y2-y1)*s_curve((x-x1)/(x2-x1))
			return y
		return ret
	if(type=='sanci'):
		for idx,i in enumerate(points[:-1]):
			x1,y1=i
			x2,y2=points[idx+1]
			a1=x1*x1*x1/3+x1*x2*x1-x1*x1*(x1+x2)/2
			a2=x2*x2*x2/3+x1*x2*x2-x2*x2*(x1+x2)/2
			a,c=solve_eryuanyici([(a1,1,y1),(a2,1,y2)])
			  #_a.append(a)
      #_c.append(c)
      #funcs.append(lambda x:_a[idx]*x*x*x/3+_a[idx]*(x1+x2)/2*x*x+_a[idx]*x1*x2*x+_c[idx])
			funcs.append(sanci(a/3,-a*(x1+x2)/2,a*x1*x2,c))
      #print(i,points[idx+1],(x1,funcs[-1](x1)),(x2,funcs[-1](x2)),dy_dx(funcs[-1],x1),dy_dx(funcs[-1],x2))
	elif(type=='sin'):
		for idx,i in enumerate(points[:-1]):
			x1,y1=i
			x2,y2=points[idx+1]
			cx=(x1+x2)/2
			cy=(y1+y2)/2
			A=(y2-y1)/2
			funcs.append(build_sin(cx,cy,(x2-x1)*2,A))
	elif(type=='ellipse'):
		for idx,i in enumerate(points[:-1]):
			x1,y1=i
			x2,y2=points[idx+1]
			funcs.append(ellipse_(x1,y1,x2,y2))
	
	def fuk_you(x):
		if(x<lex):
			return ley
		if(x>rix):
			return riy
		for idx in range(0,len(points)-1):
			if(points[idx][0]<=x and x<=points[idx+1][0]):
			#print('x,idx',x,idx)
				return funcs[idx](x)
		
	return fuk_you
def xy2theta_radius(x,y):
	theta=math.atan2(y,x)
	radius=(x*x+y*y)**0.5
	return theta,radius
def theta_radius2xy(theta,radius):
	return math.cos(theta)*radius,math.sin(theta)*radius
if(__name__=='__main__'):
	f=func1(-0.5,0.5,0,1,0.2)
	for x in range(-2,3):
		print(x,f(x))
	#print(calcEnt([1]*1151+[1145141919810893]))