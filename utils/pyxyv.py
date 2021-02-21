import requests,myio,json,getheader,os,time,copy,myhash,re,traceback,random,pic2pic,myio,zipfile
import mytimer as timer
from urllib.parse import urlencode
from os import path
#from workpathmanager import pathManager
from PIL import Image,ImageFilter
from make_gif import make_gif
'''if(__name__!='__main__'):
	from none_converters import *'''
from glob import glob
from myjobs import *
from datetime import datetime,timedelta
import lcg
localCachingGeter=lcg.localCachingGeter
#wpm=pathManager(appname='pyxyv')
#pyxyvPth=wpm.getpath(session='mainpth',ask_when_dne=True)
pyxyvPth=path.join(path.dirname(__file__),'pyxyv')
cookiejar=requests.cookies.RequestsCookieJar()
if(path.exists(path.join(pyxyvPth,'pxvcookie.json'))):
	cookieJson=myio.loadjson(path.join(pyxyvPth,'pxvcookie.json'))
else:
	cookieJson={}
crawl_throttle=timer.throttle(3,15)
#connection_throttle=timer.throttle(10,10)
#pixiv的登录后cookie用Chrome的EditThisCookie导出
for i in cookieJson:
	#for j in ['hostOnly','session','expirationDate','httpOnly','sameSite','storeId','id']:
	for j in ['id', 'httpOnly', 'sameSite', 'expirationDate', 'session', 'hostOnly', 'storeId']:
		if(j in i):
			i.pop(j)
	cookiejar.set(**i)
lcg.cookies=cookiejar

	
def savebin(filename,t,f=True):
	if(not(os.path.exists(os.path.dirname(filename)))):
		os.makedirs(os.path.dirname(filename))
	if(not(f)):
		if(os.path.exists(filename)):
			return None
	f=open(filename,'wb')
	f.write(t)
	f.close()
proxy_dict = {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081"
}	
header=getheader.headers

lcg=localCachingGeter(workpth=pyxyvPth+r'\tempcache',expiretime=86400,cookies=cookiejar,connection_throttle=(25,1),proxies=proxy_dict)
lcg_m=localCachingGeter(workpth=pyxyvPth+r'\tempcache_middle',expiretime=1200,cookies=cookiejar,proxies=proxy_dict)
lcg_s=localCachingGeter(workpth=pyxyvPth+r'\tempcache_short',expiretime=60,cookies=cookiejar,proxies=proxy_dict)
#lcg.getbin(r'https://www.pixiv.net/ajax/illust/70829971/recommend/init?limit=18',headerex={'Referer':r'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=70829971'})

#单页在medium网页中有original地址
#多页在medium网页中有original地址
#多页在manga网页中有缩略图地址
#多页在mode=manga&illust_id=71119460&page=n网页中有original地址

#lcg.gettext(r'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=71119460')


img2PID_dic_svpth=pyxyvPth+r'\save\img2piddic_save'
def getImgPID(i,donotreload=None):
	
	hash_=myhash.phashs(i)
	kwargs={"length":70,"offs":1,"rm":None,"w":8}
	hash_small=myhash.hashs(myhash.phashi(i,**kwargs))
	dic={}
	for j in ['.json','_'+hash_[:2]+'.json',hash_[:2]+'.json']:
		svpth=img2PID_dic_svpth+j
		if(path.exists(svpth)):
			dic.update(myio.loadjson(svpth))
	
	#print(len(dic))
	if(hash_ in dic):
		pid=dic[hash_]
		small=getImageFilesByPID_(pid=pid,quality='small')
		hashes_small=[myhash.hashs(myhash.phashi(Image.open(i),**kwargs)) for i in small]
		if(hash_small not in hashes_small):
			return "HASH_NOT_FIT_ERR"
		else:
			return pid
		
	else:
		return 'NO_PID_ERR'
def saveImgPID(i,PID):
	hash_=myhash.phashs(copy.copy(i))
	svpth=img2PID_dic_svpth+'_'+hash_[:2]+'.json'
	dic={}
	if(path.exists(svpth)):
		try:
			dic.update(json.loads(myio.opentext(svpth)))
		except Exception:
			pass
	dic[hash_]=PID
	myio.dumpjson(svpth,dic)
def delImgPID(i):
	hash_=myhash.phashs(copy.copy(i))
	svpth=img2PID_dic_svpth+'_'+hash_[:2]+'.json'
	dic={}
	if(path.exists(svpth)):
		dic.update(json.loads(myio.opentext(svpth)))
	dic.pop(hash_,None)
	myio.dumpjson(svpth,dic)
	
