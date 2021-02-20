#from none_converters import jieba
import jieba
from workpathmanager import pathManager
from glob import glob
import myio,json,myhash,weight_choice,math,mymath,re,random
from os import path
wpm=pathManager(appname='setubot')
#setubot_mainpth=wpm.getpath(session="mainpth",ask_when_dne=True)
lc4s=jieba.lcut_for_search

conf2p=lambda x:math.tanh((x-1.5)*2)/2+0.5			
def possibility2confidency(p):						
	temp=(p-0.5)*2									
	if(temp>0.9999):								
		temp=0.9999
	if(temp<-0.9999):
		temp=-0.9999
	temp=math.atanh(temp)
	return temp/2+1.5
if(__name__=='__main__'):
	pass
	'''for i in range(1,10):
		i=i/10
		print(i,conf2p(i),possibility2confidency(conf2p(i)))'''
	

class dialogs:
	def __init__(self,dialogs=[],savepth=None,mean_weight=None,mean_keyword_weight=None,keyword_freq={},keyword_weight={}):
		self.dialogs=dialogs
		self.savepth=savepth
		self.keyword_weight=keyword_weight
		self.mean_weight=mean_weight
		self.mean_keyword_weight=mean_keyword_weight
		self.keyword_freq=keyword_freq
		self.keyword_filt_accelerate=False
		self.keyword_filt=None
	def keyword_filt_accelerate_on(self):
		keyword_filt={}
		for idx,d in enumerate(self.dialogs):
			for keyword in d.keywords:
				if(not(keyword in keyword_filt)):
					keyword_filt[keyword]=set()
				keyword_filt[keyword].add(idx)
		self.keyword_filt=keyword_filt
		self.keyword_filt_accelerate=True
		return keyword_filt
	initial_keyword_filt_accelerate=keyword_filt_accelerate_on
	def keyword_weight_from_json(self,filename):
		self.keyword_weight=myio.loadjson(filename)
		return self.keyword_weight
	def statistics(self):
		keyword_freq={}
		keyword_weights=[]
		dlg_weights=[]
		print(len(self.dialogs))
		for dlg in self.dialogs:
			dlg.calc_keyword_freq()
			for keyword,freq in dlg.keyword_freq.items():
				keyword_freq[keyword]=keyword_freq.get(keyword,0)+freq
			for keyword,weight in dlg.keyword_weight.items():
				keyword_weights.append(weight)
			if(dlg.weight):
				dlg_weights.append(dlg.weight)
		dlg_weights=[i for i in keyword_weights if not(weight_choice.is_nan(i))]
		keyword_weights=[i for i in keyword_weights if not(weight_choice.is_nan(i))]
		#print('dlg_weights',dlg_weights)
		#print('mean_keyword_weight',keyword_weights)
		self.mean_weight=mymath.quadratic_mean(dlg_weights) if dlg_weights else 1
		self.mean_keyword_weight=mymath.quadratic_mean(keyword_weights) if keyword_weights else 1
		self.freq_sum=sum([keyword_freq[i] for i in keyword_freq])
		self.keyword_freq={i:keyword_freq[i]/(self.freq_sum/len(keyword_freq)) for i in keyword_freq}
	def save(self):
		files={}
		for d in self.dialogs:
			pass
	
	def fromTXT(filenames,maxlen=114):
		dlgs=[]
		for _ in filenames:
			if(not(path.exists(_))):continue
			try:
				t=re.split('[\n\r]+',myio.opentext(_))
			except Exception:
				continue
			for idx,i in enumerate(t[2:]):
				
				j=t[idx-1]+t[idx-2]
				if(len(i)>maxlen or len(j)>maxlen):continue
				dlgs.append(dialog(ask_key_text=j+i,reply_text=i))
		
		dlgs=dialogs(dlgs)
		dlgs.statistics()
		return dlgs
	def fromJsons(filenames):
		dlgs=[]
		
		for fn in filenames:
			try:
				fj=myio.loadjson(fn)
				if(isinstance(fj,list)):
					for idx,dlgdic in enumerate(fj):
						dlg=dialog.from_dict(dlgdic)
						dlg.savepth=fn
						dlg.save_idx=idx
						dlgs.append(dlg)
				elif(isinstance(fj,dict)):
					for hash,dlgdic in fj.items():
						dlg=dialog.from_dict(dlgdic)
						dlg.savepth=fn
						dlg.save_idx=hash
						dlgs.append(dlg)
			except Exception as e:
				print(e,fn)
		
		ret=dialogs(dialogs=dlgs)
		ret.statistics()
		return ret
	from_jsons=fromJsons
	def getReply(self,ask_text):
		relavance=[]
		kwargs={'text':ask_text,'keyword_freq':self.keyword_freq,'keyword_weight':self.keyword_weight,'default_relevance_adjustment':self.mean_weight,'default_keyword_weight':self.mean_keyword_weight}
		if((self.keyword_filt_accelerate)and(self.keyword_filt)):
			kwds=lc4s(ask_text)
			dialogs=set()
			for keyword in kwds:
				dialogs=dialogs.union(self.keyword_filt.get(keyword,{}))
			dialogs=[self.dialogs[i] for i in dialogs]
			
		else:
			dialogs=self.dialogs
		mxrel=(0,random.random(),None)
		for i in dialogs:
			rel=i.calc_relavance(**kwargs)[0]
			relavance.append(rel)
			if((rel,random.random(),i)>mxrel):
				mxrel=(rel,random.random(),i.to_dict())
		#print(mxrel)
		#print(kwargs)
		#print(relavance)
		if(not(dialogs)):
			return None
		idx=weight_choice.weight_choice(relavance,list(range(len(dialogs))))
		if(idx is not None):
			dlg=dialogs[idx]
			ret=dialog_reply(dlg,dlg.calc_relavance(**kwargs),ask_text,kwargs=kwargs)
			#print('line130',ret,relavance[idx],idx)
			if(relavance[idx]<dlg.eps):
				ret=None
		else:
			ret=None
		return ret
	get_reply=getReply
