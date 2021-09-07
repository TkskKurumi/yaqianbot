if(__name__!='__main__'):
    from bot_backend import *
    from myjobs import jobs
    import jieba,traceback,myhash,cherugo
    from nekolanguage import neko_encode,neko_decode
    import chat,pic2pic
    from horror_gif import horror_gif
from glob import glob
from os import path
from datetime import datetime
import random
from isekai_events import events





def choose_event(userinfo):
    az=[]
    for name,inst in events.items():
        az.append(inst.try_encounter(userinfo))
    return min(az)
all_species=['人类']
def spawn_player(self):
    pass
    