from threading import Thread
import time,myhash,math
#稍微封装threading的一些功能
class job():
	def start(self,target,args=None,callback=None,callback_kwargs=None,kwargs=None,timeout=math.inf,restartinfo='restarted',ontimeout='retry',on_time_out_kwargs=None,name=None):
		#print('args=%s'%(arg))
		self.target=target
		self.args=args or tuple()
		#print('self.target',str(target))
		self.restartinfo=restartinfo	
		self.kwargs=kwargs or dict()
		self.supervising=True
		kwgtr={'target':target,'kwargs':kwargs}
		self.t=Thread(target=self.gettargetret,kwargs=kwgtr)
		self.t.start()
		self.callback=callback
		self.callback_kwargs=callback_kwargs
		self.t1=Thread(target=self.supervise,args=(timeout,))
		self.t1.start()
		self.ontimeout=ontimeout					#超时
		self.on_time_out_kwargs=on_time_out_kwargs	#直接重试，循环还好停，主要是网络io没办法停
		if(name is None):
			name=myhash.hashs(str(target)+str(kwargs))
		self.name=name
		#print('job',name,'starts')
		return name
	def gettargetret(self,target,kwargs):
		self.ret=target(*self.args,**self.kwargs)
		
	def timeout1(self):
		print(self.restartinfo)
		if(self.ontimeout=='retry'):
			self.start(target=self.target,callback=self.callback,callback_kwargs=self.callback_kwargs,kwargs=self.kwargs,restartinfo=self.restartinfo)
		elif(self.ontimeout!='giveup'):
			self.start(target=self.ontimeout,callback=self.callback,callback_kwargs=self.callback_kwargs,kwargs=self.on_time_out_kwargs,restartinfo=self.restartinfo)
	def supervise(self,timeout=233):
		tim=time.process_time()
		while(self.supervising):
			time.sleep(5)
			if((time.process_time()-tim)>timeout):
				self.timeout1()
				return None
			if(not(self.t.is_alive())):
				if(self.callback):
					#print(self.callback_kwargs)
					self.callback(**self.callback_kwargs)
				return 'shit'
	def __init__(self):
		self.t=Thread()
	def join(self):
		self.supervising=False
		self.t.join()
		self.t1.join()
		return self.ret
	def is_alive(self):
		return self.t.is_alive()
class jobs:
	def __init__(self):
		self.jobs=[]
	def getFreeJob(self):
		for i in self.jobs:
			if(not(i.is_alive())):
				
				return i
		self.jobs.append(job())
		return self.jobs[-1]
	def jobcount(self,join=False):
		s=0
		for i in self.jobs:
			if(i.is_alive()):
				s+=1
			elif(join):
				try:
					i.join()
				except Exception as e:
					pass
		return s
	def start(self,kwargs):
		if('name' in kwargs):
			j=job()
			self.jobs.append(j)
		else:
			j=self.getFreeJob()
		j.start(**kwargs)
		return j
	def getReturns(self,callback_progress=None,callback_progress_kwargs={},callback_split=1):
		ret={}
		for i in range(len(self.jobs)):
			j=self.jobs[i]
			if(j.name is not None):
				ret[j.name]=j.join()
				if((callback_progress)and ((i+1)%callback_split==0)):
					callback_progress_kwargs.update({'progress':i+1,'name':j.name})
					callback_progress(**callback_progress_kwargs)
		return ret
j=jobs()