class dialog:
	def __init__(self,ask_key_text='',reply_text='',keyword_weight={},reply_voice='',reply_picture='',eps=0.01,savepth=None,voice_only=False,weight=None,source=None):
		self.ask_key_text=ask_key_text
		self.reply_text=reply_text
		self.voice_only=voice_only
		self.savepth=savepth
		self.weight=weight
		self.source=source
		self.keyword_weight=keyword_weight
		self.reply_voice=reply_voice
		self.reply_picture=reply_picture
		self.keyword_freq=None
		self.eps=eps
	def __hash__(self):
		h=self.ask_key_text+self.reply_text
		if(self.reply_picture):
			h+=self.reply_picture
		return myhash.hashi(h)
	def __eq__(self,other):
		ret=True
		ret=ret and (self.ask_key_text==other.ask_key_text)
		ret=ret and (self.reply_text==other.reply_text)
		ret=ret and (self.savepth==other.savepth)
		return ret
	def __str__(self):
		return str(self.to_dict())
	def calc_keyword_freq(self):
		lc=jieba.lcut(self.ask_key_text*2+','+self.reply_text)
		
		ret={}
		self.keywords=set(lc)
		for i in lc:
			ret[i]=ret.get(i,0)+1
		self.keyword_freq=ret
		return ret
	def calc_relavance(self,text,eps=None,keyword_freq={},keyword_weight={},default_relevance_adjustment=1,default_keyword_weight=1):
		if(self.keyword_freq is None):
			self.calc_keyword_freq()
		keywords=lc4s(text)
		relavance=0
		if(eps is None):
			eps=self.eps
		keyword_intersection={}
		not_in_suppression=1
		'''for keyword in set(keywords)-set(self.keywords):
			not_in_suppression*=(1.04)**(keyword_weight.get(keyword,0.2)/keyword_freq.get(keyword,1))
		for keyword in set(self.keywords)-set(keywords):
			not_in_suppression*=(1.04)**(keyword_weight.get(keyword,0.2)/keyword_freq.get(keyword,1))'''
		not_in_suppression=(len(set(self.keywords)^set(keywords))/4+1)**2
		#print("nis",not_in_suppression)
		for keyword in keywords:
			if(not(keyword in self.keywords)):

				continue
			kr=1/keyword_freq.get(keyword,1)
			kr**=1.3
			kr*=self.keyword_weight.get(keyword,default_keyword_weight)
			kr*=self.keyword_freq.get(keyword,1)
			kr*=keyword_weight.get(keyword,1)
			if(not(self.weight is None)):
				kr*=self.weight
			else:
				kr*=default_relevance_adjustment
				self.weight=default_relevance_adjustment
			kr/=(len(self.keywords)**0.12)
			kr/=(len(keywords)+1)**0.25
			relavance+=kr
			keyword_intersection[keyword]={}
			keyword_intersection[keyword]['relavance']=kr
			keyword_intersection[keyword]['freq']=(1/keyword_freq.get(keyword,1))**2
		# krij={}
		for i in keywords:
			for j in keywords:
				if((i not in keyword_intersection) or (j not in keyword_intersection) or (i+j not in self.ask_key_text and i+j not in self.reply_text)):
					continue
				if(i+j in text):
					kri=keyword_intersection[i]['relavance']*1.5
					krj=keyword_intersection[j]['relavance']
					
					keyword_intersection[j]['relavance']+=kri
					keyword_intersection[j]['serial_relavance']=keyword_intersection[j].get('serial_relavance',0)+kri
					
					keyword_intersection[j]['serial']=keyword_intersection[i].get('serial',set())
					keyword_intersection[j]['serial'].add(i)
					
					relavance+=kri
		'''for i,kr in krij.items():
			keyword_intersection[i]['relavance']+=kr'''
		#print(keyword_intersection)
		relavance/=not_in_suppression
		return relavance,keyword_intersection
	def from_dict(dic):
		self=dialog()
		self.ask_key_text=dic.get('dialog_ask','') or dic.get('ask_key_text','')
		self.reply_text=dic.get('dialog_reply','') or dic.get('reply_text','')
		self.voice_only=dic.get('voice_only',False)
		self.weight=dic.get('freq',dic.get('weight',None))
		self.keywords=set(lc4s(self.ask_key_text+','+self.reply_text))
		self.keyword_weight=dic.get('keyword_weight',dic.get('kwd_freq_adjust',{}))
		self.reply_voice=dic.get('reply_voice','') or dic.get('rec_kwd')
		self.reply_picture=dic.get('reply_picture','') or dic.get('shot_kwd')
		self.source=dic.get('source',{})
		self.calc_keyword_freq()
		return self
	def __dict__(self):
		return self.to_dict()
	def save(self):
		if(not(self.savepth)):
			return None
		j=myio.loadjson(self.savepth)
		j_=self.to_dict()
		j_.pop("keywords",None)
		idx=self.save_idx
		'''for idx,temp in enumerate(j):
			d=dialog.from_dict(temp)
			if((d.ask_key_text==self.ask_key_text)and(d.reply_text==self.reply_text)):
				break'''
		j[idx]=j_
		myio.dumpjson(self.savepth,j)
			
	def to_dict(self):
		ret={}
		#self.calc_keyword_freq()
		ret['keyword_freq']=self.keyword_freq
		ret['keyword_weight']=self.keyword_weight
		ret['keywords']=self.keywords
		ret['reply_text']=self.reply_text
		ret['reply_picture']=self.reply_picture
		ret['ask_key_text']=self.ask_key_text
		ret['reply_voice']=self.reply_voice
		ret['savepth']=self.savepth
		ret['voice_only']=self.voice_only
		ret['source']=self.source
		ret['weight']=self.weight
		return ret
		
