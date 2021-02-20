from bot_backend import *
from bot_backend import _bot
import simple_arg_parser,time,threading,shutil
from smart_db import saved_treap as treap
@receiver
@threading_cnt('设置群名片')
@on_exception_send
@start_with('[!！/]?set_card|[！!/]?设置群名片')
def cmd_set_card(ctx,match,rest):
	j=_bot.sync.get_group_member_info(self_id=ctx.self_id,user_id=ctx.self_id,group_id=ctx.group_id)
	role=j['role']
	if(role=='member'):
		simple_send(ctx,'QAQ菜菜没有权限给您设定群名片呜呜')
		return
	j=_bot.sync.get_group_member_info(self_id=ctx.self_id,user_id=ctx.user_id,group_id=ctx.group_id)
	'''if(not j['card_changeable']):
		simple_send(ctx,'设置了不允许他人更改群名片..(%s)'%j['card_changeable'])
		return'''
	en=simple_arg_parser.parse_args(rest.strip())
	card=en.get('default','').strip()
	suffix=en.get('suffix',None) or en.get('s',None)
	if(suffix):
		card+=chr(8238)+suffix.strip()[::-1]+chr(8237)
	_bot.sync.set_group_card(self_id=ctx.self_id,user_id=ctx.user_id,group_id=ctx.group_id,card=card)
	j1=_bot.sync.get_group_member_info(self_id=ctx.self_id,user_id=ctx.user_id,group_id=ctx.group_id,no_cache=True)
	if(j1['card']==card):
		simple_send(ctx,'似乎成功了..')
	else:
		simple_send(ctx,'似乎失败了..这是你想要的群名片..')
		simple_send(ctx,card)
@receiver
@threading_cnt('设置群名片')
@on_exception_send
@start_with('[!！/]?set_card|[！!/]?设置你的群名片')
def cmd_set_bot_card(ctx,match,rest):
	en=simple_arg_parser.parse_args(rest.strip())
	card=en.get('default','')
	suffix=en.get('suffix',None) or en.get('s',None)
	if(suffix):
		card+=chr(8238)+suffix.strip()[::-1]+chr(8237)
	_bot.sync.set_group_card(self_id=ctx.self_id,user_id=ctx.self_id,group_id=ctx.group_id,card=card)
	j1=_bot.sync.get_group_member_info(self_id=ctx.self_id,user_id=ctx.self_id,group_id=ctx.group_id,no_cache=True)
	if(j1['card']==card):
		simple_send(ctx,'似乎成功了..')
	else:
		simple_send(ctx,'似乎失败了..')
treaps={}
lck=threading.Lock()
lck1=threading.Lock()
def del_treap(name):
	pth=path.join(mainpth,'saves','mes_count_treaps',name)
	if(path.exists(pth)):
		try:
			if(path.exists(pth)):
				shutil.rmtree(pth)
		except Exception:
			pass
	treaps.pop(name,None)
def get_treap(name):
	lck.acquire()
	if(len(treaps)>500):
		enen=len(treaps)-500
		ls=[]
		for i in treaps:
			ls.append(i)
			enen-=1
			if(enen == 0):
				break
		for i in ls:
			treaps.pop(i)
	try:
		if(name in treaps):
			lck.release()
			return treaps[name]
		else:
			ret=treap(path.join(mainpth,'saves','mes_count_treaps',name))
			treaps[name]=ret
			lck.release()
			return ret
	except Exception as e:
		print(traceback.format_exc())
		pth=path.join(mainpth,'saves','mes_count_treaps',name)
		try:
			if(path.exists(pth)):
				shutil.rmtree(pth)
		except Exception:
			pass
		lck.release()
@receiver
@threading_cnt('发言计数')
def count_message(ctx):
	lck1.acquire()
	tmr=receiver_timer('发言计数')
	try:
		
		sctx=simple_ctx(ctx)
		group_id=sctx.group_id
		#simple_id=sctx.simple_id
		simple_id="%s_%s"%(sctx.group_id,sctx.user_id)
		tmtm=time.time()
		sttm=tmtm-24*3600*7
		try:
			user_cnt=get_treap(simple_id)
		
		
			old_cnt=user_cnt.size
			user_cnt[time.time()]=1
			en=[]
			for i in user_cnt:
				#print(i,user_cnt[i])
				if(i<sttm):
					en.append(i)
				else:
					break
			for i in en:
				user_cnt.pop(i)
			new_cnt=user_cnt.size
		except Exception as e:
			del_treap(simple_id)
			raise e
		try:
			grp_rank=get_treap(group_id)
			if([old_cnt,simple_id] in grp_rank):
				grp_rank.pop([old_cnt,simple_id])
			grp_rank[[new_cnt,simple_id]]=sctx.user_name
		except Exception as e:
			del_treap(group_id)
			raise e
		#lck1.release()
	except Exception as e:
		import traceback
		print(e,traceback.format_exc())
		print(simple_id,group_id)
	tmr.finish()
	lck1.release()
@receiver
@threading_cnt('发言排行')
@on_exception_send
@start_with('[!！/]?发言排行')
def cmd_mescnt_rank(ctx):
	lck1.acquire()
	try:
		sctx=simple_ctx(ctx)
		group_id=sctx.group_id
		grp_rank=get_treap(group_id)
		sz=grp_rank.size
		if(sz==0):
			simple_send(ctx,'啊咧咧？没有你群发言的计数情况耶？？')
		else:
			u=sz-1
			end=sz-10
			circles=[]
			sizes=[]
			while(u>0 and u>=end):
				idx=grp_rank.rank(u)
				key,value=grp_rank.key[idx],grp_rank.data[idx]
				cnt,sid=key
				username=value
				uid=sid.split('_')[1]
				avt=r'https://q.qlogo.cn/headimg_dl?bs=qq&dst_uin=%s&spec=0'%uid
				from bot_backend import lcg_eternal
				import pic2pic
				avt=lcg_eternal.get_image(avt)
				avt=pic2pic.circle_mask_RGBA(avt)
				txt='第%02d名\n%s,%d条'%(sz-u,username,cnt)
				txt=pic2pic.txt2im_ml(txt,fixedHeight=avt.size[0]//7,bg=(0,)*4,fill=(0,0,0,255),trim_width=True,width=avt.size[0]*2)
				siz=max(txt.size[0],avt.size[0]+txt.size[1])
				im=Image.new("RGBA",(siz,siz),(0,)*4)
				im.paste(avt,box=((siz-avt.size[0])//2,0))
				im.paste(txt,box=((siz-txt.size[0])//2,avt.size[1]))
				#im.save(r'D:\temp.png',"PNG")
				circles.append(im)
				
				sizes.append(0.95**(sz-u))
				u-=1
			import data_illustrate
			im=data_illustrate.circles(circles[:10],sizes[:10],512,512,bg=(255,)*4)
			simple_send(ctx,im)
	except Exception as e:
		simple_send(ctx,'出现了谜之错误%s'%e)
		import traceback
		print(traceback.format_exc())
		lck1.release()
	lck1.release()
