from bot_backend import my_load_plugin,running,run,add_su
from os import sys,path
from utils import simple_arg_parser
sys.path.append(path.dirname(__file__))
sys.path.append(path.join(path.dirname(__file__),'plugins'))
sys.path.append(path.join(path.dirname(__file__),'utils'))
sys.path=list(set(sys.path))[::-1]
dn=path.dirname(__file__)
for i in ['plg_admin','plg_group',
"plg_roll",
"plg_checkin",
#"plg_osu",
"plg_chat",
"plg_facegen",
"plg_setu",
"plg_bilisub",
"plg_customchat",
"plg_strgen",
"plg_wyy",
"plg_isekai"
#"plg_jianse"
]:
	my_load_plugin(path.join(dn,'plugins',i))
args=sys.argv[1:]
args=simple_arg_parser.parse_args(' '.join(args))
add_su(402254524)
print(args)
port=args.get('port') or args.get('p') or 8008
print('port =',port)
run(port)