class dialog_reply:
	def __init__(self,dialog:dialog,relavance,ask_text,kwargs=None):
		if(kwargs is None):
			kwargs={}
		self.dialog=dialog
		self.relavance=relavance
		self.possibility=conf2p(relavance[0])
		self.ask_text=ask_text
		self.kwargs=kwargs
	def suggest_relavance(self,relavance,dlg_relavance_proportion=0.4):
		self.kwargs['text']=self.ask_text
		kwargs=self.kwargs
		r,keyword_intersection=self.dialog.calc_relavance(**kwargs)
		rate=relavance/r
		dlg=self.dialog
		
		dlg.weight*=rate**dlg_relavance_proportion
		default_keyword_weight=kwargs.get('default_keyword_weight',1)
		for kwd in keyword_intersection:
			dlg.keyword_weight[kwd]=dlg.keyword_weight.get(kwd,default_keyword_weight)*(rate **(1-dlg_relavance_proportion) )
		if(dlg.savepth):
			dlg.save()
		self.relavance=dlg.calc_relavance(**kwargs)
		return dlg
	def to_dict(self):
		ret={}
		ret['dialog']=self.dialog.to_dict()
		ret['relavance']=self.relavance
		ret['possibility']=self.possibility
		ret['ask_text']=self.ask_text
		ret['kwargs']=self.kwargs
		return ret
	def __str__(self):
		#print("Q:%s(%s) A:%s, relavance:%s"%(self.ask_text,self.dialog.ask_key_text,self.dialog.reply_text,self.relavance))
		return "Q:%s(%s) A:%s, relavance:%s"%(self.ask_text,self.dialog.ask_key_text,self.dialog.reply_text,self.relavance)
