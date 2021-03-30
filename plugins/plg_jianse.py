from bot_backend import *
from jianse import jianse
js=jianse.default()

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
	result=js.jian(pic)
	if(result):	
		simple_send(ctx,'是色图！！')
	else:
		simple_send(ctx,'不够色！！')

@receiver
@threading_run
def cmd_autojianse(ctx):
	sctx=simple_ctx(ctx)
	if(sctx.pics):
		pics=sctx.get_rpics()
		for i in pics:
			from PIL import Image
			im=Image.open(i)
			if(js.jian(im)):
				simple_send(ctx,'色图！！')
				return