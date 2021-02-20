def lower_bound(ls,v,key=lambda x:x):
	l=-1
	r=len(ls)
	while(l<r-1):
		mid=(l+r)//2
		
		#print(l,r)
		
		if(key(ls[mid])>=key(v)):
			r=mid
		else:
			l=mid
	
	return r
	
if(__name__=='__main__'):
	temp=[1,2,3,4,5,6,7,8,9,114]
	temp.sort()
	key=-1
	found=lower_bound(temp,key)
	if(found!=len(temp)):
		print(temp[lower_bound(temp,key)])
	else:
		print('found==temp.end()')
		