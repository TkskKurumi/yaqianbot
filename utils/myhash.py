from PIL import Image
#from malody import im_sizelimitmax
from glob import glob
from os import path
import random,myio

import threading
#from timer import timer
def im_sizelimitmax(im,sizelimit):
	siz=sizelimitmax(im.size,sizelimit)
	return im.resize(siz,Image.LANCZOS)
	
def sizelimitmax(siz,limitsiz):
	r=1
	if(limitsiz[0]<siz[0]):
		r1=limitsiz[0]/siz[0]
		if(r1<r):
			r=r1
	if(limitsiz[1]<siz[1]):
		r1=limitsiz[1]/siz[1]
		if(r1<r):
			r=r1
	ret=tuple([int(i*r)for i in siz])
	return ret

def hashidis(i1,i2,length=30,offs=3):
	s1=[(i1>>(offs*i))%(1<<offs)for i in range(length) ]
	s2=[(i2>>(offs*i))%(1<<offs)for i in range(length) ]
	s=0
	for i in range(length):
		if(s1[i]!=s2[i]):
			s+=1
	return s/length
def phashi_old(img,length=31,offs=2,w=20,rm=35):
	img=im_sizelimitmax(img,(w,w))
	#img.show()
	l=0
	i1=0
	div=(8-offs)
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			getp=img.getpixel((i,j))
			for j in getp:
				i1=i1^((j>>div) << (l*offs))
				l+=1
				if(l==length):
					l=0
	#img.show()
	return i1>>rm
def phashi__(img,length=31,offs=2,w=20,rm=None):
	if(isinstance(img,str)):
		img=Image.open(img)
	img=im_sizelimitmax(img,(w,w)).convert('L')
	#img.show()
	if(rm==None):
		rm=length*offs-70
	l=0
	i1=0
	div=(9-offs)
	for i in range(img.size[0]-1):
		for j in range(img.size[1]):
			getp=img.getpixel((i,j))
			getp1=img.getpixel((i+1,j))
			
			i1=i1^(((getp1-getp+256)>>div) << (l*offs))
			l+=1
			if(l==length):
				l=0
	#img.show()
	return i1>>rm
	
def phashi_3x3_L(img_,length=40,offs=4,w=24,rm=None):
	if(isinstance(img_,str)):
		img=Image.open(img_)
	else:
		img=img_
	img=im_sizelimitmax(img,(w,w)).convert('L')
	#img.show()
	if(rm==None):
		rm=length*offs-70
	l=0
	i1=0
	div=(11-offs)
	for i in range(1,img.size[0]-1):
		for j in range(1,img.size[1]-1):
			getp=[[] for i_ in range(3)]
			for i_ in range(-1,2):
				for j_ in range(-1,2):
					getp[i_].append(img.getpixel((i+i_,j+j_)))
			j=getp[0][0]+getp[0][1]+getp[0][2]+getp[1][2]
			j-=getp[1][0]+getp[2][0]+getp[2][1]+getp[2][2]
			j+=256*4
			
			i1=i1^(((j)>>div) << (l*offs))
			l+=1
			if(l==length):
				l=0
	#img.show()
	return i1>>rm
	
def phashi_(img,length=63,offs=1,w=24,rm=34):
	if(isinstance(img,str)):
		img=Image.open(img)
	img=im_sizelimitmax(img,(w,w)).convert('L')
	l=0
	i1=0
	bitrm=(9-offs)
	for i in range(img.size[0]-1):
		for j in range(img.size[1]):
			getp=img.getpixel((i,j))
			getp1=img.getpixel((i+1,j))
			k=getp-getp1+256
			#print(k)
			i1=i1^((k>>bitrm) << (l*offs))
			l+=1
			if(l==length):
				l=0
	return i1>>rm

	
	
def hashi(s,leng=80,offs=1):
	
	try:
		return phashi(Image.open(s))
	except Exception:
		#print(Exception)
		try:
			t=open(s,'rb')
			i1=0
			tl=0
			while(True):
				ti=t.read(1)
				if(ti==b''):
					break
				ti=ord(ti)
				i1=i1^(ti<<((tl%leng)*offs))
				tl=tl+1
			#print('f')
			return i1
		except Exception:
			i1=0
			tl=0
			if(isinstance(s,str)):
				s=bytearray(s,'utf-8')
			else:
				s=bytearray(s)
			for i in range(len(s)):
				i_=s[i]
				i1=i1^(i_<<((tl%leng)*offs))
				tl=tl+1
			#print('s')
			return i1

def hashs(s,c=''):
	if(isinstance(s,(int,float))):
		i=int(s)
		
	else:
		i=hashi(s)
	if(c==''):
		c=[chr(i+48) for i in range(10)]
		c.extend([chr(i+97) for i in range(26)])
		c.extend([chr(i+65) for i in range(26)])
		
	mo=len(c)
	ret=''
	
	i2=abs(i)
	while(i2>0):
		ret=c[i2%mo]+ret
		i2=int(i2/mo)
	if(i<0):
		return '-'+ret
	else:
		return ret
