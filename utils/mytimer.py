import time,math,datetime,myio
from os import path
from threading import Lock
def log(a,b):					#没用的数学
	return math.log(b)/math.log(a)
class timer:					#计时器
	def __init__(self):
		self.settime()
	def settime(self):
		self.t=time.time()
	def gettime(self,settime=True):
		ret=time.time()-self.t
		if(settime):
			self.settime()
		return ret

class heater():		#加热-冷却。阻止使用bot刷屏的。每一次+onetimetime秒，每秒冷却1秒（废话），达到bufftimes*onetimetime秒之后罚时cdtime。
	def __init__(self,bufftimes=10,cdtime=600,onetimetime=30):
		self.times={}
		self.temps={}
		self.bufftimes=bufftimes
		self.cdtime=cdtime
		self.basen=1.2
		self.heatedinfoonce=set()
		self.onetimetime=onetimetime
	def heat(self,id,n=1):
		self.add(id)
		self.temps[id]+=self.onetimetime*n
		if(not(heater.__cooled__(self,id))):
			self.temps[id]=self.onetimetime*self.bufftimes+self.cdtime
	def add(self,id):
		if(id in self.temps):
			return None
		self.times[id]=timer()
		self.temps[id]=1
	def heatedInfoOnce(self,id):
		if(not(id in self.heatedinfoonce)):
			self.heatedinfoonce.add(id)
			return True
		else:
			return False
	def cool(self,id):
		if(not(id in self.times)):
			self.times[id]=timer()
			self.temps[id]=1
			return True
		else:
			t=self.times[id].gettime()
			if(t>self.cdtime):
				self.temps[id]=1
			else:
				self.temps[id]-=t
				if(self.temps[id]<0):
					self.temps[id]=0
	def __cooled__(self,id):
		if(not(id in self.temps)):
			return True
		else:
			return self.temps[id]<(self.onetimetime*self.bufftimes)
	def cooled(self,id,autoheat=1,autocool=True):
		
		self.add(id)
		if(autocool):
			self.cool(id)
		#print('\nheater\nheater\nheater'+str(log(self.basen,self.temps[id]/(self.basen**(self.cdtime))))+'\nheater\nheater\nheater')
		ret=heater.__cooled__(self,id)
		if(ret and autoheat):
			self.heat(id,autoheat)
		if(ret):
			if(id in self.heatedinfoonce):
				self.heatedinfoonce.remove(id)
		return ret
	def remaincooltime(self,id):
		if(heater.__cooled__(self,id)):
			return 0
		else:
			ret = self.temps[id]-self.onetimetime*self.bufftimes
			
			return ret
			
class throttle:
	def __init__(self,times,period):
		self.times_=[0 for i in range(times)]
		self.head=0
		self.period=period
		self.times=times
		self.lock=Lock()
	def set_wait(self,period=None):
		self.lock.acquire()
		if(period is None):
			period=self.period
		self.times_[self.head]=time.time()+period
		self.lock.release()
		return None
	def acquire(self):
		self.lock.acquire()
		wt=self.times_[self.head]
		wt_=wt+self.period-time.time()
		if(wt_>0):
			time.sleep(wt_)
		self.times_[self.head]=time.time()
		self.head=(self.head+1)%self.times
		self.lock.release()
		return True
	def is_busy(self):
		return (self.times_[self.head]+self.period-time.time())>0
	def wait_time(self):
		return self.times_[self.head]+self.period-time.time()
class speedo:
	def __init__(self,times):
		self.enen=[0 for _ in range(times)]
		self.p=0
		self.times=times
	def cnt(self):
		self.enen[self.p]=time.time()
		self.p=(self.p+1)%self.times
		return self()
	def __call__(self):
		td=self.enen[self.p-1]-self.enen[self.p]
		if(td):
			return self.times/td
		else:
			return 0
if(__name__=='__main__'):
	a=speedo(5)
	thr=throttle(3,5)
	while(True):
		thr.acquire()
		a.cnt()
		print(a())