#import mylogger			#因为logging设格式很烦就自己写了个
#logger=mylogger.logger()
#logger.openfh('bilibilimea')
import lcg,myio,re,json,time,myhash,myjobs,traceback,math,random#,random_tri_pic
#from workpathmanager import pathManager as pm	#workpathmanager是方便换电脑时候记录工作路径的模块
from urllib.parse import urlencode,quote
#from none_converters import bin2img,img2filename#none_converters是针对none-bot的各种杂项
from math import ceil
import pic2pic,myRenderer,myqr,requests
import mytimer as timer
from PIL import Image
from os import path
#logger.openfh(name='bilibilimea')
#mainpth=pm().getpath(appname='bilibili_cache',session='mainpth')
mainpth=path.join(path.dirname(__file__),'bilibili')
cachepth=path.join(mainpth,'cache')
print('bilibili cache pth',mainpth)

debugging=__name__=='__main__'
lcg_s=lcg.localCachingGeter(expiretime=10,proxies={},connection_throttle=(10,1),workpth=cachepth)		#lcg是带缓存的主要调用requests.get的模块
lcg_l=lcg.localCachingGeter(expiretime=172800,connection_throttle=(5,1),proxies={},workpth=cachepth)
lcg_m=lcg.localCachingGeter(expiretime=60,connection_throttle=(5,1),proxies={},workpth=cachepth)
lcg_ml=lcg.localCachingGeter(expiretime=3600*2,connection_throttle=(5,1),proxies={},workpth=cachepth)

throttles=[]
throttles.append(timer.throttle(2,5))




def get_gift_pic_by_name(gift_name,roomid=14917277):
	url='https://api.live.bilibili.com/gift/v4/Live/giftConfig?platform=pc&roomid=%s'%roomid
	j=lcg_ml.gettext(url)
	j=json.loads(j)['data']['list']
	'''myio.dumpjson(r'C:\temp\temp.json',j)
	__import__('os').system(r'explorer C:\temp\temp.json')'''
	for i in j:
		if(i['name']==gift_name):
			return lcg_l.get_image(i['img_basic'])
def get_gift_gif_url_by_name(gift_name,roomid=14917277):
	url='https://api.live.bilibili.com/gift/v4/Live/giftConfig?platform=pc&roomid=%s'%roomid
	j=lcg_ml.gettext(url)
	j=json.loads(j)['data']['list']
	'''myio.dumpjson(r'C:\temp\temp.json',j)
	__import__('os').system(r'explorer C:\temp\temp.json')'''
	for i in j:
		if(i['name']==gift_name):
			if('gif' in i):
				return i['gif']
			else:
				return None
dbg=True
def picurl2webp(url,quality='@320w_200h.webp'):	#B站缩略图地址
	if((url[-4:]!='webp')and(quality)):
		url_=url+quality
	else:
		url_=url
	return url_

def getSearch(keyword='神楽めあ',page=1,params={'order':'pubdate'}):
	re_del_em=re.compile(r'</?em.*?>')
	url='http://search.bilibili.com/all?'
	params['keyword']=keyword
	params['page']=page
	url=url+urlencode(params)
	#logger.info('search'+url)
	h=lcg_s.gettext(url,proxies={})
	sdata=re.findall(r'({"allData":[\s\S]+?});',h)
	if(not(sdata)):
		logger.error("search_no_result"+str(url))
		return []
	sdata=json.loads(sdata[0])['allData']['video']
	ret=[]
	for video_data in sdata:
		video_data['title_kwdem']=video_data['title']
		video_data['title']=re_del_em.sub('',video_data['title'])
		video_data['publish_date_str']=time.strftime('%Y-%m-%d %H:%M',time.localtime(int(video_data['pubdate'])))
		picurl=video_data['pic']
		while(picurl[0]=='/'):
			picurl=picurl[1:]
		video_data['pic']='https://'+picurl
	'''if(dbg):
		myio.savetext(mainpth+r'\temp.html',h)
		myio.savetext(mainpth+r'\temp.json',str(sdata))'''
	#logger.info('search result num'+keyword+str(len(sdata)))
	return sdata
	sdata=[(-i['rank_score'],i)for i in sdata]
	sdata.sort()
	sdata=[i[1]for i in sdata]
	

