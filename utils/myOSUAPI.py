import requests,myio,json,time,getheader
from myhash import splitedDict,hashs
#from workpathmanager import pathManager
from os import path
from lcg import lcg as lcg
import copy,random,math
from PIL import Image,ImageDraw
from urllib.parse import urlencode
import pic2pic
import numpy as np
from glob import glob
#wpm=pathManager(appname='osuapi')
#pth=wpm.getpath(session='mainpth',ask_when_dne=True)
pth=path.dirname(__file__)
pth=path.join(pth,'osu')
fnt=list(glob(path.join(pth,'*.ttf')))+list(glob(path.join(pth,'*.otf')))
if(fnt):
	fnt=fnt[0]
else:
	fnt=pic2pic.default_font
if(not path.exists(fnt)):
	fnt='simhei.ttf'

token_cache={}
if(path.exists(path.join(pth,'token_cache.json'))):
	token_cache=myio.loadjson(path.join(pth,'token_cache.json'))
def get_token():
	tm=time.time()
	if(token_cache.get('expire_time',0)<tm):
		data={'scope':'public','grant_type':'client_credentials'}
		client_info=myio.loadjson(path.join(pth,'client_info.json'))
		data.update(client_info)
		r=requests.post(r'https://osu.ppy.sh/oauth/token',data=data)
		try:
			j=r.json()
			token=j['access_token']
			exptime=tm+j['expires_in']
			token_cache['expire_time']=exptime
			token_cache['token']=token
			myio.dumpjson(path.join(pth,'token_cache.json'),token_cache)
		except Exception as e:
			print(e)
		
	return token_cache['token']

headera=copy.copy(getheader.headers)
#headera['Authorization']='Bearer '+get_token()
lcg_l=lcg(workpth=path.join(pth,'cache_long'),expiretime=86400,proxies={})
lcg_s=lcg(workpth=path.join(pth,'cache_short'),expiretime=15,proxies={})
base_url='https://osu.ppy.sh/api/v2/'
def get_user(user,mode=None,getter=lcg_s):
	headera['Authorization']='Bearer '+get_token()
	if(mode is None):
		r=getter.gettext(base_url+'/'.join(['users',user]),headers=headera)
	else:
		r=getter.gettext(base_url+'/'.join(['users',user,mode]),headers=headera)
	j=json.loads(r)
	#myio.dumpjson(path.join(pth,'temp_user.json'),j)
	return j
def triangle_bg(width,height,bg,fills=None,density=None,triangle_size=None,func_get_fill=None):
	if(fills is None):
		fills=[bg]
	ret=Image.new("RGBA",(width,height),bg)
	#lsrot=[0,60,120,180,240,300]
	if(density is None):
		density=300/width/height
	if(triangle_size is None):
		triangle_size=(width*height)**0.5
		triangle_size=triangle_size/density*0.003
		triangle_size**=0.5
	for i in range(int(width*height*density)):
		x,y=random.random()*width,random.random()*height
		r=(random.random()+0.2)*triangle_size
		#rot=random.choice(lsrot)
		rot=0
		if(func_get_fill is None):
			gamma=(random.random()-random.random())*2
			gamma=math.e**gamma
			c=random.choice(fills)[:3]
			c=[int(((_/255)**gamma)*255) for _ in c]
			c=tuple(c)+(170,)
		else:
			c=func_get_fill(int(x),int(y))
		layer1=Image.new("RGBA",(width,height),(0,0,0,0))
		dr=ImageDraw.Draw(layer1)
		dr.regular_polygon((x,y,r),3,rotation=rot,fill=c)
		#layer1.show()
		ret=Image.alpha_composite(ret,layer1)
	return ret
user_id_cache=splitedDict(pth=path.join(pth,'name2idcache'),splitMethod=lambda x:hashs(x)[:2])
def get_user_id(user):
	if(isinstance(user,int)):
		return user
	if(user.isnumeric()):
		return int(user)
	if(user in user_id_cache):
		return user_id_cache[user]
	uinfo=get_user(user)
	user_id_cache[user]=uinfo['id']
	return uinfo['id']
def get_user_score(user,type='best',params=None,mode=None):
	if(params is None):
		params={}
	if(mode):
		params['mode']=mode
	url=base_url+'/'.join(['users',str(get_user_id(user)),'scores',type])
	if(params):
		url+='?'+urlencode(params)
	headera['Authorization']='Bearer '+get_token()
	j=lcg_s.gettext(url,headers=headera)
	j=json.loads(j)
	#myio.dumpjson(path.join(pth,'temp_user_score.json'),j)
	#myio.dumpjson(path.join(pth,'temp_user_score_element.json'),j[0])
	return j
