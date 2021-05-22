from bot_backend import *
import wyy

def send_id(id):
	def inner(ctx):
		nonlocal id
		mp3=wyy.get_mp3(id)
		simple_send(ctx,mp3)
	return inner
def register_send_id(id):
	return '/kj %s'%plugins['plg_admin'].register_kjml('wyylisten%s'%id,send_id(id))

@receiver
@threading_run
@on_exception_send
@start_with(r'/搜歌')
def cmd_search_song(ctx,match,rest):
	k=rest.strip()
	results=wyy.search(k)
	ids=[i['id'] for i in results]
	if(len(ids)>10):
		ids=ids[:10]
	elif(len(ids)==0):
		simple_send(ctx,'呜呜，没有搜索结果！')
		return
	im=wyy.illustrate_ids(ids,extra_str=register_send_id)
	simple_send(ctx,im)
'''
host="localhost:3000"
def render_song_item(itm):
	albumid=itm['album']['id']
	url="http://%s/album?id=%d"%(host,albumid)
	j=lcg_l.gettext(url)
	j=json.loads(j)
	
	return j
@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?网抑云|[!！/]?网易云')
def _163(ctx,match,rest):
	keyword=rest.strip()
	url="http://%s/search?"%host+urlencode({"keywords":keyword})
	t=lcg_l.gettext(url)
	j=json.loads(t)
	j=j["result"]["songs"]
	if(len(j)>10):
		j=j[:10]
	if('debug' in rest):
		pass
		#myio.dumpjson(path.join(mainpth,'tempwyy.json'),j)
		#enen=',\n'.join([str(_) for _ in j[:min(len(j),4)]])
		#enen=render_song_item(j[0])
		#myio.dumpjson(path.join(mainpth,'tempwyy.json'),enen)
		#simple_send(ctx,txt2im_ml(strenen,width=512,fixedHeight=12,bg=(255,)*4,fill=(0,0,0,255)))
	itm=choice(j)
	id=itm["id"]
	url="https://music.163.com/song/media/outer/url?id=%d.mp3"%id
	f=lcg_l.get_path(url)
	f1=splitext(f)[0]+".mp3"
	simple_send(ctx,shutil.copy(f,f1))'''
	
