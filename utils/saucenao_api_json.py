import chardet
import requests,re,myhash
from requests_toolbelt.multipart.encoder import MultipartEncoder
from PIL import Image
from os import path
proxy_dict = {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081"
}	

#saucenao识图json api

api_key="c3ac05e05caeae8a6b246acd274785e748398203"
index_hmags='0'
index_hanime='0'
index_hcg='0'
index_ddbobjects='0'
index_ddbsamples='0'
index_pixiv='1'
index_pixivhistorical='1'
index_anime='0'
index_seigaillust='1'
index_danbooru='0'
index_drawr='1'
index_nijie='1'
index_yandere='0'

#generate appropriate bitmask
db_bitmask = int(index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags,2)

minsim='120!'
def sizelimitmax(siz,limitsiz):
	r=1
	if(limitsiz[0]<siz[0]):
		r1=limitsiz[0]/siz[0]
		if(r1<r):
			r=r1
	if(limitsiz[1]<siz[1]):
		r1=limitsiz[1]/siz[1]
		if(r1<r):
			r=r1
	ret=tuple([int(i*r)for i in siz])
	return ret
	
def thumbedImgFile(filename):
	im=Image.open(filename)
	
	if((im.size[1]>660)or(im.size[0]>660)):
		siz=sizelimitmax(im.size,(660,660))
		
		savepth=path.dirname(__file__)+r'\temp\%s.jpg'%myhash.hashs(filename)
		im=im.resize(siz).convert('RGB')
		im.save(savepth,'JPEG',quality=90)
		return savepth
	else:
		return filename

def search(fh,timeout=30):
	if(isinstance(fh,str)):
		fh=thumbedImgFile(fh)
		fh=open(fh,'rb')
	#filename=r"G:\pic\PXSource_bot\AgADBQADKqgxGzPS4Vf6dWZf51Ed8_qs1jIABNNnJ6-KmDnyPHgBAAEC.jpg"
	filename=fh.name
	filetype='img/jpeg'
	if(filename[-3:]=='png'):
		filetype='img/png'
	url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim='+minsim+'&dbmask='+str(db_bitmask)+'&api_key='+api_key
	files = {'file': (path.basename(fh.name), fh.read())}
				
	'''data={'file':('filename',fh, filetype)}
	data=MultipartEncoder(fields=data,boundary='----------------fnmdhabi87w6et76BRWS')'''
	try:
		req = requests.post(url,files=files,timeout=timeout,proxies=proxy_dict)
		#print(req.text)
		return req.json()
		return None
	except Exception as e:
		return 'REQ_ERR'
	'''hsave=open(r'd:\temp.html','wb')
	hsave.write(req.content)
	hsave.close()'''
	
def getPixivURL(filename,timeout=30):
	res=search(filename,timeout=timeout)
	#print(res[0])
	try:
		for i in res['results']:
			if('Pixiv' in i):
				return i['Pixiv'][0]
	except Exception:
		return 'NO_PIXIV_ERR'
	return 'NO_PIXIV_ERR'
def getPixivPID(filename,timeout=30):
	res=search(filename,timeout=timeout)
	#fh=open(r'd:\temp.json','wb')
	#fh.write(str(res).encode('utf-8'))
	#fh.close()
	#print(res)
	try:
		for i in res['results']:
			if('pixiv_id' in i['data']):
				return i['data']['pixiv_id']
	except Exception:
		return 'NO_PIXIV_ERR'
	return 'NO_PIXIV_ERR'

if(__name__=='__main__'):
	'''fh=open(r'd:\temp.json','wb')
	fh.write(str(search(r"G:\pic\20180822\001.jpg")).encode('utf-8'))
	fh.close()
	'''
	pic=r"G:\pic\PXSource_bot\AgADBQADV6gxG6PV-FeV6_O3Gz-UEwxO1TIABG10UMeQkAOs6AkDAAEC.jpg"
	pic=r"J:\new\pic\65931813_p0.jpg"
	pic=r"J:\new\setubot\temp\tempcache\VUU14g8XeMYu6wQIMQWu1.jpg"
	j=getPixivPID(pic)
	print(j)
	for i in j['results']:
		print(i)
	print(getPixivPID(pic))
