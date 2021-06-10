import numpy as np
from urllib.parse import urlencode
import websocket,mymath
import brotli,pic2pic,math
import json,re,random
import threading,time,myio

import asyncio,myhash
from os import path
from lcg import localCachingGeter
from PIL import Image,ImageFilter
from threading import Lock
from datetime import datetime
pth=path.dirname(__file__)

lcg_l=localCachingGeter(workpth=path.join(pth,'arcaea_cache','long'),expiretime=864000,connection_throttle=(25,1),proxies={})

lcg_s=localCachingGeter(workpth=path.join(pth,'arcaea_cache','short'),expiretime=60,connection_throttle=(25,1),proxies={})


def get_wiki_image(url,quality='full'):
	if(url[:4]!='http'):
		url='https://wiki.arcaea.cn'+url
	text=lcg_l.gettext(url)
	#myio.savetext(r'C:\temp\temp_arc_wiki_img.html',text)
	if(quality=='full'):
		url=url[:url.find('/index')]+re.findall(r'<div class="fullMedia"><p><a href="(.+?)"',text)[0]
	#myio.savetext(r'C:\temp\temp_arc_wiki_url.txt',url)
	return lcg_l.get_image(url)

def init_partner_info_from_wiki():
	global partner_info
	url=r'https://wiki.arcaea.cn/index.php/%E6%90%AD%E6%A1%A3'
	text=lcg_s.gettext(url)
	myio.savetext(path.join(pth,'arcaea_cache','wiki_patner_info.html'),text)
	#temp=re.findall(r'<td><a href="(/index.php/[\s\S]+?)" title="([\s\S]+?)">[\s\S]+?</a></td>',text[text.find('<h2><span id="搭档数据简表">'):])
	temp=re.findall(r'<td data-sort-value="\d+?"[\s\S]*?>\d+?</td>\s+?<td[\s\S]*?><a href="(/index.php/.+?)" title="[\s\S]+?">([\s\S]+?)</a></td>\s+?<td[\s\S]*?>...</td>',text)
	if(not temp):
		print('no patner info')
		myio.savetext(path.join(pth,'arcaea_cache','wiki_patner_info.html'),text)
	partner_info=[None]
	for _,__ in enumerate(temp):
		_ret={}
		#_ret['html']=__
		_ret['url']=__[0]
		_ret['name']=__[1].replace("&amp;","&")
		partner_info.append(_ret)
	#myio.savetext(r"C:\temp\temp%d.text"%_,__)
	partner_info[0]=time.time()+3600*24*30
	myio.dumpjson(path.join(pth,'arcaea_saves','partners.json'),partner_info)
if(path.exists(path.join(pth,'arcaea_saves','partners.json'))):
	partner_info=myio.loadjson(path.join(pth,'arcaea_saves','partners.json'))
	if(partner_info[0]<time.time()):
		init_partner_info_from_wiki()
else:
	init_partner_info_from_wiki()



clear_list = ['Track Lost', 'Normal Clear', 'Full Recall', 'Pure Memory', 'Easy Clear', 'Hard Clear']
diff_list = ['PST', 'PRS', 'FTR', 'BYD']
'''
f = open('arc_namecache.txt', 'w')
f.close()


def load_cache():
	cache = {}
	f = open('arc_namecache.txt', 'r')
	for line in f.readlines():
		ls = line.replace('\n', '').split(' ')
		cache[ls[0]] = ls[1]
	f.close()
	return cache


def put_cache(d: dict):
	f = open('arc_namecache.txt', 'w')
	for key in d:
		f.write('%s %s\n' % (key, d[key]))'''


def cmp(a):
	return a['rating']


def calc(ptt, s):
	brating = 0
	for i in range(0, 30):
		try:
			brating += s[i]['rating']
		except IndexError:
			break
	brating /= 30
	rrating = 4 * (ptt - brating * 0.75)
	return brating, rrating

calc_b_r=calc
def lookup(nickname: str):
	ws = websocket.create_connection("wss://arc.estertion.win:616/")
	ws.send("lookup " + nickname)
	buffer = ""
	while buffer != "bye":
		buffer = ws.recv()
		if type(buffer) == type(b''):
			obj2 = json.loads(str(brotli.decompress(buffer), encoding='utf-8'))
			id = obj2['data'][0]['code']
			cache = load_cache()
			cache[nickname] = id
			put_cache(cache)
			return id

