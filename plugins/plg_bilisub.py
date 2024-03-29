if(__name__=='__main__'):
	import os
	from os import path
	dn=path.dirname(__file__)
	dn=path.dirname(dn)
	os.sys.path.append(dn)
	os.sys.path=list(set(os.sys.path))
from bot_backend import *
import jieba,traceback,myio,time,bilibilimea,myqr
import random,chat,schedule,pic2pic
from glob import glob
from os import path
from threading import Lock

subscriptions=myhash.splitedDict(pth=path.join(mainpth,'saves','bilisub','subscriptions'),splitMethod=lambda x:str(x)[:2])
#{'liveid':{'group_id':ctx_tuple}}
group_id2live_id=myhash.splitedDict(pth=path.join(mainpth,'saves','bilisub','group_id2live_id'),splitMethod=lambda x:str(x)[:2])
#{'group_id':{'live_id':ctx_tuple}}
dynamic_subscriptions=myhash.splitedDict(pth=path.join(mainpth,'saves','bilisub','dysub'),splitMethod=lambda x:str(x)[:2])
#{'uid':{'group_id':ctx_tuple}}
gid2uid=myhash.splitedDict(pth=path.join(mainpth,'saves','bilisub','dysub_r'),splitMethod=lambda x:str(x)[:2])
#{'group_id':{'uid':ctx_tuple}}
noticed=myhash.splitedDict(pth=path.join(mainpth,'saves','bilisub','noticed'),splitMethod=lambda x:str(x)[:2])
#{'group_id-live_id-live_time':1,'group_id-live_id-title':'title'}
#{'group_id-dynamics':{}}
def check_live_():
	check_live()
	#if(random.random()<0.5):
	check_dynamics()
plugin_name_n='哔哩哔哩订阅'
def report_status():
	ret=[]
	ret.append('“/B 用户名”搜索一个B站用户')
	ret.append('根据提示进行订阅')
	ret.append('/订阅列表查看当前订阅了哪些用户')
	return ret
@threading_cnt('check live')
@timing('check live')
def check_live(*args,**kwargs):

	print('az',time.time())
	if(args or kwargs):
		print(args)
		print(kwargs)
	dic=subscriptions.to_dict()
	lis=list(dic)
	if(not(lis)):
		return
	flag=True
	for i in range(3):
		live_id=random.choice(lis)
		subscribers=subscriptions[live_id]
		if(not(subscribers)):
			continue
		live_info=bilibilimea.get_live_info(live_id)
		#if(live_info['live_status']==1):
		flag=False
		break
	
	if(flag):
		return
	
	for group_id,ctx_tuple in subscribers.items():
		id1='%s-%s-%s'%(group_id,live_id,live_info['live_time'])
		id2='%s-%s-title'%(group_id,live_id)
		if(live_info['live_status']==1):
			if(id1 not in noticed):
				noticed[id1]=True
				simple_send(None,bilibilimea.illustrate_live_result(live_info),ctx_tuple=ctx_tuple)
		if(noticed.get(id2,None)!=live_info['title']):
			noticed[id2]=live_info['title']
			mes='%s把直播间标题改为了%s'%(live_info['username'],live_info['title'])
			try:
				simple_send(None,mes,ctx_tuple=ctx_tuple)
			except Exception as e:
				pass
