from bot_backend import *
from datetime import datetime
from myjobs import jobs
from os import path
from glob import glob
import numpy as np
import myhash,pyxyv,pic_indexing_RGB,random,time,math,myio,traceback,pic2pic,getimgpid
from pic_enc import pic_enc
from PIL import Image
from simple_arg_parser import parse_args
from weight_choice import weight_choice
indexing_pth=path.join(mainpth,'setu_indexing')
indexing=pic_indexing_RGB.indexing(indexing_pth,mode='euclidean',color='RGB',wsiz=20,annsize2capacity=lambda x:int(x+1111))
shuffle=list(range(indexing.size))
random.shuffle(shuffle)
shuffle_idx=0
tag2idx=myhash.splitedDict(pth=path.join(mainpth,'setu_tag2idx'),splitMethod=lambda x:myhash.hashs(x)[:2].lower())
def base32(i):
	c='1234567890abcdefghijklmnopqrstuv'
	ret=[]
	while(i):
		ret.append(c[i&0b11111])
		i>>=5
	return ''.join(ret)
subtag=myhash.splitedDict(pth=path.join(mainpth,'setu_subtag'),splitMethod=lambda x:base32(myhash.hashi(x))[:3])

jbs=jobs()
trimedPid=myhash.trimDict()	#简化id，见myhash模块
plugin_name_n='色图'
def report_status():
	ret=[]
	ret.append('“来份色图”，或“色图”   看一张色图')
	ret.append('“色图 标签”   看一张带有标签的色图')
	ret.append('“/pxrank”   看今天的每日插画排行')
	ret.append('“/pxrank monthly”   看今天的每月插画排行')
	ret.append('“/pxrank monthly -d n”   看n天前的每月插画排行')
	ret.append('“/pxrank weekly”   看今天的每周插画排行')
	ret.append('“/pxsearch 关键词”   搜索插画')
	ret.append('“/pxview id或简化id”   看pixiv插画')
	ret.append('收录的色图数量%s'%indexing.size)
	return ret
def _rand_idx():
	global shuffle_idx,shuffle
	while(len(shuffle)<indexing.size):
		shuffle.append(len(shuffle))
	idx=shuffle[shuffle_idx]
	'''if(ctx is not None):
		sctx=simple_ctx(ctx)
		recent_sent_setu_illust_info[sctx.group_id]=indexing[idx]['illust_info']
		recent_sent_setu_pth[sctx.group_id]=img=get_pth_by_idx(idx)'''
	shuffle_idx=(shuffle_idx+1)%len(shuffle)
	return idx
def rand_idx(ctx=None):
	rets=[]
	for i in range(5):
		idx=_rand_idx()
		rets.append((indexing[idx]['illust_info']['bookmarkCount'],idx))
	#rets=sorted(rets)[-5:]
	idx=max(rets)[-1]
	if(ctx is not None):
		sctx=simple_ctx(ctx)
		recent_sent_setu_illust_info[sctx.group_id]=indexing[idx]['illust_info']
		recent_sent_setu_pth[sctx.group_id]=img=get_pth_by_idx(idx)
	return idx
def rand_img(ctx=None):
	idx=rand_idx(ctx=ctx)
	return indexing[idx]['pth'].replace('%mainpth%',mainpth)
def get_pth_by_idx(idx):
	return indexing[idx]['pth'].replace('%mainpth%',mainpth)