class monitor_new_video:
	def __init__(self,method=getSearch,kwargs=None,savepth=None,callback=None,autostart=False,interval=5,deduping=True,lenlimit=20):
		if(kwargs==None):
			kwargs={}
		if(savepth==None):
			savepth=mainpth+r'\save\monitor_new_video_%s.json'%myhash.hashs(str(method)+str(kwargs))
		if(callback==None):
			callback=print
		self.method=method
		self.deduping=deduping		#deduplicate去重，工地英语缩写。没有去重的话在callback函数处理去重的事情。
		self.monitorjob=myjobs.job()
		self.interval=interval
		self.savepth=savepth
		self.kwargs=kwargs
		self.callback=callback		#当发现新视频时候的回调函数
		self.posted={}				#查重
		self.lenlimit=lenlimit		#只返回前数项结果
		self.read()
		if(autostart):
			self.start()
		if(dbg):
			logger.info('new_video_monitor_initiat'+str(method)+str(kwargs))
	def read(self):
		try:
			dic=myio.loadjson(self.savepth)
			self.posted.update(dic)
		except Exception:
			pass
	def save(self):
		myio.dumpjson(self.savepth,self.posted)
	def monitor(self):
		while(self.monitoring):
			try:
				wt=self.last_t-time.time()+self.interval
				while((wt>0)and(self.monitoring)):
					time.sleep(wt/2+4)
					wt=self.last_t-time.time()+self.interval
				for i in throttles:
					i.acquire()
				self.last_t=time.time()
				try:
					results=self.method(**self.kwargs)
					if(len(results)>self.lenlimit):
						results=results[:self.lenlimit]
				except Exception as e:
					logger.error(traceback.format_exc())
					logger.error('监控新视频获取新视频时出现异常%s'%(str(e)))
					continue
				self.read()
				for result in results:
					
					id=str(result['id'])
					result['id']=id
					result['kwargs']=self.kwargs
					if((id in self.posted)and(self.deduping)):
						continue
					#print('monitored '+id)
					try:
						self.callback(result)
					except Exception as e:
						logger.error(traceback.format_exc())
						logger.error('%s%s监控新视频回调时出现异常%s'%(self.kwargs,str(e),result))
					self.posted[id]=1
					if(self.deduping):
						break
				self.save()
			except Exception as e:
				print(e)
				print(traceback.format_exc())
	def start(self):
		if(self.isAlive()):
			self.join()
		self.monitoring=True
		self.last_t=time.time()-random.random()*self.interval
		self.monitorjob.start(target=self.monitor)
	def isAlive(self):
		return self.monitorjob.isAlive()
	def join(self):
		self.monitoring=False
		self.monitorjob.join()
		
		
class monitor_live:		#监控开播
	def __init__(self,live_id=10183,savepth=None,callback=None,autostart=False,interval=5,handle_posted=True):
		
		if(savepth==None):
			savepth=mainpth+r'\save\monitor_live_%s.json'%live_id
		if(callback==None):
			callback=print
		self.monitorjob=myjobs.job()
		
		self.handle_posted=handle_posted
		self.interval=interval
		self.savepth=savepth
		#self.lenlimit=lenlimit
		self.live_id=live_id
		self.callback=callback
		self.posted={}
		self.read()
		if(autostart):
			self.start()
	def read(self):
		try:
			dic=myio.loadjson(self.savepth)
			self.posted.update(dic)
		except Exception:
			pass
	def save(self):
		myio.dumpjson(self.savepth,self.posted)
	def monitor(self):
		while(self.monitoring):
			wt=self.last_t-time.time()+self.interval
			while((wt>0)and(self.monitoring)):
				time.sleep(min(wt/2+5,60))
				wt=self.last_t-time.time()+self.interval
			for i in throttles:
				i.acquire()
			
			logger.info("%s直播监控距离上一次刷新时间%s"%(self.live_id,time.time()-self.last_t))
			self.last_t=time.time()
			api_url=r'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=%s&from=room'
			#print(api_url%self.live_id)
			try:
				# result=lcg_s.gettext(api_url%self.live_id,proxies={})	#开播信息
				result=requests.get(api_url%self.live_id).json()
			except Exception as e:
				logger.error(traceback.format_exc())
				logger.error('%s监控开播获取开播信息时出现异常%s'%(self.live_id,str(e)))
			result=result['data']
			
			self.read()
			#print(result)
			live_time=result['live_time']
			live_status=result['live_status']
			username=get_username_by_uid(result['uid'])
			result['username']=username
			result['preview_pic']=result["user_cover"]or result['keyframe']
			result['url']=r'https://live.bilibili.com/%s'%self.live_id
			
			#print(username,live_time in self.posted,live_status)	
			if(not((live_time in self.posted)and self.handle_posted)and live_status==1):
				logger.info('%s于%s开播了'%(username,live_time))
				self.last_t=time.time()+self.interval
				try:
					im=illustrate_live_result(result)
					result['illustrate']=im
				except Exception as e:
					logger.error("无法为%s渲染预览图"%username)
					print(traceback.format_exc())
				try:
					self.callback(result)
				except Exception as e:
					print(traceback.format_exc())
					logger.error('%s监控开播回调时出现异常%s'%(self.live_id,str(e)))
					continue
				self.posted[live_time]=1
			self.save()
	def start(self):
		if(self.isAlive()):
			self.join()
		self.monitoring=True
		self.last_t=time.time()-random.random()*self.interval
		self.monitorjob.start(target=self.monitor)
	def isAlive(self):
		return self.monitorjob.isAlive()
	def join(self):
		self.monitoring=False
		self.monitorjob.join()
		