class trimDict:
	def __init__(self):			#hash之后的字符串，保留可以区分不同条目最短的前缀
		self.dic={}				#例如，依次加入了abstract,	absolute,	abc,abs,ab1,ab2,ab12,cat
		self.hashedKey={}		#就会依次得到	a,			ab,			abc,abs,ab1,ab2,ab12,c
		self.Lock=threading.Lock()
	def add(self,key,value):
		self.Lock.acquire()
		hashedkey=hashs(key)
		if(key in self.hashedKey):
			trimedKey=self.hashedKey[key]
			self.dic[trimedKey]=value
			self.Lock.release()
			return trimedKey
		for i in range(1,len(hashedkey)+1):
			trimedKey=hashedkey[:i]
			if(not(trimedKey in self.dic)):
				self.dic[trimedKey]=value
				self.hashedKey[key]=trimedKey
				self.Lock.release()
				return trimedKey
		self.Lock.release()
		return 'ERR'
	def get(self,hashedkey,default=None):
		return self.dic.get(hashedkey,default)

class splitedDict:
	def dump(self,savepth):
		self.Lock.acquire()
		for i,d in self.dic.items():
			myio.dumpjson(r'%s\%s.json'%(savepth,i),d)
		self.Lock.release()
	def dumpPart1(self,name):
		self.dumpPart(self.pth,name)
	def dumpPart(self,savepth,name):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		myio.dumpjson(r'%s\%s.json'%(savepth,sk),self.dic.get(sk,{}))
	def load(self,savepth):
		print('load!!!',savepth)
		for filename in glob(savepth+r'\*.json'):
			self.lazy_load_(filename)
			#self.update(myio.loadjson(filename))
		return self
	def lazy_load_(self,pth):
		
		if((pth not in self.lazy_loaded)and(path.exists(pth))):
			self.lazy_loaded.add(pth)
			self.update(myio.loadjson(pth))
			
	def update(self,dic):
		if(not(dic)):
			return None
		for k,v in dic.items():
			self[k]=v
		return None
	def splitedKey(key):
		if(key):
			return hashs(key)[:2]
		else:
			return ''
	def pop(self,name,*args):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		if(sk in self.dic):
			if(name in self.dic[sk]):
				ret=self.dic[sk][name]
				self.dic[sk].pop(name)
				
				return ret
		if(args):
			return args[0]
		else:
			raise KeyError(name)
	def __init__(self,dic=None,splitMethod=splitedKey,pth=None,autosave=True,lazy_load=True):
		self.dic={}
		self.splitMethod=splitMethod
		self.Lock=threading.Lock()
		self.autosave=autosave
		self.pth=None
		if(isinstance(dic,dict)):
			self.update(dic)
		if(pth and not(lazy_load)):
			self.load(pth)
		self.pth=pth
		self.lazy_loaded=set()
		self.lazy_load=self.pth and lazy_load
	def splitedKey(key):
		if(key):
			return hashs(key)[:2]
		else:
			return ''
	def __setitem__(self,name,value):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		self.Lock.acquire()
		if(not(sk in self.dic)):
			self.dic[sk]={}
		self.dic[sk][name]=value
		self.Lock.release()
		if(self.autosave and self.pth):
			self.dumpPart(self.pth,name)
	def __getitem__(self,name):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		if(not(sk in self.dic)):
			raise KeyError(name)
		elif(not(name in self.dic[sk])):
			raise KeyError(name)
		else:
			return self.dic[sk][name]
	def __contains__(self,name):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		if(not(sk in self.dic)):
			return False
		elif(not(name in self.dic[sk])):
			return False
		else:
			return True
	def __delitem__(self,name):
		self.Lock.acquire()
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		self.dic.get(sk,{}).pop(name,None)
		self.Lock.release()
	def get(self,name,*args):
		sk=self.splitMethod(name)
		if(self.lazy_load):
			self.lazy_load_(self.pth+r'\%s.json'%sk)
		if(sk in self.dic):
			if(name in self.dic[sk]):
				return self.dic[sk][name]
		if(args):
			return args[0]
		else:
			raise KeyError(name)
	def __dict__(self):
		print('dict!!!')
		return self.toDict()
	
	def to_list(self):
		ret=[]
		
		if(self.lazy_load):
			self.load(self.pth)
		self.Lock.acquire()
		for i,d_ in self.dic.items():
			for j in d_:
				ret.append(j)
		self.Lock.release()
		return ret
	
	def toDict(self):
		
		d={}
		if(self.lazy_load):
			self.load(self.pth)
		self.Lock.acquire()
		
		for i,d_ in self.dic.items():
			
			d.update(d_)
		self.Lock.release()
		return d
	to_dict=toDict
	def __repr__(self):
		return str(self.toDict())
	def __str__(self):
		return str(self.toDict())
def randstr():
	return hashs(random.randint(0,2147483647))
phashi=phashi_3x3_L
phashs=lambda s:hashs(phashi(s))
if(__name__=='__main__'):
	print(hashs(r'https://www.pixiv.net/search_user.php?s_mode=s_usr&nick=As109'))
	print(hashs(r'https://www.pixiv.net/search_user.php?s_mode=s_usr&nick=QYS3'))