import time,math,datetime,myio
from os import path
import threading
def dateStr():
	t=datetime.date.today()
	return "%s-%s-%s"%(t.year,t.month,t.day)
	
	
class check_in:
	def __init__(self,savepath,limit=1):
		if(path.exists(savepath)):
			self.checked=myio.loadjson(savepath)
		else:
			self.checked={}
		self.Lock=threading.Lock()
		self.savepath=savepath
		self.limit=limit
		#self.checked={}
	
	def save(self,savepath=None):
		self.Lock.acquire()
		if(savepath is None):
			savepath=self.savepath
		myio.dumpjson(savepath,self.checked)
		self.Lock.release()
	def check_in(self,id,n=1):
		self.Lock.acquire()
		dates=dateStr()
		self.checked[dates]=self.checked.get(dates,{})
		if(id in self.checked[dates]):
			if(self.checked[dates][id]+n>self.limit):
				self.checked[dates][id]=self.limit
				self.Lock.release()
				return self.limit-self.checked[dates][id]
		else:
			self.checked[dates][id]=0
		self.checked[dates][id]+=n
		self.Lock.release()
		self.save()
		return n
	def remainLimit(self,id):
		dates=dateStr()
		return self.limit-self.checked.get(dates,{}).get(id,0)
def seconds2str(secs):
	
	days,h,min,sec=int(secs/3600/24),int(secs/3600)%24,int(secs/60)%60,secs%60
	temp=((days,'天'),(h,"小时"),(min,'分钟'),(sec,'秒'))
	ret=''
	for t,s in temp:
		if(t):
			ret+="%s%s"%(t,s)
	return ret
class check_in_split:
	def __init__(self,savepath=None,interval=6*3600):
		if(not(savepath)):
			savepath=path.dirname(__file__)+r'\temp_check_in_split.json'
		if(path.exists(savepath)):
			self.last_time=myio.loadjson(savepath)
		else:
			self.last_time={}
		self.savepath=savepath
		self.interval=interval
		self.Lock=threading.Lock()
	def check_in(self,id):
		self.Lock.acquire()
		if(time.time()<(self.last_time.get(id,0)+self.interval)):
			self.Lock.release()
			#self.last_time[id]=time.time()
			return False
		else:
			self.last_time[id]=time.time()
			self.Lock.release()
			self.save()
			return True
	def time_wait(self,id):
		return self.interval+self.last_time.get(id,0)-time.time()
	def time_wait_str(self,id):
		return seconds2str(self.time_wait(id))
	def seconds2str(secs):
		
		days,h,min,sec=int(secs/3600/24),int(secs/3600)%24,int(secs/60)%60,int(secs)%60
		temp=((days,'天'),(h,"小时"),(min,'分钟'),(sec,'秒'))
		ret=''
		for t,s in temp:
			if(t):
				ret+="%s%s"%(t,s)
		return ret
	def save(self,savepath=None):
		if(savepath is None):
			savepath=self.savepath
		self.Lock.acquire()
		myio.dumpjson(savepath,self.last_time)
		self.Lock.release()
if(__name__=='__main__'):
	print(check_in_split.seconds2str(114514))