def crawl_callback(crawl_info):
	try:
		tmr=receiver_timer('crawl_callback')
		pid=crawl_info['pid']
		print('setu v2 crawl %s'%pid)
		info=pyxyv.getIllustInfoByPID(pid)
		tags=info['tags_']#+[info['userName']]
		if('R-18' in tags):
			return None
		for i in info['tags']:
			for j in i.get('translation',{}):
				tags.append(i['translation'][j])
		for i in tags:
			for idx in range(len(i)):
				for jdx in range(idx+1):
					subtag[i[jdx:idx+1]]=subtag.get(i[jdx:idx+1],{})
					subtag[i[jdx:idx+1]][i]=1
					subtag.dumpPart1(i[jdx:idx+1])
		for impth in crawl_info['content']:
			im=Image.open(impth)
			indexing.add_image(im)
			idx=indexing.get_image_index(im)
			print('setu v2 crawl %s,idx=%s'%(pid,idx))
			
			iminfo=indexing.get(im,{})
			iminfo['pid']=pid
			iminfo['tags']=list(iminfo.get('tags',[]))+tags
			iminfo['tags']={i:1 for i in iminfo['tags']}
			iminfo['illust_info']=info
			for tag in iminfo['tags']:
				tag2idx[tag]=tag2idx.get(tag,{})
				tag2idx[tag][str(idx)]=1
				tag2idx.dumpPart1(tag)
			iminfo['pth']=impth.replace(mainpth,'%mainpth%')
			indexing[idx]=iminfo
		tmr.finish()
	except Exception as e:
		myio.savetext(path.join(mainpth,'v2errlog','%d.json'%time.time()),traceback.format_exc())
		raise e

def get_setu_by_tag(tags,consider_sub=False):
	choose_from=None
	for i in tags:
		choose_from_i=set(tag2idx.get(i,{}))
		if(consider_sub):
			#print('line75',i)
			for j in subtag.get(i,{}):
				#print('line77',i,j)
				choose_from_i|=set(tag2idx.get(j,{}))
		if(choose_from is None):
			choose_from=choose_from_i
		elif(choose_from):
			choose_from=choose_from.intersection(choose_from_i)
		else:
			return choose_from
	return choose_from
recent_sent_setu_pth={}
recent_sent_setu_illust_info={}
def modified_img(pth):
	if(pth[-3:]=='gif'):
		return pth
	
	img=Image.open(pth)
	if(img.mode!='RGB'):
		return pth
	w,h=img.size
	x,y=random.randrange(w),random.randrange(h)
	c=[(_+128)%256 for _ in img.getpixel((x,y))]
	img.putpixel((x,y),tuple(c))
	return img
@on_exception_send
def setu_tag_not_specified(ctx):
	tmr=receiver_timer('setu')
	sctx=simple_ctx(ctx)
	idx=rand_idx()
	#recent_sent_setu[sctx.group_id]=idx
	recent_sent_setu_illust_info[sctx.group_id]=indexing[idx]['illust_info']
	recent_sent_setu_pth[sctx.group_id]=img=get_pth_by_idx(idx)
	img=modified_img(img)
	simple_send(ctx,img,im_size_limit=1<<20)
	tmr.finish()

