from bot_backend import *
from myjobs import jobs
import jieba,traceback,myhash,cherugo
from nekolanguage import neko_encode,neko_decode
import random,chat,pic2pic
from horror_gif import horror_gif
from glob import glob
from os import path
from datetime import datetime
fortune_save=myhash.splitedDict(pth=path.join(mainpth,'saves','fortune'),splitMethod=lambda x:myhash.hashs(x).lower()[:2])



plugin_name_n='沙雕文字生成器'
def report_status():
	ret=[]
	ret.append('“/suffix 尾巴”   把bot这功能发出来的粘贴到群名片后面')
	ret.append('就可以被@时带尾巴')
	ret.append('“/切噜一下 文本”   把文本翻译为切噜语')
	ret.append('“/翻译切噜 文本”   把切噜语翻译为原文')
	ret.append('“/今日运势”   占卜一下今日运势')
	ret.append('“/取名”   随机一个奇怪的网名')
	return ret


@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?suffix')
def cmd_suffix(ctx,match,rest):
	simple_send(ctx,chr(8238)+rest.strip()[::-1]+chr(8237))
@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?切噜一下')
def cmd_str2cheru(ctx,match,rest):
	simple_send(ctx,'切噜～♪'+cherugo.str2cheru(rest.strip()))

@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?取名')
def cmd_quming(ctx):
	color=random.choice([(0,0,255),(255,0,7),(0,0xcc,0x66)])
	a=['废墟', '深海', '反应堆', '学园', '腐烂', '东京', '三维', '四次元', '少管所', '流星', '闪光', '南极', '消极', '幽浮', '网路', '暗狱', '离子态', '液态', '黑色', '抱抱', '暴力', '垃圾', '社会', '残暴', '残酷', '工口', '戮尸', '原味', '毛茸茸', '香香', '霹雳', '午夜', '美工刀', '爆浆', '机关枪', '无响应', '手术台', '麻风病', '虚拟', '速冻', '智能', '2000', '甜味', '华丽', '反社会', '玛利亚', '无', '梦之', '蔷薇', '无政府', '酷酷', '西伯利亚', '人造', '法外', '追杀', '通缉', '女子', '微型', '男子', '超', '毁灭', '大型', '绝望', '阴间', '死亡', '坟场', '高科技', '奇妙', '魔法', '极限', '社会主义', '无聊']
	b=['小丑', '仿生', '纳米', '原子', '丧', '电子', '十字架', '咩咩', '赛博', '野猪', '外星', '窒息', '变态', '触手', '小众', '悲情', '飞行', '绿色', '电动', '铁锈', '碎尸', '电音', '蠕动', '酸甜', '虚构', '乱码', '碳水', '内脏', '脑浆', '血管', '全裸', '绷带', '不合格', '光滑', '标本', '酸性', '碱性', '404', '变身', '反常', '樱桃', '碳基', '矫情', '病娇', '进化', '潮湿', '砂糖', '高潮', '变异', '复合盐', '伏特加', '抑郁', '暴躁', '不爱说话', '废物', '失败', '幻想型', '社恐', '苦涩', '粘液', '浓厚', '快乐', '强制', '中二病', '恶魔', 'emo', '激光', '发射', '限量版', '迷因', '堕落', '放射性']
	c=['天使', '精灵', '女孩', '男孩', '宝贝', '小妈咪', '虫', '菇', '公主', '少女', '少年', '1号机', '子', '恐龙', '蜈蚣', '蟑螂', '食人鱼', '小飞船', '舞女', '桃子', '团子', '精', '酱', '废料', '生物', '物质', '奶茶', '搅拌机', '液', '火锅', '祭司', '体', '实验品', '试验体', '小猫咪', '样本', '颗粒', '血块', '汽水', '蛙', '软体', '机器人', '人质', '小熊', '圣母', '胶囊', '乙女', '主义者', '屑', '垢', '污渍', '废人', '毛血旺', '怪人', '肉', '河豚', '豚', '藻类', '唾沫', '咒语', '建筑', '球', '小狗', '碳', '元素', '少先队员', '博士', '糖']
	name=random.choice(a)+random.choice(b)+random.choice(c)
	im=pic2pic.txt2im(name,fill=color,bg=(255,)*4,fixedHeight=100)
	im=horror_gif(im,resolution=5000,r_w0=0.004,r_w1=0.0002)
	simple_send(ctx,im)
@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?翻译切噜')
def cmd_cheru2str(ctx,match,rest):
	rest=rest.strip()
	if(rest[:4]=='切噜～♪'):
		rest=rest[4:]
	simple_send(ctx,cherugo.cheru2str(rest))

@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?按钮')
def cmd_button(ctx,match,rest):
	self_id=ctx.CurrentQQ
	sctx=simple_ctx(ctx)
	group_id=int(sctx.group_id)
	_=rest.strip().split()
	title=_[0]
	_=_[1:]
	msg={
		"app": "com.tencent.autoreply",
		"desc": "",
		"view": "autoreply",
		"ver": "0.0.0.1",
		"prompt": "[动画表情]",
		"meta": {
			"metadata": {
				"title": "title",
				"buttons": [
					{
						"slot": 1,
						"action_data": "sadasds",
						"name": "asdsad",
						"action": "notify"
					},
					{
						"slot": 2,
						"action_data": "aaa",
						"name": "asdasd",
						"action": "notify"
					}
				],
				"type": "guest",
				"token": "LAcV49xqyE57S17B8ZT6FU7odBveNMYJzux288tBD3c="
			}
		},
		"config": {
			"forward": 1,
			"showSender": 1
		}
	}
	btns=[]
	i=1
	while(i<len(_)):
		__={
			"slot":(i+1)//2,
			"action_data":_[i-1],
			"name":_[i],
			"action":"notify"
		}
		btns.append(__)
		i+=2
	import bot_backend
	bot_backend._acts[self_id].send_group_json_msg(group_id,msg)
	
	msg['meta']['metadata']['title']=title
	msg['meta']['metadata']['buttons']=btns
	myio.dumpjson(path.join(mainpth,'temp.json'),msg)
	import bot_backend
	bot_backend._acts[self_id].send_group_json_msg(group_id,msg)

@receiver
@threading_run
@on_exception_send
@start_with(r'[/!！]?今日运势')
def today_fortune(ctx):
	sctx=simple_ctx(ctx)
	id=sctx.user_id+datetime.now().strftime('%Y-%m-%d')
	if(id in fortune_save):
		mes=fortune_save[id]
	else:
		mes=[]
		mes.append(random.choice(['凶','吉','大凶','大吉','小凶','小吉']))
		_=['玩游戏','结婚','出游','水群','打滚','女装','写作业','交友','告白','分手','驾车','乘船','单推','做舔狗','抽烟','购房','安葬','嫁娶','开光','动土','破土','入宅','赴任']
		yiji=random.sample(_,6)
		mes.append('宜:'+','.join(yiji[:3]))
		mes.append('忌:'+','.join(yiji[3:]))
		mes='\n'.join(mes)
		fortune_save[id]=mes
	simple_send(ctx,sctx.user_name+'的今日运势：\n'+mes)

@receiver_nlazy
@threading_run
@on_exception_send
@start_with(r'/嗯喵')
def cmd_to_enmiao(ctx,match,rest):
	rest=rest.strip()
	ret=neko_encode(rest)
	simple_send(ctx,ret)
@receiver_nlazy
@threading_run
@on_exception_send
@start_with(r'/翻译嗯喵')
def cmd_from_enmiao(ctx,match,rest):
	rest=rest.strip()
	ret=neko_decode(rest)
	simple_send(ctx,ret)
