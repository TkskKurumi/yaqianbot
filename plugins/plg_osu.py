from bot_backend import *
from os import path
from myhash import splitedDict
import myOSUAPI
from simple_arg_parser import parse_args
qqid2osuid=splitedDict(pth=path.join(mainpth,'saves','qqid2osuid'),splitMethod=lambda x:str(x)[:3])

plugin_name_n='OSU'
def report_status():
	ret=[]
	ret.append('“/osu”   查看OSU!成绩')
	ret.append('“/osu -m {mode}”   查看指定模式的成绩')
	ret.append('      {mode}可以是fruits/mania/osu/taiko')
	ret.append('“/osu_set”   设定osu名字(与QQ号关联)')
	return ret
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?osu_set')
def cmd_osu_set(ctx,match,rest):
	sctx=simple_ctx(ctx)
	uid=sctx.user_id
	osuid=rest.strip()
	'''if(len(arc_id)!=9 or not arc_id.isnumeric()):
		simple_send(ctx,'好友码难道不是应该是⑨位数字吗？？？')
		return'''
	qqid2osuid[uid]=osuid
	simple_send(ctx,'绑定成功啦！！')
@receiver
@threading_run
@on_exception_send
@start_with('[/!！]?osu')
def cmd_osu(ctx,match,rest):
    if(rest):
        if(rest[0]=='_'):
            return
    sctx=simple_ctx(ctx)
    uid=sctx.user_id
    args=parse_args(rest)
    osuid=args.get('u',None) or args.get('user',None)
    mode=args.get('m',None) or args.get('mode',None)
    if(osuid is None):
        if(uid not in qqid2osuid):
            simple_send(ctx,'菜菜还不知道您的osu名称捏！输入“/osu_set 用户名”来绑定哟~')
            return
        else:
            osuid=qqid2osuid[uid]
    uinfo=myOSUAPI.get_user(user=osuid,mode=mode)
    im=myOSUAPI.illust_user_info(uinfo,score_mode=mode)
    simple_send(ctx,im)

