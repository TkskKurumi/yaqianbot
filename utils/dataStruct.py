import random,copy,mymath
from os import path
class heap:
	def __init__(self,values=[],fcmp=lambda x,y:1 if(x>y) else 0 if(x==y) else -1,rev=1):
		self.values=[]
		self.fcmp_=fcmp
		self.rev=rev
		self.fcmp=lambda x,y:self.rev*self.fcmp_(x,y)
		rev=1
		for i in values:
			self.push(i)
	def fa(u):
		return int((u-1)/2)
	def le(u):
		return u*2+1
	def ri(u):
		return u*2+2
	def size(self):
		return len(self.values)
	def sw(self,u,v):
		swap=copy.copy(self.values[u])
		self.values[u]=self.values[v]
		self.values[v]=swap
	def push(self,v):
		u=self.size()
		self.values.append(v)
		fa=heap.fa(u)
		fcmp=self.fcmp
		while(fcmp(self.values[u],self.values[fa])==1):
			swap=copy.copy(self.values[u])
			self.values[u]=self.values[fa]
			self.values[fa]=swap
			u=fa
			fa=heap.fa(u)
		return v
	def pop(self):
		ret=copy.copy(self.values[0])
		self.sw(0,-1)
		self.values.pop(-1)
		u=0
		ri=heap.ri(u)
		le=heap.le(u)
		fcmp=self.fcmp
		while(ri<self.size()):
			if(fcmp(self.values[le],self.values[ri])==1):
				v=le
			else:
				v=ri
			if(fcmp(self.values[v],self.values[u])==1):
				self.sw(u,v)
			else:
				break
		return ret
class treap:
	def __init__(self,keys=[],values=[],fcmp=lambda x,y:1 if(x>y) else 0 if(x==y) else -1):
		self.fcmp=fcmp
		self.root=-1
		self.keys=[]
		self.size=0
		self.values=[]
		self.hkeys=[]
		self.lson=[]
		self.rson=[]
		self.fa=[]
		for i in range(len(keys)):
			self.add(keys[i],values[i])
	def remove(self,key):
		u=self.find1(key,self.root)
		if(self.keys[u]!=key):
			return None
		
	def find1(self,key,u):
		#print('key=%d,key[u]=%d'%(key,self.keys[u]))
		if(self.fcmp(key,self.keys[u])==0):
			return u
		elif(self.fcmp(key,self.keys[u])==-1):
			if(self.lson[u]==-1):
				return u
			else:
				return self.find1(key,self.lson[u])
		else:
			if(self.rson[u]==-1):
				return u
			else:
				return self.find1(key,self.rson[u])
	def isrson(self,u):
		fa=self.fa[u]
		if(fa==-1):
			return False
		else:
			return u==self.rson[fa]
	def lrot(self,u):
		if(not(self.isrson(u))):
			return None
		fa=self.fa[u]
		L=self.lson[u]
		gfa=self.fa[fa]
		#print('lrot%d,fa=%d'%(u,fa))
		#self.dbgpr()
		if(gfa!=-1):
			if(self.isrson(fa)):
				self.rson[gfa]=u
			else:
				self.lson[gfa]=u
		else:
			self.root=u
		self.fa[u]=gfa
		self.fa[fa]=u
		self.lson[u]=fa
		self.rson[fa]=L
		return True
	def rrot(self,u):
		
		if(self.isrson(u)):
			return None
		fa=self.fa[u]
		if(fa==-1):
			return None
		
		R=self.rson[u]
		gfa=self.fa[fa]
		if(gfa!=-1):
			if(self.isrson(fa)):
				self.rson[gfa]=u
			else:
				self.lson[gfa]=u
		else:
			self.root=u
		self.fa[u]=gfa
		self.rson[u]=fa
		self.fa[fa]=u
		self.lson[fa]=R
		return True
	def get(self,key,*default):
		f1=self.find1(key,self.root)
		if(self.keys[f1]==key):
			return self.values[f1]
		elif default:
			return default[0]
		else:
			raise KeyError(key)
	def add(self,key,value):
		if(self.root==-1):
			self.keys.append(key)
			self.values.append(value)
			self.hkeys.append(random.random())
			self.lson.append(-1)
			self.rson.append(-1)
			self.root=0
			self.fa.append(-1)
			#self.dbgpr()
			self.size=1
			return None
		if(self.get(key,None)is not None):
			u=self.find1(key,self.root)
			self.values[u]=value
			return None
		fa=self.find1(key,self.root)
		u=self.size
		if(self.fcmp(key,self.keys[fa])==-1):
			self.lson[fa]=u
		else:
			self.rson[fa]=u
		self.fa.append(fa)
		self.lson.append(-1)
		self.rson.append(-1)
		self.keys.append(key)
		self.values.append(value)
		self.hkeys.append(random.random())
		self.size+=1
		#self.dbgpr()
		while(self.up(u)):
			pass
		return None
	def up(self,u):
		fa=self.fa[u]
		if(fa==-1):
			return False
		if(self.hkeys[fa]<self.hkeys[u]):
			return False
		if(self.isrson(u)):
			self.lrot(u)
		else:
			self.rrot(u)
		return True
	def down(self,u):
		ls=self.lson[u]
		rs=self.rson[u]
		if(ls==-1):
			if(rs==-1):
				return False
			return self.lrot(rs)
		if(rs==-1):
			self.rrot(ls)
		if(self.hkeys[ls]<self.hkeys[rs]):
			return self.rrot(ls)
		else:
			return self.lrot(rs)
	def dbgpr(self):
		print(self.keys)
		print(self.lson)
		print(self.rson)
		print(self.fa)
		print(self.root)
	def sort(self):
		if(self.size==0):
			return None
		newi=[0]*self.size
		i_=['L']
		u_=[self.root]
		ni=0
		while(i_):
			u=u_[-1]
			if(i_[-1]=='L'):
				i_[-1]='M'
				if(self.lson[u]!=-1):
					i_.append('L')
					u_.append(self.lson[u])
					continue
			if(i_[-1]=='M'):
				i_[-1]='R'
				newi[u]=ni
				ni+=1
				if(self.rson[u]!=-1):
					i_.append('L')
					u_.append(self.rson[u])
					continue
			if(i_[-1]=='R'):
				i_.pop(-1)
				u_.pop(-1)
		keys_=[0]*self.size
		hkey_=[0]*self.size
		values_=[0]*self.size
		fa_=[0]*self.size
		lson_=[0]*self.size
		rson_=[0]*self.size
		for i in range(self.size):
			keys_[newi[i]]=self.keys[i]
			hkey_[newi[i]]=self.hkeys[i]
			values_[newi[i]]=self.values[i]
			
			fa_[newi[i]]=(lambda x:-1 if(x==-1)else newi[x])(self.fa[i])
			
			lson_[newi[i]]=(lambda x:-1 if(x==-1)else newi[x])(self.lson[i])
			rson_[newi[i]]=(lambda x:-1 if(x==-1)else newi[x])(self.rson[i])
		self.keys=keys_
		self.hkeys=hkey_
		self.fa=fa_
		self.root=newi[self.root]
		self.lson=lson_
		self.rson=rson_
		self.values=values_
		return keys_
		
