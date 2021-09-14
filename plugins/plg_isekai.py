if(__name__!='__main__'):
    from bot_backend import *
    from myjobs import jobs
    import jieba,traceback,myhash,cherugo
    from nekolanguage import neko_encode,neko_decode
    import chat,pic2pic
    from horror_gif import horror_gif
    import pic2pic
    from pilloWidget import widgets
    from PIL import Image
from glob import glob
from os import path
from datetime import datetime
import random
from isekai_events import events
from isekai_player import player_status
import isekai_player,isekai_events
import time
from glob import glob
from PIL import Image
from aiocqhttp import MessageSegment as mseg
def get_resource(name,end='\n') -> list:
    
    pth=path.join(mainpth,'static_pics','isekai',name,"*")
    pths=glob(pth)
    if(pths):
        p=random.choice(pths)
        im=Image.open(p)
        return [im,end]
    else:
        return []
def render_rt(mes):
    _mes=[]
    for i in mes:
        if(isinstance(i,str)):
            if(path.exists(i) and i[-3:] in 'jpg,png,bmp,gif'):
                _mes.append(Image.open(i))
                _mes.append('\n')
            else:
                _mes.append(i+'\n')
        elif(isinstance(i,Image.Image)):
            _mes.append(i)
            _mes.append('\n')
        else:
            _mes.append(str(i)+'\n')
    rich_text=widgets.richText(contents=_mes,alignX=0.01,imageLimit=(500,768),width=512,fontSize=36,font=pic2pic.default_font,bg=(255,)*4,fill=(0,0,0,255),autoSplit=False)
    return rich_text.render()
def choose_event(player):
    az=[]
    for name,inst in events.items():
        az.append(inst.try_encounter(player))
    print(sorted(az))
    return min(az)[1]
all_species=['人类','猫人','精灵','史莱姆']
def spawn_player(name='张三'):
    species=random.choice(all_species)
    if(species in '史莱姆'):
        gender='无性'
    else:
        gender=random.choice(['男性','女性'])
    location='森林'
    if(species=='人类'):
        if(random.random()<0.8):
            location='城镇'
    return player_status(name,gender,species,0,location=location)

@receiver_nlazy
@threading_run
@on_exception_send
@start_with(r'[~/]异世界')
def cmd_isekai(ctx):
    sctx=simple_ctx(ctx)
    name=sctx.user_name
    player=spawn_player(name)
    mes=[]
    reported=0
    def send_mes():
        nonlocal mes
        '''import pic2pic
        
        mes='\n'.join(mes)'''
        mes.append("="*20)
        mes.extend(player.report_status())
        #im=pic2pic.txt2im_ml(mes,bg=(255,)*4,fill=(0,0,0,255),width=512,fixedHeight=24)
        im=render_rt(mes)
        simple_send(ctx,[mseg.at(int(sctx.user_id)),im],im_size_limit=2<<20)
        mes=[]
        reported=0
    
    for i in range(500):
        if(i):
            mes.append("="*20)
        mes.append("%s:"%player.strold())
        evt=choose_event(player)
        
        mes.extend(evt.encounter(player))
        if(not player.is_alive()):
            mes.append("%s死了"%name)
            break
        mes.append("\n")
        player.get_old(0.5+random.random())
        mes.extend(player.dump_mes())
        if(len(mes)>256):
            send_mes()
            reported=0
            time.sleep(10)
        if(len(mes)>reported+40):
            mes.append("="*20)
            mes.extend(player.report_status())
    
    if(mes):
        send_mes()