import os,time,pic2pic,myGeometry,math,mymath
import make_gif,random_deform,mesh_deform,random
from PIL import Image
import numpy as np
from mytimer import timer
def horror_gif(img,resolution=45000,r_w0=0.017,r_w1=0.006):
	
	tmr=timer()
	point=myGeometry.point

	qd={}
	
	img=pic2pic.squareSize(img,resolution)
	w,h=img.size
	r_h0=0.007
	r_h1=0.002
	omega_y0=20
	omega_y1=50
	omega_x0=20
	omega_x1=50
	omega_t00=0.3
	omega_t01=0.8
	omega_t10=0.5
	omega_t11=1
	hengtiao_ul_min=0.02
	hengtiao_ul_max=0.3


	r_rgb=0.02*((w*h)**0.5)
	r_rgb1=0.1*((w*h)**0.5)
	npa=lambda a:np.array(a,np.float64)
	imgs=[]
	func1=lambda p:(int(p.x)%w,int(p.y)%h)
	frames=25
	hengtiao=random.sample(range(frames),int(frames/5))
	black=random.sample(range(frames),int(frames/10))
	reverse=random.sample(range(frames),int(frames/20))
	black_r=0.3
	ht_rr=0.8
	ht_rg=0.3
	ht_rb=0.3
	for t in range(frames):
		for x in range(w):
			for y in range(h):
				dx=math.sin(y/h*omega_y0+t*omega_t00)*w*r_w0+math.sin(y/h*omega_y1+t*omega_t01)*w*r_w1
				dy=math.sin(x/w*omega_x0+t*omega_t10)*h*r_h0+math.sin(x/w*omega_x1+t*omega_t11)*h*r_h1
				qd[(x,y)]=npa((x+dx,y+dx))
		img0=random_deform.random_deform(img,cnt=0,neibour_cnt=4,qd=qd,method=2)
		img1=Image.new("RGBA",img0.size)
		
		dr=point.rarg(random.random()*r_rgb,random.random()*math.pi*2)
		dg=point.rarg(random.random()*r_rgb,random.random()*math.pi*2)
		db=point.rarg(random.random()*r_rgb,random.random()*math.pi*2)
		tih=t in hengtiao
		tib=t in black
		tir=t in reverse
		if(tih):
			ul=(random.random()*(hengtiao_ul_max-hengtiao_ul_min)+hengtiao_ul_min)*h
			ul=int(ul)
			print(ul,h)
			up=random.randrange(0,h-ul)
			dr1=point.rarg(random.random()*r_rgb1,random.random()*math.pi*2)
			dg1=point.rarg(random.random()*r_rgb1,random.random()*math.pi*2)
			db1=point.rarg(random.random()*r_rgb1,random.random()*math.pi*2)
		
		p00=point(0,0)
		rr=rg=rb=1
		yih=False
		for y in range(h):
			if(tih and y==up):
				dr+=dr1
				dg+=dg1
				db+=db1
				_=[ht_rr,ht_rg,ht_rb]
				random.shuffle(_)
				rr,rg,rb=ht_rr,ht_rg,ht_rb
				yih=True
			for x in range(w):
				
				r=func1(dr+point(x,y))
				r=int(img0.getpixel(r)[0]*rr)
				g=func1(dg+point(x,y))
				g=int(img0.getpixel(g)[1]*rg)
				b=func1(db+point(x,y))
				b=int(img0.getpixel(b)[2]*rb)
				if(tir and not yih):
					img1.putpixel((x,y),(255-r,255-g,255-b))
				elif(tib):
					img1.putpixel((x,y),(int(r*black_r),int(g*black_r),int(b*black_r)))
				else:
					img1.putpixel((x,y),(r,g,b))
			if(tih and y==up+ul):
				dr-=dr1
				dg-=dg1
				db-=db1
				rr=rg=rb=1
				yih=False
		imgs.append(img1)
	print(tmr.gettime())
	gif=make_gif.make_gif(imgs,ss=resolution,fps=18)
	return gif
if(__name__=='__main__'):
	gif=horror_gif(Image.open(r"G:\pyxyv\tempimgcache\10345855_p0_master1200.jpg"),resolution=4000)
	print(gif)
	os.system('explorer %s'%gif)