class DJSet:
	def __init__(self,svpth):
		self.next={}
		self.svpth=svpth
		if(path.exists(svpth)):
			self.next=json.loads(chardetopen.opentext(svpth))
	def ufind1(self,u):
		if(not(u in self.next)):
			return u
		elif(self.next[u]==u):
			return u
		self.next[u]=self.ufind1(self.next[u])
		return self.next[u]
	def union(self,u,v):
		u=self.ufind1(u)
		v=self.ufind1(v)
		if(u==v):
			return None
		self.next[u]=v
		self.save()
	def save(self,savepth=None):
		if(not(savepth)):
			savepth=self.svpth
		if(savepth=='do_not_save'):
			return None
		fh=open(self.svpth,'w')
		fh.write(json.dumps(self.next))
		fh.close()
	def ufind(self,u):
		ret=self.ufind1(u)
		self.save()
		return ret

class djs_int:
	def __init__(self,svpth,size):
		self.next=[i for i in range(size)]
		self.svpth=svpth
		if(path.exists(svpth)):
			self.next=json.loads(chardetopen.opentext(svpth))
	def ufind1(self,u):
		if(self.next[u]==u):
			return u
		#print('u',u,'find next',self.next[u])
		self.next[u]=self.ufind1(self.next[u])
		return self.next[u]
	def union(self,u,v):
		u=self.ufind1(u)
		v=self.ufind1(v)
		if(u==v):
			return None
		self.next[u]=v
		self.save()
	def save(self,savepth=None):
		if(not(savepth)):
			savepth=self.svpth
		if(savepth=='do_not_save'):
			return None
		fh=open(self.svpth,'w')
		fh.write(json.dumps(self.next))
		fh.close()
	def ufind(self,u):
		ret=self.ufind1(u)
		self.save()
		return ret