@on_exception_send
def setu_tag_specified(ctx,tags,extra_mes=None):
	choose_from=get_setu_by_tag(tags)
	sctx=simple_ctx(ctx)
	if(not choose_from):
		choose_from=get_setu_by_tag(tags,consider_sub=True)
	if(choose_from):
		ls=list(choose_from)
		random.shuffle(ls)
		mx=(0,'0')
		for i in ls[:5]:
			mx=max((indexing[int(i)]['illust_info']['bookmarkCount'],i),mx)
		idx=int(mx[1])
		#idx=int(random.choice(list(choose_from)))
		#recent_sent_setu[sctx.group_id]=idx
		recent_sent_setu_illust_info[sctx.group_id]=indexing[idx]['illust_info']
		recent_sent_setu_pth[sctx.group_id]=pth=get_pth_by_idx(idx)
		img=modified_img(pth)
		if(extra_mes):
			simple_send(ctx,extra_mes+[img],im_size_limit=1<<20)
		else:
			simple_send(ctx,img,im_size_limit=1<<20)
	else:
		idx=rand_idx()
		recent_sent_setu_illust_info[sctx.group_id]=indexing[idx]['illust_info']
		recent_sent_setu_pth[sctx.group_id]=img=get_pth_by_idx(idx)
		img=modified_img(img)
		if(extra_mes):
			simple_send(ctx,[img,'没有符合条件的色图..随便发一张⑧']+extra_mes,im_size_limit=1<<20)
		else:
			simple_send(ctx,[img,'没有符合条件的色图..随便发一张⑧'],im_size_limit=1<<20)


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
@receiver
@threading_cnt('多来点色图')
@on_exception_send
@start_with('[!！/]?多来点')
def setu_duolaidian(ctx,match,rest):
	rest=rest.strip()
	sctx=simple_ctx(ctx)
	group_id=sctx.group_id
	if(group_id not in recent_sent_setu_illust_info):
		simple_send(ctx,['你还没有看过色图，无法进行相关推荐'])
	else:
		tmr=receiver_timer('多来点色图')
		info=recent_sent_setu_illust_info[group_id]
		pth=recent_sent_setu_pth[group_id]
		pid=info['original_info']['illustId']
		start_crawl_ids([pid])
		tags=[]
		mx=None
		for i in info['tags_']+[rest]:
			tmr1=receiver_timer('多来点色图load tag2idx')
			le=len(tag2idx.get(i,{}))
			tmr1.finish()
			if(le<2):
				continue
			mx=le if mx is None else max(mx,le)
			tags.append((i,le))
		tags_=[]
		weights=[]
		for i,le in tags:
			weight=min(mx/le,25)
			if(rest):
				weight=80**(longest_common_subsequence(rest,i)/len(i))
			weights.append(weight)
			tags_.append(i)
		tag=weight_choice(weights,tags_)
		if(tag in info['tags_']):
			setu_tag_specified(ctx,[tag],['其他关于“%s”的图'%tag])
		else:
			setu_tag_specified(ctx,[tag])
		info=recent_sent_setu_illust_info[group_id]
		pth=recent_sent_setu_pth[group_id]
		pid=info['original_info']['illustId']
		start_crawl_ids([pid])
		tmr.finish()
