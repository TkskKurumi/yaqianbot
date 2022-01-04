from bot_backend import *
from check_in import check_in as check_in_manager
from os import path
import myio,random,pic2pic,myhash
import numpy as np
from lcg import lcg as lcg_
from PIL import Image,ImageDraw
from myRenderer import renderer
from threading import Lock

plugin_name_n='签到'
def report_status():
	ret=[]
	ret.append('“/签到”   签到')
	ret.append('“/状态”   查看好感度和财布点')
	return ret
lcg=lcg_()
check_in_mgrs={}
config={
	"emotion_level":
		[
			[0,"陌生人","你"],
			[10,"朋友","你"],
			[25,"挚友","你"],
		]
}
file_pth=path.dirname(__file__)
def reload_config():
	global config,check_in_mgrs
	if(path.exists(path.join(file_pth,'plg_checkin_configs.json'))):
		config=myio.loadjson(path.join(file_pth,'plg_checkin_configs.json'))
	else:
		config={}
	check_in_mgrs={}
reload_config()
workpth=path.join(mainpth,'saves','check_in_save')

def getEmotionLevelIdx(e):
	i=0
	el=config['emotion_level']
	while(e>=el[i+1][0]):
		i+=1
	return i
def getEmotionLevel(e):
	i=0
	el=config['emotion_level']
	while(e>=el[i+1][0]):
		i+=1
	return el[i]
def getEmotionLevelName(e):
	return getEmotionLevel(e)[1]
def getEmotionLevelAppellation(e):
	return getEmotionLevel(e)[2]

def get_random_bg_image(ctx=None):
	try:
		return Image.open(plugins['plg_setu'].rand_img(ctx=ctx))
	except Exception:
		return Image.new("RGB",(512,512),(127,127,127))

def get_check_in_mgr(group_id):
	if(group_id in check_in_mgrs):
		return check_in_mgrs[group_id]
	else:
		ret=check_in_manager(savepath=path.join(workpth,'check_in','%s.json'%group_id))
		check_in_mgrs[group_id]=ret
		return ret

coin_lock=Lock()
coins=myhash.splitedDict(pth=path.join(workpth,'coin_save'),splitMethod=lambda x:str(x)[:3])
emotions=myhash.splitedDict(pth=path.join(workpth,'emotion_save'),splitMethod=lambda x:str(x)[:3])
def get_coin(group_id,user_id):
	#coin_lock.acquire()
	#pth=path.join(workpth,'coin','%s.json'%group_id)
	j=coins.get(group_id,{})
	return j.get(user_id,0)
	
def gain_coin(group_id,user_id,n):
	
	j=coins.get(group_id,{})
	j[user_id]=j.get(user_id,0)+n
	coins[group_id]=j
	return j[user_id]
def cost_coin(group_id,user_id,n):
	#coin_lock.acquire()
	j=coins.get(group_id,{})
	j[user_id]=j.get(user_id,0)-n
	coins[group_id]=j
	return j[user_id]

def afford_coin(group_id,user_id,n):
	#coin_lock.acquire()
	return get_coin(group_id,user_id)>=n

def get_emotion(group_id,user_id):
	j=emotions.get(group_id,{})
	return j.get(user_id,0)
	
def gain_emotion(group_id,user_id,n):
	
	j=emotions.get(group_id,{})
	j[user_id]=j.get(user_id,0)+n
	emotions[group_id]=j
	return j[user_id]
def calc_checkin_coin_gain():
	global config
	a=config.get('checkin_coin_gain_min',5)
	b=config.get('checkin_coin_gain_min',15)
	return a+(b-a)*random.random()

def calc_checkin_emotion_gain():
	global config
	a=config.get('checkin_coin_gain_min',5)
	b=config.get('checkin_coin_gain_min',5)
	return a+(b-a)*random.random()

def get_coin_name():
	return config.get('coin_name','财布点')
def coin_name():
	return get_coin_name()
def get_emotion_name():
	return config.get('emotion_name','好感度')
def get_coin_measure():
	return config.get('coin_measure','点')
def wrap_coin_statement(n):
	return "%.1f%s%s"%(n,get_coin_measure(),get_coin_name())
def wrap_emotion_statement(n):
	return "%.1f点%s"%(n,get_emotion_name())
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?签到')
def check_in(ctx,match,rest_text):
	sctx=simple_ctx(ctx)
	group_id=str(sctx.group_id)
	user_id=str(sctx.user_id)
	cinmgr=get_check_in_mgr(group_id)
	ret=cinmgr.check_in(str(user_id))
	
	
	
	if(ret):
		cg=calc_checkin_coin_gain()
		eg=calc_checkin_emotion_gain()
		c=gain_coin(group_id,user_id,cg)
		e=gain_emotion(group_id,user_id,eg)
		prof_pic=get_profile_pic(ctx,coin_delta=cg,emotion_delta=eg)
		#simple_send(ctx,'签！！！\n您有%s和%s'%(wrap_coin_statement(c),wrap_emotion_statement(e)))
		
		simple_send(ctx,prof_pic)
	else:
		c=get_coin(group_id,user_id)
		e=get_emotion(group_id,user_id)
		prof_pic=get_profile_pic(ctx=ctx,extra_title='您已经签过到了')
		simple_send(ctx,prof_pic)
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?状态')
def check_in_status(ctx,match,rest_text):
	tmr=receiver_timer('状态')
	sctx=simple_ctx(ctx)
	group_id=str(sctx.group_id)
	user_id=str(sctx.user_id)
	c=get_coin(group_id,user_id)
	e=get_emotion(group_id,user_id)
	prof_pic=get_profile_pic(ctx)
	simple_send(ctx,prof_pic)
	tmr.finish()
