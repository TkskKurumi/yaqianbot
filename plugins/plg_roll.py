from bot_backend import *
import random,myhash,re,time
last_roll=myhash.splitedDict(pth=path.join(mainpth,'saves','last_roll'),splitMethod=lambda x:myhash.hashs(x).lower()[:2])

def judge_abua(s):
	n=len(s)
	for i in range(1,n-1):
		if(s[i] in '不没'):
			if(s[i-1]==s[i+1]):
				return s[i-1:i+2]
	return None
	
def random_mes_rec(minlen=2,maxlen=4,rate=1.1):
	if('plg_chat' not in plugins):
		return "什么"
	__=1
	dlgs_=get_plugin_namespace('plg_chat').dlgs_by_gid
	dlgs__=list(dlgs_)
	if(not(dlgs__)):
		get_plugin_namespace('plg_chat').get_dlgs_by_gid('1126809443')
		dlgs_=get_plugin_namespace('plg_chat').dlgs_by_gid
		dlgs__=list(dlgs_)
	ret=''
	
	while(not ret):
		_=random.choice(dlgs__)
		_=dlgs_[_]
		dlgs=_.dialogs
		_=random.choice(dlgs)
		_=_.reply_text
		print('line25',_)
		if(len(_)>=minlen/__ and len(_)<maxlen*__):
			ret=_
		__=__*rate
	temp=ret.replace('你','cantbeinthestring')
	temp=temp.replace('我','你')
	temp=temp.replace('cantbeinthestring','我')
	return temp
members_cache={}
@receiver
@on_exception_send
@start_with('问')
def wen(ctx,match,rest):
	global members_cache
	temp=rest.strip()
	sctx=simple_ctx(ctx)
	if(not(temp)):
		return
	if(judge_abua(temp)):
		while(judge_abua(temp)):
			_=judge_abua(temp)
			__=random.choice([_[0],_[1:]])
			temp=temp.replace(_,__,1)
		'''ret=temp.replace('你','cantbeinthestring')
		ret=ret.replace('我','你')
		ret=ret.replace('cantbeinthestring','我')
		temp=ret'''
	while('还是' in temp):
		tmp1=''
		if(('是' in temp)and(temp.index('是')<temp.index('还是'))):
			idx=temp.index('是')
			tmp1=temp[:idx+1]
			temp=temp[idx+1:]
		_=temp.split('还是')
		ret=tmp1+random.choice(_)
		'''ret=ret.replace('你','cantbeinthestring')
		ret=ret.replace('我','你')
		ret=ret.replace('cantbeinthestring','我')'''
		temp=ret
	def shui():
		if(random.random()<0.95):
			gid=int(simple_ctx(ctx).group_id)
			members_=None
			if(gid in members_cache):
				tm,members_=members_cache[gid]
				if(time.time()>tm+120):
					members_=None
			if(members_ is None):
				import bot_backend
				if(bot_backend._backend_type=='cqhttp'):
					from bot_backend import _bot
					ls=_bot.sync.get_group_member_list(self_id=int(sctx.self_id),group_id=int(sctx.group_id))
					members_=[]
					for i in ls:
						lvl=int(i['level'])
						members_+=[i['card'] or i['nickname']] * lvl * lvl
					
				else:
					from bot_backend import _acts_noq
					act=_acts_noq[ctx.CurrentQQ]
					#members=act.get_group_user_list(int(simple_ctx(ctx).group_id))
					members=act.getGroupMembers(int(simple_ctx(ctx).group_id))
					members=list(members)
					members_=[]
					for i in members:
						for j in range(i['MemberLevel']*i['MemberLevel']):
							members_.append(i['GroupCard'] or i['NickName'])
				members_cache[gid]=time.time(),members_
			return random.choice(members_)
		else:
			return random_mes_rec(minlen=2,maxlen=3)
	smgsm=re.compile('干?什么|怎么做')
	if('plg_chat' in plugins):
		if(('为什么' in temp) or smgsm.findall(temp) or ('谁' in temp)):
			_=temp.split('为什么')
			__=len(_)-1
			__=[random_mes_rec(minlen=3,maxlen=7) for ___ in range(__)]
			ret=''
			for i in range(len(__)):
				ret+=_[i]+'因为'+__[i]+'，所以'
			ret+=_[-1]
			
			#_=ret.split('什么')
			_=smgsm.split(ret)
			__=len(_)-1
			__=[random_mes_rec(maxlen=5) for ___ in range(__)]
			ret=''
			for i in range(len(__)):
				ret+=_[i]+__[i]
			ret+=_[-1]
			
			_=ret.split('谁')
			__=len(_)-1
			__=[shui() for ___ in range(__)]
			ret=''
			for i in range(len(__)):
				ret+=_[i]+__[i]
			ret+=_[-1]
			
			'''ret=ret.replace('你','cantbeinthestring')
			ret=ret.replace('我','你')
			ret=ret.replace('cantbeinthestring','我')'''
			temp=ret
	if('多少' in temp):
		_=temp.split('多少')
		temp=''
		for i in range(len(_)-1):
			temp+=_[i]+str(random.randint(1,100))
		temp+=_[-1]
	if('几个' in temp):
		_=temp.split('几个')
		temp=''
		for i in range(len(_)-1):
			temp+=_[i]+str(random.randint(1,10))+"个"
		temp+=_[-1]
	
	if(temp==rest.strip()):
		return
	temp=temp.replace('你','cantbeinthestring')
	temp=temp.replace('我','你')
	temp=temp.replace('cantbeinthestring','我')
	simple_send(ctx,temp)
	return
@receiver
@on_exception_send
@start_with('[/!！]?roll')
def roll(ctx,match,rest):
	sctx=simple_ctx(ctx)
	temp=rest.strip()
	if(not(temp)):
		if(sctx.simple_id in last_roll):
			temp=last_roll[sctx.simple_id]
		else:
			simple_send(ctx,'您还没有输入要骰什么内容呐！')
			return
	last_roll[sctx.simple_id]=temp
	if(re.match(r'\d+d\d+$',temp)):
		m,n=re.findall('\d+',temp)
		m=int(m)
		n=int(n)
		mes=[]
		for i in range(m):
			mes.append(random.randint(1,n))
		if(m>1):
			sm=sum(mes)
			ret='+'.join([str(_) for _ in mes])+'='+str(sm)
		else:
			ret=str(mes[0])
	elif(judge_abua(temp)):
		while(judge_abua(temp)):
			_=judge_abua(temp)
			__=random.choice([_[0],_[1:]])
			temp=temp.replace(_,__,1)
		ret=temp.replace('你','cantbeinthestring')
		ret=ret.replace('我','你')
		ret=ret.replace('cantbeinthestring','我')
		
	else:		
		_=temp.split()
		if(len(_)>1):
			ret=random.choice(_)
			ret='当然是%s啦~'%ret
		else:
			ret=path.join(mainpth,'Mea音','roll.mp3')
	simple_send(ctx,ret)