img2PID_dic_rough_svpth=pyxyvPth+r'\save\img2piddic_rough_save'
def getImgPID_rough(i):
	kwargs={"length":70,"offs":1,"rm":None,"w":8}
	hash_=myhash.hashs(myhash.phashi(i,**kwargs))
	dic={}
	for j in ['.json','_'+hash_[:2]+'.json',hash_[:2]+'.json']:
		svpth=img2PID_dic_rough_svpth+j
		if(path.exists(svpth)):
			try:
				dic.update(json.loads(myio.opentext(svpth)))
			except Exception:
				pass
		
	#print(len(dic))
	if(hash_ in dic):
		return dic[hash_]
	else:
		return 'NO_IMG_ERR'
def saveImgPID_rough(i,PID):
	kwargs={"length":70,"offs":1,"rm":None,"w":8}
	hash_=myhash.hashs(myhash.phashi(copy.copy(i),**kwargs))
	print(hash_)
	svpth=img2PID_dic_rough_svpth+'_'+hash_[:2]+'.json'
	print(svpth)
	dic={}
	if(path.exists(svpth)):
		try:
			dic.update(json.loads(myio.opentext(svpth)))
		except Exception:
			pass
	dhash_=dic.get(hash_,{})
	dhash_[PID]=1
	dic[hash_]=dhash_
	fh=open(svpth,'w')
	fh.write(json.dumps(dic))
	fh.close()
	

	
def getToday():
	#connection_throttle.acquire()
	t=lcg_s.gettext(r'https://www.pixiv.net/ranking.php?mode=daily')
	f=re.findall(r'<link rel="canonical" href="https://www.pixiv.net/ranking.php\?mode=daily&amp;date=(\d{8})">',t)[0]
	return datetime(year=int(f[:4]),month=int(f[4:6]),day=int(f[6:]))
def getImageURLsByPID(pid=70829971):
	#print(getImgPID(r"D:\pyxyv\tempcache\4GFfby.png"))
	
	url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s'%pid
	#connection_throttle.acquire()
	h=lcg.gettext(url)
	
	info=getIllustInfoByPID(pid=pid)
	if('ERR' in info):
		return info
	#print(info['pageCount'])
	ret={}
	if(info['pageCount']==1):
		ret['pages']=[(info['original_info']['urls']['original'],url)]
		ret['master1200']=[(info['original_info']['urls']['regular'],url)]
		ret['len']=1
		return ret
	else:
		ret['pages']=[]
		ret['referurl']=[]
		ret['len']=info['pageCount']		
		hmangamode=lcg.gettext('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s'%pid)
		#print(lcg.getpath('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s'%pid))
		u=json.loads(re.findall(r'"urls":(\{.+?\})',hmangamode)[0])
		p0=u["regular"]
		ret['master1200']=[p0.replace("_p0_","_p%d_"%i) for i in range(info['pageCount'])]
		ret['master1200']=[(j,'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s'%pid)for j in ret['master1200']]
		#print(ret['master1200'])
		for i in range(info['pageCount']):
			#connection_throttle.acquire()
			
			url=r'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=%s&page=%s'%(pid,i)
			#connection_throttle.acquire()
			h=lcg.gettext(url)
			#print('findallpurl',re.findall(r'src="(https://i.pximg.net/img-original/img/.+?/%s_p.+?)"'%pid,h))
			ret['pages'].append((re.findall(r'src="(https://i.pximg.net/img-original/img/.+?/%s_p.+?)"'%pid,h)[0],url))
			#ret['referurl'].append(url)
		#print(ret['len'])
		#print(ret['pages'])
		#print(ret['referurl'])
		return ret
	return None

def getImageBinariesByPID(pid=70829971):
	imageURLs=getImageURLsByPID(pid=pid)
	if('ERR' in imageURLs):
		return imageURLs
	ret=[]
	for i in range(imageURLs['len']):
		iurl=imageURLs['pages'][i][0]
		ext=re.findall('\.jpg|\.png|\.gif|\.bmp|\.jpeg',iurl, flags=re.IGNORECASE)[0]
		rurl=imageURLs['pages'][i][1]
		#connection_throttle.acquire()
		ret.append((lcg.getbin(iurl,headerex={'Referer':rurl},retry=8),ext))
	return ret
def getThumbedImageFilesByPID(pid=70829971,svpth=pyxyvPth+r'\tempimgcache\\'):
	return getImageFilesByPID_(pid=pid,quality='regular',svpth=svpth)
	imageURLs=getImageURLsByPID(pid=pid)
	if('ERR' in imageURLs):
		return imageURLs
	ret=[]
	for i in range(imageURLs['len']):
		iurl=imageURLs['master1200'][i][0]
		rurl=imageURLs['master1200'][i][1]
		#connection_throttle.acquire()
		bi=lcg.getbin(iurl,headerex={'Referer':rurl},retry=8)
		savpth=svpth+'\\'+myhash.hashs(myhash.hashi(bi))+'.jpg'
		ret.append(savpth)
		savebin(savpth,bi)
		saveImgPID(savpth,pid)
		saveImgPID_rough(savpth,pid)
		
	return ret
	
