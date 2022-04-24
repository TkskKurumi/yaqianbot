from bot_backend import *
from os import path
from tetrio.user import user as iouser
from tetrio import illust
from tetrio.colors import color
from simple_arg_parser import parse_args
import random
qq2io = splitedDict(pth=path.join(
    mainpth, 'saves', 'qq2io'), splitMethod=lambda x: str(x)[:2])


@receiver
@threading_run
@on_exception_send
@start_with("/io")
def cmd_tetrio(ctx, match, rest):

    sctx = simple_ctx(ctx)
    uid = sctx.user_id

    args = parse_args(rest.strip())
    user = args.get("u") or args.get("user")
    setuser = args.get("s") or args.get("set")
    if(user is None):
        if(uid in qq2io):
            user = qq2io[uid]
        else:
            simple_send(ctx, "还不知道您的tetr.io账号捏!")
    else:
        if(uid not in qq2io):
            setuser = True
    if(setuser):
        simple_send(ctx, "为您QQ绑定tetr.io账号%s" % user)
        qq2io[uid] = user

    u = iouser(user)
    c = color.HSV(random.random()*360, 100, 70)
    style = random.choice(["light", "dark"])
    pic = illust.profile(u, color=c, style=style)
    simple_send(ctx, pic)
