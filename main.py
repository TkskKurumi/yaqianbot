from bot_backend import my_load_plugin,running,run
from os import sys,path
sys.path.append(path.dirname(__file__))
sys.path.append(path.join(path.dirname(__file__),'plugins'))
sys.path=list(set(sys.path))
dn=path.dirname(__file__)
for i in ['plg_admin','plg_group',
"plg_roll",
"plg_checkin",
"plg_osu",
"plg_chat"
]:
	my_load_plugin(path.join(dn,'plugins',i))

run()