def test0():
	temp=myio.loadjson(setubot_mainpth+r'\Mea_dialog\Mea.json')
	for i in range(10):
		d=temp[i]
		dlg=dialog.from_dict(d)
		print(dlg.to_dict())
	#print(json.dumps(dlg.to_dict()))
	
def test1():
	
	#dlgLib=dialogs.fromJsons(glob(r"J:\new\setubot\Mea_dialog_v2\mea*.json"))
	#dlgLib=dialogs.fromJsons(glob(r"M:\pic\setubot\Mea_dialog_v2\mea20190226 17-47-48.json"))
	dlgLib=dialogs.fromJsons(glob(r"M:\pic\setubot\Mea_dialog_v2\mea*.json"))
	#dlgLib.keyword_weight_from_json(r"D:\ZXF\微云\code\cqnonebot\saves\stop_words.json")
	
	#dlgLib=dialogs.fromTXT([r"M:\pic\setubot\saves\message_record\Group792076474.log"])
	#dlgLib.initial_keyword_filt_accelerate()
	i=input('询问')
	r=None
	while(i):
		
		if(i=='sp'):
			relavance=possibility2confidency(float(input('pos')))
			if(r):
				d=r.suggest_relavance(relavance)
				print(d.to_dict())
			else:
				print('no r')
		elif(i=='save'):
			pass
		elif(i=='sr'):
			relavance=float(input('rel'))
			if(r):
				d=r.suggest_relavance(relavance)
				print(d.to_dict())
			else:
				print('no r')
		elif(i=='exec'):
			try:
				exec(input())
			except Exception as e:
				print(e)
				import traceback
				print(traceback.format_exc())
		else:
			r=dlgLib.getReply(i)
			if(r):
				print(r.dialog)
				print(r.dialog.reply_text)
				print(r.relavance)
			else:
				print('没有应答')
		i=input('询问')
	exit()
if(__name__=='__main__'):
	#print(conf2p(2))
	test1()