class segmentTree_count_2d:
	def __init__(self,data,width,height,left=0,upper=0):	#左闭右开
		self.left,self.upper,right,lower=left,upper,left+width,upper+height
		self.right,self.lower=right,lower
		#print(left,upper,width,height)
		self.height,self.width=height,width
		self.data=data
		midx=int(left+width/2)
		midy=int(upper+height/2)
		self.midx,self.midy=midx,midy
		if(height*width==0):
			self.count={}
			return None
		if(width==1 and height==1):
			c=data[left][upper]
			self.count={c:1}
			return None
		self.sons=[[None for i in range(2)]for j in range(2)]
		self.count={}
		lefts=[left,midx]
		uppers=[upper,midy]
		widths=[midx-left,right-midx]
		heights=[midy-upper,lower-midy]
		for i in range(2):
			for j in range(2):
				l,u,w,h=lefts[i],uppers[j],widths[i],heights[j]
				#print('from',width,height,left,upper)
				#print('to',w,h,l,u)
				#input()
				s=segmentTree_count_2d(data,w,h,l,u)
				self.sons[i][j]=s
				for c in s.count:
					self.count[c]=self.count.get(c,0)+s.count[c]
	def update(self,width,height,left,upper):
		right,lower=left+width,upper+height
		if(self.width*self.height==0):
			return {}
		if(width*height==0):
			return self.count
		if((self.width==1)and(self.height==1)):
			self.count={self.data[self.left][self.upper]:1}
			return self.count
		if((right<=self.left)or(self.right<=left)or(lower<=self.upper)or(self.lower<=upper)):
			return self.count
		# print(left,upper,right,lower)
		# print(self.left,self.upper,self.right,self.lower,self.width,self.height)
		
		ret={}
		for i in range(2):
			for j in range(2):
				s=self.sons[i][j]
				co=s.update(width,height,left,upper)
				for c in co:
					ret[c]=ret.get(c,0)+co[c]
		self.count=ret
		return self.count
	def query(self,width,height,left,upper):
		right,lower=left+width,upper+height
		if(self.width*self.height==0):
			return {}
		if(width*height==0):
			return {}
		if((right<=self.left)or(self.right<=left)or(lower<=self.upper)or(self.lower<=upper)):
			return {}
		if((left<=self.left)and(self.right<=right)and(upper<=self.upper)and(self.lower<=lower)):
			return self.count
			
		ret={}
		for i in range(2):
			for j in range(2):
				s=self.sons[i][j]
				co=s.query(width,height,left,upper)
				for c in co:
					ret[c]=ret.get(c,0)+co[c]
		return ret
	def queryEnt(self,width,height,left,upper):
		c=self.query(width,height,left,upper)
		c=[c[i] for i in c]
		return mymath.calcEnt(c)
DJS=DJSet

class memo:
	def __init__(self,searchMethod=lambda x:x):
		self.searchMethod=searchMethod
		self.mem={}
	def get(self,key):
		if(key in self.mem):
			return self.mem[key]
		else:
			ret=self.searchMethod(key)
			self.mem[key]=ret
			return ret
	def pop(self,key,*default):
		return self.mem.pop(key,*default)

def debugTreap():
	#a=treap([233,123,521,89,7],['v233','v123','v521','v89','7'])
	lis=[[random.randint(0,5) for i in range(5)] for j in range(5) ]
	
	for i in range(5):
		print(lis[i])
		
		
	segmentTree=segmentTree_count_2d(lis,5,5,0,0)
	print(segmentTree.count)
	for i in range(2,5):
		for j in range(2,5):
			lis[i][j]=random.randint(0,10)
	
	for i in range(5):
		print(lis[i])
	
	segmentTree.update(3,3,2,2)
	print(segmentTree.query(3,3,2,2))
	print(segmentTree.count)
def arr(shape,fill=0):
	ret=[copy.deepcopy(fill) for i in range(shape[-1])]
	if(len(shape)>=2):
		for i in list(shape)[-2::-1]:
			ret=[copy.deepcopy(ret) for j in range(i)]
	return ret
if(__name__=="__main__"):
	
	def s(k):
		print('seach',k)
		return 'v'+k
	a=memo(s)
	print(a.get('fuck'))
	print(a.get('fuck'))
	print(a.get('shit'))
	print(a.get('shit'))
	print(a.pop('shit'))
	print(a.pop('shit','dne'))
	print(a.pop('shit'))
	
	