@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?色图信息$')
def setu_info(ctx,match):
	sctx=simple_ctx(ctx)
	group_id=sctx.group_id
	if(group_id not in recent_sent_setu_illust_info):
		simple_send(ctx,['你还没有看过色图呐！'])
	else:
		info=recent_sent_setu_illust_info[group_id]
		pth=recent_sent_setu_pth[group_id]
		puserId=info['userId']
		#uinfo=pyxyv.getUserInfo(uid=puserId)
		width=1280
		banner_height=width//7
		gold_rate=(1+5**0.5)/2
		username_height=int(banner_height/gold_rate)
		tag_height=int(username_height/3)
		username_top=int((banner_height-username_height)/2)
		
		#usr_url=uinfo['url']
		'''imBanner=pyxyv.lcg.get_image(uinfo.get('banner',uinfo['avatar_big']),referer=usr_url)
		imBanner=pic2pic.imBanner(imBanner,(1080,200))'''
		imBanner=Image.new("RGBA",(width,banner_height),(46,151,216,255))
		
		imMain=Image.open(pth)
		imMain=pic2pic.imBanner(imMain,(width,int(width*1.18)))
		
		imUsername=pic2pic.txt2im(info['original_info']['title']+' by. '+info['userName'],fixedHeight=username_height,fill=(255,)*4)
		imBanner.paste(imUsername,box=(username_top,username_top),mask=imUsername)
		
		tmp=[]
		bbl_res=pic2pic.load_bubble(path.join(mainpth,'static_pics','bubble2'))
		for i in info['tags_']:
			func=kj_show_tag([i])
			kj=plugins['plg_admin'].register_kjml('kjshowtag'+i,func)
			txt=i+'，输入“/kj %s”'%kj
			txt=pic2pic.txt2im(txt,fixedHeight=tag_height,fill=(41,96,165,255),shadow_fill=(255,255,255,230),shadow_delta=(2,2))
			bbl=pic2pic.bubble(txt,**bbl_res)
			tmp.append(bbl)
		imTags=pic2pic.horizontal_layout(tmp,border=width//200,width=width)
		
		height=imBanner.size[1]+imMain.size[1]+imTags.size[1]
		ret=Image.new("RGBA",(width,height))
		ret.paste(imBanner,(0,0))
		ret.paste(imMain,(0,imBanner.size[1]))
		ret.paste(imTags,(0,imBanner.size[1]+imMain.size[1]))
		#ret.show()
		simple_send(ctx,[ret,info['url']],im_size_limit=1<<20)
	

@receiver_nlazy
@threading_run
@start_with(r'[!！/]?色图time')
def setu_time(ctx):

	if(not(judge_setu_available(ctx))):
		simple_send(ctx,'功能暂时停用..')
		return
	for i in range(5):
		setu_tag_not_specified(ctx)
group_white_list=myhash.splitedDict(pth=path.join(mainpth,'saves','setu_white_list'),splitMethod=lambda x:str(x)[:3].lower())
def add_white_list(ctx,gid=None):
	if(gid is None):
		sctx=simple_ctx(ctx)
		gid=sctx.group_id
	group_white_list[gid]=1
def remove_white_list(ctx,gid=None):
	if(gid is None):
		sctx=simple_ctx(ctx)
		gid=sctx.group_id
	group_white_list[gid]=0
def judge_white_list(ctx,gid=None):
	if(gid is None):
		sctx=simple_ctx(ctx)
		gid=sctx.group_id
	return group_white_list.get(gid,0)
def judge_setu_available(ctx):
	if(judge_white_list(ctx)):
		return True
	#return datetime.now().hour>=1 and datetime.now().hour<=3
	return True
@receiver_nlazy
@threading_run
@start_with(r'[!！/]?色图($| )|来(份|张)色图|来(份|张)[\s\S]的色图')
def setu(ctx,match):
	try:
		if(not(judge_setu_available(ctx))):
			simple_send(ctx,'功能暂时停用..')
			return
		sctx=simple_ctx(ctx)
		text=sctx.text
		args=[ctx]
		if(text[len(match.group()):]):
			tags=text[len(match.group()):].strip().split()
			args.append(tags)
			func=setu_tag_specified
		elif(re.match(r'来(份|张)[\s\S]的色图',text)):
			tags=re.findall(r'来(份|张)([\s\S]+)的色图',text)[0][1].strip().split()
			if(not tags):
				return
			args.append(tags)
			func=setu_tag_specified
		else:
			func=setu_tag_not_specified
		jbs.start({'target':func,'args':args})
	except Exception as e:
		simple_send(ctx,str(e))
		print(traceback.format_exc())


def kj_show_tag(tags):
	def func(ctx,tags=tags):
		setu_tag_specified(ctx,tags,tags)
	return func


def show_user(ctx,*args,**kwargs):
	usrinfo=pyxyv.getUserInfo(*args,**kwargs)
	pic=pyxyv.usr_info2pic(usrinfo,trimedPid=trimedPid)
	simple_send(ctx,pic)
def kj_show_user(username):
	def func(ctx,username=username):
		simple_send(ctx,'正在加载%s所创作插画'%username)
		show_user(ctx,username=username)
	return func

def func_tag_extra_text(tag):
	tmp='userName:'
	if(tag[:len(tmp)]==tmp):
		func=kj_show_user(tag[len(tmp):])
	else:
		func=kj_show_tag([tag])
	kj=plugins['plg_admin'].register_kjml('kjshowtag'+tag,func)
	txt='输入“/kj %s”'%kj
	return txt
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?pxsearch|[!！/]?pixiv_search')
def pxsearch(ctx,match,rest_text):
	args=parse_args(rest_text.strip())
	keyword=args.get('default',None) or args.get('k',None) or args.get('keyword',None)
	if(not keyword):
		simple_send(ctx,'你没有输入关键词呐！！！111')
		return
	else:
		keyword=keyword.strip()
	page='1'
	for i in ['p','page','-page']:
		if(i in args):
			page=args[i].strip()
	result_title='关于“%s”的插画第%s页'%(keyword,page)
	simple_send(ctx,'正在搜索'+result_title)
	search_result=pyxyv.search(keyword=keyword,page=page,mode='safe')
	ret=pyxyv.results2pic(search_result,trimedPid,jobs1=jobs(),result_title=result_title)
	simple_send(ctx,[ret])

@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?pxuser|[!！/]?pixiv_user')
def pixiv_user(ctx,match,rest_text):
	print('line229')
	args=parse_args(rest_text.strip())
	# keyword=''
	for i in ['keyword','default']:
		if( i in args):
			keyword=args[i].strip()
	page='1'
	for i in ['p','page']:
		if(i in args):
			page=args[i].strip()
	simple_send(ctx,'正在加载%s所创作插画第%s页'%(keyword,page))
	if(keyword.isnumeric()):
		usrinfo=pyxyv.getUserInfo(uid=keyword,page=int(page))
	else:
		usrinfo=pyxyv.getUserInfo(username=keyword,page=int(page))
	pic=pyxyv.usr_info2pic(usrinfo,trimedPid=trimedPid)
	simple_send(ctx,pic)
@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?pxrank|[!！/]?pixiv_rank')
def pxrank(ctx,match,rest_text):
	args=parse_args(rest_text.strip())
	mode='daily'
	mode_natural={'daily':"每日",'weekly':'每周','monthly':"每月",'rookie':'新人'}
	page='1'
	dd=0
	for i in ['m','mode','default']:
		if(i in args):
			mode=args[i].strip()
	#simple_send(ctx,str(args))
	for i in ['p','page']:
		if(i in args):
			page=args[i]
	if(mode not in mode_natural):
		simple_send(ctx,'未知的模式%s哒！'%mode)
		return
	if(not page.isnumeric()):
		simple_send(ctx,'页码必须是整数哒！')
		return
	for i in ['d','date']:
		if(i in args and args[i].isnumeric()):
			dd=int(args[i])
	if(dd):
		result_title='%d天前%s排行的第%s页'%(dd,mode_natural[mode],page)
	else:
		result_title='今日%s排行的第%s页'%(mode_natural[mode],page)
	simple_send(ctx,'正在查询'+result_title)
	search_result=pyxyv.getRanking(mode=mode,page=page,datedelta=dd)
	ret=pyxyv.results2pic(search_result,trimedPid,jobs1=jobs(),result_title=result_title)
	simple_send(ctx,[ret])

@receiver
@threading_run
def try_crawl(ctx):
	sctx=simple_ctx(ctx)
	text=sctx.text
	ids=re.findall(r'illust_id=(\d+)',text)
	ids+=re.findall(r'artworks/(\d+)',text)
	_ids=set()
	for i in ids:
		info=pyxyv.getIllustInfoByPID(i)
		tags=info['tags_']
		if('R-18' not in tags):
			_ids.add(i)
	if(_ids and is_su(ctx)):
		start_crawl_ids(list(_ids))
		simple_send(ctx,'开始爬取！！')

def start_crawl_ids(ids):
	svpth=path.join(mainpth,time.strftime('%Y',time.localtime()))
	kwargs=(lambda **kwargs:kwargs)(numlimit=100,svpth=svpth,muchbookmarkedsvpth=svpth,callback=crawl_callback,bookmarkmin=100,bookmarkmuch=500,start_pid=ids,timelimit=math.inf,wait=10)
	jbs.start({'target':pyxyv.defaultCrawl,'kwargs':kwargs})
	

@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?pxview|[!！/]?pixiv_view')
def pxview(ctx,match,rest_text):
	#simple_send(ctx,[rest_text.strip()])
	sctx=simple_ctx(ctx)
	pid=rest_text.strip()
	if(not pid):
		simple_send(ctx,'您没有输入pixiv id哒！')
	pid=trimedPid.get(pid,pid)
	info=pyxyv.getIllustInfoByPID(pid)
	
	files=pyxyv.getImageFilesByPID_(pid,quality='regular')
	pth=files[0]
	recent_sent_setu_illust_info[sctx.group_id]=info
	recent_sent_setu_pth[sctx.group_id]=pth
	
	if('R-18' in info['tags_']):
		#simple_send(ctx,'R-18内容不予展示，哼唧！')
		_=[]
		for i in files:
			im=Image.open(i)
			W,H=pic_enc.select_W_H(im.size)
			_.append(pic_enc.enc(im,W,H))
		files=_
	for i in files:
		simple_send(ctx,i,im_size_limit=2<<20)

@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?识图')
def shitu(ctx):
	sctx=simple_ctx(ctx)
	pics=sctx.get_rpics()
	allow_low_sim=False
	if('低相似度' in sctx.text):
		allow_low_sim=True
	#pics=get_recent_sent_img_file(senderstr(session.ctx))
	if(not pics):
		simple_send(ctx,'您还没有发送图片呐！')
		return
	pic=pics[0]
	im=Image.open(pic)
	vec=indexing.img2v(im,indexing.wsiz)
	nns=indexing.get_nns_by_vector(vec,min(20,indexing.size),include_distances=True)[:5]
	ret=[]
	has0_9=False
	kf=(35*indexing.f)**0.5
	bs=0.9**(1/kf)
	func=lambda x:bs**x
	retimg=[]
	for dist,i in nns:
		#vec_=indexing.get_item_vector(i)
		#similarity=pic_indexing.vec_similarity(vec_,vec)
		similarity=func(dist)
		
		if(similarity>=0.72 or allow_low_sim):
			img=indexing.get_item_img(i)
			info=indexing[i]['illust_info']
			hashed=myhash.phashs(img).lower()
			tpid=trimedPid.add(hashed,indexing[i]['pid'])
			title='id:%s(%s)-%.1f%%'%(tpid,indexing[i]['pid'],similarity*100)
			img=pyxyv.illust_illust_info(info,img,title=title,func_tag_extra_text=func_tag_extra_text)
			retimg.append(img)
			if(similarity>0.95):
				has0_9=True
				break
	
	text_mes=[]
	if(not(has0_9)):
		try:
			saucepid=str(getimgpid.getPixivPID(pic,donotsearchsaucenao=False))
			if('ERR' not in saucepid):
				
				file=pyxyv.getImageFilesByPID_(saucepid,quality='small')
				mx=0
				mxfile=None
				for i in file:
					vec_=indexing.img2v(Image.open(i),indexing.wsiz)
					dist=indexing.dist_func(vec_,vec)
					similarity=func(dist)
					if(similarity>mx):
						mxfile=i
						mx=similarity
				if(mx>0.5 or allow_low_sim):
					url=r'https://www.pixiv.net/artworks/%s'%saucepid
					info=pyxyv.getIllustInfoByPID(saucepid)
					img=Image.open(mxfile)
					hashed=myhash.phashs(img).lower()
					tpid=trimedPid.add(hashed,saucepid)
					title='id:%s(%s)-%.1f%%'%(tpid,saucepid,mx*100)
					img=pyxyv.illust_illust_info(info,img,title=title,func_tag_extra_text=func_tag_extra_text)
					retimg.append(img)
		except Exception as e:
			text_mes.append('Saucenao出现了谜之错误!%s'%e)
	if(retimg):
		simple_send(ctx,retimg+text_mes)
	else:
		simple_send(ctx,['居然..没有搜索结果！']+text_mes)
	
	


if(__name__=='__main__'):
	pass
	start_crawl_ids([83420473,83418647])