dy_locks={}
@threading_cnt('check dynamics')
@timing('check dynamics')
def check_dynamics(dbg=False,*args,**kwargs):
	if(args or kwargs):
		print("wtf",args,kwargs)
	uid=dynamic_subscriptions.to_dict()
	if(not uid):
		return
	uid=list(uid)
	uid=random.choice(uid)
	subscribers=dynamic_subscriptions[uid]
	dynamics=bilibilimea.get_dynamic_cards(uid)
	if(len(dynamics)>6):
		dynamics=dynamics[:6]
	name=bilibilimea.get_user_info_by_uid(uid)['name']
	if(uid in dy_locks):
		dy_locks[uid].acquire()
	else:
		dy_locks[uid]=Lock()
		dy_locks[uid].acquire()
	for gid,ctx_tuple in subscribers.items():
		try:
			n=noticed.get('%s-dynamics'%uid,{})
			imgs=[]
			for i in dynamics:
				dyid=bilibilimea.get_dynamic_id(i)
				print('ln102',dyid)
				id='%s-%s'%(gid,dyid)
				if((id not in n) or gid==dbg):
					imgs.append(bilibilimea.illust_dynamic(i))
					n[id]=True
					noticed['%s-dynamics'%uid]=n
			if(imgs):
				qr=myqr.make(r'https://space.bilibili.com/%s'%uid)
				imgs.append(qr)
				img=pic2pic.pinterest(imgs,min(len(imgs)//2,2),bg=(255,)*4)
				img=pic2pic.addTitle(img,'%s的新动态'%name)
				try:
					simple_send(None,img,ctx_tuple=ctx_tuple,im_size_limit=1<<20)
					
				except Exception as e:
					print(traceback.format_exc())
			else:
				print('\n\n\nall dynamics %s was noticed\n\n\n'%uid)
		except Exception:
			dy_locks[uid].release()
			return
	dy_locks[uid].release()
	pass
				
schedule.every(45).seconds.do(check_live_)
@threading_run
def bilisub_runpending():
	while(True):
		schedule.run_pending()
		time.sleep(46)
bilisub_runpending()
plg_admin=get_plugin_namespace('plg_admin')
def get_func_sub_dynamics(ctx,uid):
	def func(ctx=ctx,uid=uid):
		sctx=simple_ctx(ctx)
		gid=sctx.group_id
		ctx_tuple=sctx.ctx_tuple
		dynamic_subscriptions[uid]=dynamic_subscriptions.get(uid,{})
		dynamic_subscriptions[uid][gid]=ctx_tuple
		dynamic_subscriptions.dumpPart1(uid)
		gid2uid[gid]=gid2uid.get(gid,{})
		gid2uid[gid][uid]=ctx_tuple
		gid2uid.dumpPart1(gid)
		info=bilibilimea.get_user_info_by_uid(uid)
		simple_send(ctx,'订阅了%s的动态'%info['name'])
	return func
def get_func_cancel_sub_dynamics(ctx,uid):
	def func(ctx=ctx,uid=str(uid)):
		sctx=simple_ctx(ctx)
		gid=sctx.group_id
		ctx_tuple=sctx.ctx_tuple
		dynamic_subscriptions[uid]=dynamic_subscriptions.get(uid,{})
		dynamic_subscriptions[uid].pop(gid,None)
		dynamic_subscriptions.dumpPart1(uid)
		gid2uid[gid]=gid2uid.get(gid,{})
		gid2uid[gid].pop(uid)
		gid2uid.dumpPart1(gid)
		info=bilibilimea.get_user_info_by_uid(uid)
		simple_send(ctx,'取消订阅了%s的动态'%info['name'])
	return func

def get_func_sub(ctx,live_id):
	def func(ctx=ctx,live_id=str(live_id)):
		#simple_send(ctx,'订阅%s,功能还没做好（'%live_id)
		sctx=simple_ctx(ctx)
		group_id=sctx.group_id
		ctx_tuple=sctx.ctx_tuple
		
		subscriptions[live_id]=subscriptions.get(live_id,{})
		subscriptions[live_id][group_id]=ctx_tuple
		subscriptions.dumpPart1(live_id)
		
		group_id2live_id[group_id]=group_id2live_id.get(group_id,{})
		group_id2live_id[group_id][live_id]=ctx_tuple
		group_id2live_id.dumpPart1(group_id)
		
		info=bilibilimea.get_live_info(live_id)
		
		simple_send(ctx,'订阅了%s的直播'%info['username'])
	return func
def get_func_cancel_sub(ctx,live_id):
	def func(ctx=ctx,live_id=live_id):
		#simple_send(ctx,'订阅%s,功能还没做好（'%live_id)
		sctx=simple_ctx(ctx)
		group_id=sctx.group_id
		ctx_tuple=sctx.ctx_tuple
		
		subscriptions[live_id]=subscriptions.get(live_id,{})
		subscriptions[live_id].pop(group_id,'')
		subscriptions.dumpPart1(live_id)
		
		group_id2live_id[group_id]=group_id2live_id.get(group_id,{})
		group_id2live_id[group_id].pop(live_id,'')
		group_id2live_id.dumpPart1(group_id)
		
		info=bilibilimea.get_live_info(live_id)
		
		simple_send(ctx,'取消订阅了%s'%info['username'])
	return func

@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?B ')
def cmd_bili_search(ctx,match,rest):
	@timing('B搜索')
	def _f(ctx,match,rest):
		sctx=simple_ctx(ctx)
		ids=set()
		rest=rest.strip()
		_=bilibilimea.search_user(rest)
		for i in _.get('result',[]):
			ids.add(str(i['mid']))
		if(rest.isnumeric()):
			ids.add(rest)
			_=bilibilimea.get_live_info(rest)
			if(_):
				ids.add(str(_['uid']))
		imgs=[]
		print('ln215',ids)
		for i in ids:
			print(i)
			info=bilibilimea.get_user_info_by_uid(i)
			extra_texts=''
			if(info.get('roomid',None)):
				func_sub=get_func_sub(ctx,info['roomid'])
				kj=plg_admin.register_kjml(sctx.simple_id+'bilisub'+str(info['roomid']),func_sub)
				extra_texts+='订阅直播输入"/kj %s"'%kj
			func_sub=get_func_sub_dynamics(ctx,i)
			kj=plg_admin.register_kjml(sctx.simple_id+"bili_dysub"+str(i),func_sub)
			extra_texts+='订阅动态输入"/kj %s"'%kj
			im=bilibilimea.illust_user_by_uid(i,extra_texts=extra_texts)
			imgs.append(im)
		if(imgs):
			simple_send(ctx,pic2pic.picMatrix(imgs))
		else:
			simple_send(ctx,'莫得搜索结果QAQ')
	return _f(ctx,match,rest)
@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?订阅列表')
def cmd_sub_list(ctx):
	@timing('订阅列表')
	def _f(ctx):
		sctx=simple_ctx(ctx)
		group_id=sctx.group_id
		live_ids=group_id2live_id.get(group_id,{})
		uids=set(list(gid2uid.get(group_id,{})))
		dy_uids=set(list(gid2uid.get(group_id,{})))
		lv_uids=set()
		imgs=[]
		for i in live_ids:
			if(i==0):
				continue
			info=bilibilimea.get_live_info(i)
			uid=str(info['uid'])
			uids.add(uid)
			lv_uids.add(uid)
		for i in uids:
			info=bilibilimea.get_user_info_by_uid(i)
			extra_texts=''
			if(info.get('roomid',None)):
				if(i in lv_uids):
					func_sub=get_func_cancel_sub(ctx,info['roomid'])
					kj=plg_admin.register_kjml(sctx.simple_id+'cancel_bilisub'+str(info['roomid']),func_sub)
					extra_texts+='取消订阅直播输入"/kj %s"\n'%kj
				else:
					func_sub=get_func_sub(ctx,info['roomid'])
					kj=plg_admin.register_kjml(sctx.simple_id+'bilisub'+str(info['roomid']),func_sub)
					extra_texts+='订阅直播输入"/kj %s"\n'%kj
			if(i in dy_uids):
				func_sub=get_func_cancel_sub_dynamics(ctx,i)
				kj=plg_admin.register_kjml(sctx.simple_id+"cancel_bili_dysub"+str(i),func_sub)
				extra_texts+='取消订阅动态输入"/kj %s"'%kj
			else:
				func_sub=get_func_sub_dynamics(ctx,i)
				kj=plg_admin.register_kjml(sctx.simple_id+"bili_dysub"+str(i),func_sub)
				extra_texts+='订阅动态输入"/kj %s"'%kj
			im=bilibilimea.illust_user_by_uid(i,extra_texts=extra_texts)
			imgs.append(im)
		simple_send(ctx,pic2pic.picMatrix(imgs))
	return _f(ctx)
lcg_s=lcg_(workpth=path.join(mainpth,'temp'),expiretime=30,proxies={})
@receiver
@on_exception_send
@start_with("/随机V")
def cmd_random_vup(ctx):
	import json
	
	#simple_send(ctx,"获取列表")
	j=lcg_s.gettext("https://api.vtbs.moe/v1/living")
	j=json.loads(j)
	import random
	liveid=random.choice(j)
	from bilibilimea import get_live_info,illustrate_live_result
	#simple_send(ctx,"获取直播间信息")
	info=get_live_info(liveid)
	#simple_send(ctx,"绘制结果")
	im=illustrate_live_result(info,prev_pic='preview_pic')
	simple_send(ctx,[im,'(封面)'])
	im=illustrate_live_result(info,prev_pic='keyframe')
	simple_send(ctx,[im,'(在播内容)'])
	
@receiver
@threading_run
@on_exception_send
@start_with("/V拼图")
def cmd_vup_pintu(ctx):
	import json
	from threading import Thread
	from PIL import Image
	import bilibilimea,time
	from lcg import lcg as lcg_
	from os import path
	import numpy as np
	from concurrent.futures import ThreadPoolExecutor
	from threading import Lock
	import random,traceback
	mainpth=path.dirname(__file__)
	lcg_s=lcg_(workpth=path.join(mainpth,'temp'),expiretime=30,proxies={})
	lcg_l=lcg_(workpth=path.join(mainpth,'temp'),expiretime=3600,proxies={})

	all_living=lcg_s.gettext(r'https://api.vtbs.moe/v1/living')
	all_living=json.loads(all_living)
	avatars=[]
	uids=[]
	pool=ThreadPoolExecutor(max_workers=8)
	lck=Lock()
	print('%d vtbs are on live!'%len(all_living))
	if(len(all_living)>100):
		all_living=random.sample(all_living,100)
	all_living=set(all_living)
	az=len(all_living)
	def f(liveid,avts,lck):
		try:
			#info=bilibilimea.get_live_info(liveid,getter=bilibilimea.lcg_l)
			info=json.loads(lcg_l.gettext(r'https://api.vtbs.moe/v1/room/%s'%liveid))
			uid=info['uid']
			#info=bilibilimea.get_user_info_by_uid(uid)
			avatar=bilibilimea.get_avatar_by_uid(uid,acceptable_time=24*3600*7)
			
			lck.acquire()
			avatars.append(avatar)
			uids.append(uid)
			lck.release()
			print('downloaded avatar of',info['uid'],'%d/%d'%(len(avatars),len(avatars)+len(all_living)-1))
		except Exception as e:
			traceback.print_exc()
			pass
		all_living.remove(liveid)
	for idx,liveid in enumerate(list(all_living)):
		#info=json.loads(lcg_s.gettext(r'https://api.vtbs.moe/v1/room/%s'%liveid))
		#print('downloading avatar %d/%d'%(idx,len(all_living)))
		pool.submit(f,liveid,avatars,lck)
	enmiao=0
	while(all_living):
		time.sleep(5)
		if(enmiao*5>300):
			simple_send(ctx,'下载不下来..')
			return
		if(enmiao%6==0):
			simple_send(ctx,'下载VUP们的头像..%d%%'%len(avatars))
		enmiao+=1
		
	from annoy import AnnoyIndex
	from pic_indexing_RGB_img2vecs import img2vec_rgb
	siz=32
	index=AnnoyIndex(siz*siz*3,'euclidean')
	for idx,i in enumerate(avatars):
		vec=img2vec_rgb(i,siz)
		index.add_item(idx,vec)
	index.build(2)
	bg=Image.open(simple_ctx(ctx).get_rpics()[0]).convert("RGB")
	#bg=Image.open(r"C:\setubot-iot\1zSD0saiWMGqMCKMKCEAMv.jpg").convert("RGB")
	grid_w,grid_h=bg.size
	grid_tot=max(1000,len(avatars)*2)
	rate=(grid_tot/grid_w/grid_h)**0.5
	grid_w,grid_h=int(grid_w*rate+1),int(grid_h*rate+1)
	bg=bg.resize((grid_w*siz,grid_h*siz),Image.LANCZOS)
	ret=Image.new("RGB",bg.size)
	arr=np.asarray(bg).swapaxes(0,1)
	visited={}
	result_id=np.zeros((grid_w,grid_h),np.uint16)
	for x in range(grid_w):
		for y in range(grid_h):
			vec=img2vec_rgb(arr[x*siz:(x+1)*siz,y*siz:(y+1)*siz],siz)
			idxs=index.get_nns_by_vector(vec,5)
			idx=min(idxs,key=lambda x:visited.get(x,0))
			visited[idx]=visited.get(idx,0)+1
			ret.paste(avatars[idx].resize((siz,siz)),(x*siz,y*siz))
			result_id[x,y]=idx
	ret=Image.blend(ret,bg,0.1)
	simple_send(ctx,ret)
	index.unload()
	if('plg_picans' in plugins):
		mod=plugins['plg_picans']
		for x in range(grid_w):
			for y in range(grid_h):
				p=ret.crop((x*siz,y*siz,(x+1)*siz,(y+1)*siz))
				idx=result_id[x,y]
				uid=uids[idx]
				info=bilibilimea.get_user_info_by_uid(uid,acceptable_time=3600*24*7)
				name=info.get('uname',None) or info.get('username','..我不知道')
				mod.comment_pic(p,'VUP识别','这个V叫做'+name)
		for idx,uid in enumerate(uids):
			info=bilibilimea.get_user_info_by_uid(uid,acceptable_time=3600*24*7)
			name=info.get('uname',None) or info.get('username','..我不知道')
			mod.comment_pic(avatars[idx],'VUP识别','这个V叫做'+name)