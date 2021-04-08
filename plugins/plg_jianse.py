from bot_backend import *
#from jianse import jianse
from nnnsfw import predictor as _predictor
import myhash
from os import path
#js=jianse.default()
predictor=_predictor()
configs=myhash.splitedDict(path.join(mainpth,'saves','jianse_toggle'))
@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]鉴')
def cmd_jianse(ctx):
	sctx=simple_ctx(ctx)
	rpics=sctx.get_rpics()
	if(not rpics):
		simple_send(ctx,'您还没有发图啊！！')
		return
	from PIL import Image
	pic=Image.open(rpics[0])
	buse,setu=predictor.predict(pic)
	if(setu>buse):	
		simple_send(ctx,'是色图！！')
	else:
		simple_send(ctx,'不够色！！')
@receiver
@threading_run
@on_exception_send
@start_with(r'/开关鉴色')
def cmd_toggle_jianse(ctx):
	sctx=simple_ctx(ctx)
	gid=sctx.group_id
	val=configs.get(gid,True)
	configs[gid]=not val
	if(val):
		simple_send(ctx,'关闭了')
	else:
		simple_send(ctx,'开启了')
@receiver
@threading_run
def cmd_autojianse(ctx):
	sctx=simple_ctx(ctx)
	gid=sctx.group_id
	if(not configs.get(gid,True)):
		return
	if(sctx.pics):
		pics=sctx.get_rpics()
		for i in pics:
			from PIL import Image
			im=Image.open(i)
			buse,setu=predictor.predict(im)
			if(setu>buse):
				simple_send(ctx,'色图！！')
				return