from lcg import lcg
from os import path
from PIL import Image
from glob import glob
import random
workpth=path.dirname(__file__)+r'\emoji'
lcg_l=lcg(workpth=workpth,expiretime=3600)
def format_name(a):
	
	if(isinstance(a,int)):
		ret = hex(a)
	elif(isinstance(a,str)):
		if(len(a)==1):
			ret = hex(ord(a))
		else:
			ret = hex(int(a,16))
	if(ret[:2]=='0x'):
		return ret[2:]
def get_git_twemoji(a,res='72x72'):
	a=format_name(a)
	#url=r'https://raw.githubusercontent.com/twitter/twemoji/gh-pages/%s/%s.png'%(res,a)
	url=r'https://github.com/twitter/twemoji/raw/master/assets/%s/%s.png'%(res,a)
	print(url)
	return lcg_l.get_image(url,proxies={})
def get_twimg(a,res='72x72'):
	a=format_name(a)
	url=r'https://abs.twimg.com/emoji/v2/%s/%s.png'%(res,a)
	return lcg_l.get_image(url,proxies={})
def get_openemoji(a):
	a=format_name(a).upper()
	url="https://openmoji.org/php/download_from_github.php?emoji_hexcode=%s&emoji_variant=color"%a
	return lcg_l.get_image(url,proxies={})
def get_emoji(a):
	try:
		return get_openemoji(a)
	except Exception as e:
		print('ln47',e)
	try:
		return get_git_twemoji(a)
	except Exception as e:
		print('ln32',e)
	try:
		return get_twimg(a)
	except Exception as e:
		print('ln37',e)
	return Image.open(random.choice(glob(workpth+r'\err\*.png')))
	
if(__name__=='__main__'):
	get_emoji(0x1f195).show()