def illust_user_info(uinfo,bg=None,scores=None,score_subtitles=None,score_mode=None):
	#uinfo=
	if(isinstance(uinfo,str)):
		uinfo=get_user(uinfo)
	avatar_url=uinfo['avatar_url']
	username=uinfo['username']
	avatar=lcg_l.get_image(avatar_url)
	#avatar.show()
	width,height=1200,550
	border=int(((width*height)**0.5)*0.03)
	iwid,ihei=width-border*2,height-border*2
	grate=0.618
	if(bg is None):
		bg=pic2pic.imBanner(avatar,(width,height)).convert("RGB")
		def func(x,y):
			x_=x+y
			y_=y+width-x
			x_=(x*998244353)%width
			y_=(y*10000007)%height
			x_=(x_+x)>>1
			y_=(y_+y)>>1
			return bg.getpixel((x_,y_))+(128,)
		mc=pic2pic.get_main_color(bg)
		bg=triangle_bg(width,height,mc,func_get_fill=func)
	bg_arr=pic2pic.pil2cv2(bg)
	bg_dark=pic2pic.cv22pil((bg_arr/2.5).astype(np.uint8))
	bg_bright=pic2pic.cv22pil(((bg_arr.astype(np.int32)+384)/2.5).astype(np.uint8))
	ret=bg_bright
	ret.paste(bg_dark.resize((iwid,ihei)),(border,border))
	ret=ret.convert("RGBA")
	
	def new_layer():
		return Image.new("RGBA",(width,height),(0,)*4)
	
	layer1=new_layer()	#paste avatar
	avt_size=int((ihei-border*3)*0.768)
	avt_circle=avatar.resize((avt_size,avt_size))
	avt_circle=pic2pic.circle_mask_RGBA(avt_circle)
	avt_top=ihei-avt_size-border
	layer1.paste(avt_circle,(border*2,avt_top+border))
	ret=Image.alpha_composite(ret,layer1)
	
	layer1=new_layer()	#paste username
	username_height=ihei-border*3.8-avt_size
	pusername=pic2pic.txt2im(username,fill=(255,255,255),bg=(0,)*4,fixedHeight=username_height,font=fnt)
	layer1.paste(pusername,(border*2,border*2))
	ret=Image.alpha_composite(ret,layer1)
	
	layer1=new_layer()	#paste rank
	rank_height=username_height*(grate**0.5)
	pp,rank=uinfo['statistics']['pp'],uinfo['statistics']['global_rank']
	rank_text="%.1fpp / #%d"%(pp,rank)
	prank=pic2pic.txt2im(rank_text,fill=(255,)*4,bg=(0,)*4,fixedHeight=rank_height,font=fnt)
	layer1.paste(prank,(width-prank.size[0]-border*2,border*2))
	
	crank_height=rank_height*grate	#paste country rank
	crank=uinfo['statistics']['rank']['country']
	country_code=uinfo['country_code']
	crank_text='%s#%d (%s)'%(country_code,crank,uinfo['rank_history']['mode'])
	pcrank=pic2pic.txt2im(crank_text,fill=(255,)*4,bg=(0,)*4,fixedHeight=crank_height,font=fnt)
	pcrank_left=width-pcrank.size[0]-border*2
	pcrank_top=int(border*2.618+prank.size[1])
	layer1.paste(pcrank,(pcrank_left,pcrank_top))
	
	pflag=lcg_l.get_image(r'https://osu.ppy.sh/images/flags/%s.png'%country_code)
	pflag=pic2pic.fixHeight(pflag,crank_height/(grate**0.5))
	pflag_left=pcrank_left-border-pflag.size[0]
	layer1.paste(pflag,(pflag_left,pcrank_top))
	ret=Image.alpha_composite(ret,layer1)

	layer1=new_layer()	#scores
	if(scores is None):
		score1=get_user_score(uinfo['id'],type='recent',mode=score_mode)
		score2=get_user_score(uinfo['id'],type='best',mode=score_mode)
		scores=score1[:2]
		score_subtitles=[]
		for idx in range(len(scores)):
			score_subtitles.append('Recent %d'%(idx+1))
		scores=scores+score2[:5-len(scores)]
		idx=1
		while(len(score_subtitles)<len(scores)):
			score_subtitles.append('BP#%d'%idx)
			idx+=1
	bb=int(border*0.4)
	bx=int(border*1.3)
	
	left=avt_circle.size[0]+border*2+bx
	top=pcrank_top+pflag.size[1]+bb
	wid=width-left-border-bx
	hei=height-top-border-bb
	bb=border//5
	single_hei=int((hei-bb*(len(scores)-1))/len(scores))
	for idx,i in enumerate(scores):
		if(score_subtitles):
			_subtitle=score_subtitles[idx]
		else:
			_subtitle=''
		im=illust_score(i,wid,single_hei,subtitle=_subtitle)
		layer1.paste(im,(left,top))
		top+=single_hei+bb
	ret=Image.alpha_composite(ret,layer1)

	return ret