def get_profile_pic(ctx=None,coin_delta=None,emotion_delta=None,extra_title=None,fix_avatar=None,auto_color=True,bgImage=None):
	if(ctx is None):
		group_id='1126809443'
		user_id='402254524'
		#user_id="515479347"
		username="千"
	else:
		sctx=simple_ctx(ctx)
		group_id=str(sctx.group_id)
		user_id=str(sctx.user_id)
		username=sctx.user_name
	if(coin_delta is not None):
		if(coin_delta>0):
			coin_delta="(+%.1f)"%coin_delta
		elif(coin_delta<0):
			coin_delta="(%.1f)"%coin_delta
	if(emotion_delta is not None):
		if(emotion_delta>0):
			emotion_delta="(+%.2f)"%emotion_delta
		elif(emotion_delta<0):
			emotion_delta="(%.2f)"%emotion_delta
			
	res=(930,300)
	width,height=res
	border=res[1]//20
	avt_size=res[1]-border*2
	coin_name=get_coin_name()
	emotion_name=get_emotion_name()
	avatar=(fix_avatar or lcg.get_image(r'https://q.qlogo.cn/headimg_dl?bs=qq&dst_uin=%s&spec=0'%user_id,proxies={})).resize((avt_size,avt_size))
	co=get_coin(group_id,user_id)
	em=get_emotion(group_id,user_id)
	emlvl=getEmotionLevelIdx(em)
	em_level_name=config['emotion_level'][emlvl][1]
	em_next=config['emotion_level'][emlvl+1][0]
	emlvlname=getEmotionLevelName(em)
	em_progress=em/em_next
	print('em_progress',em_progress,'em',em,'em_next',em_next)
	if(auto_color):
		bg_color1=pic2pic.get_main_color(avatar)
		bg_color1=pic2pic.RGB2HSV(*bg_color1)
		H,S,V=bg_color1
		H=int(H+18)%360
		if(S>15):
			bg_color=np.array(pic2pic.ImageColor.getrgb("hsv(%d,72%%,90%%)"%H))
		else:
			bg_color=np.array(pic2pic.ImageColor.getrgb("hsv(%d,%d%%,62%%)"%(H,S)))
		#print(H,bg_color,bg_color1)
	else:
		bg_color=np.array([11,140,185])
	bg_color_dark=(bg_color/2).astype('int32')
	bg_color_bright=((bg_color+255*3)/4).astype('int32')
	font_color1=((bg_color+255*6)/7).astype('int32')
	bg_color=tuple(bg_color)
	bg_color_dark=tuple(bg_color_dark)
	bg_color_bright=tuple(bg_color_bright)
	font_color1=tuple(font_color1)
	saifu_color=(255,255,170)
	emotion_color=np.array([255,86,140])
	emotion_color_dark=tuple((emotion_color/6).astype('int32'))
	emotion_color_bright=tuple(((emotion_color+255*3)/4).astype('int32'))
	emotion_color=tuple(emotion_color)
	
	
	
	border1=res[1]//24
	border_emotion_progress=int(border1/2)
	username_rate=1.73
	txt_height_username=int((height-border*2-border1*5)/(3+username_rate)*username_rate)
	txt_height=int((height-border*2-border1*5)/(3+username_rate))
	txt_name_pos=(border+avatar.size[0]+border1,border+border1)
	name_left,name_top=txt_name_pos
	
	
	#circle_mask=Image.open(mainpth+r'\static_pics\circle_mask.png').resize((avt_size,avt_size))
	#saifu_mask=Image.open(mainpth+r'\static_pics\check_in_saifu_mask.png').resize((txt_height,txt_height))
	#pic_emotion=Image.open(mainpth+r'\static_pics\check_in_emotion.png').resize((txt_height,txt_height))
	if(username):
		try:
			iUsername=pic2pic.txt2im(username,fill=font_color1,fixedHeight=txt_height_username)
		except Exception:
			iUsername=Image.new("RGBA",(1,txt_height_username))
	else:
		iUsername=Image.new("RGBA",(1,txt_height_username))
	i_saifu=pic2pic.txt2im("%s:"%coin_name,fill=font_color1,fixedHeight=txt_height)
	pic_emotion_name=pic2pic.txt2im("%s:"%emotion_name,fill=font_color1,fixedHeight=txt_height)
	pic_emotion_progress_indication=pic2pic.txt2im("%s进度"%emotion_name,fill=emotion_color_dark,fixedHeight=txt_height-border_emotion_progress*2,bg=emotion_color_bright)
	pic_emotion_progress=pic2pic.txt2im("%.2f/%d"%(em,em_next),fill=emotion_color_bright,fixedHeight=txt_height-border_emotion_progress*4)
	pic_emotion_next=pic2pic.txt2im("%s->%s"%(config['emotion_level'][emlvl][1],config['emotion_level'][emlvl+1][1]),fill=emotion_color_bright,fixedHeight=txt_height-border_emotion_progress*4)
	pic_saifu_count=pic2pic.txt2im(("%.1f"%co)+(coin_delta if coin_delta else ""),fill=bg_color_bright,fixedHeight=txt_height)
	pic_em_lvl=pic2pic.txt2im(("%s"%em_level_name)+(emotion_delta if emotion_delta else ""),fill=bg_color_bright,fixedHeight=txt_height)
	
	progress_bar_left=name_left+pic_emotion_progress_indication.size[0]+border_emotion_progress*2
	progress_bar_right=width-border-border1-border_emotion_progress
	progress_bar_top=name_top+txt_height*2+border1*3+txt_height_username+border_emotion_progress
	progress_bar_lower=height-border-border1-border_emotion_progress
	progress_bar_mid=int(progress_bar_left*(1-em_progress)+progress_bar_right*em_progress)
	
	ret=Image.new("RGB",res,bg_color_bright)
	if(not(bgImage)):
		'''d.rectangle((border,border,width-border,height-border),fill=bg_color_dark)'''
		bgImage=get_random_bg_image(ctx)
	if(bgImage):
		bgImage_B=pic2pic.imBanner(bgImage,(res[0]-border*2,res[1]-border*2)).convert("RGBA")
		bgImage_A=Image.new("RGBA",bgImage_B.size,(*bg_color_dark,120))
		ret.paste(Image.alpha_composite(bgImage_B,bgImage_A),(border,border))
	ret1=Image.new("RGBA",res,(0,0,0,0))
	d=ImageDraw.Draw(ret)
	
	d.rectangle((name_left,progress_bar_top-border_emotion_progress,width-border-border1,height-border-border1),fill=emotion_color_bright)
	d.rectangle((progress_bar_left,progress_bar_top,progress_bar_mid,progress_bar_lower),fill=emotion_color)
	d.rectangle((progress_bar_mid,progress_bar_top,progress_bar_right,progress_bar_lower),fill=emotion_color_dark)
	
	avatar=pic2pic.circle_mask_RGBA(avatar)
	ret.paste(avatar,(border,border),avatar)
	
	ret1.paste(iUsername,txt_name_pos)

	saifu=pic2pic.txt2im('￥',fill=saifu_color,bg=(0,0,0,0)).resize((txt_height,txt_height))
	ret.paste(saifu,(txt_name_pos[0],txt_name_pos[1]+txt_height_username+border1),saifu)
	ret1.paste(pic2pic.txt2im('❤',fill=(255,86,140),bg=(0,)*4).resize((txt_height,txt_height)),(name_left,name_top+txt_height_username+border1*2+txt_height))
	ret1.paste(i_saifu,(name_left+txt_height+border1,name_top+txt_height_username+border1))
	ret1.paste(pic_saifu_count,(width-border-border1-pic_saifu_count.size[0],name_top+txt_height_username+border1))
	ret1.paste(pic_emotion_name,(name_left+txt_height+border1,name_top+txt_height_username+border1*2+txt_height))
	ret1.paste(pic_em_lvl,(width-border-border1-pic_em_lvl.size[0],name_top+txt_height_username+border1*2+txt_height))
	ret.paste(pic_emotion_progress_indication,(name_left+border_emotion_progress,name_top+txt_height*2+border1*3+txt_height_username+border_emotion_progress))
	ret1.paste(pic_emotion_progress,(progress_bar_left+border_emotion_progress,progress_bar_top+border_emotion_progress))
	ret1.paste(pic_emotion_next,(progress_bar_right-border_emotion_progress-pic_emotion_next.size[0],progress_bar_top+border_emotion_progress))
	
	
	ret=Image.alpha_composite(ret.convert("RGBA"),ret1)
	if(extra_title):
		#ret.show()
		imTitle=renderer(type='verticle',bg=bg_color_dark,border={'type':renderer.border_type_absolute,"width":border,"color":bg_color_bright},contents_gap=border1,fill=bg_color_bright,align_contents_size=False)
		imTitle.add_content(pic2pic.txt2im(extra_title,bg=bg_color_dark,fill=bg_color_bright,fixedHeight=txt_height))
		imTitle.align_contents_pos[0]=0.5
		imTitle.add_content(ret.crop((border,border,ret.size[0]-border,ret.size[1]-border)))
		imTitle=imTitle.render()
		return imTitle
		
	return ret