def getImageFilesByPID(pid=70829971,svpth=pyxyvPth+r'\tempimgcache\\'):
	binaries=getImageBinariesByPID(pid)
	if('ERR' in binaries):
		return binaries
	ret=[]
	for bi,ext in binaries:
		svpath=svpth+'\\'+myhash.hashs(myhash.hashi(bi))+ext
		
		savebin(svpath,bi)
		ret.append(svpath)
	for i in ret:
		saveImgPID(i,pid)
		saveImgPID_rough(i,pid)
	return ret

illust_info_cache=myhash.splitedDict(pth=pyxyvPth+r'\illust_info_cache',splitMethod=lambda x:str(x)[:3])

	
def getIllustInfoByPID(pid=70793074):
	if(str(pid) in illust_info_cache):
		ret=illust_info_cache[str(pid)]
		if(ret.get("exptime",0)>time.time()):
			#print('cached ill info for',pid)
			return ret
		else:
			#print('ill info expires',pid)
			pass
	url='https://www.pixiv.net/artworks/%s'%pid
	#connection_throttle.acquire()
	h=lcg.gettext(url)
	'''myio.savetext(r'D:\temp.html',h)
	__import__("os").system(r'explorer D:\temp.html')
	exit()'''
	temp=re.findall(r'%s:[\s\S]*?(\{.+\}) },user:'%pid,h)
	temp=temp or re.findall(r'({"illustId":"%s"[\s\S]+?})},"user'%pid,h)
	if(not(temp)):
		return 'NO_ILLUST_INFO_ERR'
	temp=temp[0]
	#print('temp',temp)
	ret={}
	try:
		dic=json.loads(temp)
		#print(dic)
	except Exception:
		return 'JSON_LOAD_EXCEPTION_ERR'
	for i in ['pageCount','bookmarkCount','likeCount',"userName","userId"]:
		if i in dic:
			ret[i]=dic[i]
	ret['tags']=dic['tags']['tags']
	ret['url']=url
	ret['tags_']=[i['tag'] for i in ret['tags']]+['userName:'+ret['userName']]
	ret['p0_urls']=dic['urls']
	if('userId' in ret):
		ret['userURL']=r'https://www.pixiv.net/users/%s'%ret['userId']
	ret['original_info']=dic
	ret['illustTitle']=dic['illustTitle']
	ret['exptime']=time.time()+lcg.expiretime
	illust_info_cache[str(pid)]=ret
	return ret
	
#print(getIllustInfoByPID())
def randomCrawl():
	timer1=timer.timer()
	pids=range(70396480,70396495)
	pids=[70396493]
	
	leng=233
	
	pids=set([random.randint(68396400,70396400) for i in range(leng)])
	
	#pids=[70558528,70676743,70064554]
	
	leng=len(pids)
	for pid in pids:
		print('=====\nPID',pid)
		try:
			info=getIllustInfoByPID(pid)			
			if(info=='NO_ILLUST_INFO_ERR'):
				print('NO_ILLUST_INFO_ERR')
				leng-=1
				continue
			elif(info['bookmarkCount']<150):
				print('NOT_WELL_bookmarked')
				leng-=1
				continue
			elif(info['pageCount']>10):
				print('TO_MUCH_PAGE')
				leng-=1
				continue
			print(getThumbedImageFilesByPID(pid))
			#time.sleep(1.5)
		except Exception as e:
			
			print(str(e))
			print(traceback.format_exc())
			leng-=1
	print(leng)
	print(timer1.gettime())
	print(getImgPID(r"D:\pyxyv\tempimgcache\1dlp0d2FWYm2Cv.jpg"))
	'''
	for i in getImageFilesByPID(71170430):
		print(img2filename(bin2img(i)))'''
def getRanking(mode='daily',page='1',date=None,datedelta=0,content='illust'):					#mode in ['daily','weekly','monthly','']
	delta1day=timedelta(days=1)
	if(not(date)):
		date=getToday()
		if(datedelta):
			
			datedelta=abs(int(datedelta))
			
			date=date-datedelta*delta1day
	if(not(isinstance(date,str))):
		date=date.strftime('%Y%m%d')
	
	params={'mode':mode,'p':page,'content':content,'format':'json'}
	if(date!=datetime.now().strftime('%Y%m%d')):
		params['date']=date
	url='https://www.pixiv.net/ranking.php?'+urlencode(params)
	#connection_throttle.acquire()
	#print(url)
	h=lcg.gettext(url)
	d=json.loads(h)
	d['content_num']=len(d['contents'])
	d['preview_pic_referer']=url
	#print(url)
	#print([i for i in d])
	return d

	
