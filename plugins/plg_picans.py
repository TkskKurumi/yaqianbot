from bot_backend import *
from os import path
from glob import glob
import pic2pic,random
import pic_indexing_RGB
from PIL import Image
pth=path.join(mainpth,'saves','pic_ans')
indexing=pic_indexing_RGB.indexing(pth,mode='euclidean',color='RGB',wsiz=20,annsize2capacity=lambda x:int(min(x*2,x+50)))
def calc_similarity(dist):
	az=30*(indexing.f**0.5)
	#a**az=0.85
	#a**x=(0.85 ** 1/az)**x=0.85**(x/az)
	return 0.90**(dist/az)
@receiver
@threading_run
@on_exception_send
@start_with("/评论图片")
def cmd_learn_pic(ctx,match,rest):
	sctx=simple_ctx(ctx)
	if(not sctx.get_rpics()):
		simple_send(ctx,'你还没有发送图片！')
		return
	if(not rest.strip()):
		simple_send(ctx,'你没有输入评论的内容！')
		return
	uid=sctx.user_id
	uname=sctx.user_name
	im=Image.open(sctx.get_rpics()[0]).convert("RGB")
	d=indexing.get(im,dict())
	dd={'uname':uname,'comment':rest.strip()}
	d[uid]=dd
	indexing[im]=d
	show_pic_comments(ctx)

def show_pic_comments(ctx):
	sctx=simple_ctx(ctx)
	if(not sctx.get_rpics()):
		simple_send(ctx,'你还没有发送图片！')
		return
	im=Image.open(sctx.get_rpics()[0]).convert("RGB")
	d=indexing.get(im,None)
	if(not d):
		simple_send(ctx,'图片还没人评论呢')
		return
	mes=[]
	for i,j in d.items():
		mes.append("%s:%s"%(j['uname'],j['comment']))
	simple_send(ctx,mes)
@receiver
@threading_run
@on_exception_send
@start_with("/图片评论")
def cmd_pic_comments(ctx):
	show_pic_comments(ctx)

@receiver
@threading_run
@to_me
def tome_pic(ctx):
	sctx=simple_ctx(ctx)
	if(sctx.pics):
		im=Image.open(sctx.get_rpics()[0]).convert("RGB")
		dist,idx=indexing.get_nns_by_image(im,1,include_distances=True)[0]
		print('ln64',calc_similarity(dist))
		if(calc_similarity(dist)>0.80):
			d=indexing[idx]
			ls=list(d)
			dd=d[random.choice(ls)]
			simple_send(ctx,'%s:%s'%(dd["uname"],dd['comment']))
		else:
			simple_send(ctx,'这图是啥？')
		