def query(id: str):
	s = ""
	song_title, userinfo, scores = _query(id)
	b, r = calc(userinfo['rating'] / 100, scores)
	s += "Player: %s\nPotential: %.2f\nBest 30: %.5f\nRecent Top 10: %.5f\n\n" % (userinfo['name'], userinfo['rating'] / 100, b, r)
	score = userinfo['recent_score'][0]
	s += "Recent Play: \n%s  %s %.1f  \n%s\nPure: %d(%d)\nFar: %d\nLost: %d\nScore: %d\nRating: %.2f" % (song_title[score['song_id']]['en'], diff_list[score['difficulty']], score['constant'], clear_list[score['clear_type']],
			  score["perfect_count"], score["shiny_perfect_count"], score["near_count"], score["miss_count"], score["score"], score["rating"])
	return s


def best(id: str, num: int):
	if num < 1:
		return []
	result = []
	s = ""
	song_title, userinfo, scores = _query(id)
	s += "%s's Top %d Songs:\n" % (userinfo['name'], num)
	for j in range(0, int((num - 1) / 15) + 1):
		for i in range(15 * j, 15 * (j + 1)):
			if i >= num:
				break
			try:
				score = scores[i]
			except IndexError:
				break
			s += "#%d  %s  %s %.1f  \n\t%s\n\tPure: %d(%d)\n\tFar: %d\n\tLost: %d\n\tScore: %d\n\tRating: %.2f\n" % (i+1, song_title[score['song_id']]['en'], diff_list[score['difficulty']], score['constant'], clear_list[score['clear_type']],
				  score["perfect_count"], score["shiny_perfect_count"], score["near_count"], score["miss_count"], score["score"], score["rating"])
		result.append(s[:-1])
		s = ""
	return result
_query_cache=myhash.splitedDict(pth=path.join(path.dirname(__file__),'arcaea_saves'),splitMethod=lambda x:x[:3])
_query_cache_lock={}
song_id2title={}
song_title2id={}
def _query(id: str,acceptable_time=120):
	global song_id2title,song_title2id
	lck=_query_cache_lock.get(id,Lock())
	_query_cache_lock[id]=lck
	lck.acquire()
	try:
		if(id in _query_cache):
			cch=_query_cache[id]
			if(cch['expiretime']+acceptable_time>time.time()):
				lck.release()
				ret=cch['content']
				song_id2title=ret[0]
				for sid,_ in song_id2title.items():
					
					for __,___ in _.items():
						song_title2id[___.lower()]=sid
				return ret
			
		ws = websocket.create_connection("wss://arc.estertion.win:616/")
		ws.send(id)
		buffer = ""
		scores = []
		userinfo = {}
		song_title = {}
		while buffer != "bye":
			try:
				buffer = ws.recv()
			except websocket._exceptions.WebSocketConnectionClosedException:
				ws = websocket.create_connection("wss://arc.estertion.win:616/")
				ws.send(lookup(id))
			if type(buffer) == type(b''):
				# print("recv")
				obj = json.loads(str(brotli.decompress(buffer), encoding='utf-8'))
				# al.append(obj)
				if obj['cmd'] == 'songtitle':
					song_title = obj['data']
				elif obj['cmd'] == 'scores':
					scores += obj['data']
				elif obj['cmd'] == 'userinfo':
					userinfo = obj['data']
		scores.sort(key=cmp, reverse=True)
		_query_cache[id]={'expiretime':time.time(),'content':[song_title,userinfo,scores]}
		lck.release()
		song_id2title=song_title
		for sid,_ in song_title.items():
			for __,___ in _.items():
				song_title2id[___.lower()]=sid
		return song_title, userinfo, scores
	except Exception as e:
		try:
			lck.release()
		except Exception as ee:
			pass
		raise e
def get_wiki_url_by_song_name(name):
	_=urlencode({'search':name})
	#url='https://wiki.arcaea.cn/api.php?action=opensearch&format=json&formatversion=2&namespace=0&limit=10&suggest=true&'+_
	url='https://wiki.arcaea.cn/api.php?action=opensearch&format=json&formatversion=2&namespace=0&limit=10&suggest=true&'+_
	print(url)
	j=json.loads(lcg_l.gettext(url))
	print(j)
	url=j[-1][0].replace("http://","https://")
	return url
