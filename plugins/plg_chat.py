from bot_backend import *
import jieba,traceback,myio
import random,chat
from glob import glob
from os import path
from threading import Lockpth=path.join(mainpth,'dialogs')
dialogs=chat.dialogs.fromJsons(glob(path.join(pth,'*.json')))
def reload_dialogs():
	global dialogs
	dialogs=chat.dialogs.fromJsons(glob(path.join(pth,'*.json')))
	dialogs.initial_keyword_filt_accelerate()
dlgs_by_gid={}
repeat_mode=myhash.splitedDict(pth=path.join(mainpth,'saves','repeat_mode'),splitMethod=lambda x:str(x)[:3])
repeat_mode_enum={'ignore','normal'}
@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?重载对话')
def cmd_reload_dialogs(ctx):
	if(ctx.user_id not in ['402254524',402254524]):
		simple_send(ctx,'您没有权限！！')
		return
	reload_dialogs()
@receiver
@threading_cnt('更改复读模式')
@on_exception_send
@start_with('[!！/]?repeat_mode')
def cmd_repeat_mode(ctx,match,rest_text):
	sctx=simple_ctx(ctx)
	gid=sctx.group_id
	mode=rest_text.strip()
	if(mode not in repeat_mode_enum):
		simple_send(ctx,'复读模式必须为%s中的一个'%repeat_mode_enum)
	else:
		repeat_mode[gid]=mode
	simple_send(ctx,'复读模式现在为%s'%repeat_mode[gid])
dlgs_by_gid_lck=Lock()
def glob_exts(pth,exts):
	ret=[]
	for i in exts:
		#ret+=list(glob(pth+'\\*.'+i))
		ret+=list(glob(path.join(pth,"*."+i)))
	return ret
@timing("根据记录生成对话")
def get_dlgs_by_gid(gid):
	global dlgs_by_gid,dlgs_by_gid_lck
	
	try:
		if(len(dlgs_by_gid)>20):
			dlgs_by_gid.pop(list(dlgs_by_gid)[0])
		if(gid in dlgs_by_gid):
			return dlgs_by_gid[gid]
		else:
			pth=path.join(mainpth,'saves','message_record','%s.log'%gid)
			pths=list(glob(path.join(mainpth,'saves','message_record','*.log')))
			if(len(pths)>3):
				pths=random.sample(pths,3)
			dlgs_by_gid[gid]=chat.dialogs.fromTXT([pth]+pths)
			dlgs_by_gid[gid].initial_keyword_filt_accelerate()
			#dlgs_by_gid[gid].initial_keyword_filt_accelerate()
			return dlgs_by_gid[gid]
	except Exception:
		myio.savetext(path.join(mainpth,'logs','get_dlgs_by_gid_%s.log'%gid),traceback.format_exc()+'\n%s'%([pth]+pths))
		pass
def dialog2mes(dlg):
	ret=[]
	#print('line11',not dlg.voice_only,dlg.reply_text)
	
	if((not dlg.voice_only)and(dlg.reply_text)):
		ret.append(dlg.reply_text)
	if(dlg.reply_voice):
		_=list(glob(path.join(mainpth,'dialogs','voice',dlg.reply_voice+'*.mp3')))
		_+=list(glob(path.join(mainpth,'dialogs','voice',dlg.reply_voice+'*.wav')))
		_+=list(glob(path.join(mainpth,'dialogs','voice',dlg.reply_voice+'*.ogg')))
		if(_):
			ret.append(random.choice(_))
	if(dlg.reply_picture):
		_=list(glob(path.join(mainpth,'dialogs','picture',dlg.reply_picture+'*.jpg')))
		_+=list(glob(path.join(mainpth,'dialogs','picture',dlg.reply_picture+'*.gif')))
		_+=list(glob(path.join(mainpth,'dialogs','picture',dlg.reply_picture+'*.png')))
		if(_):
			ret.append(random.choice(_))
	return ret
