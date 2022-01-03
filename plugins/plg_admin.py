from bot_backend import *

import cpuinfo,psutil,random,traceback,importlib,threading,mytimer
from lcg import lcg as lcg_
import pic2pic,myhash,time
from os import path
from PIL import Image
plugin_disabled=myhash.splitedDict(pth=path.join(mainpth,'saves','disabled_plugin'),splitMethod=lambda x:myhash.hashs(x)[:2].lower())

kjml={}
trim_kjml=myhash.trimDict()
def register_kjml(id,func):
	simpleid=trim_kjml.add(myhash.hashs(id),id)
	kjml[id]=func
	return simpleid
register_fast_cmd=register_kjml
@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?kj')
def cmd_kj(ctx,match,rest):
	rest=rest.strip()
	id=trim_kjml.get(rest,None)
	if(id not in kjml):
		simple_send(ctx,'没有快捷命令')
		return
	f=kjml[id]
	if(f.__code__.co_argcount):
		ret=kjml[id](ctx)
	else:
		ret=kjml[id]()
	if(ret):
		kjml.pop(id,None)
sent_warning=0
@receiver
def active_count_warning(ctx):
	global sent_warning
	if(threading.activeCount()>900):
		if(time.time()>sent_warning):
			if(path.exists(path.join(mainpth,'su.json'))):
				ctx_tuple=myio.loadjson(path.exists(path.join(mainpth,'su.json')))
			else:
				ctx_tuple=('Group',1126809443,3434614020)
			from bot_backend import receiver_times
			_=[]
			for name,j in receiver_times.items():
				tm,tms=j
				_.append('%s%d次用时%.1f'%(name,tms,tm))
			from bot_backend import threading_cnts
			for name,cnt in threading_cnts.items():
				if(cnt):
					_.append('%d个%s正在运行'%(cnt,name))
			_.append('总共%d个线程正在运行'%len(threading.enumerate()))
			simple_send(None,_,ctx_tuple=ctx_tuple)
			sent_warning=time.time()+120
@receiver
@on_exception_send
@start_with('reload_plugin')
def admin_reload_plugin(ctx,match,rest):
	sctx=simple_ctx(ctx)
	if(not is_su(ctx)):
		simple_send(ctx,'你没有此命令的权限呐！')
		return
	rest=rest.strip()
	if(rest not in plugins):
		simple_send(ctx,'不存在这个插件')
		return
	simple_send(ctx,'重新加载%s'%rest)
	importlib.reload(plugins[rest])
	simple_send(ctx,'重新加载了%s'%rest)
@receiver
@start_with('exec')
def admin_exec(ctx,match):
	sctx=simple_ctx(ctx)
	if(not is_su(ctx)):
		simple_send(ctx,'你没有运行的权限呐！想Hack吗？爬爬爬')
		return
	text=sctx.text[4:]
	def _(ctx=ctx,script=text):
		try:
			exec(script)
			simple_send(ctx,'运行好啦~~')
		except Exception as e:
			simple_send(ctx,'出现了谜之错误!%s'%e)
			traceback.print_exc()
	#jbs.start({"target":_})
	from bot_backend import thread_pool
	thread_pool.submit(_)
	simple_send(ctx,'正在运行~')
	
@receiver
@threading_run
@on_exception_send
@start_with('perf')
def admin_test(ctx):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	if(not is_su(ctx)):
		return
	from bot_backend import receiver_times
	_=[]
	for name,j in receiver_times.items():
		tm,tms=j
		_.append('%s%d次用时%.1f'%(name,tms,tm))
	from bot_backend import threading_cnts
	for name,cnt in threading_cnts.items():
		if(cnt):
			_.append('%d个%s正在运行'%(cnt,name))
	_.append('总共%d个线程正在运行'%len(threading.enumerate()))
	if('plg_setu' in plugins):
		bg=plugins['plg_setu'].rand_img(ctx)
		mes=pic2pic.txt2im_ml('\n'.join(_),width=1080,fixedHeight=42,trim_width=True,fill=(0,0,0,255),bg=(255,255,255,170),align=0.5)
		bg=pic2pic.imBanner(Image.open(bg),mes.size).convert("RGBA")
		mes=Image.alpha_composite(bg,mes)		
	else:
		mes=pic2pic.txt2im_ml('\n'.join(_),width=1080,fixedHeight=42,trim_width=True,fill=(0,0,0,255),bg=(255,)*4,align=0.5)
	
	simple_send(ctx,mes)