def search(keyword='白タイツ',page=1,order='date_d',mode='safe'):
	if(isinstance(keyword,list)):
		word=' '.join(keyword)
	else:
		word=keyword
	params={}
	params['word']=word
	params['p']=page
	params['order']=order
	params['mode']=mode
	params['s_mode']='s_tag'
	url='https://www.pixiv.net/ajax/search/artworks/%s?'%word+urlencode(params)
	#print(url)
	#connection_throttle.acquire()
	h=lcg.gettext(url).replace('&quot;','"')
	
	# myio.savetext(r'E:\temp.html',h)
	# import os
	# os.system(r"explorer E:\temp.html")
	
	j=json.loads(h)['body']
	
	#f=re.findall('({"illustId"([^{}]|{.+?})+?})',h)
	f=j['illustManga']['data']
	ret={}
	ret['preview_pic_referer']='https://www.pixiv.net/search.php?'+urlencode(params)
	#print('preview_pic_referer',ret['preview_pic_referer'])
	ret['total_num']=j['illustManga']['total']
	ret['content_num']=len(f)
	ret['results']=f
	ret['contents']=ret['results']
	return ret
def getRelatedRecommendedPIDs(pid=70558528,limit=18):
	r=r'https://www.pixiv.net/artworks/%s'%pid
	
	url=r"https://www.pixiv.net/ajax/illust/%s/recommend/init?limit=%d&lang=zh"%(pid,limit)
	#connection_throttle.acquire()
	
	t=lcg_s.gettext(url,headerex={"Referer":r})
	#print(t)
	dic=json.loads(t)
	return dic['body']['nextIds']
def bfsRecommandCrawl(urls=None,timelimit=20,wait=1.1,allow_R18=False,svpth=pyxyvPth+r'\tempimgcache\\',bookmarkmin=100,start_pid=[70805502],numlimit=2,pagerecommendlimit=10,pagecountlimit=4,muchbookmarkedsvpth=None,bookmarkmuch=1900,callback=None,callback_kwargs=None,restrict_tags=None):
	start_t=time.time()
	visited=set([])
	head=0
	if(callback_kwargs is None):
		callback_kwargs={}
	re_=re.compile(r'https://www.pixiv.net/artworks/\d+')
	re__=re.compile(r'artworks/(\d+)')
	if(not(muchbookmarkedsvpth)):
		muchbookmarkedsvpth=svpth
	if(not(urls)):
		urls=[r'https://www.pixiv.net/artworks/'+str(startpid) for startpid in start_pid]
	print(urls)
	print(svpth)
	print(muchbookmarkedsvpth)
	print(bookmarkmin,bookmarkmuch)
	
	
	while((head<len(urls)and((time.time()-start_t)<timelimit))and(head<numlimit)):
		crawl_throttle.acquire()
		url=urls[head]
		if(url in visited):
			print('visited')
			head+=1
			continue
		visited.add(url)
		if(re_.match(url)):
			print('\n=====illustpage:%s,num=%d=====\n'%(url,head+1))
			try:
				pid=re__.findall(url)[0] 
				print(pid)
				
				
				
				time.sleep(wait)
				info=getIllustInfoByPID(pid)	
				if(info=='NO_ILLUST_INFO_ERR'):
					print('NO_ILLUST_INFO_ERR')
					
					
				elif((info['bookmarkCount']<bookmarkmin)and(not(pid in start_pid))):
					print('NOT_WELL_bookmarked')
					
					
				elif(info['pageCount']>pagecountlimit and(not(pid in start_pid))):
					print('TO_MUCH_PAGE')
					
				
					
				elif(not(allow_R18) and ('R-18' in info['tags_']) and(not(pid in start_pid))):
					print('R-18_SKIP')
				elif(restrict_tags and not(set(restrict_tags).intersection(set(info['tags_'])))):
					print("no related tag")
				else:
					if(info['bookmarkCount']>bookmarkmuch):
						print('muchbookmarked')
						cbInfo={"pid":pid}
						cbInfo["content"]=getImageFilesByPID_(pid,svpth=muchbookmarkedsvpth,quality='original')
						print(cbInfo)
					else:
						cbInfo={"pid":pid}
						cbInfo["content"]=getThumbedImageFilesByPID(pid,svpth=svpth)
						print(cbInfo)
					if(cbInfo and callback):
						callback_kwargs['crawl_info']=cbInfo
						callback(**callback_kwargs)
					pids=getRelatedRecommendedPIDs(pid)
					
					if(len(pids)>pagerecommendlimit):
						pids=random.sample(pids,pagerecommendlimit)
					urls+=[r'https://www.pixiv.net/artworks/%s'%i for i in pids]
					
			except Exception as e:
				
				print(str(e))
				print(traceback.format_exc())
		
		head+=1
	print(head,time.time()-start_t)
	return head

