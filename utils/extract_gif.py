import myhash,myio,re
from PIL import Image
from os import path
import os
from glob import glob
def_pth=path.dirname(__file__).replace('\lib\library.zip','')
def_pth=path.join(def_pth,'extracted_gif')
cache={}
def extract_gif(pth,workpth=def_pth,ffmpeg_pth='ffmpeg'):
	if(pth in cache):
		return [i.copy() for i in cache[pth]]
	f=open(pth,'rb')
	b=f.read()
	f.close()
	s=myhash.hashs(b)
	output_pth=path.join(workpth,s)
	ls=glob(path.join(output_pth,"*.png"))
	print(output_pth)
	if(ls):
		print("???")
		return [Image.open(i) for i in ls]
	elif(not(path.exists(output_pth))):
		os.makedirs(output_pth)
	
	script='"%s" -i "%s" "%s\%%04d.png" 2>"%s"'%(ffmpeg_pth,pth,output_pth,path.join(workpth,s+'.log'))
	print('script:',script)
	tmp=os.popen(script)
	print(tmp.read())
	tmp.close()
	ls=glob(path.join(output_pth,"*.png"))
	cache[pth]=[Image.open(i) for i in ls]
	return [i.copy() for i in cache[pth]]
def get_fps(pth,workpth=def_pth,ffmpeg_pth='ffmpeg'):
	f=open(pth,'rb')
	b=f.read()
	f.close()
	name=myhash.hashs(b)
	_=path.join(workpth,name+'.log')
	if(not path.exists(_)):
		
		extract_gif(pth,workpth=workpth,ffmpeg_pth=ffmpeg_pth)
	t=myio.opentext(_)
	#print(t)
	fps=re.findall(r"\d+ fps|\d+.\d+ fps",t)[0]
	return float(fps.replace(' fps',''))
	
if(__name__=='__main__'):
	print(get_fps(r"G:\setubot\Mea_Shot\（哈欠）果然无理？？（听不懂.gif"))