recent_reply=None
def chat_to_me(ctx):
	global recent_reply
	tmr=receiver_timer('reply to me')
	sctx=simple_ctx(ctx)
	#user_id=sctx.user_id
	group_id=sctx.group_id
	mes_text=sctx.trim_ated_text.strip()
	rep=dialogs.getReply(mes_text)
	temp=['/ar','/dr','/rr']
	for _ in temp:
		if(_ in mes_text):
			tmr.finish()
			return
	if(rep):
		recent_reply=rep
	_=(not rep) and (random.random()<0.9)
	__=random.random()<0.05
	if(_ or __):
		rep1=get_dlgs_by_gid(group_id).getReply(mes_text)
		if(rep1):
			rep=rep1
	if(rep):
		mes=dialog2mes(rep.dialog)
		print(mes)
		print(rep.dialog)
		simple_send(ctx,mes)
	else:
		if(random.random()<0.5):
			if(random.random()<0.5):
				_=glob_exts(path.join(mainpth,'随机表情'),['png','gif','jpg','bmp'])
				if(not(_)):
					_=glob_exts(path.join(mainpth,'dialogs','voice'),['wav','mp3','ogg'])
			else:
				from bot_backend import pic_cnt,lcg_eternal
				_=plugins['plg_facegen'].sample_by_cnt(pic_cnt,80)
				_=lcg_eternal.get_path(_[1])
				_=fix_img_ext(_)
				_=[_]
		else:
			_=glob_exts(path.join(mainpth,'dialogs','voice'),['wav','mp3','ogg'])
		simple_send(ctx,[random.choice(_)])
	tmr.finish()
@receiver
@threading_cnt('应答对话')
@to_me
@on_exception_send
def func_chat(ctx):
	chat_to_me(ctx)
mes_recording_buff={}
repeat_cnt={}
active_rate=myhash.splitedDict(pth=path.join(mainpth,'saves','active_rate'),splitMethod=lambda x:str(x)[:3])
@receiver
@threading_cnt('active_rate')
@on_exception_send
@start_with('[!！/]?active_rate|[!！/]主动发言概率')
def cmd_active_rate(ctx,match,rest):
	try:
		if(rest!='inf'):
			rate=float(rest)
		if(rate>0.334):
			simple_send(ctx,'频率太高了')
			return
		if(rate<=0 or rate>=1):
			simple_send(ctx,'奇怪的数字')
			return
	except Exception as e:
		simple_send(ctx,'奇怪的数字')
		return
	sctx=simple_ctx(ctx)
	group_id=sctx.group_id
	active_rate[group_id]=rate
	simple_send(ctx,'设置好咯')
@receiver
@threading_cnt('写入聊天记录')
def record_message(ctx):
	try:
		sctx=simple_ctx(ctx)
		gid,uid,text=sctx.group_id,sctx.user_id,sctx.text
		text=text.replace('\r','\n').replace('\n\n','\n').strip('\n')
		if(not(text)):
			return
		repeat_cnt[gid]=repeat_cnt.get(gid,{})
		repeat_cnt[gid][text]=repeat_cnt[gid].get(text,0)+1
		_=active_rate.get(gid,0.03)
		_=_**(1/repeat_cnt[gid][text])
		
		print('chat line108',repeat_cnt[gid][text],_)
		if(random.random()<_ and not sctx.ated):
			print('ln176')
			repeat_cnt[gid][text]=0
			if(repeat_mode.get(gid,'normal')=='normal'):
				print('ln179')
				chat_to_me(ctx)
		if(len(repeat_cnt[gid])>20):
			temp=random.sample(list(repeat_cnt[gid]),10)
			for i in temp:
				repeat_cnt[gid].pop(i,None)
		mes_recording_buff[gid]=mes_recording_buff.get(gid,'')
		mes_recording_buff[gid]+=text.strip('\n\r')+'\n'
		tmr=receiver_timer('record message')
		if(len(mes_recording_buff[gid])>500):
			tmr1=receiver_timer('save record message')
			pth=path.join(mainpth,'saves','message_record','%s.log'%gid)
			if(path.exists(pth)):
				f=open(pth,'rb')
				tot=f.read().decode('utf-8',errors='ignore')
				f.close()
			else:
				tot=''
			tot+=mes_recording_buff[gid]
			mes_recording_buff[gid]=''
			if(len(tot)>124288):
				tot=tot[-124288:]
			myio.savetext(pth,tot)
			tmr1.finish()
		tmr.finish()
	except Exception as e:
		myio.savetext(path.join(mainpth,'logs','record_message exception.log'),traceback.format_exc())