def results2pic(results,trimedPid,jobs1=None,tpidlock=None,result_title=None):
	if(not(jobs1)):
		jobs1=jobs()
	
	for j in range(len(results['contents'])):
		i=results['contents'][j]
		for k in ['illustId','illust_id']:
			if(k in i):
				pxid=str(i[k])
		if(('R-18' in i['tags'])or('R-18G' in i['tags'])):
			continue
		purl=i['url']
		tkwa={'url':purl,'headerex':{'Referer':results['preview_pic_referer']},'retry':8}
		kwa={'target':lcg.get_image,'kwargs':tkwa,'name':j}
		jobs1.start(kwa)
	
	jret=jobs1.getReturns()		#获得子线程返回值，是get二进制格式的图片
	il=pic2pic.ImageLib()
	for idx in jret:
		#print(name)
		content=results['contents'][idx]
		title=content.get("title",None) or content.get("illustTitle",None)
		name=content.get("illust_id",None) or content.get("illustId",None) or content.get('id',None)
		p=jret[idx].convert('RGBA')	#打开二进制图片，转换成RGBA格式
		res=min(p.size)
		res=(res,res)
		p=pic2pic.imBanner(p,res)
		
		txthei=int(res[0]*0.15)	#文字高度
		#locktpid=locker_.getlock('tpid')
		#locktpid.acquire()
		if(tpidlock):
			tpidlock.acquire()					#线程锁，防止多个查看搜索结果的指令扰乱了简化id
		hashed=myhash.phashs(p).lower()
		tpid=trimedPid.add(hashed,name)
		if(tpidlock):
			tpidlock.release()
		#locktpid.release()
		
		#加字
		border=res[0]//20
		res=(res[0]+border*2,res[1]+txthei*2+border*2)
		p1=Image.new("RGB",res,(255,255,255))
		p1.paste(p,(border,border))
		iPid=pic2pic.txt2im("%s / %s"%(name,tpid),bg=(255,255,255,255)).convert("RGB")
		iPid=pic2pic.fixHeight(iPid,txthei)
		if(iPid.size[0]>p.size[0]):
			iPid=pic2pic.fixWidth(iPid,p.size[0])
		p1.paste(iPid,(border,border+p.size[1]))
		iTitle=pic2pic.fixHeight(pic2pic.txt2im(title,bg=(255,255,255,255)),txthei)
		if(iTitle.size[0]>p.size[0]):
			iTitle=iTitle.crop((0,0,p.size[0],txthei))
		p1.paste(iTitle,(border,border+p.size[1]+txthei))
		
		il.openImage(p1)		#合成大图的ImageLib，见pic2pic.py
	n=len(results['contents'])
	col=int((n*0.9)**0.5)				#合成大图的列数量
	siz=col*180							#合成大图的宽度
	ret=il.allthumb(wid=[300]*col)
	if(result_title):
		iTitle=pic2pic.txt2im(result_title,bg=(255,255,255,255))
		iTitle=pic2pic.im_sizelimitmax(iTitle,(ret.size[0],ret.size[0]//6))
		ret_=Image.new("RGB",(ret.size[0],ret.size[1]+iTitle.size[1]),(255,255,255))
		ret_.paste(ret,(0,iTitle.size[1]))
		ret_.paste(iTitle,(0,0))
		return ret_
	#retfile=img2filename(ret,convert='RGB',type='JPEG')
	return ret

defaultCrawl=bfsRecommandCrawl

def aaa():#(__name__=='__main__'):
	#defaultCrawl(urls=Noe,start_pid=[70831662],wait=0,timelimit=float('inf'),numlimit=114514)
	for pid in set([73812374,73848679,73865462,73876597,73893989,73908835,73908878,73772001,73848679,73848679,73876597,73692879,73669300,73675032,73663995,73661826,73532276,73524871,73567493,73477134,73471695,73466037]):
		print(getImageFilesByPID(pid,svpth=r'M:\pic\meaqua\\'))
		print(getImageFilesByPID(pid,svpth=r'M:\pic\mea\\'))
	
	#open('d:\\temp.txt','w',encoding='utf-8').write(str(f))
	#print(len(getRelatedRecommendedPIDs()))
	
def getGif(pxinfo):
	url=pxinfo['p0_urls']['original']
	url=url.replace('img-original','img-zip-ugoira')
	url=url.replace('0.jpg','600x600.zip')
	id=pxinfo['original_info']['id']
	referer=r'https://www.pixiv.net/'
	ret=lcg.get_path(url,headerex={"Referer":referer})
	zfile=zipfile.ZipFile(ret)
	pth=path.join(pyxyvPth,'gif','extract',id)
	if(not path.exists(pth)):
		os.makedirs(pth)
	imgs=[]
	for i in zfile.namelist():
		imgs.append(Image.open(zfile.extract(i,pth)))
	ret=make_gif(imgs,pth=path.join(pyxyvPth,'gif','make'))
	
	return ret
	
def getImageFilesByPID_(pid,pages=None,quality="regular",svpth=pyxyvPth+r'\tempimgcache'):
	pxinfo=getIllustInfoByPID(pid)
	#print(pxinfo)
	p0url=pxinfo['p0_urls'][quality]
	#print(pxinfo['p0_urls'])
	if('ugoira' in pxinfo['p0_urls']['original']):
		return [getGif(pxinfo)]
	ret=[]
	headerex={'Referer':pxinfo['url']}
	pages=pages or range(int(pxinfo['pageCount']))
	for i in pages:
		purl=p0url.replace("_p0","_p%d"%i)
		#print(headerex)
		b=lcg.getbin(purl,headerex=headerex,retry=8)
		name=path.basename(purl)
		myio.savebin(svpth+'\\'+name,b)
		ret.append(svpth+'\\'+name)
	for i in ret:
		saveImgPID(i,pid)
		saveImgPID_rough(i,pid)
	#print(ret)
	return ret
getUserIDByName_save=myhash.splitedDict(pth=pyxyvPth+r'\getUserIDByName_save')
def getUserIDByName(username):
	if(username in getUserIDByName_save and getUserIDByName_save[username]):
		return getUserIDByName_save[username]
	url=r'https://www.pixiv.net/search_user.php?s_mode=s_usr&nick=%s'%username
	print(url)
	t=lcg_s.gettext(url)
	# myio.savetext(r'C:\temp\temp.html',t)
	# os.system(r'explorer C:\temp\temp.html')
	pattern=r'<h1><a href="/users/(\d+)" target="_blank" class="title">[\s\S]+?</a></h1>'
	#myio.savetext(r'D:\temp.html',t)
	# os.system(r"explorer D:\temp.html")	
	#exit()
	ret=re.findall(pattern,t)
	getUserIDByName_save[username]=ret
	print(username,ret)
	return ret
def getUserInfo(uid=None,username=None,page=1):
	print(f'pyxyv lineno580uid={uid}username={username}page={page}')
	if(not(uid)):
		print('get uid from username')
		if(not(username)):
			return None
		uid=getUserIDByName(username)
		if(not(uid)):
			return None
		else:
			uid=uid[0]
	params={"id":uid,'type':'illust','p':page}
	url='https://www.pixiv.net/member_illust.php?'+urlencode(params)
	# print(url)
	ret={}
	t=lcg_m.gettext(url)
	# myio.savetext(r'D:\temp.html',t)
	# os.system(r'explorer D:\temp.html')
	user_info=json.loads(re.findall(r'content=\'({"timestamp"[\s\S]+?})\'>',t)[0])['user'][str(uid)]
	user_info1=json.loads(lcg_m.gettext(r'https://www.pixiv.net/ajax/user/%s/profile/all'%uid,headerex={'Referer':url}))
	ret['name']=user_info['name']
	if(username):
		if(not(username.lower() in ret['name'].lower())):	
			getUserIDByName_save.pop(username,None)
	illusts=user_info1['body']['illusts']
	ret['illusts_all']=list(illusts)
	ret['illusts_num']=len(illusts)
	ret['page_num']=(ret['illusts_num']-1)//48+1
	ret['page']=page
	ret['illusts']=list(illusts)[(page-1)*48:min(page*48,len(illusts))]
	illusts_info={}
	for illusts in splitList(ret['illusts'],10):
		illusts_=["ids[]=%s"%i for i in illusts]
		u=r'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s&work_category=illust&is_first_page=1'%(uid,"&".join(illusts_))
		#print(u)
		j=json.loads(lcg.gettext(u,headerex={"Referer":url}))
		illusts_info.update(j['body']['works'])
	ret['illusts_info']=illusts_info
	ret['works']=illusts_info
	ret['avatar']=user_info['imageBig']
	ret['avatar_small']=user_info['image']
	ret['avatar_big']=user_info['imageBig']
	
	if(user_info['background']):
		ret['banner']=user_info['background']['url']
	
	ret['uid']=user_info['userId']
	ret['url']=url
	
	return ret
def usr_info2pic(uinfo,trimedPid,tPidLock=None,blockedTags={'R-18','R-18G'}):
	width=1200
	'''print(uinfo['illusts'])
	for i in uinfo['illusts']:
		print(uinfo['illusts_info'][i]['tags'])'''
	illusts=[i for i in uinfo['illusts'] if(not( set(uinfo['illusts_info'][i]['tags']).intersection(blockedTags) ))]
	column=int(len(illusts)**0.5)
	#row=8
	jbs=jobs()
	illust_size=width/column
	illust_textSize=0.15
	illust_size=(int(illust_size),int((1+2*illust_textSize)*illust_size))
	banner_height=int(width/3.3)
	avt_size=int(banner_height/1.5)
	avt_top=int(banner_height-avt_size*0.7)
	avt_left=int(width*0.2-avt_size/2)
	avt_pos=(avt_top,avt_left)
	username_height=avt_size//3
	username_top=int(avt_top+avt_size-username_height/2)
	username_left=avt_left+avt_size+username_top-banner_height
	illust_top=username_top+username_height+(username_top-banner_height)
	illust_border=0.05
	illust_size_=tuple([int(i*(1-illust_border*2)) for i in illust_size])
	illust_offset_top=(illust_size[1]-illust_size_[1])//2
	illust_offset_left=(illust_size[0]-illust_size_[0])//2
	
	
	rfurl=uinfo['url']
	print(rfurl)
	def getIllustPic(idx,size):
		pid=illusts[idx]
		rfurl=uinfo['url']
		
		info=uinfo['illusts_info'][pid]
		url=info['url']
		pid=info['id']
		title=info['title']
		theight=(size[1]-size[0])//2
		ppsize=size[0]
		illust_pic=Image.new("RGBA",size,(255,255,255,255))
		try:
			i=lcg.get_image(url,headerex={"Referer":rfurl},retry=8).resize((size[0],size[0]),Image.LANCZOS).convert("RGBA")
		except Exception as e:
			i=Image.new("RGBA",(ppsize,ppsize),(255,255,255,255))
		
		illust_pic.paste(i,(0,0))
		ititle=pic2pic.fixHeight(pic2pic.txt2im(title,bg=(255,255,255,255)),theight)
		
		illust_pic.paste(ititle,(0,ppsize+theight))
		if(tPidLock):
			tPidLock.acquire()
		tPid=trimedPid.add(myhash.phashs(i).lower(),pid)
		#iTPid=pic2pic.fixHeight(pic2pic.txt2im(tPid,bg=(255,255,255,255)),theight)
		#illust_pic.paste(iTPid,(0,ppsize+theight*2))
		if(tPidLock):
			tPidLock.release()
		ipid=pic2pic.txt2im(pid+' / '+tPid,bg=(255,255,255,255))
		ipid=pic2pic.im_sizelimitmax(ipid,(size[0],theight))
		illust_pic.paste(ipid,(0,ppsize))
		return illust_pic
	
	res=(width,illust_top+illust_size[1]*(1+(len(illusts)-1)//column))
	print("uinfo size",res,res[1]/res[0])
	#print(len(illusts))
	avt_size=(avt_size,avt_size)
	
	ret=Image.new("RGB",res,(255,255,255))
	ibanner=lcg.get_image(uinfo.get('banner',uinfo['avatar_big']),referer=rfurl,retry=8)
	ibanner=pic2pic.imBanner(ibanner,(width,banner_height))
	ret.paste(ibanner,(0,0))
	ret.paste(lcg.get_image(uinfo['avatar_big'],referer=rfurl,retry=8).resize(avt_size,Image.LANCZOS),(avt_left,avt_top))
	iname=pic2pic.fixHeight(pic2pic.txt2im(uinfo['name'],bg=(255,255,255,255)),username_height)
	ret.paste(iname.convert("RGB"),(username_left,username_top))
	pagenum_t='第%s/%s页'%(uinfo['page'],uinfo['page_num'])
	ipagenum=pic2pic.fixHeight(pic2pic.txt2im(pagenum_t,bg=(255,255,255,255)),username_height//2).convert("RGB")
	ret.paste(ipagenum.convert("RGB"),(username_left+iname.width+(username_top-banner_height),username_top+username_height//4))
	for idx,pid in enumerate(illusts):
		tkwa={'idx':idx,"size":illust_size_}
		kwa={"target":getIllustPic,"kwargs":tkwa,"name":idx}
		jbs.start(kwa)
	for idx,i in jbs.getReturns().items():
		
		c=int(idx)%column
		r=int(idx)//column
		top=illust_offset_top+r*illust_size[1]+illust_top
		left=illust_offset_left+c*illust_size[0]
		ret.paste(i,(left,top))
	return ret
def splitList(ls,size):
	return [ls[i:min((i+size,len(ls)))] for i in range(0,len(ls),size)]


def test_user():
	td=myhash.trimDict()
	t1=timer.timer()
	for uname in ['翼','逆流茶会']:
		t1.settime()
		uids=getUserIDByName(uname)
		print("get_uid time",t1.gettime(),uids)
		info=getUserInfo(username=uname,page=1)
		print("get_info_time",t1.gettime())
		#myio.dumpjson(r"J:\temp.json",info)
		i=usr_info2pic(info,td)
		print('illustrating used %.2f sec'%t1.gettime())
		i.show()
def test_get_pid():
	i=Image.open(r"E:\new\CQ\2\data\image\478EF91FDB3137B9ABDF673C68D7C5FB.png")
	import getimgpid
	p=getimgpid.getPixivPID(r"E:\new\CQ\2\data\image\478EF91FDB3137B9ABDF673C68D7C5FB.png")
	print(p)
	
	print(getIllustInfoByPID(p))
	print(getImageFilesByPID(p))
	for i in getImageFilesByPID(p):
		print(myhash.hashs(i))
	
def test_ranking_pic():
	#r=search()
	r=getRanking()
	myio.dumpjson(pyxyvPth+r'\temp.json',r)
	
	#print(r)
	p=results2pic(r,myhash.trimDict(),result_title="每日排行")
	p.show()
	
	r=search()
	myio.dumpjson(pyxyvPth+r'\temp.json',r)
	
	#print(r)
	p=results2pic(r,myhash.trimDict(),result_title="？")
	p.show()
	
	
def temp_bfs_craw():
	restrict_tags=['神楽めあ','湊あくあ','Meaqua','meaqua','めあくあ']
	bfsRecommandCrawl(timelimit=float('inf'),urls=None,start_pid=[72216137,74846970,74585952,74239871,76116003,76148700,72881232],svpth=r'M:\pic\temp\craw_meaqua',numlimit=114514,restrict_tags=restrict_tags,allow_R18=True,bookmarkmuch=500,bookmarkmin=86,wait=0.5)
def illust_illust_info(info,imMain,title='<illustTitle> by <userName>',bbl_res=None,blur_if_ns=True,func_tag_extra_text=None):
	#info=recent_sent_setu_illust_info[group_id]
	for i in info:
		title.replace('<%s>'%i,str(info[i]))
	if('original_info' in info):
		oinfo=info['original_info']
		for i in oinfo:
			title.replace('<%s>'%i,str(oinfo[i]))
	
	#pth=recent_sent_setu_pth[group_id]
	puserId=info['userId']
	#uinfo=pyxyv.getUserInfo(uid=puserId)
	width=400
	banner_height=width//8
	gold_rate=(1+5**0.5)/2
	username_height=int(banner_height/gold_rate)
	tag_height=int(username_height/1.618)
	username_top=int((banner_height-username_height)/2)
	
	#usr_url=uinfo['url']
	'''imBanner=pyxyv.lcg.get_image(uinfo.get('banner',uinfo['avatar_big']),referer=usr_url)
	imBanner=pic2pic.imBanner(imBanner,(1080,200))'''
	imBanner=Image.new("RGBA",(width,banner_height),(46,151,216,255))
	
	#imMain=Image.open(pth)
	imMain=pic2pic.imBanner(imMain,(width,int(width*1.18)))
	print(info['tags_'])
	if(blur_if_ns and ('R-18' in info['tags_'])):
		imMain=imMain.filter(ImageFilter.GaussianBlur(width//20))
	imUsername=pic2pic.txt2im(title,fixedHeight=username_height,fill=(255,)*4)
	imBanner.paste(imUsername,box=(username_top,username_top),mask=imUsername)
	
	tmp=[]
	if(bbl_res is None):
		_=pathManager(appname='setubot-iot').getpath(session='mainpth')
		bbl_res=pic2pic.load_bubble(path.join(_,'static_pics','bubble2'))
	for i in info['tags_']:
		if(func_tag_extra_text):
			i+=' '+func_tag_extra_text(i)
		txt=pic2pic.txt2im(i,fixedHeight=tag_height,fill=(41,96,165,255),shadow_fill=(255,255,255,230),shadow_delta=(width//200,width//200))
		bbl=pic2pic.bubble(txt,**bbl_res)
		tmp.append(bbl)
	imTags=pic2pic.horizontal_layout(tmp,border=2,width=width)
	
	height=imBanner.size[1]+imMain.size[1]+imTags.size[1]
	ret=Image.new("RGBA",(width,height))
	ret.paste(imBanner,(0,0))
	ret.paste(imMain,(0,imBanner.size[1]))
	ret.paste(imTags,(0,imBanner.size[1]+imMain.size[1]))
	return ret
if(__name__=='__main__'):
	
	#info=getIllustInfoByPID(81730617)
	#print(getImageFilesByPID_(85763605,quality='regular'))
	test_ranking_pic()
	#ims=getImageFilesByPID_(81730617,quality='regular')
	#illust_illust_info(info,Image.open(ims[0])).save(r'G:\temp.png')
	