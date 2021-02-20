import json,os,random
from os import path,makedirs
#dpcnt=0
class ls_iterator:
	def __init__(self,l):
		self.l=l
		self.n=0
	def __next__(self):
		if(self.n>=self.l.size):
			raise StopIteration()
		ret=self.l[self.n]
		self.n+=1
		return ret
class ls:
	def __len__(self):
		return self.size
	def _loadpart(self,part):
		if(part in self.loaded):
			return
		pth=path.join(self.pth,"%d.json"%part)
		if(path.exists(pth)):
			f=open(pth,'r')
			self._setpart(part,json.load(f))
			f.close()
		self.loaded.add(part)
	def _setpart(self,part,j):
		while(len(self.parts)<=part):
			self.parts.append(None)
		self.parts[part]=j
	def _dumppart(self,part):
		
		if(part not in self.loaded):
			self._loadpart(part)
		pth=path.join(self.pth,"%d.json"%part)
		try:
			if(self.parts[part] is not None):
				f=open(pth,'w')
				json.dump(self.parts[part],f)
				f.close()
		except IndexError as e:
			print(len(self.parts))
			print(self.lazy_save)
			raise e
	def __setitem__(self,idx,value):
		if(idx>=self.size):
			raise IndexError
		part=idx//self.split
		_idx=idx%self.split
		if(part not in self.loaded):
			self._loadpart(part)
		if(self.parts[part] is None):
			self.parts[part]=[None for _ in range(self.split)]
		self.parts[part][_idx]=value
		if(self.lazy_save is False):
			self._dumppart(part)
		else:
			self.lazy_save.add(part)
	def save_lazy(self):
		if(not self.lazy_save):
			return
		for i in self.lazy_save:
			self._dumppart(i)
		self.lazy_save=set()
	def __getitem__(self,idx):
		if(isinstance(idx,slice)):
			start,stop,step=0,self.size,1
			if(idx.start is not None):
				start=idx.start
			if(idx.stop is not None):
				stop=(idx.stop+self.size)%self.size
			if(idx.step is not None):
				step=idx.step
				if(step<0 and start<stop):
					start,stop=stop-1,start-1
			return [self[i] for i in range(start,stop,step)]
		if(idx>=self.size):
			raise IndexError
		part=idx//self.split
		if(part not in self.loaded):
			self._loadpart(part)
		_idx=idx%self.split
		return self.parts[part][_idx]
	def append(self,value):
		idx=self.size
		if(idx>=self.split*self.split*self.split):
			#enen=int(idx**0.5)
			self.change_split(2*self.split)
		part=idx//self.split
		while(len(self.parts)<=part):
			self.parts.append(None)
		self.size+=1
		self.__setitem__(idx,value)
		self._dumpmeta()
	def _dumpmeta(self):
		j={'size':self.size,'split':self.split}
		f=path.join(self.pth,'meta.json')
		f=open(f,'w')
		json.dump(j,f)
		f.close()
	def pop(self):
		if(self.size):
			self.size-=1
			self._dumpmeta()
		else:
			raise IndexError
	def __init__(self,pth,split=4,lazy_save=False):
		self.pth=pth
		if(not path.exists(pth)):
			makedirs(pth)
		self.split=split
		if(path.exists(path.join(pth,'meta.json'))):
			f=open(path.join(pth,'meta.json'),'r')
			j=json.load(f)
			f.close()
			self.size=j['size']
			self.split=j['split']
		else:
			self.size=0
			self.split=split
		self.parts=[]
		self.loaded=set()
		if(lazy_save is True):
			self.lazy_save=set()
		else:
			self.lazy_save=False
	def clear(self):
		self.size=0
		self._dumpmeta()
	def __iter__(self):
		return ls_iterator(self)
	def change_split(self,new_split):
		self.save_lazy()
		tmp=[]
		for i in self:
			tmp.append(i)
		for i in range(self.size//self.split):
			os.remove(path.join(self.pth,"%d.json"%i))
		self.split=new_split
		self.size=0
		
		self._dumpmeta()
		self.parts=[]
		self.loaded=set()
		for i in tmp:
			self.append(i)
		self.save_lazy()
class treap_iterator():
	def __init__(self,tree):
		self.tree=tree
		self.stk_u=[tree.root]
		self.stk_i=[0]
		self.visited=[0 for i in range(tree.size)]
	
	def __next__(self):
		if(not self.tree.size):
			raise StopIteration()
		while(self.stk_u):
			u=self.stk_u[-1]
			i=self.stk_i[-1]
			if(i==0):
				# print('ln15',u)
				self.stk_i[-1]=i=1
				#print(u,self.tree.size)
				if(self.tree.lson[u]!=None):
					self.stk_u.append(self.tree.lson[u])
					self.stk_i.append(0)
					continue
				
			if(i==1):
				# print('ln22',u)
				self.stk_i[-1]=i=2
				return self.tree.key[u]
			if(i==2):
				# print('ln26',u)
				self.stk_i[-1]=i=3
				if(self.tree.rson[u]!=None):
					self.stk_u.append(self.tree.rson[u])
					self.stk_i.append(0)
					continue
				
			# print('ln32',u)
			self.stk_u.pop()
			self.stk_i.pop()
		raise StopIteration()
class treap:
	def __init__(self):
		self.root=None
		#self.empty_idx=[]
		self.data=[]
		self.key=[]
		self.sizes=[]
		self.lson=[]
		self.rson=[]
		self.fa=[]
		self.hkey=[]
	def _lower_bound(self,key):
		ret=u=self.root
		while(u is not None):
			ls=self.lson[u]
			rs=self.rson[u]
			k=self.key[u]
			if(key<k):
				if(ls is None):
					return ret
				else:
					ret=u
					u=ls
			elif(key>k):
				if(rs is None):
					return ret
				else:
					u=rs
			else:
				return u
		return ret
	def lrfk(self,idx):
		return self.lson[idx],self.rson[idx],self.fa[idx],self.key[idx]
	def _append(self,key,data,hkey):
		ret=len(self.data)
		self.data.append(data)
		self.key.append(key)
		self.hkey.append(hkey)
		self.sizes.append(1)
		self.lson.append(None)
		self.rson.append(None)
		self.fa.append(None)
		return ret
	def kdh(self,u):
		return self.key[u],self.data[u],self.hkey[u]
	def swap_data(self,u,v):
		k,d,h=self.kdh(u)
		self.key[u]=self.key[v]
		self.data[u]=self.data[v]
		self.hkey[u]=self.hkey[v]
		self.key[v]=k
		self.data[v]=d
		self.hkey[v]=h
	def _get_sizes(self,u):
		if(u is None):
			return 0
		else:
			return self.sizes[u]
	def rotup(self,u):
		ls,rs,fa,k=self.lrfk(u)
		if(fa is None):
			return
		lfa,rfa,fafa,kfa=self.lrfk(fa)
		
		if(k<kfa):
			self.rson[u]=fa
			self.fa[fa]=u
			
			self.lson[fa]=rs
			if(rs is not None):
				self.fa[rs]=fa
			
			self.sizes[fa]=self._get_sizes(rs)+self._get_sizes(rfa)+1
			self.sizes[u]=self._get_sizes(ls)+self.sizes[fa]+1
		else:
			self.lson[u]=fa
			self.fa[fa]=u
			
			self.rson[fa]=ls
			if(ls is not None):
				self.fa[ls]=fa
			
			self.sizes[fa]=self._get_sizes(lfa)+self._get_sizes(ls)+1
			self.sizes[u]=self._get_sizes(rs)+self.sizes[fa]+1
		
		self.fa[u]=fafa
		if(fafa is None):
			self.root=u
		else:
			if(fa==self.lson[fafa]):
				self.lson[fafa]=u
			else:
				self.rson[fafa]=u
	def popup(self,u):
		while(True):
			ls,rs,fa,k=self.lrfk(u)
			h=self.hkey[u]
			if(fa is None):
				break
			if(h>self.hkey[fa]):
				break
			else:
				self.rotup(u)
				'''print('===')
				print(self.lson)
				print(self.rson)		
				print(self.fa)		'''
	def swap_idx(self,u,v):
		if(self.fa[u]==v):
			return self.swap_idx(v,u)
		lu,ru,fu,ku=self.lrfk(u)
		lv,rv,fv,kv=self.lrfk(v)
		su=self.sizes[u]
		self.sizes[u]=self.sizes[v]
		self.sizes[v]=su
		if(self.root==u):
			self.root=v
		elif(self.root==v):
			self.root=u
		self.swap_data(u,v)
		if(lu==v):
			#print('ln154')
			if(lv is not None):
				self.fa[lv]=u
			if(rv is not None):
				self.fa[rv]=u
			self.lson[u]=lv
			self.rson[u]=rv
			self.fa[u]=v
			self.lson[v]=u
			if(ru is not None):
				self.fa[ru]=v
			self.rson[v]=ru
			self.fa[v]=fu
			if(fu is not None):
				if(u==self.lson[fu]):
					self.lson[fu]=v
				else:
					self.rson[fu]=v
		elif(ru==v):
			#print('ln173')
			if(lv is not None):
				self.fa[lv]=u
			self.lson[u]=lv
			
			if(rv is not None):
				self.fa[rv]=u
			self.rson[u]=rv
			
			self.fa[u]=v
			self.rson[v]=u
			if(lu is not None):
				self.fa[lu]=v
			self.lson[v]=lu
			self.fa[v]=fu
			if(fu is not None):
				if(u==self.rson[fu]):
					self.rson[fu]=v
				else:
					self.lson[fu]=v
		elif((fu is not None)and(fu==fv)):
			rf=self.rson[fu]
			self.rson[fu]=self.lson[fu]
			self.lson[fu]=rf
			
			if(lu is not None):
				self.fa[lu]=v
			self.lson[v]=lu
			if(ru is not None):
				self.fa[ru]=v
			self.rson[v]=ru
			
			if(rv is not None):
				self.fa[rv]=u
			self.rson[u]=rv
			if(lv is not None):
				self.fa[lv]=u
			self.lson[u]=lv
		else:
			if(lu is not None):
				self.fa[lu]=v
			self.lson[v]=lu
			if(ru is not None):
				self.fa[ru]=v
			self.rson[v]=ru
			if(fu is not None):
				if(u == self.lson[fu]):
					self.lson[fu]=v
				else:
					self.rson[fu]=v
			self.fa[v]=fu
			
			if(rv is not None):
				self.fa[rv]=u
			self.rson[u]=rv
			if(lv is not None):
				self.fa[lv]=u
			self.lson[u]=lv
			if(fv is not None):
				if(v==self.lson[fv]):
					self.lson[fv]=u
				else:
					self.rson[fv]=u
			self.fa[u]=fv
		return
	def remove(self,u):
		while(True):
			l,r,f,k=self.lrfk(u)
			if(l is None):
				if(r is None):
					if(f is None):
						self.root=None
						self.data.pop()
						self.key.pop()
						self.hkey.pop()
						self.sizes.pop()
						self.lson.pop()
						self.rson.pop()
						self.fa.pop()
						return
					
					if(u != self.size-1):
						self.swap_idx(u,self.size-1)
					u=self.size-1
					fu=self.fa[u]
					#print('ln238',self.lson[u],self.rson[u],self.fa[u])
					if(fu is not None):
						if(self.lson[fu]==u):
							self.lson[fu]=None
						else:
							self.rson[fu]=None
					while(fu is not None):
						self.sizes[fu]-=1
						fu=self.fa[fu]
					self.sizes.pop()
					self.data.pop()
					self.key.pop()
					self.hkey.pop()
					self.fa.pop()
					self.lson.pop()
					self.rson.pop()
					return
				else:
					self.rotup(r)
			else:
				if(r is None):
					self.rotup(l)
				else:
					if(self.hkey[l]<self.hkey[r]):
						self.rotup(l)
					else:
						self.rotup(r)
			
	def insert(self,key,data,hkey=None):
		u=self.root
		if(hkey is None):
			hkey=random.random()
		if(u is None):
			self.data.append(data)	#self.data=[data]
			self.key.append(key)	#self.key=[key]
			self.sizes.append(1)	#self.sizes=[1]
			self.lson.append(None)	#self.lson=[None]
			self.rson.append(None)	#self.rson=[None]
			self.fa.append(None)	#self.fa=[None]
			self.hkey.append(hkey)	#self.hkey=[hkey]
			self.root=0
			return 0
		lb=self._lower_bound(key)
		if(self.key[lb]==key):
			self.data[lb]=data
			return lb
		while(True):
			self.sizes[u]+=1
			ls,rs,fa,k=self.lrfk(u)
			if(key<k):
				if(ls is None):
					v=self._append(key,data,hkey)
					self.fa[v]=u
					self.lson[u]=v
					self.popup(v)
					return v
				else:
					u=ls
			else:
				if(rs is None):
					v=self._append(key,data,hkey)
					self.fa[v]=u
					self.rson[u]=v
					self.popup(v)
					return v
				else:
					u=rs
	@property
	def size(self):
		return len(self.data)
	def rank(self,idx):
		u=self.root
		idx+=1
		while(True):
			_=self._get_sizes(self.lson[u])
			if(idx<=_):
				u=self.lson[u]
			elif(idx==_+1):
				return u
			else:
				idx-=_+1
				u=self.rson[u]
	def __iter__(self):
		return treap_iterator(self)
	def __getitem__(self,key):
		lb=self._lower_bound(key)
		if(self.key[lb]==key):
			return self.data[lb]
		else:
			raise KeyError(key)
	def __setitem__(self,key,value):
		self.insert(key,value)
	def __contains__(self,key):
		if(not self.size):
			return False
		if(self.root is None):
			return False
		lb=self._lower_bound(key)
		return self.key[lb]==key
	def pop(self,key):
		lb=self._lower_bound(key)
		if(self.key[lb]==key):
			ret=self.data[lb]
			self.remove(lb)
			return ret
		else:
			raise KeyError(key)
	def get(self,key,*args):
		lb=self._lower_bound(key)
		if(self.key[lb]==key):
			return self.data[lb]
		elif(args):
			return args[0]
		else:
			raise KeyError(key)
	def _max_depth(self):
		dep=[-1 for _ in range(self.size)]
		def get_dep(u):
			if(self.fa[u] is None):
				return 0
			if(dep[u]!=-1):
				return dep[u]
			ret=get_dep(self.fa[u])+1
			dep[u]=ret
			return ret
		mx=0
		for i in range(self.size):
			mx=max(mx,get_dep(i))
		return mx
class saved_treap(treap):
	def save_lazy(self):
		for l in [self.data,self.key,self.sizes,self.rson,self.lson,self.fa,self.hkey]:
			l.save_lazy()
	def __setitem__(self,key,value):
		treap.__setitem__(self,key,value)
		self.save_lazy()
	def pop(self,key):
		treap.pop(self,key)
		self.save_lazy()
	def __init__(self,pth,lazy_save=True):
		self.pth=pth
		if(not path.exists(pth)):
			os.makedirs(pth)
		if(path.exists(path.join(pth,'meta.json'))):
			f=open(path.join(pth,'meta.json'))
			j=json.load(f)
			self.root=j['root']
			f.close()
		else:
			self.root=None
		self.data=ls(path.join(pth,'data'),lazy_save=lazy_save)
		self.key=ls(path.join(pth,'key'),lazy_save=lazy_save)
		self.sizes=ls(path.join(pth,'sizes'),lazy_save=lazy_save)
		self.rson=ls(path.join(pth,'rson'),lazy_save=lazy_save)
		self.lson=ls(path.join(pth,'lson'),lazy_save=lazy_save)
		self.fa=ls(path.join(pth,'fa'),lazy_save=lazy_save)
		self.hkey=ls(path.join(pth,'hkey'),lazy_save=lazy_save)
	
	def __setattr__(self,name,value):
		treap.__setattr__(self,name,value)	
		if(name=='root'):
			self._dumpmeta()
		
	def _dumpmeta(self):
		f=open(path.join(self.pth,'meta.json'),'w')
		json.dump({'root':self.root},f)
		f.close()
if(__name__=='__main__'):
	a=saved_treap(r'C:\setubot-iot\temp1',lazy_save=True)
	print([_ for _ in a])
	for i in '1234567890azxswdqcevrvfkiutrg-=][;':
		a[i]='value:'+i
	if('fuck' in a):
		a.pop('fuck')
	else:
		a['fuck']='az'
	print([_ for _ in a])
	print(a.key[a.rank(a.size-1)])
	#print(dpcnt)