import getheader,random,copy,myhash,time,requests,json,myio
import threading
from PIL import Image
from mytimer import timer,throttle
#from workpathmanager import pathManager
from myio import *
from glob import glob
from os import path
header=getheader.headers
headers=header
proxy_dict = {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081"
}



#wpm=pathManager(appname='lcg_general')
dbg=False
#hashs=lambda x:myhash.hashs(myhash.hashi(x,leng=18,offs=7))
def hashi(s,le=10):
	reti=0
	for idx,i in enumerate(s):
		reti^=ord(i)<<(idx%le)
	return reti
def hashs(s):
	return hex(hashi(s,16))[2:]
def cookie_json2cookiejar(dic):
	cookiejar=requests.cookies.RequestsCookieJar()
	for i in dic:
		for j in ['id', 'httpOnly', 'sameSite', 'expirationDate', 'session', 'hostOnly', 'storeId']:
			if(j in i):
				i.pop(j)
		cookiejar.set(**i)
	return cookiejar
#defPth=wpm.getpath(session='mainpth',ask_when_dne=True)
#print(defPth)
defPth=path.join(path.dirname(__file__),'temp')
class localCachingGeter:
	def c_t_a(self):
		#print('acq')
		
		if(self.connection_throttle):
			if(self.connection_throttle.is_busy()):
				#print("lcg busy",self.connection_throttle.wait_time())
				pass
			ret=self.connection_throttle.acquire()
			#print('acq ok')
			# return ret
	connection_throttle_acuire=c_t_a
	def __init__(self,workpth=defPth,expiretime=2,proxies=None,maxCacheNum=2000,lock=None,cookies=None,connection_throttle=(30,2)):
		self.savepth=path.join(workpth,'tempcache')
		self.exptime_save_pth=path.join(workpth,'save','exptime_%s'%expiretime)
		self.exptimes={}
		self.text_mem={}
		self.bin_mem={}
			

		if(proxies is None):
			proxy_dict = {
				"http": "http://127.0.0.1:1081",
				"https": "http://127.0.0.1:1081"
			}
			self.proxies=proxy_dict
		else:
			self.proxies=proxies
		self.cookies=cookies
		#self.exptimes['']={}
		if(isinstance(connection_throttle,tuple)):
			self.connection_throttle=throttle(*connection_throttle)
		elif(isinstance(connection_throttle,throttle)):
			self.connection_throttle=throttle
		else:
			self.connection_throttle=None
		if(lock==True):
			self.lock=threading.Lock()
		else:
			self.lock=None
		self.maxCacheNum=maxCacheNum
		for i in glob(path.join(self.exptime_save_pth,'exptime_save*.json')):
			try:
				i_=i.replace(path.join(self.exptime_save_pth,'exptime_save'),'').replace('.json','')
				self.exptimes[i_]=json.loads(opentext(i))
			except Exception:
				pass
		self.expiretime=expiretime
	def getsavepth(self,url,headers=header,proxies=None,cookies=None,headerex={},expiretime=None,type='text',referer=None,**kwargs):
		header_=copy.deepcopy(headers)
		if(referer):
			headerex["Referer"]=referer
		header_.update(headerex)
		if(proxies is None):
			proxies=self.proxies
		if(expiretime==None):
			expiretime=self.expiretime
		#print(time.time())
		if(headerex):
			hash_=hashs(url+str(headerex))
		else:
			hash_=hashs(url)
		if(type=='text'):
			ext='.html'
		else:
			ext='.tmp'
		savepth=path.join(self.savepth,'%s%s'%(hash_,ext))
		return savepth
	getpath=getsavepth
	def gettext(self,url,headers=header,proxies=None,cookies=None,headerex={},expiretime=None,retry=3,referer=None):
		
		header_=copy.deepcopy(headers)
		if(proxies is None):
			proxies=self.proxies
		if(referer):
			headerex["Referer"]=referer
		header_.update(headerex)
		if(cookies is None):
			cookies=self.cookies
		if(expiretime==None):
			expiretime=self.expiretime
		#print(time.time())
		if(headerex):
			hash_=hashs(url+str(headerex))
		else:
			hash_=hashs(url)
		savepth=path.join(self.savepth,'%s.html'%hash_)
		#print(url,savepth)
		if(not( hash_[:2] in self.exptimes)):
			self.exptimes[hash_[:2]]={}
			
		#exptimes_=self.exptimes['']
		exptimes_=(self.exptimes[hash_[:2]])
		if(url in exptimes_):
			if(exptimes_[url]>time.time()):
				if(hash_ in self.text_mem):
					#print('mem cache')
					return self.text_mem[hash_]
				elif(path.exists(savepth)):
					#print('cached',url)
					h=opentext(savepth)
					self.text_mem[hash_]=h
					return opentext(savepth)
				elif(dbg):
					print("cache file not fount")
			else:
				self.text_mem.pop(hash_,None)
		elif(dbg):
			print('exptime_dne')
		self.exptimes[hash_[:2]][url]=int(time.time()+expiretime)
		if(dbg):
			print(url)
		while(retry>=1):
			try:
				self.c_t_a()
				r=requests.get(url,headers=header_,proxies=proxies,cookies=cookies)
				break
			except Exception as e:
				print(e)
				pass
			retry-=1
		#h=decodebstr(r.content)
		self.c_t_a()
		r=requests.get(url,headers=header_,proxies=proxies,cookies=cookies)
			
		#r=requests.get(url,headers=header_,proxies=proxies,cookies=cookies)
		
		#print(str(r.cookies))
		if(r.status_code!=200):
			print('GET HTTP ERR')
			print(url,headers,proxies,headerex)
			print(r.text)
			r.raise_for_status()
			return None
		
		savebin(savepth,r.content)
		try:
			h=r.content.decode('utf-8')
		except Exception as e:
			
			h=myio.opentext(savepth)
		
		self.save(hash_[:2])
		self.text_mem[hash_]=h
		return h
	def get_path(self,url,headers=header,proxies=None,cookies=None,headerex={},expiretime=None,referer=None):
		header_=copy.deepcopy(headers)
		if(proxies is None):
			proxies=self.proxies
		if(referer):
			headerex["Referer"]=referer
		header_.update(headerex)
		#print(time.time())
		if(expiretime==None):
			expiretime=self.expiretime
		if(headerex):
			hash_=hashs(url+str(headerex))
		else:
			hash_=hashs(url)
		self.getbin(url,headers=headers,proxies=proxies,cookies=cookies,headerex=headerex,expiretime=expiretime)
		savepth=path.join(self.savepth,'%s.tmp'%hash_)
		return savepth
	def getbin(self,url,headers=header,proxies=None,cookies=None,headerex={},expiretime=None,retry=3,referer=None):
		header_=copy.deepcopy(headers)
		if(proxies is None):
			proxies=self.proxies
		if(referer):
			headerex["Referer"]=referer
		header_.update(headerex)
		#print(time.time())
		if(cookies is None):
			cookies=self.cookies
		
		if(expiretime==None):
			expiretime=self.expiretime
		if(headerex):
			hash_=hashs(url+str(headerex))
		else:
			hash_=hashs(url)
		savepth=path.join(self.savepth,'%s.tmp'%hash_)
		if(not( hash_[:2] in self.exptimes)):
			self.exptimes[hash_[:2]]={}
		#print(url,savepth)
