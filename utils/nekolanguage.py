import random
from struct import pack
def bin_rnd():
	return int(random.random()/0.5)
encoding='gb18030'
#a='abc'.encode(encoding)
#charcters='嗯喵啊哦呀嗷呜♡'
#charcters=['喵','啊♡','哦','嗷','呀♡','♡','呜','嗯喵']
charcters=['嗯喵','喵','啊','哦♡','呀♡','嗷','呜喵','♡','阿♡','哈','~','哒♡','哟','噢♡','..','喵!']
char2int={i:j for j,i in enumerate(charcters)}
#print(char2int)
#exit()
def neko_encode(s):
	s1=s.encode(encoding)
	n=len(s1)
	#print('n',n)
	ret=[]
	for i in range(n):
		i=int(s1[i])
		#print(i)
		#lo3=i&(0b111)
		#mid3=i&(0b111000)
		#hi2=(i&(0b11000000))|(bin_rnd()<<8)
		lo4=i&(0b1111)
		hi4=i>>4
		ret.extend([hi4,lo4])
	return ''.join([charcters[_] for _ in ret])
def neko_decode(s):
	ret=b''
	buf1=''
	buf2=[]
	le=len(s)
	for idx,i in enumerate(s):
		buf1+=i
		j=s[(idx+1)%le]
		if((buf1 in char2int)and(i+j!='喵!')):
			buf2.append(char2int[buf1])
			buf1=''
		#print(buf1)
		if(len(buf2)==2):
			#hi2,mid3,lo3=buf2
			hi4,lo4=buf2
			buf2=[]
			#hi2=hi2&0b11
			_=(hi4<<4)|lo4
			#print(_)
			ret+=pack('B',_)
	return ret.decode(encoding)
if(__name__=='__main__'):
	az=neko_encode('嗯喵翻译机')
	print(az)
	print(neko_decode(az))