@receiver
@threading_cnt('post to pastebin')
@on_exception_send
@start_with('paste')
def admin_post(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	if(not is_su(ctx)):
		return
	rest=rest.strip()
	if(not path.exists(rest)):
		simple_send(ctx,'no such file')
		return
	keypth=path.join(mainpth,'pastebinapikey.txt')
	if(not path.exists(keypth)):
		simple_send(ctx,'unknown pastebin key')
		return
	from myio import opentext
	key=opentext(keypth)
	content=opentext(rest)
	import requests
	r=requests.post(r'https://pastebin.com/api/api_post.php',data={'api_dev_key':key,'api_paste_code':content,'api_paste_private':0,'api_paste_name':path.splitext(path.basename(rest))[0],'api_paste_expire_date':'10M','api_paste_format':'python','api_option':'paste'})
	simple_send(ctx,r.text)
@receiver
@threading_cnt('save from pastebin')
@on_exception_send
@start_with('get')
def admin_get(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	rest=rest.strip()
	ls=rest.split()
	if(not is_su(ctx)):
		return
	if(len(ls)<2):
		simple_send(ctx,'filename and URL')
	savepth,url=ls[:2]
	if(path.exists(savepth)):
		f=open(savepth,'rb')
		b=f.read()
		f.close()
		f=open(savepth+'.bak','wb')
		f.write(b)
		f.close()
		simple_send(ctx,'backup '+savepth+'.bak')
	t=time.time()
	import requests
	r=requests.get(url)
	b=r.content
	f=open(savepth,'wb')
	f.write(b)
	f.close()
	t=time.time()-t
	simple_send(ctx,'done %d bytes in %.1f seconds'%(len(b),t))
@receiver
@threading_cnt('功能')
@on_exception_send
@start_with('[!！/]?sysinfo|[!！/]?help|[!！/]?功能')
def admin_sysinfo(ctx,match):
	@timing('功能')
	def f(ctx=ctx,match=match):
		sctx=simple_ctx(ctx)
		mes=[]
		info=cpuinfo.get_cpu_info()
		spl='='*10
		
		mes.append(spl+"CPU"+spl)
		mes.append('型号：%s'%info.get('brand_raw','??'))
		mes.append('线程数：%s'%info.get('count','??'))
		mes.append('核心数：%s'%psutil.cpu_count(logical=False))
		mes.append('使用率：%s%%'%psutil.cpu_percent())
		mem=psutil.virtual_memory()
		
		
		mes.append(spl+'内存'+spl)
		mes.append('总%.1fGB'%(mem.total/(1<<30)))
		mes.append('已用%.1fGB(%.1f%%)'%(mem.used/(1<<30),mem.used*100/mem.total))
		mes.append(spl+'bot'+spl)
		from bot_backend import send_speedo,receive_speedo
		mes.append('发送消息频率%.1f/sec'%send_speedo())
		mes.append('接收消息频率%.1f/sec'%receive_speedo())
		
		for _ in plugins:
			d=plugins[_].__dir__()
			if(('plugin_name_n' in d)and('report_status' in d)):
				mes.append('%s%s%s'%(spl,plugins[_].plugin_name_n,spl))
				mes+=plugins[_].report_status()
			
		wid=512
		_wid=0
		lnheight=wid>>5
		border=int(lnheight/1.618)
		mxhei=lnheight*3
		hei=border
		top=border
		imgs=[]
		for i in mes:
			if(isinstance(i,str)):
				if(i[-4:] in ['.png' ,'.jpg'] and path.exists(i)):
					i=Image.open(i)
					i=pic2pic.im_sizelimitmax(i,(wid-border*2,mxhei))
				else:
					i=pic2pic.txt2im_ml(i,fill=(0,0,0,255),bg=(255,)*4,fixedHeight=lnheight,width=wid-border*2,trim_width=True,align=0.5)
			imgs.append(i)
			hei+=i.size[1]+border
			_wid=max(_wid,i.size[0]+border*2)
		wid=_wid
		if('plg_setu' in plugins):
			mes=plugins['plg_setu'].rand_img(ctx)
			mes=Image.open(mes).convert("RGBA")
			mes=pic2pic.imBanner(mes,(wid,hei))
		else:
			mes=Image.new("RGBA",(wid,hei),(255,)*4)
		for i in imgs:
			mes.paste(i,box=((wid-i.size[0])//2,top),mask=i)
			top+=i.size[1]+border
		
		'''if('plg_setu' in plugins):
			bg=plugins['plg_setu'].rand_img(ctx)
			mes=pic2pic.txt2im_ml('\n'.join(mes),width=1080,fixedHeight=42,trim_width=True,fill=(0,0,0,255),bg=(255,255,255,170),align=0.5)
			bg=pic2pic.imBanner(Image.open(bg),mes.size).convert("RGBA")
			mes=Image.alpha_composite(bg,mes)		
		else:
			mes=pic2pic.txt2im_ml('\n'.join(mes),width=1080,fixedHeight=42,trim_width=True,fill=(0,0,0,255),bg=(255,)*4,align=0.5)
		'''
		simple_send(ctx,mes,im_size_limit=1<<20)
	f()