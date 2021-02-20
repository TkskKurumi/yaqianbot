from bot_backend import my_load_plugin,running,run#,init
from os import sys,path
sys.path.append(path.dirname(__file__))
sys.path.append(path.join(path.dirname(__file__),'plugins'))
sys.path=list(set(sys.path))
dn=path.dirname(__file__)
#from plugins import plg_admin,plg_setu
for i in ['plg_admin','plg_group',
"plg_roll",
"plg_checkin",
"plg_osu"
]:
	my_load_plugin(path.join(dn,'plugins',i))
'''
bots=[]
qqs=[
(2472252332,8887),
(3434614020,8888),
(2402153471,8889),
(3120300894,8890),
(515479347,8891)
]
for qq,port in qqs:
	#bots.append(init(qq=qq,host='127.0.0.1',port=port))'''

run()