def get_score_rank_badge(rank,width=150,height=100):
	if(rank=='B'):
		c=(220,165,20,255)
		cfnt=(0,0,0)
	if(rank=='A'):
		c=(100,200,0,255)
		cfnt=(0,0,0)
	elif(rank=='S'):
		c=(0,150,170,255)
		cfnt=(255,214,102)
	elif(rank=='SS'):
		c=(0,150,170,255)
		cfnt=(255,214,102)
	else:
		c=(0,150,170,255)
		cfnt=(210,240,255)
	ret=triangle_bg(width,height,c,density=0.002,triangle_size=35)
	dr=ImageDraw.Draw(ret)
	dr.regular_polygon((0,0,height/2),3,fill=(0,)*4,rotation=180)
	dr.regular_polygon((width,0,height/2),3,fill=(0,)*4,rotation=180)
	dr.regular_polygon((0,height,height/2),3,fill=(0,)*4,rotation=0)
	dr.regular_polygon((width,height,height/2),3,fill=(0,)*4,rotation=0)
	
	ret1=pic2pic.txt2im(rank,fill=cfnt,bg=(0,)*4,fixedHeight=height,shadow_fill=(0,0,0,255),shadow_delta=(3,3),font=fnt)
	ret.paste(ret1,((width-ret1.size[0])//2,int((height*0.7-ret1.size[1])/2)),mask=ret1)
	return ret
def illust_score(info,width=720,height=None,brightness='dark',subtitle=''):
	if(height is None):
		height=width//10
	#bg=triangle_bg()
	border=height//11
	ihei=height-border*2
	
	bg=info['beatmapset']['covers']['slimcover']
	bg=lcg_l.get_image(bg)
	bg=pic2pic.imBanner(bg,(width,height))
	if(brightness == 'dark'):
		bg=pic2pic.pil2cv2(bg)/2.5
		bg=pic2pic.cv22pil(bg.astype(np.uint8))
		txtfill=(255,)*4
	else:
		bg=pic2pic.pil2cv2(bg).astype(np.int32)+384
		bg=pic2pic.cv22pil((bg/2.5).astype(np.uint8))
		txtfill=(0,0,0,255)
	ret=bg.convert("RGBA")
	dr=ImageDraw.Draw(ret)
	dr.regular_polygon((0,0,height/2),3,fill=(0,)*4,rotation=180)
	dr.regular_polygon((width,0,height/2),3,fill=(0,)*4,rotation=180)
	dr.regular_polygon((0,height,height/2),3,fill=(0,)*4,rotation=0)
	dr.regular_polygon((width,height,height/2),3,fill=(0,)*4,rotation=0)
	lleft=height//4
	#border=height//8
	grate=0.78
	def new_layer():
		return Image.new("RGBA",(width,height),(0,)*4)
	layer1=new_layer()
	
	badge=get_score_rank_badge(info['rank'],int(ihei*1.5),ihei)
	#badge=pic2pic.fixHeight(badge)
	layer1.paste(badge,(lleft,border))
	lleft+=badge.width+border
	#im=pic2pic.txt2im()
	ln1height=int((ihei-border)/(1+grate))
	ln2height=int(ln1height*grate)
	txt=info['beatmapset']['title_unicode']
	pic=pic2pic.txt2im(txt,fill=txtfill,bg=(0,)*4,fixedHeight=ln1height)
	layer1.paste(pic,(lleft,border))
	txt=info['beatmap']['version']
	if(info['mods']):
		txt+='  (+'+','.join(info['mods'])+')'
	pic=pic2pic.txt2im(txt,fill=txtfill,bg=(0,)*4,fixedHeight=ln2height,font=fnt)
	layer1.paste(pic,(lleft,2*border+ln1height))
	if(info['pp']):
		if(info.get('weight',None)):
			txt+=' (%.1fpp)'%info['weight']['pp']
		txt='%s %.1fpp'%(subtitle,info['pp'])
		pic=pic2pic.txt2im(txt,fill=txtfill,bg=(0,)*4,fixedHeight=ln1height,font=fnt)
	else:
		txt='%s unranked'%subtitle
		pic=pic2pic.txt2im(txt,fill=txtfill,bg=(0,)*4,fixedHeight=ln1height,font=fnt)
	ri=width-height//3
	layer1.paste(pic,(ri-pic.size[0],border))
	txt='%s  %.1f%%'%(info['score'],info['accuracy']*100)
	pic=pic2pic.txt2im(txt,fill=txtfill,bg=(0,)*4,fixedHeight=ln2height,font=fnt)
	layer1.paste(pic,(ri-pic.size[0],2*border+ln1height))

	ret=Image.alpha_composite(ret,layer1)

	return ret
if(__name__=='__main__'):
	'''j=get_user('TkskKurumi')
	print(j['statistics']['pp'],j['statistics']['pp_rank'])
	j=get_user('TkskKurumi',mode='osu')
	print(j['statistics']['pp'],j['statistics']['pp_rank'])
	triangle_bg(300,100,(255,100,160,255)).show()'''
	'''scores=get_user_score('TkskKurumi','best')
	illust_score(scores[0]).show()
	#illust_score(scores[1]).show()
	exit()'''
	
	uinfo=get_user('TkskKurumi',mode='osu')
	myio.dumpjson(r'D:\temp.json',uinfo)
	illust_user_info(uinfo,score_mode='osu').show()
	