import os
from os import path
os.sys.path.append(path.join(path.dirname(__file__),'utils'))
from aiocqhttp import CQHttp,Event
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from make_gif import make_gif
from aiocqhttp import MessageSegment as mseg
import asyncio,os,myhash,re,shutil,traceback
import html,threading,schedule,time,random,myio
from lcg import lcg as lcg_
from mytimer import speedo,throttle
from functools import wraps

from myhash import splitedDict
from glob import glob
#pm=pathManager(appname='setubot-iot')
#mainpth=pm.getpath(session='mainpth',ask_when_dne=True)
mainpth=path.join(path.dirname(__file__),'files')
_backend_type='cqhttp'
#bot=CQHttp()
pic_cnt=splitedDict(pth=path.join(mainpth,'saves','pic_count'),splitMethod=lambda x:x[:2])
pic_cnt_byug={}
def get_pic_cnt_dic(sctx):
	general=pic_cnt
	uid='u'+sctx.user_id
	gid='g'+sctx.group_id
	if(uid in pic_cnt_byug):
		byu=pic_cnt_byug[uid]
	else:
		byu=splitedDict(pth=path.join(mainpth,'saves','pic_count_by',uid),splitMethod=lambda x:x[:2])
		pic_cnt_byug[uid]=byu
	if(gid in pic_cnt_byug):
		byg=pic_cnt_byug[gid]
	else:
		byg=splitedDict(pth=path.join(mainpth,'saves','pic_count_by',gid),splitMethod=lambda x:x[:2])
		pic_cnt_byug[gid]=byg
	return general,byu,byg
def get_pic_cnt_byu(uid):
	if(uid[0]!='u'):
		uid='u'+uid
	if(uid in pic_cnt_byug):
		byu=pic_cnt_byug[uid]
	else:
		byu=splitedDict(pth=path.join(mainpth,'saves','pic_count_by',uid),splitMethod=lambda x:x[:2])
		pic_cnt_byug[uid]=byu
	return byu
def get_pic_cnt_byg(gid):
	if(gid[0]!='g'):
		gid='g'+gid
	if(gid in pic_cnt_byug):
		byg=pic_cnt_byug[gid]
	else:
		byg=splitedDict(pth=path.join(mainpth,'saves','pic_count_by',gid),splitMethod=lambda x:x[:2])
		pic_cnt_byug[gid]=byg
	return byg
max_workers=500
thread_pool=ThreadPoolExecutor(max_workers=max_workers)
lcg_l=lcg_(workpth=path.join(mainpth,'temp'),expiretime=86400,proxies={})
lcg_eternal=lcg_(workpth=path.join(mainpth,'temp'),expiretime=1<<60,proxies={})
running=True
threading_cnts={}
pool_active_count=0
def threading_cnt(name):
	def f(func,args,kwargs,func_name=name):
		try:
			global pool_active_count,threading_cnts
			pool_active_count+=1
			threading_cnts[func_name]=threading_cnts.get(func_name,0)+1
			try:
				func(*args,**kwargs)
			except Exception as e:
				pool_active_count-=1
				threading_cnts[func_name]-=1
				print(e)
				raise e
			pool_active_count-=1
			threading_cnts[func_name]-=1
		except Exception as ee:
			print(ee,func,args,kwargs,func_name)
	def deco(func):
		@wraps(func)
		def inner(*args,**kwargs):
			thread_pool.submit(f,func,args,kwargs)
		return inner
	return deco

def on_exception_send(func):
	@wraps(func)
	def inner(ctx,*args,**kwargs):
		try:
			func(ctx,*args,**kwargs)
		except Exception as e:
			fexc=str(ctx)+'\n'+traceback.format_exc()
			print(fexc)
			name="exception_"+myhash.hashs(fexc)
			myio.savetext(path.join(mainpth,"logs",name+".log"),fexc)
			simple_send(ctx,'出现了谜之错误%s\n日志:%s'%(e,name))
	return inner

def threading_run(func):
	return threading_cnt(func.__name__)(func)

def base32(i):
	c='1234567890abcdefghijklmnopqrstuv'
	ret=[]
	while(i):
		ret.append(c[i&0b11111])
		i>>=5
	return ''.join(ret)

def img2filename(im,im_size_limit=1<<20):
	ls=list(glob(path.join(mainpth,'temppic',"*.*")))
	if(len(ls)>1000):
		en=random.sample(ls,500)
		for i in en:
			try:
				os.remove(i)
			except Exception as e:
				print(e)

	name=myhash.phashi(im,w=64)
	name=base32(name)
	#name=str(name).zfill(4)
	if(isinstance(im,list)):
		return make_gif(im)
	elif(im.mode=='RGBA'):
		typ='PNG'
		ext='.png'
		save_kwargs={'optimize':True}
	else:
		typ='JPEG'
		ext='.jpg'
		save_kwargs={}
	if(not path.exists(path.join(mainpth,'temppic'))):
		os.makedirs(path.join(mainpth,'temppic'))
	pth=path.join(mainpth,'temppic',name+ext)
	im.save(pth,typ,**save_kwargs)
	while(path.getsize(pth)>im_size_limit):
		print('szlimit')
		siz=list(im.size)
		siz[1]=int(siz[1]*0.7)
		siz[0]=int(siz[0]*0.7)
		siz=tuple(siz)
		im=im.resize(siz,Image.LANCZOS)
		im.save(pth,typ,**save_kwargs)
	return pth
