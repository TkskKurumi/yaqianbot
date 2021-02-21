import saucenao_api_json,pyxyv,myhash
def getPixivPID(filename,timeout=30,donotreloadpyxyvsave=None,donotsearchsaucenao=True):
	if(not ('ERR' in str(pyxyv.getImgPID(filename)))):
		return str(pyxyv.getImgPID(filename,donotreloadpyxyvsave))
	if(not(donotsearchsaucenao)):
		pid=str(saucenao_api_json.getPixivPID(filename,timeout=timeout))
		if(not('ERR' in pid)):
			pyxyv.saveImgPID(filename,pid)
		return pid
	
	return 'NO_PIXIV_ID_ERR'
if(__name__=='__main__'):
	file=r"J:\new\setubot\temp\tempcache\VUU14g8XeMYu6wQIMQWu1.jpg"
	#print(myhash.hashs(file))#20EpmW
	#print(saucenao_api_json.getPixivPID(file))
	print(getPixivPID(file,donotsearchsaucenao=False))
	#print(isinstance(getPixivPID(r"D:\pyxyv\tempimgcache\2cpmJVeC2M48WM.jpg"),str))
	