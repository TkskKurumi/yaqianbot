from bot_backend import *
from myjobs import jobs
import jieba,traceback,myio,myhash
import random,chat,pic2pic
from glob import glob
from os import path
import shutil
plg_chat=get_plugin_namespace('plg_chat')
shown_rep=None
pending=myhash.splitedDict(pth=path.join(mainpth,'saves','pending_custom_dialogs'),splitMethod=lambda x:str(x)[:3])
def show_rep(ctx,rep):
	if(rep is None):
		simple_send(ctx,'rep is None')
		return
	mes_rep=plg_chat.dialog2mes(rep.dialog)
	mes_ask=rep.dialog.ask_key_text
	simple_send(ctx,['实际的问句:',rep.ask_text,'设定的问句:',mes_ask,'答:']+mes_rep)
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]rr')
def show_recent_reply(ctx,match,rest):
	if(not is_su(ctx)):
		simple_send(ctx,'您无权调整应答呀')
		return
	global shown_rep
	shown_rep=plg_chat.recent_reply
	show_rep(ctx,shown_rep)
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]ar')
def approve_reply(ctx,match,rest):
	if(rest):
		return
	global shown_rep
	sctx=simple_ctx(ctx)
	#if(sctx.user_id!='402254524'):
	if(not is_su(ctx)):
		simple_send(ctx,'您无权调整应答呀')
		return
	if(shown_rep is not None):
		r0=shown_rep.relavance[0]
		# r1=r0*0.7
		# r1=min((r1**0.8)*(shown_rep.dialog.eps**0.2),r1)
		shown_rep.suggest_relavance(r0*2)
		shown_rep=plg_chat.dialogs.getReply(shown_rep.ask_text)
		if(shown_rep):
			show_rep(ctx,shown_rep)
		else:
			simple_send(ctx,'调整后没有应答哒！')
	else:
		simple_send(ctx,'rep is None')
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]dr')
def disapprove_reply(ctx,match,rest):
	global shown_rep
	sctx=simple_ctx(ctx)
	#if(sctx.user_id!='402254524'):
	if(not is_su(ctx)):
		simple_send(ctx,'您无权调整应答呀')
		return
	if(shown_rep is not None):
		r0=shown_rep.relavance[0]
		r1=r0*0.3
		r1=min((r1**0.8)*(shown_rep.dialog.eps**0.2),r1)
		shown_rep.suggest_relavance(r1)
		shown_rep=plg_chat.dialogs.getReply(shown_rep.ask_text)
		if(shown_rep):
			show_rep(ctx,shown_rep)
		else:
			simple_send(ctx,'调整后没有应答哒！')
	else:
		simple_send(ctx,'rep is None')

shown_pending=None
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]审核问答')
def audit_custom_reply(ctx,match,rest):
	global shown_pending
	sctx=simple_ctx(ctx)
	#if(sctx.user_id not in['402254524']):
	if(not is_su(ctx)):
		simple_send(ctx,'你没有权限审核问答呐！！！！')
		return
	ls=list(pending.toDict())
	if(not(ls)):
		simple_send(ctx,'没有需要审核的条目')
		return
	shown_pending=random.choice(ls)
	send_pending(ctx,pending[shown_pending])
	
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]问答OK')
def audit_custom_reply_ok(ctx,match,rest):
	global shown_pending
	sctx=simple_ctx(ctx)
	if(not is_su(ctx)):
	#if(sctx.user_id not in['402254524']):
		simple_send(ctx,'你没有权限审核问答呐！！！！')
		return
	if(not shown_pending):
		simple_send(ctx,'还没有查看要审核的问答呐！')
		return
	svpth=path.join(mainpth,'dialogs','custom_%d.json'%random.randrange(10))
	if(path.exists(svpth)):
		_=myio.loadjson(svpth)
	else:
		_=[]
	dic=pending[shown_pending]
	simple_send(ctx,['ok',svpth])
	ctx_tuple=dic.pop('ctx_tuple')
	send_pending(None,dic,ctx_tuple=ctx_tuple,extra_info='通过啦！')
	if('reply_picture' in dic):
		bsname=path.basename(dic['reply_picture'])
		shutil.copyfile(dic['reply_picture'],path.join(mainpth,'dialogs','picture',bsname))
		dic['reply_picture']=path.splitext(bsname)[0]
	
	_.append(dic)
	myio.dumpjson(svpth,_)
	pending.pop(shown_pending)
	
	
	plg_chat.reload_dialogs()
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]问答不行')
def audit_custom_reply_ng(ctx,match,rest):
	global shown_pending
	sctx=simple_ctx(ctx)
	if(not is_su(ctx)):
	#if(sctx.user_id not in['402254524']):
		simple_send(ctx,'你没有权限审核问答呐！！！！')
		return
	if(not shown_pending):
		simple_send(ctx,'还没有查看要审核的问答呐！')
		return
	dic=pending[shown_pending]
	ctx_tuple=dic.pop('ctx_tuple')
	pending.pop(shown_pending)
	send_pending(None,dic,ctx_tuple=ctx_tuple,extra_info='⑧行')
	simple_send(ctx,'ng')
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]添加问答')
def add_custom_reply(ctx,match,rest):
	_=rest.strip().split(' ')
	#simple_send(ctx,','.join(_))
	ask=None
	rep=''
	ret={}
	with_pic=False
	for i in _:
		if(i in ['带图','with_pic']):
			with_pic=True
		else:
			if(ask is None):
				ask=i
			else:
				rep=i
	ret["ask_key_text"]=ask
	ret["reply_text"]=rep
	if(not ask):
		simple_send(ctx,'您没有输入触发问句呐！')
		return
	sctx=simple_ctx(ctx)
	if(with_pic):
		#ret['reply_picture']=fix_img_ext(lcg_l.get_path(sctx.rpics[0]['Url']))
		ret['reply_picture']=fix_img_ext(lcg_l.get_path(sctx.rpics[0][1]))
		_hash=myhash.hashs(ask+rep+ret['reply_picture'])
	else:
		_hash=myhash.hashs(ask+rep)
	ret['ctx_tuple']=('Friend',int(sctx.user_id),ctx.CurrentQQ)
	pending[_hash]=ret
	send_pending(ctx,ret)
def send_pending(ctx,dic,ctx_tuple=None,extra_info=''):
	mes=['问：%s\n答：%s'%(dic['ask_key_text'],dic['reply_text'])]
	if(extra_info):
		mes.append(extra_info)
	if('reply_picture' in dic):
		#pth=lcg_l.get_path(dic['reply_picture'])
		mes.append(dic['reply_picture'])
	simple_send(ctx,mes,ctx_tuple=ctx_tuple)

def test_gif(img):
	try:
		img.seek(1)
		return True
	except Exception:
		return False
def fix_img_ext(pth):
	img=Image.open(pth)
	bsname=path.splitext(path.basename(pth))[0]
	if(test_gif(img)):
		ext='.gif'
	elif(img.mode=='RGBA'):
		ext='.png'
	else:
		ext='.jpg'
	return shutil.copyfile(pth,path.join(mainpth,bsname+ext))