def fuzzy_search_song(name):
	temp=[]
	for i in song_id2title:
		for _,j in song_id2title[i].items():
			temp1=LCS(name.lower(),j.lower())/len(name)/len(j)
			if(j in song_alters):
				for jj in song_alters[j]:
					temp2=LCS(name.lower(),jj.lower())/len(name)/len(jj)
					temp1=max(temp1,temp2)
			temp.append((temp1,j,i))
	return sorted(temp)[::-1]
def get_song_cover_by_name(name):
	if(name.lower() in song_title2id):
		sid=song_title2id[name.lower()]
		pth0=path.join(pth,'arcaea_saves','resources','songs',sid,'base.jpg')
		
		if(path.exists(pth0)):
			print('local cover')
			return Image.open(pth0)
		pth0=path.join(pth,'arcaea_saves','resources','songs',"dl_"+sid,'base.jpg')
		
		if(path.exists(pth0)):
			print('local cover')
			return Image.open(pth0)
		
	_=urlencode({'search':name})
	#url='https://wiki.arcaea.cn/api.php?action=opensearch&format=json&formatversion=2&namespace=0&limit=10&suggest=true&'+_
	url='https://wiki.arcaea.cn/api.php?action=opensearch&format=json&formatversion=2&namespace=0&limit=10&suggest=true&'+_
	print(url)
	j=json.loads(lcg_l.gettext(url))
	print(j)
	url=j[-1][0].replace("http://","https://")
	print('url=',url)
	text=lcg_l.gettext(url)
	#myio.savetext(r'C:\temp\temp_arcaea_wiki_song.html',text)
	url='https://wiki.arcaea.cn'+re.findall(r'<a href="(/index.php/%E6%96%87%E4%BB%B6:Songs_.+?)"',text)[0]
	return get_wiki_image(url)
	print(url)
def get_partner_icon(num):
	num=int(num)
	if(num<=5):
		return Image.open(path.join(pth,'arcaea_saves','resources','%d_icon.png'%(num-1)))
	else:
		return Image.open(path.join(pth,'arcaea_saves','resources','%d_icon.png'%num))
		
		
def ptt_im(n,bg=(0,0,0,0),fill=(255,255,255,255),rate=0.8,height=100,decimal_len=2):
	inte=int(n)
	frac=math.modf(n)[0]
	height1=int(rate*height)
	inte=pic2pic.txt2im(str(inte)+".",fill=fill,bg=bg,fixedHeight=height,font=fnt_exo)
	
	frac=str(frac)[2:]
	if(not frac):
		frac='0'
	elif(len(frac)>decimal_len):
		frac=frac[:decimal_len]
	frac=pic2pic.txt2im(frac,fill=fill,bg=bg,fixedHeight=height1,font=fnt_exo)
	width=inte.size[0]+frac.size[0]
	top=inte.size[1]-frac.size[1]
	ret=Image.new("RGBA",(width,inte.size[1]),bg)
	ret.paste(inte)
	ret.paste(frac,(inte.size[0],top))
	return ret
