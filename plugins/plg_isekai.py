if(__name__!='__main__'):
    from bot_backend import *
    from myjobs import jobs
    import jieba,traceback,myhash,cherugo
    from nekolanguage import neko_encode,neko_decode
    import chat,pic2pic
    from horror_gif import horror_gif
    import pic2pic
from glob import glob
from os import path
from datetime import datetime
import random
from isekai_events import events
from isekai_player import player_status
import isekai_player,isekai_events



def choose_event(player):
    az=[]
    for name,inst in events.items():
        az.append(inst.try_encounter(player))
    print(sorted(az))
    return min(az)[1]
all_species=['人类','猫人','精灵']
def spawn_player(name='张三'):
    species=random.choice(all_species)
    gender=random.choice(['男性','女性'])
    location='森林'
    if(species=='人类'):
        if(random.random()<0.8):
            location='城镇'
    return player_status(name,gender,species,0,location=location)

@receiver_nlazy
@threading_run
@on_exception_send
@start_with(r'/异世界')
def cmd_isekai(ctx):
    sctx=simple_ctx(ctx)
    name=sctx.user_name
    player=spawn_player(name)
    mes=[]
    reported=0
    for i in range(80):
        mes.append("%s:"%player.strold())
        evt=choose_event(player)
        
        mes.extend(evt.encounter(player))
        if(not player.is_alive()):
            mes.append("%s死了"%name)
            break
        if(len(mes)-reported>20):
            
            mes.extend(player.report_status())
            reported=len(mes)
        
        else:
            mes.append("\n")
        player.get_old(0.5+random.random())
        
        
    
    
    if(mes):
        mes='\n'.join(mes)
        im=pic2pic.txt2im_ml(mes,bg=(255,)*4,fill=(0,0,0,255),width=512,fixedHeight=18)
        simple_send(ctx,im)