from pic2pic import *
import myhash
from lcg import lcg
from os import path
import json,myio,shutil
#from PIL import Image
pth=path.join(path.dirname(__file__),'netease')
lcg_e=lcg(workpth=path.join(pth,'cache'),expiretime=1<<60,proxies={})
lcg_l=lcg(workpth=path.join(pth,'cache'),expiretime=86400,proxies={})
lcg_s=lcg(workpth=path.join(pth,'cache'),expiretime=600,proxies={})
host="localhost:3000"

def search(keywords):
	url=f'http://{host}/search?keywords={keywords}'
	return json.loads(lcg_s.gettext(url))['result']['songs']
def song_detail(id):
	url=f'http://{host}/song/detail?ids={id}'
	#print(url)
	#return lcg_s.gettext(url)
	return json.loads(lcg_s.gettext(url))['songs'][0]
def illustrate_song_slim(id,width=720,extra_str=None):
	info=song_detail(id)
	
	height=width//9
	border=height//6
	gr=0.618
	
	def new_layer(w=width-border*2,h=height,bg=(0,0,0,0)):
		return Image.new("RGBA",(w,h),bg)
	
	album=info.get('al',None) or info.get('album',None)
	p_album=lcg_e.get_image(album['picUrl'])
	p_album=circle_mask_RGBA(p_album).resize((height,height),Image.LANCZOS)
	
	color=get_main_color(p_album)
	hue=RGB2HSV(*color)[0]
	color_s=HSV2RGB(RGB2HSV(*color)[0],35,100)
	color_t=HSV2RGB(hue,100,20)
	color_t1=HSV2RGB(hue,50,50)
	
	ret=new_layer(bg=color_s+(255,))
	layer1=new_layer(bg=(255,255,255,247))
	ret=Image.alpha_composite(ret,layer1)
	layer1=new_layer()
	layer1.paste(p_album.resize((height,height),Image.LANCZOS))
	ret=Image.alpha_composite(ret,layer1)
	bg=ret.getpixel((0,0))[:3]
	
	layer1=new_layer()
	txt_height=int((height-border)/(1+gr))
	p_songname=txt2im(info['name'],fixedHeight=txt_height,shadow_fill=color_s,shadow_delta=(2,2),fill=color_t)
	layer1.paste(p_songname,box=(height+border,0))
	
	txt_height1=int(txt_height*gr)
	arname=", ".join([i['name'] for i in info['ar']])
	aral=arname+' - '+album['name']
	p_aral=txt2im(aral,fixedHeight=txt_height1,shadow_fill=color_s,shadow_delta=(1,1),fill=color_t1)
	layer1.paste(p_aral,box=(height+border,txt_height+border))
	
	ret=Image.alpha_composite(ret,layer1)
	
	if(extra_str is not None):
		if(callable(extra_str)):
			extra_str=extra_str(id)
		layer1=new_layer()
		p_extra=txt2im(extra_str,fixedHeight=txt_height,shadow_fill=color_s,shadow_delta=(2,2),fill=(0,0,0,255),bg=bg+(80,))
		left=max(0,layer1.size[0]-p_extra.size[0])
		top=int((layer1.size[1]-p_extra.size[1])*gr)
		layer1.paste(p_extra,(left,top))
		ret=Image.alpha_composite(ret,layer1)
	
	layer=new_layer(w=width,h=height+border*2,bg=bg+(255,))
	layer.paste(ret,(border,border))
	return layer
def illustrate_ids(ids,width=720,extra_str=None):
	imgs=[]
	for id in ids:
		imgs.append(illustrate_song_slim(id,width=width,extra_str=extra_str))
	return picMatrix(imgs,column_num=1,border=0)
def get_mp3(id):
	#url="https://music.163.com/song/media/outer/url?id=%d.mp3"%id
	url="https://music.163.com/song/media/outer/url?id=%s.mp3"%id
	f=lcg_e.get_path(url)
	f1=path.splitext(f)[0]+".mp3"
	return shutil.copy(f,f1)
if(__name__=='__main__'):
	j=search('你的猫咪')
	ids=[i['id'] for i in j]
	id=j[0]['id']
	myio.dumpjson(path.join(pth,'temp.json'),j)
	j=song_detail(id)
	myio.dumpjson(path.join(pth,'temps.json'),j)
	illustrate_song_slim(id,extra_str='/kj nanaazhi').show()
	illustrate_ids(ids[:6]).show()
	print(get_mp3(id))