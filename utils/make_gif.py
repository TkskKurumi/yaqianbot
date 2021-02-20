from os import path
import myhash,os,time
from glob import glob
from PIL import Image
pth=path.join(path.dirname(__file__),'make_gif')
def glob_exts(pth,exts):
	ret=[]
	for i in exts:
		ret+=list(glob(pth+'\\*.'+i))
	return ret
in_progress={}
def make_gif(imgs,size=None,ss=None,pth=pth,fps=12,quality=100,width=None,height=None):
	hashi=0
	if(size is None):
		if(width is not None):
			if(height is None):
				height=imgs[0].size[1]/imgs[0].size[0]*width
			size=width,height
		elif(height is not None):
			width=imgs[0].size[0]/imgs[0].size[1]*width
			size=width,height
		elif(ss is not None):
			w,h=imgs[0].size
			r=(ss/w/h)**0.5
			size=int(w*r),int(h*r)
	for idx,_ in enumerate(imgs):
		hashi^=myhash.phashi(_)*idx
		
	hashi^=size[0]^(size[1]<<9)^(fps<<18)
	name=myhash.hashs(hashi)
	seqpth=path.join(pth,'%s'%name)
	svpth=path.join(pth,'%s.gif'%name)
	if(path.exists(svpth) and not(in_progress.get(name,False))):
		print('line20')
		return svpth
	elif(path.exists(svpth)):
		while(in_progress.get(name,False)):
			time.sleep(1)
		return svpth
	in_progress[name]=True
	if(not(path.exists(seqpth))):
		os.makedirs(seqpth)
	
	for idx,_ in enumerate(imgs):
		_.resize(size).save(path.join(seqpth,'%04d.png'%idx),'PNG')
	
	if(' ' in seqpth):
		seqpths=glob_exts(seqpth,['png'])
		seqpths=' '.join(['"%s"'%i for i in seqpths])
	else:
		seqpths=seqpth+'\*.gif'
	
	script=f'gifski {seqpths} --fps {fps} --quality {quality} --width {size[0]} --height {size[1]} -o "{svpth}"'
	#print(script)
	os.popen(script).read()
	
	
	
	in_progress[name]=False
	return svpth	
if(__name__=='__main__'):
	
	imgs=[Image.open(i) for i in glob_exts(r'M:\pic\ahegao',['jpg'])[10:]]
	#print(imgs)
	print(make_gif(imgs,ss=10000))