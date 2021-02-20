import chardet,os,json,myhash,random,time
from os import path
from bs4 import UnicodeDammit
#from timer import timer
encode_mem={}
encode_mem_savepth=__file__+'.json'
dbg=False
text_mem={}
def clear_text_mem():
	if(len(text_mem)<40):
		return None
	for i in random.sample(list(text_mem),10):
		text_mem.pop(i,None)
if(path.exists(encode_mem_savepth)):
	fh=open(encode_mem_savepth,'r')
	encode_mem=json.loads(fh.read())
	fh.close()

def save_encode_mem():
	if(len(encode_mem)>450):
		for i in random.sample(list(encode_mem),150):
			encode_mem.pop(i,None)
	dumpjson(encode_mem_savepth,encode_mem,ensure_ascii=True)
#一些读写的函数
debug=__name__=='__main__'
def opentext(filename,encoding=None):
	filename=filename.replace('\"','').replace('\'','')
	a=open(filename,'rb')
	b=a.read()
	a.close()
	if(not(b)):
		return ''
	t1=time.time()
	hashs=myhash.hashs(b)
	if(debug):
		print('binary hashs time',time.time()-t1)
	if(hashs in text_mem):
		return text_mem[hashs]
	if(not(encoding)):
		dammit=UnicodeDammit(b)
		encoding=dammit.original_encoding
		c=b.decode(encoding)
	else:
		try:
			c=b.decode(encoding)
		except Exception as e:
			c=opentext(filename,encoding=None)
	
	clear_text_mem()
	text_mem[hashs]=c
	return(c)
def detect(filename):
	filename=filename.replace('\"','').replace('\'','')
	a=open(filename,'rb')
	b=a.read()
	return(chardet.detect(b)['encoding'])
def loadjson(filename,delete_bom=True):
	try:
		t=opentext(filename,encoding='utf-8').strip('\ufeff')
		if(not(t)):
			return None
		return json.loads(t)
	except Exception as e:
		print('json decode %s fail'%filename)
		raise e
def dumpjson(filename,content,make_backup=True,ensure_ascii=True):
	savetext(filename,json.dumps(content,ensure_ascii=ensure_ascii),make_backup=make_backup)
def savetext(filename,content,encoding='utf-8',make_backup=False):
	if((make_backup)and(os.path.exists(filename))):
		savetext(filename+'.bak',opentext(filename,encoding=encoding),make_backup=False)
	if(not(os.path.exists(os.path.dirname(filename)))):
		try:
			os.makedirs(os.path.dirname(filename))
		except Exception as e:
			print(filename)
			raise e
	fh=open(filename,'w',encoding=encoding)
	fh.write(content)
	fh.close()
def updatejson(filename,dic,k=None,make_backup=True):
	dic_={}
	if(path.exists(filename)):
		try:
			dic_=loadjson(filename)
			if(not(isinstance(dic_,dict))):
				dic_={}
		except Exception:
			dic_={}
	if(k):
		temp=dic_
		for i in k:
			if(not(i in temp)):
				temp[i]={}
			temp=temp[i]
		temp.update(dic)
	else:
		dic_.update(dic)
	dumpjson(filename,dic_,make_backup=make_backup)
	return dic_
def savebin(filename,t,f=True):
	if(not(os.path.exists(os.path.dirname(filename)))):
		os.makedirs(os.path.dirname(filename))
	if(not(f)):
		if(os.path.exists(filename)):
			return None
	f=open(filename,'wb')
	f.write(t)
	f.close()
def decodebstr(bs):
	dammit=UnicodeDammit(bs)
	encod=dammit.original_encoding
	#print(encod)
	return bs.decode(encod)
if(__name__=='__main__'):
	#t1=timer()
	#opentext(r"J:\new\setubot\setu_tag_save_tagItems.json",encoding='utf-8')
	updatejson(r'C:\temp\dne.json',{"a":"114514"})
	#print(t1.gettime())
	#opentext(r"D:\ZXF\pytwit\long_cache\tempcache\3eVMDbD8E8ugqKn.html")
	#print(t1.gettime())