#		exptimes_=self.exptimes['']
		exptimes_=self.exptimes[hash_[:2]]
		#print(savepth)
		if(url in exptimes_):
			if(exptimes_[url]>time.time()):
				if(path.exists(savepth)):
					#print('cached',url)
					fh=open(savepth,'rb')
					ret=fh.read()
					fh.close()
					return ret
		self.exptimes[hash_[:2]][url]=int(time.time()+expiretime)
		while(retry>=1):
			try:
				self.c_t_a()
				r=requests.get(url,headers=header_,proxies=proxies,cookies=cookies)
				break
			except Exception as e:
				print(e)
				pass
			retry-=1
		#h=decodebstr(r.content)
		self.c_t_a()
		r=requests.get(url,headers=header_,proxies=proxies,cookies=cookies)
		savebin(savepth,r.content)
		self.save(hash_[:2])
		return r.content
		
	def getimage(self,url,**kwargs):
		bin=self.getbin(url,**kwargs)
		kwargs['type']='bin'
		pth=self.getpath(url,**kwargs)
		#print(pth)
		try:
			ret=Image.open(pth)
		except Exception as e:
			try:
				print(myio.opentext(pth))
			except Exception as e2:
				pass
			try:
				
				os.remove(pth)
				print('get_image fail, deleted file:',pth)
			except Exception as e1:
				
				pass
			print("get_image fail",url,pth)
			
			raise e
		return ret
	
	get_image=getimage
	def save(self,session):
		if(self.lock):
			self.lock.acquire()
			
		if(len(self.text_mem)>200):
			for i in random.sample(list(self.text_mem),50):
				self.text_mem.pop(i,None)
		tmp=path.join(self.savepth,'*')
		if(len(list(glob(tmp)))>self.maxCacheNum):
			samplenum=min(int(len(list(glob(tmp)))*0.3),self.maxCacheNum)
			t=random.sample(list(glob(tmp)),samplenum)
			for i in t:
				try:
					os.remove(i)
				except Exception as e:
					pass
		t=time.time()
		pth=path.join(self.exptime_save_pth,'exptime_save%s.json'%session)
		myio.updatejson(pth,self.exptimes[session])
		if(self.lock):
			self.lock.release()
lcg=localCachingGeter
if(__name__=='__main__'):
	a=localCachingGeter()
	a.gettext(r'https://twitter.com/freeze_mea')
	print(a.get_path(r'https://g-search2.alicdn.com/img/bao/uploaded/i4/i3/4227787682/O1CN0126cP36CBbAn5kBX_!!0-item_pic.jpg_250x250.jpg_.webp'))
	#a.getimage('https://yt3.ggpht.com/a-/AN66SAzr4U836xFYhleL4eqnlO73KN2xUYrchiZZXg=s88-mo-c-c0xffffffff-rj-k-no')[0].show()