send_throttle=throttle(1,1)
send_pool=ThreadPoolExecutor(max_workers=30)
def simple_send(event,mes,im_size_limit=1<<20,ctx_tuple=None,*args,**kwargs):
	try:
		global _bot
		send_throttle.acquire()
		event=event or ctx_tuple
		_mes=[]
		flag=False
		if(not isinstance(mes,list)):
			mes=[mes]
		for i in mes:
			if(flag):
				_mes.append(mseg.text('\n'))
			else:
				flag=True
			if(isinstance(i,Image.Image)):
				_mes.append(mseg.image('file:///'+img2filename(i,im_size_limit=im_size_limit)))
			elif(isinstance(i,str) and path.exists(i)):
				
				if(i[-3:].lower() in ['jpg','bmp','gif','png']):
					_mes.append(mseg.image('file:///'+i))
				elif(i[-3:].lower() in['mp3','wav']):
					if(len(mes)>1):
						if(_mes):
							_mes.pop()
						else:
							flag=False
						simple_send(event,i,ctx_tuple=ctx_tuple)
					else:
						_mes=[mseg.record('file:///'+i)]
				else:
					_mes.append(mseg.text(i))
			elif(isinstance(i,mseg)):
				_mes.append(i)
			else:
				_mes.append(mseg.text(str(i)))
		#print(_mes)
		send_speedo.cnt()
		send_pool.submit(asyncio.run,_bot.send(event,_mes,self_id=event['self_id']))
	except Exception as e:
		traceback.print_exc()
rpics={}
class simple_evt:
	def __init__(self,event):
		mes=html.unescape(event.message)
		self_id=str(event.self_id)
		user_id=str(event.user_id)
		if(event.message_type=='group'):
			group_id=str(event.group_id)
			simple_id=f"{group_id}_{user_id}"
			self.atid=re.findall(r'\[CQ:at,qq=(\d+?)\]',mes)
			self.ated=self_id in self.atid
		else:
			group_id=simple_id="friend_"+user_id
			self.atid=[self_id]
			self.ated=True
		pics=re.findall(r'\[CQ:image,file=(.+?),url=(.+?)\]',mes)
		if(pics):
			rpics[simple_id]=pics
			
		self.user_name=event.sender.get('card',None) or event.sender.get('nickname',None) or '无法获取用户名'
		self.user_id=user_id
		self.self_id=self_id
		self.group_id=group_id
		self.pics=pics
		self.rpics=rpics.get(simple_id,None)
		self._event=event
		self.simple_id=simple_id
		self.trim_ated_text=self.text=re.sub(r'\[CQ:.+?\] ?','',mes)
	def __getattr__(self,s):
		return self._event.__getattribute__(s)
	def get_rpics(self,svpth=None):
		if(svpth is None):
			svpth=path.join(mainpth,'temp')
		ret=[]
		if(self.rpics is None):
			return None
		for f,url in self.rpics:
			enen=lcg_eternal.get_path(url)
			enen=fix_img_ext(enen,svpth=svpth)
			ret.append(enen)
		return ret
	@property
	def ctx_tuple(self):
		return dict(self._event)
	def to_tuple(self):
		return dict(self._event)
def fix_img_ext(pth,svpth=path.join(mainpth,'temp')):
	img=Image.open(pth)
	bsname=path.splitext(path.basename(pth))[0]
	if(test_gif(img)):
		ext='.gif'
	elif(img.mode=='RGBA'):
		ext='.png'
	else:
		ext='.jpg'
	return shutil.copyfile(pth,path.join(svpth,bsname+ext))
def test_gif(img):
	try:
		img.seek(1)
		return True
	except Exception:
		return False

simple_ctx=simple_evt


receiver_times={}
class receiver_timer:
	def __init__(self,name):
		self.tm=time.time()
		self.name=name
	def finish(self):
		dur,tim=receiver_times.get(self.name,(0,0))
		dur+=time.time()-self.tm
		tim+=1
		receiver_times[self.name]=dur,tim
def timing(name):
	def deco(func):
		@wraps(func)
		def inner(*args,**kwargs):
			tmr=receiver_timer(name)
			ret=func(*args,**kwargs)
			tmr.finish()
			return ret
		return inner
	return deco
receivers={}
def receiver(func):
	global receivers
	print('register receiver',func.__name__)
	receivers[func.__name__]=func
	#print(receivers)
	return func
receivers_nlazy={}
def receiver_nlazy(func):
	global receivers
	print('register nolazy receiver',func.__name__)
	receivers_nlazy[func.__name__]=func
	#print(receivers)
	return func


