import random,algorithm,math
#加权的random.choice
#权重全为0的时候会返回none
def is_nan(i):
	return (i<0)==(i>0) and i!=0
def weightchoice(weight,ls):
	
	if(len(ls)==1):
		return ls[0]
	s=[]
	SUM=0
	for idx,i in enumerate(weight):
		SUM+=0 if is_nan(i) else i
		if(is_nan(i)):
			print(i,ls[idx])
		s.append(SUM)
		
	r=random.random()*SUM
	'''if(algorithm.lower_bound(s,r)==len(ls)):
		print(s[-5:],SUM)'''
	return ls[algorithm.lower_bound(s,r)]
weight_choice=weightchoice
if(__name__=='__main__'):
	
	w=[0,0,0,math.inf]
	l=[2,4,8,0.01]
	freq={}
	
	for i in range(1000):
		c=weightchoice(w,l)
		freq[c]=freq.get(c,0)+1
	print(freq,w,l)
	