def render_frame_by_ptt(ptt):
	
	if(ptt>=12.5):
		temp=6
	elif(ptt>=12):
		temp=5
	elif(ptt>=11):
		temp=4
	elif(ptt>=10):
		temp=3
	elif(ptt>=7):
		temp=2
	elif(ptt>=3.5):
		temp=1
	else:
		temp=0
	layer0=Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','rating_%d.png'%temp))
	h=int(layer0.size[1]*0.3)
	pttt=ptt_im(ptt,height=h)
	left,top=[(layer0.size[_]-pttt.size[_])//2 for _ in range(2)]
	layer0.paste(pttt,box=(left,top-h//10),mask=pttt)
	return layer0
def get_partner_img_by_id(id):
	if(id==0):
		id=1
	url='https://wiki.arcaea.cn'+partner_info[id]['url']
	text=lcg_l.gettext(url)
	#myio.savetext(path.join(pth,'temp_partner_page.html'),text)
	temp=re.findall(r'<a href="(/index.php/%E6%96%87%E4%BB%B6:Partner_[\s\S]+?.png)" class="image">',text)[0]
	return get_wiki_image(temp)
def generate_bg_by_partner(id,w,h):
	img=get_partner_img_by_id(id)
	ww,hh=img.size
	colors=[]
	for i in range(100):
		x,y=random.randrange(ww),random.randrange(hh)
		c=img.getpixel((x,y))
		if(c[3]>60):
			colors.append(c)
	colors,_=pic2pic.kmeans(colors,4)
	colors=[list(i) for i in colors]
	
	bi=mymath.bilinear(*colors)
	print(colors,bi(0.5,0.5))
	img=Image.new("RGBA",(50,50))
	for i in range(50):
		for j in range(50):

			img.putpixel((i,j),tuple([int(_) for _ in bi(i/49,j/49)]))
	return img.resize((w,h),Image.LANCZOS)
def get_score_count_mat(pc,spc,nc,mc,rt,h=100):
	pure=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','pure.png')),h)
	far=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','far.png')),h)
	lost=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','lost.png')),h)
	print(fnt_exo)
	rating=pic2pic.txt2im('RATING',bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	
	pn=pic2pic.txt2im('%s(%s)'%(pc,spc),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	fn=pic2pic.txt2im('%s'%(nc,),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	ln=pic2pic.txt2im('%s'%(mc,),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	rn=ptt_im(rt,height=h)
	mat=[	pure,	pn,
			far,	fn,
			lost,	ln,
			rating,	rn]
	
	mat=pic2pic.picMatrix(mat,column_num=2,bg=(0,)*4)
	return mat
fnt_exo=path.join(pth,'arcaea_saves','resources','Exo-Regular.ttf')
def illust_user_info(id,acceptable_time=120,show_score=None):
	st,uinfo,scores=_query(id,acceptable_time=acceptable_time)
	if(show_score):
		recent=show_score
	else:
		recent=uinfo['recent_score'][0]
	song_title=st[recent['song_id']]['en']
	recent_song_cover=get_song_cover_by_name(song_title).convert("RGBA")
	width,height=1280,720
	gold_rate=(5**0.5-1)/2
	_1_3=1/3
	def new_layer():
		return Image.new("RGBA",(width,height))
	#bg
	layer0=pic2pic.imBanner(recent_song_cover,(width,height))
	layer0=layer0.filter(ImageFilter.GaussianBlur(width//50))
	#暗化边框亮化底
	layer1=Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','layer1.png')).resize((width,height))
	
	layer0=Image.alpha_composite(layer0,layer1)
	
	#song_cover
	layer1=new_layer()
	recent_cover_top=int(height*0.5)
	recent_cover_size=int(height*0.35)
	recent_cover_left=width//20
	layer1.paste(recent_song_cover.resize((recent_cover_size,recent_cover_size)),(recent_cover_left,recent_cover_top))
	
	layer0=Image.alpha_composite(layer0,layer1)
	
	#recent_diff_base,title_base
	layer1=new_layer()
	recent_diff=Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','sort_button.png'))
	recent_diff_left=recent_cover_left+int(recent_cover_size*0.1)
	recent_diff_width=int(recent_cover_size)
	recent_diff=pic2pic.fixWidth(recent_diff,recent_diff_width)
	recent_diff_height=recent_diff.size[1]
	recent_diff_top=recent_cover_top+recent_cover_size-int(recent_diff_height*gold_rate)
	layer1.paste(recent_diff,(recent_diff_left,recent_diff_top))
	title_base=Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','title_base.png'))
	title_base_left=int(width*gold_rate*(1-gold_rate)*gold_rate)
	title_base_width=int(width*gold_rate*gold_rate)
	title_base=pic2pic.fixWidth(title_base,title_base_width)
	title_base_height=title_base.size[1]
	title_base_top=recent_cover_top-int(title_base_height*1.2)
	layer1.paste(title_base,(title_base_left,title_base_top))
	print(uinfo['character'])
	partner_img=get_partner_img_by_id(uinfo['character'])
	partner_img=pic2pic.fixHeight(partner_img,height)
	layer1.paste(partner_img,(title_base_left+title_base_width,0))
	
	layer0=Image.alpha_composite(layer0,layer1)
	#recent_diff,recent_constant,title
	diff_size=int(recent_diff_height*gold_rate)
	diff=pic2pic.txt2im(diff_list[recent['difficulty']],bg=(0,)*4,fill=(57,49,62,255),fixedHeight=diff_size,font=fnt_exo)
	const=ptt_im(recent['constant'],height=diff_size,fill=(255,)*4)
	diff_top=recent_diff_top+(recent_diff_height-diff_size)//2
	diff_left=recent_diff_left+(recent_diff_width//2-diff.size[0])//2
	layer1.paste(diff,(diff_left+width//100,diff_top-width//500))
	const_top=diff_top
	const_left=recent_diff_left+(recent_diff_width//2-const.size[0])//2+recent_diff_width//2
	layer1.paste(const,(const_left-width//113,const_top-width//500))
	title_height=int(title_base_height*gold_rate)
	title_max_width=int(title_base_width*gold_rate)
	title=pic2pic.txt2im(song_title,fill=(255,)*4,bg=(0,)*4,fixedHeight=title_height,font=fnt_exo)
	if(title.size[0]>title_max_width):
		title=pic2pic.fixWidth(title,title_max_width)
	title_width,title_height=title.size
	title_left=title_base_left+(title_base_width-title_width)//2
	title_top=title_base_top+(title_base_height-title_height)//2
	layer1.paste(title,(title_left,title_top))
	
	layer0=Image.alpha_composite(layer0,layer1)
	#scores
	
	score_top=recent_cover_top
	score_height_with_border=(height-score_top)//4
	
	h=114
	pure=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','pure.png')),h)
	far=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','far.png')),h)
	lost=pic2pic.fixHeight(Image.open(path.join(pth,'arcaea_saves','resources','illust_basic','lost.png')),h)
	rating=pic2pic.txt2im('RATING',bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	
	pn=pic2pic.txt2im('%d(%d)'%(recent['perfect_count'],recent['shiny_perfect_count']),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	fn=pic2pic.txt2im('%d'%(recent['near_count'],),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	ln=pic2pic.txt2im('%d'%(recent['miss_count'],),bg=(0,)*4,fill=(255,)*4,fixedHeight=h,font=fnt_exo)
	rn=ptt_im(recent['rating'],height=h)
	mat=[	pure,	pn,
			far,	fn,
			lost,	ln,
			rating,	rn]
	
	mat=pic2pic.picMatrix(mat,column_num=2,bg=(0,)*4)
	#mat.show()
	mat_right=int(width*gold_rate)
	mat_left=const_left+int(const.size[0]*0.3)
	mat_xmid=(mat_right+mat_left)>>1
	mat_bottom=height-recent_cover_left
	mat_top=score_top+score_height_with_border
	
	mat_ymid=(mat_bottom+mat_top)>>1
	mat_width,mat_height=mat_right-mat_left,mat_bottom-mat_top
	mat=pic2pic.im_sizelimitmax(mat,(mat_width,mat_height))
	mat_width,mat_height=mat.size
	mat_top=mat_ymid-mat_height//2
	mat_left=mat_xmid-mat_width//2
	
	layer1.paste(mat,(mat_left,mat_top))
	layer0=Image.alpha_composite(layer0,layer1)
	
	#player info,score
	layer1=new_layer()
	ptt=render_frame_by_ptt(uinfo['rating']/100)
	ptt_height=int(title_base_top*0.9)
	ptt_top=int(title_base_top*(1-gold_rate)/2)
	ptt_left=recent_cover_left
	ptt=pic2pic.fixHeight(ptt,ptt_height)
	layer1.paste(ptt,(ptt_left,ptt_top))
	
	h=int(ptt_height/5)
	b,r=calc_b_r(uinfo['rating']/100,scores)
	player_info_left=int(ptt_left*1.4+ptt_height)
	player_name_info="   %s\nBest30  %.3f\nRecent10  %.3f"%(uinfo['name'],b,r)
	player_name_info=pic2pic.txt2im_ml(player_name_info,fixedHeight=h,width=width-player_info_left,fill=(255,)*4,line_space=0.2,font=fnt_exo)
	player_info_top=int((title_base_top-player_name_info.size[1])*gold_rate)
	layer1.paste(player_name_info,(player_info_left,player_info_top))
	
	recent_score=recent['score']
	recent_score=str(recent_score).zfill(8)
	recent_score=recent_score[:2]+"'"+recent_score[2:5]+"'"+recent_score[-3:]
	score_height=int(score_height_with_border*gold_rate)
	recent_score=pic2pic.txt2im(recent_score,fill=(255,)*4,fixedHeight=score_height,font=fnt_exo)
	recent_score_left=mat_xmid-recent_score.width//2
	recent_score_top=score_top+(score_height-recent_score.size[1])//2
	layer1.paste(recent_score,(recent_score_left,recent_score_top))
	
	layer0=Image.alpha_composite(layer0,layer1)
	
	#layer0.show()
	return layer0
	
		
class QueryThread(threading.Thread):
	def __init__(self, cmd, ctx, bot, state):
		threading.Thread.__init__(self)
		self.operation = cmd.name[0]
		self.ctx = ctx
		self.bot = bot
		self.state = state

	def run(self):
		funcs = []
		if self.operation == 'arcaea':
			try:
				message = query(self.state['id'])
			except Exception as e:
				message = "An exception occurred: %s" % repr(e)
			funcs.append(self.bot.send(self.ctx, message=message))
		elif self.operation == 'best':
			try:
				s = best(self.state['id'], self.state['num'])
			except Exception as e:
				s = ["An exception occurred: %s" % repr(e)]
			for elem in s:
				funcs.append(self.bot.send(self.ctx, message=elem))
		loop = asyncio.new_event_loop()
		loop.run_until_complete(asyncio.wait(funcs))
		loop.close()
def const2level(const):
	if(const>=11):
		return '11'
	elif(const>=10.7):
		return '10+'
	elif(const>=10):
		return '10'
	elif(const>=9.7):
		return '9+'
	else:
		return str(int(const))
def illust_level(const=None,level=None,shadow_fill=None,shadow_delta=(1,1),fill=(255,)*4,bg=(0,)*4,height=110,plus_size=0.5):
	if(level is None):
		level=const2level(const)
	plus=level[-1]=='+'
	level=level.strip('+')
	level=pic2pic.txt2im(level,fill=fill,bg=bg,fixedHeight=height,shadow_fill=shadow_fill,shadow_delta=shadow_delta,font=fnt_exo)
	if(plus):
		plus=pic2pic.txt2im('+',fill=fill,bg=bg,fixedHeight=int(plus_size*height),shadow_fill=shadow_fill,shadow_delta=shadow_delta,font=fnt_exo)
		ret=Image.new("RGBA",(level.size[0]+plus.size[0],level.size[1]),(0,)*4)
		ret.paste(level)
		ret.paste(plus,(level.size[0],0))
		return ret
	else:
		return level
def calc_score_grade(score):
	if(score['score']>=9900000):
		return "EX+"
	elif(score['score']>=9800000):
		return "EX"
	elif(score['score']>9500000):
		return "AA"
	elif(score['score']>9200000):
		return 'A'
	elif(score['score']>8900000):
		return 'B'
	elif(score['score']>8600000):
		return 'C'
	else:
		return 'D'
def grade_icon(score=None,grade=None):
	if(grade is None):
		grade=calc_score_grade(score)
	return Image.open(path.join(pth,'arcaea_saves','resources','grade_icons','grade_%s.png'%grade))
def best_clear_type_str(score):
	t=score['best_clear_type']
	if(t==5):
		return "HARD"
	elif(t==1):
		return "NORMAL"
	elif(t==4):
		return "EASY"
	elif(t==0):
		return "FAIL"
	elif(t==2):
		return "FULL"
	else:
		return "PURE"
def clear_type_icon(score=None,s=None):
	if(s==None):
		s=best_clear_type_str(score)
	return Image.open(path.join(pth,'arcaea_saves','resources','clear_icons','clear_badge_%s.png'%s))
song_info=myhash.splitedDict(pth=path.join(path.dirname(__file__),'arcaea_saves','song_info'),splitMethod=lambda x:myhash.hashs(x)[:2].lower())
if(path.exists(path.join(pth,'arcaea_saves','song_alters.json'))):
	song_alters=myio.loadjson(path.join(pth,'arcaea_saves','song_alters.json'))
else:
	song_alters={}
def get_pack_name_by_song_title(title):
	#print(title)
	if(title in song_info):
		if('pack_name' in song_info[title]):
			return song_info[title]['pack_name']
	url=get_wiki_url_by_song_name(title)
	h=lcg_l.gettext(url)
	j=re.findall('RLCONF=({[\s\S]+?});',h)[0].replace('!1','0').replace('!0','1')
	j=json.loads(j)
	for i in j['wgCategories']:
		if('曲包曲目' in i):
			song_info[title]=song_info.get(title,{})
			ret=i[:-4].replace(" Collaboration","")
			song_info[title]['pack_name']=ret
			song_info.dumpPart1(title)
			return ret
	#print('no pack name',title)
	myio.savetext(r'G:\temp.html',h)
def illust_score(score,line4='第四行内容'):
	global song_id2title
	from mytimer import timer
	tmr=timer()
	layer1=Image.open(path.join(pth,'arcaea_saves','resources','illust_score','illust_score.png'))
	width,height=layer1.size
	gold_rate=(5**0.5-1)/2	
	def new_layer():
		return Image.new("RGBA",(width,height),(0,)*4)
	
	layer0=new_layer()
	title=song_id2title[score['song_id']]['en']
	cover=get_song_cover_by_name(title)
	print('line539',tmr.gettime())
	cover=pic2pic.imBanner(cover,(155,104))
	layer0.paste(cover,(75,10))
	layer0=Image.alpha_composite(layer0,layer1)
	
	layer1=new_layer()
	h=27
	constant=score['constant']
	constant=ptt_im(constant,height=h,decimal_len=1)
	im_title=pic2pic.txt2im("  "+title,fixedHeight=h,bg=(0,)*4,fill=(255,)*4,font=fnt_exo,shadow_fill=(0,0,0,255),shadow_delta=(1,1))
	im_level=illust_level(const=score['constant'],height=44)
	mat=get_score_count_mat(pc=score['perfect_count'],spc=score['shiny_perfect_count'],nc=score['near_count'],mc=score['miss_count'],rt=score['rating'],h=35)
	mat=pic2pic.fixHeight(mat,135)
	clear_badge=clear_type_icon(score=score)
	clear_badge=pic2pic.imBanner(clear_badge,(65,65))
	grade_badge=grade_icon(score=score)
	grade_badge=pic2pic.fixHeight(grade_badge,48)
	w,h=grade_badge.size
	le=261-w//2
	to=54-h//2
	
	score_str=str(score['score']).zfill(8)
	score_str=score_str[:2]+"'"+score_str[2:5]+"'"+score_str[-3:]
	im_score=pic2pic.txt2im(score_str,fill=(255,)*4,bg=(0,)*4,fixedHeight=28,font=fnt_exo)
	
	time_played=datetime.fromtimestamp(score['time_played']/1000)
	time_played=time_played.strftime("%Y/%m/%d")
	print('line566',tmr.gettime())
	pack_name=get_pack_name_by_song_title(title)
	print('line568',tmr.gettime())
	print(pack_name)
	_3line="取得日期: "+time_played+'\n曲包:'+pack_name
	if(line4):
		_3line+='\n'+line4
	#_3line=pic2pic.txt2im_ml(_3line,fill=(255,)*4,bg=(0,)*4,fixedHeight=18,font=fnt_exo,line_space=0.3,width=width-43)
	_3line=pic2pic.txt2im_ml(_3line,fill=(255,)*4,bg=(0,)*4,fixedHeight=18,line_space=0.3,width=width-43)
	
	layer1.paste(grade_badge,(le,to))
	layer1.paste(im_score,(106,120))
	layer1.paste(mat,(width-mat.size[0],115))
	layer1.paste(clear_badge,(308,22))
	layer1.paste(im_level,(34,18))
	layer1.paste(constant,(27,82))
	layer1.paste(im_title,(27+constant.size[0],82))
	
	layer0=Image.alpha_composite(layer0,layer1)
	
	layer1=new_layer()
	layer1.paste(_3line,(46,160))
	layer0=Image.alpha_composite(layer0,layer1)
	return layer0

def longest_common_subsequence(l1,l2):
	n=len(l1)
	m=len(l2)
	dp=np.zeros((n+1,m+1),np.int32)
	for i in range(0,n+1):
		for j in range(0,m+1):
			if(i==0 or j==0):
				dp[i,j]=0
			else:
				A=l1[i-1]
				B=l2[j-1]
				if(A==B):
					dp[i,j]=dp[i-1,j-1]+1
				else:
					dp[i,j]=max(dp[i-1,j],dp[i,j-1])
	return dp[n,m]
LCS=longest_common_subsequence
if(__name__=='__main__'):
	t=lcg_l.gettext(r'https://wiki.arcaea.cn/index.php/Can_I_Friend_You_on_Bassbook%3F_Lol')
	print(get_song_cover_by_name('Can I Friend You on Bassbook? Lol'))