from os import path
from glob import glob
import random,arcaea_crawler,myhash,pic2pic
from bot_backend import *
qqid2arcid=myhash.splitedDict(pth=path.join(mainpth,'saves','qqid2arcid'),splitMethod=lambda x:str(x)[:3])
yy_fortune_mem=myhash.splitedDict(pth=path.join(mainpth,'saves','yy_fortune_mem'),splitMethod=lambda x:str(x)[:3])
plugin_name_n='Arcaea'
def report_status():
	ret=[]
	ret.append('“/arc”   查看最近打歌')
	ret.append('“/arc查分 歌名”   查看歌曲FTR成绩')
	ret.append('“/arc查分 歌名 [BYD|FTR|PRS|PST]”   查看歌曲成绩')
	ret.append('“/arc_set 好友码”   绑定自己的好友码')
	ret.append('“/b30”   查看best30')
	return ret
@receiver
@threading_cnt('Arcaea最近成绩')
@on_exception_send
@start_with('[/!！]?arc')
def arc_recent(ctx,match,rest):
	
	sctx=simple_ctx(ctx)
	if(('arc_set' in sctx.text) or ('arc查歌' in sctx.text)):
		return
	uid=sctx.user_id
	if(rest.strip() and rest.strip().isnumeric()):
		arc_id=rest.strip()
	elif(uid in qqid2arcid):
		arc_id=qqid2arcid[uid]
	elif(sctx.atid):
		if(str(atid[0])in qqid2arcid):
			arc_id=qqid2arcid[str(atid[0])]
		else:
			simple_send(ctx,'我还不知道他的好友码呐！')
			return
	else:
		simple_send(ctx,'未知您的Arcaea好友码啊！！！\n输入arc_set 好友码绑定')
		#simple_send(ctx,str(qqid2arcid.toDict()))
		return
	if(len(arc_id)!=9):
		simple_send(ctx,'好友码难道不是应该是⑨位数字吗？？？')
		return
	ret=arcaea_crawler.illust_user_info(arc_id)
	simple_send(ctx,ret)
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?arc_set')
def arc_set(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	arc_id=rest.strip()
	if(len(arc_id)!=9 or not arc_id.isnumeric()):
		simple_send(ctx,'好友码难道不是应该是⑨位数字吗？？？')
		return
	qqid2arcid[uid]=arc_id
	simple_send(ctx,'绑定成功啦！！')
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?b30')
def arc_b30(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	if(rest.strip() and rest.strip().isnumeric()):
		arc_id=rest.strip()
	elif(uid in qqid2arcid):
		arc_id=qqid2arcid[uid]
	elif(sctx.atid):
		if(str(atid[0])in qqid2arcid):
			arc_id=qqid2arcid[str(atid[0])]
		else:
			simple_send(ctx,'我还不知道他的好友码呐！')
			return
	else:
		simple_send(ctx,'未知您的Arcaea好友码啊！！！\n输入arc_set 好友码绑定')
		#simple_send(ctx,str(qqid2arcid.toDict()))
		return
	song_title,uinfo,scores=arcaea_crawler._query(arc_id)
	ret=[]
	for idx,i in enumerate(scores[:min(30,len(scores))]):
		ret.append(arcaea_crawler.illust_score(i,line4='BEST%d'%(idx+1)))
	ret=pic2pic.picMatrix(ret,column_num=1,border=0,bg=(0,)*4)
	w,h=ret.size
	bg=arcaea_crawler.generate_bg_by_partner(uinfo['character'],w,h)
	ret=Image.alpha_composite(bg,ret).convert("RGB")
	simple_send(ctx,ret,im_size_limit=1<<21,img_type="JPEG")
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?arc查歌|[/!！]?arc查分')
def arc_query_song(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	if(uid in qqid2arcid):
		arc_id=qqid2arcid[uid]
	elif(sctx.atid):
		if(str(atid[0])in qqid2arcid):
			arc_id=qqid2arcid[str(atid[0])]
		else:
			simple_send(ctx,'我还不知道他的好友码呐！')
			return
	else:
		simple_send(ctx,'未知您的Arcaea好友码啊！！！\n输入arc_set 好友码绑定')
		return
	name=rest.strip()
	if(not(name)):
		simple_send(session,"没有输入歌名啊！！")
		return None
	difficulty=2
	for diff_int,diff_str in enumerate(['[PST]','[PRS]','[FTR]','[BYD]']):
		if(diff_str in name):
			name=name.replace(diff_str,'').strip()
			difficulty=diff_int
	_,uinfo,scores=arcaea_crawler._query(arc_id)
	sid=arcaea_crawler.fuzzy_search_song(name)[0][-1]
	temp=None
	for i in scores:
		if(i['song_id']==sid and i['difficulty']==difficulty):
			ret=arcaea_crawler.illust_user_info(arc_id,show_score=i)
			simple_send(ctx,ret)
			return None
		elif(i['song_id']==sid):
			temp=arcaea_crawler.illust_user_info(arc_id,show_score=i)
	if(temp):
		simple_send(ctx,temp)
	else:
		simple_send(ctx,'？？没有找到成绩')
	
	