def start_with(st):
	_re=re.compile(st)
	def deco(func,st=st):
		@wraps(func)
		def inner(ctx):
			text=simple_ctx(ctx).text
			match=_re.match(text)
			argc=func.__code__.co_argcount
			#print(argc,func.__name__)
			if(match):
				if(argc==1):
					return func(ctx)
				elif(argc==2):
					return func(ctx,match)
				elif(argc==3):
					return func(ctx,match,text[match.span()[1]:])
				else:
					raise Exception('argc'+str(argc))
			else:
				#print(text,'isnt start with',st)
				pass
		return inner
	return deco
'''@bot.on_message('private')
async def _(event: Event):
    await bot.send(event, '你发了：')
    return {'reply': event.message}
'''
'''@bot.on_message
async def _(event:Event):
	mes=event.message
	if(mes[:4]=='exec'):
		import html
		mes=html.unescape(mes[4:])
		exec(mes)'''
		
plugins={}

def get_plugin_by_name(name):
	return plugins[name]
class get_plugin_namespace:
	def __init__(self,name):
		self.name=name
		pass
	def __getattr__(self,s):
		return plugins[self.name].__getattribute__(s)
	
def to_me(func):
	@wraps(func)
	def inner(ctx,*args,**kwargs):
		sctx=simple_ctx(ctx)
		if(sctx.ated):
			return func(ctx,*args,**kwargs)
	return inner

def my_load_plugin(file):
	dn=path.dirname(file)
	name=path.splitext(path.basename(file))[0]
	os.sys.path.append(dn)
	os.sys.path=list(set(os.sys.path))
	#print(dn,os.sys.path)
	mod=__import__(name)
	if('__plugin_name__' in mod.__dir__()):
		plugins[mod.__plugin_name__]=mod
	else:
		plugins[name]=mod
send_speedo=speedo(5)
receive_speedo=speedo(20)
skip_until=0
@threading_run
def general_reveicer(ctx):
	global send_speedo,receive_speedo,receivers,pool_active_count,skip_until
	sctx=simple_ctx(ctx)
	
	#print(sctx)
	#print('ln218')
	try:
		print('%.1f/sec'%receive_speedo(),'%.1f/sec'%send_speedo(),pool_active_count)
		schedule.run_pending()
		if(sctx.pics):
			for i in sctx.pics:
				for j in get_pic_cnt_dic(sctx):
					name,url=i
					cnt,url=j.get(name,(0,url))
					j[name]=(cnt+1,url)
		receive_speedo.cnt()
		for _,__ in receivers_nlazy.items():
			__(ctx)
		if(time.time()<skip_until):
			en=list(threading_cnts.items())
			en=[_ for _ in en if _[1] ]
			en.sort(key=lambda x:-x[1])
			print('skip message!!!',en)
			return
		if(pool_active_count>max_workers*0.8):
			en=list(threading_cnts.items())
			en=[_ for _ in en if _[1] ]
			en.sort(key=lambda x:-x[1])
			print('skip message!!!',en)
			skip_until=time.time()+60
			return
		for _,__ in receivers.items():
			__(ctx)
	except Exception as e:
		print('ln232',e)
	
superusers=set()
def is_su(event):
	if(isinstance(event),simple_evt):
		return event.user_id in superusers
	elif(callable(event)):
		@wraps(event)
		def inner(evt,*args,**kwargs):
			if(is_su(evt)):
				return event(evt,*args,**kwargs)
		return inner
	else:
		return str(event.user_id) in superusers
async def _general_reveicer(event):
	general_reveicer(event)
async def _echo(event):
	global pool_active_count
	f4=event.message[:4]
	f5=event.message[:5]
	
	if(event.message=='ping'):
		mes=['pong,%d'%pool_active_count]
		#await _bot.send(event,)
		#global skip_until
		if(time.time()<skip_until):
			mes.append('偷懒中，还有%d秒结束'%(skip_until-time.time()))
		else:
			mes.append('正在努力干活哟')
		simple_send(event,mes)
	elif(event.message=='pong'):
		en=list(threading_cnts.items())
		en.sort(key=lambda x:-x[1])
		enen=min(len(en),5)
		en=en[:enen]

		en1=list(receiver_times.items())
		en1.sort(key=lambda x:-x[1][0])
		enen1=min(len(en1),5)
		en1=en1[:enen1]
		mes=[]
		for i,j in en:
			mes.append("%d x %s"%(j,i))
		for i,j in en1:
			j,k=j
			mes.append("%s %d sec %d times"%(i,j,k))
		simple_send(event,mes)
	elif(f4=='xxec' and event.user_id==402254524):
		mes=html.unescape(event.message[4:])
		exec(mes)
'''async def _xxec(event):
	if(event.message[:4]=='xxec' and event.user_id==402254524):
		mes=html.unescape(event.message[4:])
		exec(mes)'''
_bots={}
loop=asyncio.new_event_loop()
_bot=CQHttp()
_bot.on_message(_general_reveicer)
_bot.on_message(_echo)
#_bot.on_message(_xxec)

def run(port=8008):
	
	loop.create_task(_bot.run_task(host='127.0.0.1',port=port))
	loop.run_forever()