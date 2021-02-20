import requests
import json
from urllib import request
import chardet,os
from requests_toolbelt.multipart.encoder import MultipartEncoder

#smms图床

recordPath=os.path.dirname(__file__)+r"\smmsrecord.json"
def readFileStr(filename):
	filename=filename.replace('\"','').replace('\'','')
	a=open(filename,'rb')
	b=a.read()
	c=b.decode(chardet.detect(b)['encoding'])
	a.close()
	return(c)
def uploaded(filename):
	r=readFileStr(recordPath)
	jl=json.loads(r)
	if(filename in jl):	
		return True
def deleteall():
	r=readFileStr(recordPath)
	jl=json.loads(r)
	for i in jl:
		request.urlopen(jl[i]['delete'])
	f=open(recordPath,'w')
	f.write('{}')
	f.close()
def geturl(filename):
	r=readFileStr(recordPath)
	jl=json.loads(r)
	if(filename in jl):	
		return jl[filename]['url']
	else:
		a=smms(filename,'DNE')
		return a.url

def getdelete(filename):
	r=readFileStr(recordPath)
	jl=json.loads(r)
	if(filename in jl):	
		return jl[filename]['delete']
	else:
		return 'not found'

def gethash(filename):
	r=readFileStr(recordPath)
	jl=json.loads(r)
	if(filename in jl):	
		return jl[filename]['hash']
	else:
		return 'not found'
		
class smms():
	
	def __init__(self,filename,ex='unknown'):
		if(ex=='unknown'):
			if(uploaded(filename)):
				self.url=geturl(filename)
				self.delete=getdelete(filename)
				self.hash=gethash(filename)
				return None
			
		url = r'https://sm.ms/api/upload'
		f=open(filename,'rb')
		filetype='img/jpeg'
		if(filename[-3:]=='png'):
			filetype='img/png'
		data={'smfile':('filename',f, filetype)}
		data=MultipartEncoder(fields=data,boundary='---------------------nishishabi87w6et76BRWS')
		#print(filetype)	
		req = requests.post(url, data=data,headers={'Content-Type': data.content_type})
		#print(req.text)
		jl=json.loads(req.text)
		#print(jl)
		self.url=jl['data']['url']
		self.delete=jl['data']['delete']
		self.hash=jl['data']['hash']
		r=readFileStr(recordPath)
		jl1=json.loads(r)
		jl1[filename]={'url':self.url,'delete':self.delete,'hash':self.hash}
		f=open(recordPath,'w')
		temp=json.dumps(jl1)
		temp1=temp.split('},')
		temp=''
		for i in range(len(temp1)-1):
			temp=temp+temp1[i]+"},\n"
		temp=temp+temp1[-1]
		f.write(temp)
		f.close()
			