def get_username_by_uid(uid):
	url=r'https://space.bilibili.com/%s/#/'%uid
	h=lcg_l.gettext(url,proxies={})
	title=re.findall(r'<title>(.+?)</title>',h)[0]
	name=re.findall(r'(.+)的个人空间',title)[0]
	return name
def getimgfile(url,quality='@320w_200h.webp',geter=lcg_m,referer=None):
	if((url[-4:]!='webp')and(quality)):
		#print(url[-4:])
		url_=url+quality
	else:
		url_=url
	if(referer):
		img=geter.get_image(url_,referer=referer)
		file=geter.get_path(url_,referer=referer)
	else:
		img=geter.get_image(url_)
		file=geter.get_path(url_)
	#img=bin2img(imgbin,pth=mainpth+r'\temp\\')
	
	#time.sleep(0.1)
	return file
	#print(len(sdata['allData']['video']))
live_result_illust_cache={}
def illustrate_live_result(result,prev_pic='preview_pic'):
	cache_id="%s_%s_%s"%(result['username'],result['live_time'],prev_pic)
	if(cache_id in live_result_illust_cache):
		return live_result_illust_cache[cache_id]
	url=result['url']
	username=result['username']
	im_prev=lcg_l.get_image(result[prev_pic],headerex={"Referer":url})
	w,h=im_prev.size
	avatar_size=int(0.24*h)
	
	img_avatar=get_avatar_by_uid(result['uid']).resize((avatar_size,avatar_size),Image.LANCZOS)
	border_color=pic2pic.get_main_color(im_prev)
	img_avatar=pic2pic.circle_mask_RGBA(img_avatar,(255,255,255,255))
	
	img_username_=pic2pic.txt2im(result['username'],fixedHeight=int(avatar_size/1.618),bg=(255,255,255,255),fill=(0,0,0,255))
	img_username_=pic2pic.im_sizelimitmax(img_username_,(w-avatar_size,h))
	untop=int((avatar_size -  img_username_.size[1])/2)
	
	img_username=Image.new("RGBA",(w,avatar_size),(255,255,255,255))
	img_username.paste(img_avatar,(0,0))
	img_username.paste(img_username_,(avatar_size,untop))
	
	titleHeight=int(avatar_size/1.618/1.618)
	title_fill=(62,62,62,255)
	title="于%s开始直播：\n%s"%(result['live_time'],result['title'])
	img_title_=pic2pic.txt2im_ml(title,bg=(255,255,255,255),fill=title_fill,fixedHeight=titleHeight,width=w-avatar_size)
	qr=pic2pic.im_sizelimitmax(myqr.make(result['url']),(avatar_size,avatar_size))
	img_title=Image.new("RGBA",(w,max(img_title_.size[1],avatar_size)),(255,255,255,255))
	img_title.paste(img_title_,(0,0))
	img_title.paste(qr,(img_title_.size[0],0))
	
	renderer=myRenderer.renderer(type='verticle',contents_gap=titleHeight//2,border={"type":'0','width':titleHeight//2,'color':border_color},bg=(255,255,255,255),align_pos_default=1-0.618)
	renderer.add_content(im_prev)
	renderer.add_content(img_username)
	renderer.add_content(img_title)
	#renderer.add_content(qr)
	ret=renderer.render()
	live_result_illust_cache[cache_id]=ret
	return ret
def get_avatar_by_uid(uid):
	url=r'https://api.bilibili.com/x/space/acc/info?mid=%s&jsonp=jsonp'%uid
	rurl=r'https://space.bilibili.com/%s'%uid
	#j=json.loads(lcg_ml.gettext(url,headerex={"Referer":rurl}))['data']
	j=get_user_info_by_uid(uid)
	avatar=j['face']
	try:
		avatar=lcg_l.get_image(avatar,headerex={"Referer":rurl},proxies={})
	except Exception as e:
		avatar=Image.new("RGB",(52,52),(255,255,255))
	return avatar
def get_live_info(live_id):
	api_url=r'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=%s&from=room'
	result=lcg_s.gettext(api_url%live_id,proxies={})	#开播信息
	result=json.loads(result)
	if(result['msg']!='ok'):
		return None
	result=result['data']
	#print(result)
	live_time=result['live_time']
	live_status=result['live_status']
	username=get_username_by_uid(result['uid'])
	result['username']=username
	result['preview_pic']=result["user_cover"]or result['keyframe']
	result['url']=r'https://live.bilibili.com/%s'%live_id
	return result
user_info_cache=myhash.splitedDict(pth=path.join(mainpth,'uinfo_cache'),splitMethod=lambda x:str(x)[:2])
def get_user_info_by_uid(uid,acceptable_time=300):
	uid=str(uid)
	if(uid in user_info_cache):
		tm,info=user_info_cache[uid]
		if(tm+acceptable_time>time.time()):
			return info
	
	
	rurl=r"https://space.bilibili.com/%s"%uid
	def get_up_stat():
		url=r'https://api.bilibili.com/x/space/upstat?mid=%s&jsonp=jsonp&callback=__jp5'%uid
		j = json.loads(lcg_ml.gettext(url,headerex={"Referer":rurl})[6:-1])['data']
		return j
	def get_follow_stat():
		url=r'https://api.bilibili.com/x/relation/stat?vmid=%s&jsonp=jsonp&callback=__jp4'%uid
		j = json.loads(lcg_ml.gettext(url,headerex={"Referer":rurl})[6:-1])['data']
		return j
	def get_info():
		url=r'https://api.bilibili.com/x/space/acc/info?mid=%s&jsonp=jsonp'%uid
		j = json.loads(lcg_ml.gettext(url,headerex={"Referer":'https://space.bilibili.com/'}))['data']
		return j
	def vtbsmoe_detail():
		url=r'https://api.vtbs.moe/v1/detail/%s'%uid
		j = json.loads(lcg_ml.gettext(url,retry=1))
		return j
	def get_room_info_old():
		url=r'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid=%s'%uid
		j = json.loads(lcg_ml.gettext(url,headerex={'Referer':'https://space.bilibili.com/'}))['data']
		return j
	def base_on_html():
		ret={}
		h=lcg_ml.gettext(r'https://m.bilibili.com/space/%s'%uid,headers=lcg.getheader.headers_mobile)
		'''_=re.findall(r'<div class="face"><img src="(.+?)" class="bfs-img avatar"',h)
		ret['face']='https:'+_[0]
		_=re.findall(r'iconfont ic_userlevel_(\d)',h)
		ret['level']=int(_[0])
		_=re.findall(r'<div class="desc"><span class="content">(.+?)</span',h)
		ret['sign']=_[0]
		'''
		__=re.findall(r'__INITIAL_STATE__=([\s\S]+?);\(function',h)
		ret.update(json.loads(__[0])['space']['info'])
		#myio.savetext(r'G:\temp.html',h)
		return ret
	ret={}
	try:
		ret.update(base_on_html())
	except Exception as e:
		print('html error',e)
	
	try:
		ret.update(get_info())
	except Exception as e:
		print('get info error')
	try:
		ret.update(get_follow_stat())
	except Exception:
		pass
	try:
		ret.update(get_room_info_old())
	except Exception as e:
		pass
	try:
		ret.update(vtbsmoe_detail())
	except Exception as e:
		print('不在vtbs.moe内')
	user_info_cache[uid]=[time.time(),ret]
	return ret
def get_img_lvl(lvl):
	return lcg_l.get_image(r'https://s1.hdslb.com/bfs/static/mult/images/lv%d.png'%lvl)
def nl_num(n):
	if(n>10000):
		return "%.1f万"%(n/10000)
	else:
		return str(n)
def illust_user_by_uid(uid,extra_texts="",show_qr=True):
	import numpy as np
	info=get_user_info_by_uid(uid)
	#myio.dumpjson(r'E:\new\temp.json',info)
	#import os
	#os.system(r"explorer E:\new\temp.json")
	def color_bannerize(c):
		H,S,V=pic2pic.RGB2HSV(*c)
		S=100*0.3+S*0.7
		V=100*0.7+V*0.3
		ret=pic2pic.HSV2RGB(H,S,V)
		#print(pic2pic.RGB2HSV(*ret)[0],H)
		return ret
	def color_dark_text(c):
		H,S,V=pic2pic.RGB2HSV(*c)
		S=100
		V=20*0.7+V*0.3
		ret=pic2pic.HSV2RGB(H,S,V)
		#print(pic2pic.RGB2HSV(*ret)[0],H)
		return ret
	def color_bright_text(c):
		H,S,V=pic2pic.RGB2HSV(*c)
		S=1.6
		V=100
		ret=pic2pic.HSV2RGB(H,S,V)
		#print(pic2pic.RGB2HSV(*ret)[0],H)
		return ret
	level=info['level']
	
	img_avt=get_avatar_by_uid(uid)
	
	colors=pic2pic.get_main_colors(img_avt,num=5,cnt_weight=0.23,color_similarity_weight=1.7,exclude_colors=[[0,0,0],[255,255,255]]*5,sweight=1.4,rough=0.7)
	colors.sort(key=lambda x:sum(x))
	#colors_banner=[color_bannerize(i) for i in colors]
	#print(colors)
	def get_img_banner():
		url=info.get('topPhoto',None) or info.get('top_photo',None)
		if(url):
			return lcg_l.get_image(url)
		else:
			return random_tri_pic.rand_color1(300,174,colors,fac_min=2,fac_max=20,n=75)
	#img_banner=random_tri_pic.rand_color1(300,174,colors,fac_min=2,fac_max=20,n=75)
	#img_banner=random_tri_pic.rand_color1(300,174,colors_banner,n=120)
	img_banner=get_img_banner()
	# random_tri_pic.rand_color(300,174,colors).show()
	#img_banner.show()
	#img_avt.show()
	
	
	width,border,banner_height,avt_size=1080,20,360,300
	name_height=avt_size//2+border
	if(show_qr):
		qr_size=int(avt_size*(0.5-0.5**1.5)+border)
		img_qr=myqr.make(qrlink=r'https://space.bilibili.com/%s/'%uid).resize((qr_size,qr_size))
		
	color_dark_text=color_dark_text(colors[0])+(255,)
	bg_color=color_bright_text(colors[1])+(255,)
	
	others="关注数:%s，粉丝数:%s"%(nl_num(info['following']),nl_num(info['follower']))
	others+='\n'+info['sign']
	if(extra_texts):
		others+='\n'+extra_texts
	img_others=pic2pic.txt2im_ml(others,fill=color_dark_text,fixedHeight=int(name_height/3.5),width=width-border*2)
	
	layer0=Image.new("RGBA",(width,banner_height+name_height+img_others.size[1]+border),bg_color)
	layer0.paste(pic2pic.imBanner(img_banner.convert("RGBA"),(width,banner_height)),(0,0))
	img_avt=pic2pic.circle_mask_RGBA(img_avt).resize((avt_size,avt_size),Image.LANCZOS)
	layer0.paste(img_avt,box=(border,banner_height-avt_size//2),mask=img_avt)
	
	
	img_name_=pic2pic.txt2im(info['name'],fixedHeight=name_height-border*2,fill=color_dark_text)
	img_lvl=pic2pic.fixHeight(get_img_lvl(info['level']),int(img_name_.size[1]*0.5))
	img_name=Image.new("RGBA",(img_name_.size[0]+border+img_lvl.size[0],img_name_.size[1]),(0,0,0,0))
	img_name.paste(img_name_,(0,0))
	img_name.paste(img_lvl,(img_name.size[0]-img_lvl.size[0],img_name.size[1]-img_lvl.size[1]))
	if(img_name.size[0]>width-border*3-avt_size):
		img_name=pic2pic.fixWidth(img_name,width-border*3-avt_size)
	layer0.paste(img_name,box=(border*2+avt_size,banner_height+border),mask=img_name)
	layer0.paste(img_others,(border,banner_height+name_height),mask=img_others)
	if(show_qr):
		layer0.paste(img_qr,(border*2+avt_size-qr_size,banner_height+name_height-qr_size))
	#layer0.show()
	temp=Image.new("RGB",(layer0.size[0]+border*2,layer0.size[1]+border*2),color_bannerize(colors[0]))
	temp.paste(layer0,(border,border))
	return temp
	
	
def test_monitor_live():
	a=monitor_live(live_id='21341098',callback=lambda x:(x['illustrate'].show(),exit()),handle_posted=False)
	a.start()
class dick:
	def __init__(self,dic):
		for i in dic:
			exec('self.%s=dic["%s"]'%(i,i))
		self.original_dic=dic
	def get(self,k,default):
		return self.original_dic.get(k,default)
	def __getitem__(self,k):
		return self.original_dic[k]
	def __setitem__(self,i,v):
		self.original_dic[i]=v
		exec('self.%s=eval(v)'%i)
	def __contains__(self,k):
		return k in self.original_dic
def get_dynamic_reposts(tid):
	
	ret=[]
	if(re.match(r'https://t.bilibili.com/\d+',tid)):
		tid=re.findall(r'\d+',tid)[0]
	
	repost_detail=r'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail?dynamic_id=%s'%tid
	print(repost_detail)
	myio.dumpjson(r'C:\temp\temp.json',json.loads(lcg_s.gettext(repost_detail)))
	repost_detail=dick(json.loads(lcg_s.gettext(repost_detail))['data'])
	ret+=repost_detail.items
	while(repost_detail.has_more):
		repost_detail=r'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail?dynamic_id=%s&offset=%s'%(tid,repost_detail.offset)
		repost_detail=dick(json.loads(lcg_s.gettext(repost_detail))['data'])
		ret+=repost_detail.items
	for i in ret:
		i['card']=json.loads(i['card'])
		i['content']=i['card']['item']['content']
		i['content_trim']=i['card']['item']['content'].split('//')[0]
		
		i.update(i['desc']['user_profile']['info'])
	return ret
def search_user(kwd):
	rurl=r'https://search.bilibili.com/upuser?keyword='+quote(kwd)
	url=r'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=bili_user&page=1&order=&keyword=%s&category_id=&user_type=&order_sort=&changing=mid&__refresh__=true&_extra=&highlight=1&single_column=0'%quote(kwd)
	text=lcg_s.gettext(url,headerex={"Referer":rurl})
	j=json.loads(text)['data']
	return j
	
def get_dynamic_cards(uid,num=12):
	ret=[]
	next_offset=0
	has_more=1
	params={'visitor_uid':0,'host_uid':uid,'need_top':1}
	rurl=r'https://space.bilibili.com/%s/dynamic'%uid
	while(True):
		if(len(ret)>=num):
			break
		if(not has_more):
			break
		params['offset_dynamic_id']=next_offset
		url=r'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?'+urlencode(params)
		h=lcg_ml.gettext(url,headerex={"Referer":rurl})
		j=json.loads(h)
		data=j['data']
		has_more=data['has_more']
		next_offset=data['next_offset']
		for i in data.get('cards',[]):
			i['card']=json.loads(i['card'])
			
			'''if('origin' in i['card']):
				i['card']['origin']=json.loads(i['card']['origin'])'''

			ret.append(i)
		
	return ret
illust_dynamic_cache={}
def illust_dynamic(data,dbg=False):
	if(isinstance(data,str)):
		data=json.loads(data)
	card=data['card']
	
	def illust_article():
		if(dyid in illust_dynamic_cache):
			return illust_dynamic_cache[dyid]
		uid=card['author']['mid']
		username=card['author']['name']
		aid=card['id']
		uinfo=get_user_info_by_uid(uid)
		width=512
		cover_height,border,avatar_size=width//3,width//40,width//8
		avatar_top,title_height,title_top=cover_height-avatar_size//2,avatar_size//2,cover_height+border//2
		username_height,username_top=int(title_height*0.9),title_top+title_height+border
		tags_height=int(username_height*0.618)
		tags=['点赞:%d'%card['stats']['like'],'投币:%d'%card['stats']['coin'],'收藏:%d'%card['stats']['favorite'],'转发:%d'%card['stats']['share']]
		
		for i in card['tags']:
			tags.append(i['name'])
		
		im_cover=lcg_l.get_image(card['banner_url']).convert("RGBA")
		im_cover=pic2pic.imBanner(im_cover,(width,cover_height))
		
		im_avatar=get_avatar_by_uid(uid).resize((avatar_size,avatar_size))
		border_color=pic2pic.get_main_color(im_avatar)
		im_avatar=pic2pic.circle_mask_RGBA(im_avatar)
		
		im_title=pic2pic.txt2im(card['title'],fill=(0,0,0,255),bg=(0,)*4,fixedHeight=title_height)
		im_contents=pic2pic.txt2im_ml(username+'\n'+card['summary']+'...',fill=(0,0,0,255),bg=(0,)*4,fixedHeight=username_height,width=width-border*2)
		bubble=pic2pic.default_bubble()
		
		tags=[pic2pic.bubble(pic2pic.txt2im(_,fill=(0,0,0,255),bg=(0,)*4,fixedHeight=tags_height),**bubble) for _ in tags]
		im_tags=pic2pic.horizontal_layout(tags,width=width-border*2,border=border//4)
		im_tags_top=username_top+im_contents.size[1]+border
		
		height=im_tags_top+im_tags.size[1]+border
		def new_layer(fill=(0,)*4):
			return Image.new("RGBA",(width,height),fill)
		layer0=new_layer((255,)*4)
		layer0.paste(im_cover,(0,0))
		layer1=new_layer()
		layer1.paste(im_avatar,(border,avatar_top))
		layer1.paste(im_title,(border+border//2+avatar_size,title_top))
		layer1.paste(im_contents,(border,username_top))
		layer1.paste(im_tags,(border,im_tags_top))
		layer0=Image.alpha_composite(layer0,layer1)
		ret=Image.new("RGBA",(width+border*2,height+border*2),border_color)
		ret.paste(layer0,(border,border))
		return ret
	
	def illust_video():
		if(dyid in illust_dynamic_cache):
			return illust_dynamic_cache[dyid]
		uid=card['owner']['mid']
		username=card['owner']['name']
		aid=card['aid']
		uinfo=get_user_info_by_uid(uid)
		width=512
		cover_height,border,avatar_size=int(width/2.5),width//40,width//8
		avatar_top,title_height,title_top=cover_height-avatar_size//2,avatar_size//2,cover_height+border//2
		username_height,username_top=int(title_height*0.9),title_top+title_height+border
		tags_height=int(username_height*0.618)
		tags=['点赞:%d'%card['stat']['like'],'投币:%d'%card['stat']['coin'],'收藏:%d'%card['stat']['favorite'],'转发:%d'%card['stat']['share']]
		h=lcg_ml.gettext(r'https://api.bilibili.com/x/web-interface/view/detail/tag?aid=%d'%aid)
		j=json.loads(h)
		for i in j['data']:
			tags.append(i['tag_name'])
		
		im_cover=lcg_l.get_image(card['pic']).convert("RGBA")
		im_cover=pic2pic.imBanner(im_cover,(width,cover_height))
		
		im_avatar=get_avatar_by_uid(uid).resize((avatar_size,avatar_size))
		border_color=pic2pic.get_main_color(im_avatar)
		im_avatar=pic2pic.circle_mask_RGBA(im_avatar)
		
		im_title=pic2pic.txt2im(card['title'],fill=(0,0,0,255),bg=(0,)*4,fixedHeight=title_height)
		im_contents=pic2pic.txt2im_ml(username+'\n'+card['desc'],fill=(0,0,0,255),bg=(0,)*4,fixedHeight=username_height,width=width-border*2)
		bubble=pic2pic.default_bubble()
		
		tags=[pic2pic.bubble(pic2pic.txt2im(_,fill=(0,0,0,255),bg=(0,)*4,fixedHeight=tags_height),**bubble) for _ in tags]
		im_tags=pic2pic.horizontal_layout(tags,width=width-border*2,border=border//4)
		im_tags_top=username_top+im_contents.size[1]+border
		
		height=im_tags_top+im_tags.size[1]+border
		def new_layer(fill=(0,)*4):
			return Image.new("RGBA",(width,height),fill)
		layer0=new_layer((255,)*4)
		layer0.paste(im_cover,(0,0))
		layer1=new_layer()
		layer1.paste(im_avatar,(border,avatar_top))
		layer1.paste(im_title,(border+border//2+avatar_size,title_top))
		layer1.paste(im_contents,(border,username_top))
		layer1.paste(im_tags,(border,im_tags_top))
		layer0=Image.alpha_composite(layer0,layer1)
		ret=Image.new("RGBA",(width+border*2,height+border*2),border_color)
		ret.paste(layer0,(border,border))
		return ret
	def illust_with_pic():
		if(dyid in illust_dynamic_cache):
			return illust_dynamic_cache[dyid]
		return illust_normal()
	def illust_normal():
		if(dyid in illust_dynamic_cache):
			return illust_dynamic_cache[dyid]
		item=card['item']
		uid=card['user']['uid']
		with_pic='pictures' in item
		uinfo=get_user_info_by_uid(uid)
		avatar=get_avatar_by_uid(uid)
		width=512
		gold_rate,border,avatar_height=0.618,width//40,width//8
		username_height,contents_height=int(avatar_height*0.618),int(avatar_height*gold_rate*gold_rate)
		if(with_pic):
			content=item['description']
		else:
			content=item['content']
		im_contents=pic2pic.txt2im_ml(content,width=512-border*2,fixedHeight=contents_height,fill=(0,0,0,255),bg=(0,)*4)
		im_username=pic2pic.txt2im(uinfo['name'],fill=(0,0,0,255),bg=(0,)*4,fixedHeight=username_height)
		im_avatar=get_avatar_by_uid(uid).resize((avatar_height,avatar_height))
		border_color=pic2pic.get_main_color(im_avatar)
		im_avatar=pic2pic.circle_mask_RGBA(im_avatar)
		if(with_pic):
			pictures=[]
			rate=0
			for i in item['pictures']:
				img_src=i['img_src']
				if(dbg):
					print(img_src)
				img=lcg_l.get_image(img_src+'@200w').convert("RGBA")
				rate+=img.size[1]/img.size[0]
				pictures.append(img)
			le=len(pictures)
			rate=rate/le
			w,h=320,int(320*rate)
			if(dbg):
				for i in item['pictures']:
					img_src=i['img_src']
					print(lcg_l.get_path(img_src+'@200w'))
					print('ln664',img_src+'@200w')
				for i in pictures:
					i.show()
					pic2pic.imBanner(i,(w,h)).show()
				print(pictures)
				print('ln669',w,h)
			pictures=[pic2pic.imBanner(_,(w,h)) for _ in pictures]
			col_num=ceil(le**0.5)
			im_pictures=pic2pic.picMatrix(pictures,column_num=col_num,border=0)
			im_pictures=pic2pic.fixWidth(im_pictures,width-border*2)
			height=avatar_height+im_contents.size[1]+border*4+im_pictures.size[1]
		else:
			height=avatar_height+im_contents.size[1]+border*3
		def new_layer(fill=(0,)*4):
			return Image.new('RGBA',(width,height),fill)
			
		layer0=imBanner=pic2pic.imBanner(lcg_l.get_image(uinfo.get('topPhoto',None) or uinfo.get('top_photo',None)),(width,height)).convert("RGBA")
		layer1=new_layer(fill=(255,255,255,220))
		layer0=Image.alpha_composite(layer0,layer1)
		layer1=new_layer()
		layer1.paste(im_avatar,(border,border))
		layer1.paste(im_username,(border*2+avatar_height,border+avatar_height-im_username.size[1]))
		layer1.paste(im_contents,(border,border*2+avatar_height))
		if(with_pic):
			layer1.paste(im_pictures,(border,height-im_pictures.size[1]-border))
		layer0=Image.alpha_composite(layer0,layer1)
		
		ret=Image.new("RGBA",(width+border*2,height+border*2),border_color)
		ret.paste(layer0,(border,border))
		return ret
	def illust_repost():
		if(dyid in illust_dynamic_cache):
			return illust_dynamic_cache[dyid]
		item=card['item']
		uid=card['user']['uid']
		with_pic='pictures' in item
		uinfo=get_user_info_by_uid(uid)
		avatar=get_avatar_by_uid(uid)
		width=512
		gold_rate,border,avatar_height=0.618,width//40,width//8
		username_height,contents_height=int(avatar_height*0.618),int(avatar_height*gold_rate*gold_rate)
		content=item['content']
		im_contents=pic2pic.txt2im_ml(content,width=512-border*2,fixedHeight=contents_height,fill=(0,0,0,255),bg=(0,)*4)
		im_username=pic2pic.txt2im(uinfo['name'],fill=(0,0,0,255),bg=(0,)*4,fixedHeight=username_height)
		im_avatar=get_avatar_by_uid(uid).resize((avatar_height,avatar_height))
		border_color=pic2pic.get_main_color(im_avatar)
		im_avatar=pic2pic.circle_mask_RGBA(im_avatar)
		im_orig=illust_dynamic({"card":json.loads(card['origin'])})
		im_orig=pic2pic.fixWidth(im_orig,width-border*2)
		#im_orig.show()
		height=border*4+avatar_height+im_orig.size[1]+im_contents.size[1]
		def new_layer(fill=(0,)*4):
			return Image.new('RGBA',(width,height),fill)
		layer0=imBanner=pic2pic.imBanner(lcg_l.get_image(uinfo.get('topPhoto',None) or uinfo.get('top_photo',None)),(width,height)).convert("RGBA")
		layer1=new_layer(fill=(255,255,255,220))
		layer0=Image.alpha_composite(layer0,layer1)
		layer1=new_layer()
		layer1.paste(im_avatar,(border,border))
		layer1.paste(im_username,(border*2+avatar_height,border+avatar_height-im_username.size[1]))
		layer1.paste(im_contents,(border,avatar_height+border*2))
		layer1.paste(im_orig,(border,height-im_orig.size[1]-border))
		layer0=Image.alpha_composite(layer0,layer1)
		ret=Image.new("RGBA",(width+border*2,height+border*2),border_color)
		ret.paste(layer0,(border,border))
		return ret
	if('author' in card):
		dyid='art%s'%card['id']
		return illust_article()
	elif('aid' in card):
		aid=card['aid']
		dyid='a%s'%aid
		return illust_video()
	elif('origin' in card):
		dyid='d%s'%data['desc']['dynamic_id']
		return illust_repost()
	elif('pictures' in card['item']):
		dyid='p%s'%card['item']['id']
		return illust_with_pic()
	else:
		dyid='d%s'%card['item']['rp_id']
		return illust_normal()
def get_dynamic_id(data):
	if(isinstance(data,str)):
		data=json.loads(data)
	card=data['card']
	if('author' in card):
		dyid='art%s'%card['id']
		return dyid
	elif('aid' in card):
		aid=card['aid']
		dyid='a%s'%aid
		return dyid
	elif('origin' in card):
		dyid='d%s'%data['desc']['dynamic_id']
		return dyid
	elif('pictures' in card['item']):
		dyid='p%s'%card['item']['id']
		return dyid
	else:
		dyid='d%s'%card['item']['rp_id']
		return dyid
if(__name__=='__main__'):
	print(get_gift_pic_by_name('小心心'))