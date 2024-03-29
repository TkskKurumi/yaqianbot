if(__name__!='__main__'):
    from bot_backend import *
from os import get_terminal_size
import random
from isekai_player import player_status as cplayer
import plg_isekai
get_resource=lambda *args,**kwargs:plg_isekai.get_resource(*args,**kwargs)
events=dict()
inevitable=float('-inf')
impossible=float('inf')
prior=-5

def f_calc_priority(rarity,delta=0):
    return random.normalvariate(rarity,rarity**0.5)+delta


#general events
class event:
    def __init__(self,name,rarity=1,priority_delta=0):
        self.rarity=rarity
        self.name=name
        self.priority_delta=priority_delta
        global events
        events[name]=self
    def judge_possible(self,player:cplayer) ->bool:
        return True
    def calc_priority(self,player:cplayer) ->float:
        return random.normalvariate(self.rarity,self.rarity**0.5)+self.priority_delta
    def try_encounter(self,player:cplayer) ->tuple:
        return self.calc_priority(player),self
    def __str__(self):
        return "Event(%s)"%self.name
    def __repr__(self):
        return self.__str__()
    def __lt__(self,other):
        return self.name<other.name
    def encounter(self,player:cplayer) ->list:
        mes=[]
        name=player.name
        
        mes=['%s遭遇事件%s'%(name,self.name)]

        return mes
class event_born(event):
    def __init__(self):
        super().__init__('出生')
    def calc_priority(self,player):
        if(player.species=='史莱姆'):
            return impossible
        if(player.yearold==0):
            return inevitable
        else:
            return impossible
    def try_encounter(self,player):
        return self.calc_priority(player),self
    def encounter(self,player):
        mes=[]
        mes.append('你被卡车创死，转生到了异世界..')
        gender='' if player.gender=='无性' else player.gender
        mes.append('你是一位%s'%(player.refine_species()))
        mes.append('出生在%s'%player.location)
        
        return mes
class event_old_disease(event):
    def __init__(self):
        super().__init__("老年病")
    def calc_priority(self,player):
        if(player.species=='魅魔' or player.species=='史莱姆'):
            return impossible
        if(player.yearold<50):
            return impossible
        if(player.species=="精灵"):
            if(player.yearold<100):
                return impossible
            p=5-(player.yearold-100)/20 #when 180 yearold,p become 1
        else:
            p=5-(player.yearold-50)/5   #when 70 yearold, p become 1
        if(player.status.get('职业')=='魔王军'):
            return f_calc_priority(max(p,0.1),prior)
        return f_calc_priority(max(p,0.1))
    def encounter(self,player):
        mes=[]
        name=player.name
        alive=player.win_by_lvl(3)
        if(alive):
            if(random.random()<0.3):
                mes.append("%s感到免疫力在下降"%player.name)
            elif(random.random()<0.5):
                mes.append("%s感到筋骨没有以前灵活了"%player.name)
            else:
                mes.append("%s感到牙齿没有以前好了"%player.name)
        else:
            player.hp=0
            if(random.random()<0.3):
                mes.append("%s摔了一跤撞到了后脑勺.."%name)
            elif(random.random()<0.5):
                mes.append("%s得了严重的肺病"%name)
            else:
                mes.append("%s突发恶疾！！"%name)
        return mes
class event_farm_slime(event):
    #刷小怪
    def __init__(self):
        super().__init__(name='打小怪',rarity=1)
    def calc_priority(self,player):
        if(player.location=='城镇'):
            return impossible
        if(player.species=='史莱姆'):
            return impossible
        if(player.yearold<11):
            return f_calc_priority(5)
        else:
            tmp=0.5+25/player.hp
            if(player.status.get('职业')=='冒险者'):
                tmp=max(0.5,tmp-0.5)
            return f_calc_priority(tmp)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_cost=15/player.lvl
        lvl_earn=0.7**player.lvl
        
        hp=player.lose_hp(hp_cost)
        player.lvl+=lvl_earn
        
        mes.append("%s在打史莱姆"%player.name)
        mes.extend(get_resource('史莱姆'))
        if(hp==0):
            if(player.yearold<11):
                mes.append("幼小的%s根本不知道怪物的可怕，作死了"%name)
            else:
                monster_name=random.choice(['史莱姆'])
                mes.append("%s真是杂鱼，居然%s都打不过"%(name,monster_name))
            return mes
        if(random.random()<0.5):
            player.earn_item('史莱姆精华液')
            mes.append("掉了%.1f血能力值提升了%.1f，获得了一份史莱姆精华液"%(hp_cost,lvl_earn))
        else:
            mes.append("掉了%.1f血能力值提升了%.1f"%(hp_cost,lvl_earn))
        
        player.old_speed=0.1
        return mes
class event_farm_goblin(event):
    def __init__(self):
        super().__init__(name='打哥布林',rarity=1.1)
    def calc_priority(self,player):
        if(player.location=='城镇'):
            return impossible
        hp_cost=15/(player.lvl-0.9)
        
        if(hp_cost<0):
            return impossible
        if(hp_cost>10):
            return impossible
        tmp=0.8+hp_cost/20
        if(player.status.get('职业')=='冒险者'):
            tmp=max(0.8,tmp-0.5)
        return f_calc_priority(tmp)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_cost=15/(player.lvl-1)
        hp=player.lose_hp(hp_cost)
        lvl_earn=0.7**(player.lvl-0.5)
        player.lvl+=lvl_earn
        mes.append("%s去打哥布林"%name)
        if(hp==0):
            mes.append("%s真是杂鱼，居然哥布林都打不过"%(name))
            return mes
        mes.append("掉了%.1f血能力值提升了%.1f"%(hp_cost,lvl_earn))
        player.old_speed=0.1
        return mes
class event_recover_hp(event):
    def __init__(self):
        super().__init__('回血')
    def calc_priority(self,player):
        if(player.hp>49):
            return impossible
        if(player.location=='学校'):
            return f_calc_priority(player.hp/50,prior)
        return f_calc_priority(player.hp/50)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_recover=min(player.lvl/2,1)*((50-player.hp)**0.5+5)
        rnd=(random.random()*0.7+0.15)
        hp_recover*=rnd
        hp_recover=min(hp_recover,50-player.hp)
        player.hp+=hp_recover
        if(rnd>0.5):
            mes.append("%s喝了口治疗药，恢复了%.1f HP"%(name,hp_recover))
        else:
            mes.append("%s小做休息，恢复了%.1f HP"%(name,hp_recover))
        return mes
class event_child_play(event):
    def __init__(self):
        super().__init__("幼儿时期玩")
    def calc_priority(self,player):
        if(player.yearold>8):
            return impossible
        return f_calc_priority(1.2)
    def encounter(self,player):
        mes=[]
        if(player.species=='人类'):
            if(player.gender=='男性'):
                mes.append("%s喜欢玩泥巴"%player.name)
            else:
                mes.append("%s喜欢玩布偶"%player.name)
        elif(player.species=='猫人'):
            mes.append("%s在抓老鼠"%player.name)
        else:
            mes.append("%s在玩"%player.name)
        return mes
#move place events
class event_newlocation(event):
    def __init__(self,newloc,*args,**kwargs):
        super().__init__("前往%s"%newloc,*args,**kwargs)
        self.newloc=newloc
    def calc_priority(self,player):
        if(player.location==self.newloc):
            return impossible
        else:
            return f_calc_priority(self.rarity,self.priority_delta)
    def encounter(self,player):
        mes=[]
        player.location=self.newloc
        mes.append("%s前往了%s"%(player.name,self.newloc))
        return mes
class event_goto_forest(event_newlocation):
    def __init__(self):
        super().__init__("森林")
    def calc_priority(self,player):
        if(player.location=='森林'):
            return impossible
        if(player.status.get("职业")=='杂货店主'):
            return impossible
        if(player.status.get('职业')=='冒险者'):
            return f_calc_priority(1.5)
        if(player.species=='精灵'):
            return f_calc_priority(2.2)
        else:
            return f_calc_priority(2.5)
    def encounter(self,player):
        mes=[]
        player.location='森林'
        if(player.species=='精灵'):
            mes.append("%s回到了故乡，大森林"%player.name)
        else:
            mes.append("%s来到了大森林"%player.name)
        return mes
class event_goto_town(event):
    def __init__(self):
        super().__init__('前往城镇')
    def calc_priority(self, player:cplayer):
        if(player.location=='城镇'):
            return impossible
        if(player.species=='史莱姆'):
            return impossible
        elif(player.inventory_num()>5):
            return f_calc_priority(0.5)
        elif(player.species=='人类'):
            return f_calc_priority(2.2)
        else:
            return f_calc_priority(2.5)
    def encounter(self,player):
        player.location='城镇'
        mes=[]
        name=player.name
        mes.append("%s来到了城镇"%name)
        return mes

achievement_transgender={"变身美少女":"在工口地牢里变成女孩子"}
class event_enter_ero_dungeon(event):
    def __init__(self):
        super().__init__(name='进入工口地牢',rarity=3.5)
    def calc_priority(self, player):
        if(player.location=='工口地牢'):
            return impossible
        if(player.yearold<12 or player.yearold>40):
            return impossible
        if(player.location!='森林'):
            return f_calc_priority(8.5)
        
        if('hidden-进过工口地牢' in player.status):
            return f_calc_priority(5.5)
        return super().calc_priority(player)
    def encounter(self,player):
        mes=[]
        name=player.name
        player.status['hidden-进过工口地牢']=True
        if(player.location!='森林'):
            mes.append("%s突然间很想去森林"%name)
        mes.append("%s在森林深处散步"%name)
        mes.append("%s看到地上有个写着奇怪文字的石碑"%name)
        mes.append("靠近后，地上出现了一道门")
        mes.append("%s想要走进去，但当刚刚触碰到门内的时候，感到天旋地转"%name)
        mes.append("当%s醒来时，发现自己在陌生的地方"%name)
        mes.append("在一个爱心型魔法阵的中央，石质的四壁地板天花板，不知道在哪里")
        if(player.gender=='男性'):
            player.gender='女性'
            mes.append("而且变成了女孩子！！！")
            player.achievements.update(achievement_transgender)
        player.location='工口地牢'
        player.old_speed=0.01
        return mes
#female elf events
achievement_orc_slayer={"反本子剧情":"女精灵逆袭兽人"}
class event_elf_raped(event):
    def __init__(self):
        super().__init__(name='精灵被嗯喵',rarity=1)
    def calc_priority(self,player):
        if(player.gender=='女性' and player.species=='精灵' and player.location=='森林' and player.yearold>14):
            return super().calc_priority(player)
        else:
            return impossible
    def encounter(self,player):
        mes=[]
        mes.append("%s被兽人抓住了"%player.name)
        if(player.win_by_lvl(5)):
            mes.append("但是她把兽人都打爆了")
            player.achievements.update(achievement_orc_slayer)
        else:
            hp=player.lose_hp(10*(1-player.win_rate_by_lvl(4)))
            if(hp==0):
                mes.append("%s被关起来变成了兽人的RBQ，被雷普到死"%player.name)
            else:
                mes.extend(get_resource('女精灵兽人'))
                mes.append("%s被关起来嗯喵❤嗯喵喵❤喵喵呜呜❤"%player.name)
                mes.append("掉了%.1fHP"%10)
                player.numeric_status_count('经验次数')
        return mes
class event_elf_akuochi(event):
    #恶堕
    def __init__(self):
        super().__init__(name='女精灵恶堕')
    def calc_priority(self, player: cplayer) -> float:
        if(player.species=='精灵' and player.gender=='女性'):
            if(player.status.get('经验次数',0)>=5):
                if(player.location!='工口地牢'):
                    return inevitable
        return impossible
    def encounter(self, player: cplayer) -> list:
        mes=[]
        name=player.name
        mes.append("%s%s因为经验次数达到5次"%(player.refine_species(),player.name))
        mes.append("%s变成了魅魔，hso！"%name)
        player.species='魅魔'
        return mes
class event_elf_daily(event):
    def __init__(self):
        super().__init__(name='精灵在森林的平常生活')
    def calc_priority(self,player):
        if(player.species=='精灵' and player.location=='森林'):
            return f_calc_priority(1)
        else:
            return impossible
    def encounter(self,player):
        mes=[]
        name=player.name
        lvl_earn=0.3**player.lvl
        player.lvl+=lvl_earn
        if(lvl_earn>0.1):
            mes.append("%s在精灵村寨日常，能力值提升了%.1f"%(name,lvl_earn))
        else:
            mes.append("%s在精灵村过着与世无争的生活"%name)
        return mes

        
#neko events
class event_neko_catch_fish(event):
    def __init__(self):
        super().__init__(name='猫娘抓鱼',rarity=1)
    def calc_priority(self,player):
        if(player.species=='猫人' and player.location=='森林'):
            return f_calc_priority(0.8+player.yearold/3)
        else:
            return impossible
    def encounter(self,player):
        mes=[]
        name=player.name
        lvl_earn=0.3**player.lvl
        player.lvl+=lvl_earn
        mes.append("%s正在练习摸鱼，能力值提升了%.1f"%(name,lvl_earn))
        return mes
class event_filter_neko(event):
    def judge_possible(self,player):
        return player.species=="猫人"
class event_filt_femaleneko(event):
    def judge_possible(self,player):
        return player.species=="猫人" and player.gender=='女性'
class event_neko_prpr(event_filter_neko):
    def __init__(self):
        super().__init__(name='猫猫舔爪子')
    def calc_priority(self,player):
        print('ln173',super().judge_possible)
        if(not super().judge_possible(player)):
            
            return impossible
        if(player.yearold<=5):
            return f_calc_priority(0.8)
        return impossible
    def encounter(self,player):
        mes=[]
        name=player.name
        mes.append("%s舔了舔自己的爪子"%name)
        return mes

#disaster events
class event_forest_fire(event):
    def __init__(self):
        super().__init__(name='森林大火',rarity=4)
    def encounter(self,player):
        mes=[]
        if(player.location!='森林'):
            mes.append("听说大森林着火了，生活在其中的居民四处逃亡，很可怜，但%s不在森林，没事"%player.name)
        else:
            if(player.species=='精灵'):
                mes.append("森林，%s的家园燃起熊熊大火"%player.name)
            else:
                mes.append('森林燃起熊熊大火')
            hp_cost=player.hp/2
            player.hp-=hp_cost
            mes.append("%s侥幸逃生，HP减少%.1f"%(player.name,hp_cost))
            mes.append("%s移居到城镇"%player.name)
            player.location='城镇'
        return mes
achievement_beat_maou={"就这？":"杀死魔王"}
class event_maou_massacre(event):
    def __init__(self):
        super().__init__(name="魔王大屠杀",rarity=5.9)
    def calc_priority(self, player):
        if(player.status.get('职业')=='魔王' or player.status.get('师从魔王')):
            return impossible
        if(player.status.get('职业')=='魔王军'):
            return impossible
        if(player.location=='学校'):
            return f_calc_priority(5.9,prior)
        
        return super().calc_priority(player)
    def encounter(self,player):
        
        if(player.win_by_lvl(3.8)):
            accept=random.random()<0.5
            if(accept):
                mes=[]
                lvl_earn=player.lvl*0.4+1
                mes.append("魔王邀请%s加入魔王军，%s同意了"%(player.name,player.name))
                if(player.species=='精灵' and player.gender=='女性'):
                    player.species='魅魔'
                    mes.append("%s变成了魅魔，hso"%player.name)
                else:
                    mes.append("魔王对%s使用了增幅魔法"%player.name)
                mes.append("能力值提升了%.1f"%lvl_earn)
                player.status['师从魔王']=True
                player.status['职业']='魔王军'
                player.location='魔王领地'
                return mes
            else:
                mes=[]
                mes.append("魔王邀请%s加入魔王军，%s拒绝了"%(player.name,player.name))
                if(player.win_by_lvl(8)):
                    mes.append("%s杀死了魔王"%player.name)
                    player.achievements.update(achievement_beat_maou)
                    mes.append("魔王的随从们看到这一幕，纷纷认%s为新的老大")
                    mes.append("%s成为了魔王!?"%player.name)
                    player.status['职业']='魔王'
                    player.location='魔王领地'
                else:
                    if(player.win_by_lvl(5)):
                        mes.append("%s暂时击退了魔王"%player.name)
                    else:
                        player.hp=0
                        mes.append("%s被魔王一怒之下虐成了渣"%player.name)
                return mes
        if(random.random()<0.5):
            player.hp=0
            mes=[]
            mes.append("魔王宣言要统治世界")
            mes.append("经过%s时，魔王军烧杀抢掠"%player.location)
        else:
            hp_cost=player.hp/2
            mes=[]
            mes.append("魔王宣言要统治世界")
            mes.append("经过%s时，魔王军烧杀抢掠"%player.location)
            mes.append("%s死里逃生，降低了%.1fhp"%(player.name,hp_cost))
            player.hp-=hp_cost
        return mes

#school events
class event_enter_school(event):
    def __init__(self):
        super().__init__(name='进入学校')
    def calc_priority(self, player):
        if(player.location=='学校'):
            return impossible
        if(player.yearold>10 or player.yearold<5.6):
            return impossible
        if(player.species=='人类'):
            return f_calc_priority(1.3)
        elif(player.species=='史莱姆'):
            return impossible
        else:
            return f_calc_priority(1.8)
    def encounter(self,player):
        prev_loc=player.location
        mes=[]
        mes.append("%s从%s来到学校"%(player.name,prev_loc))
        player.location='学校'
        pass
        return mes
class event_graduate(event):
    def __init__(self):
        super().__init__(name='学校毕业')
    def calc_priority(self, player):
        if(player.location!='学校'):
            return impossible
        if(player.yearold>16):
            return inevitable
        return f_calc_priority(4)
    def encounter(self,player):
        mes=[]
        mes.append("%s从学校毕业回到了家乡%s"%(player.name,player.born_location))
        if(player.status.get('学园偶像')):
            player.status['学园偶像']=False
        player.location=player.born_location
        return mes
class event_study(event):
    def __init__(self):
        super().__init__(name='学校学习')
    def calc_priority(self, player):
        if(player.location!='学校'):
            return impossible
        else:
            return f_calc_priority(1,prior)
    def encounter(self,player):
        mes=[]
        lvl_earn=0.2+0.3**player.lvl
        player.lvl+=lvl_earn
        mes.append("%s在学校学习战斗，能力值提升了%.1f"%(player.name,lvl_earn))
        return mes
class event_SIF(event):
    def __init__(self):
        super().__init__(name='有人想要成立学园偶像')
    def calc_priority(self, player):
        if('already_SIF' in player.status):
            return impossible
        elif(player.location!='学校'):
            return impossible
        else:
            return f_calc_priority(1.2,prior)
    def encounter(self,player):
        player.status['already_SIF']=True
        mes=[]
        mes=['学校里有一个同学成立了学园偶像部']
        if(player.gender=='女性' and random.random()<0.5):
            player.status['学园偶像']=True
            mes.append("%s成为了学园偶像☆"%player.name)
            az="Pop Pin μ Li ela Party Glow Aqua Ours Saint Snow Rise Sun Dream"
            az+=" Vivid Pastel Pallete Rose Furan Saga 48 super miracle Shiny Girls"
            az=az.split()
            group_name=" ".join(random.sample(az,3))
            mes.append("你们的组合叫%s"%group_name)
        return mes
#SIF events
class event_SIF_practice(event):
    def __init__(self):
        super().__init__(name='学园偶像练习')
    def calc_priority(self, player):
        if('学园偶像' not in player.status):
            return impossible
        if(player.location!='学校'):
            return impossible
        return f_calc_priority(0.5,prior)
    def encounter(self,player):
        mes=[]
        nm=player.name
        if(random.random()<0.3):
            mes.append("%s正在练习跳舞"%nm)
        elif(random.random()<0.5):
            mes.append("%s正在练习唱歌"%nm)
        else:
            mes.append("%s尝试变得kira kira"%nm)
        return mes
class event_SIF_live(event):
    def __init__(self):
        super().__init__(name='学园偶像live')

    def calc_priority(self, player):
        if('学园偶像' not in player.status):
            return impossible
        if(player.location!='学校'):
            return impossible
        return f_calc_priority(0.8,prior)
    def encounter(self,player):
        mes=[]
        nm=player.name
        if(random.random()<0.3):
            mes.append("你们的live很成功")
        elif(random.random()<0.5):
            mes.append("你们的live很失败，粉丝说“总有一天我会让这里座无虚席！”")
        else:
            mes.append("Live举办的那天下雨了")
        return mes
#follow maou events
class event_invading(event):
    def __init__(self):
        super().__init__("跟魔王打劫")
    def calc_priority(self, player):
        if(player.status.get("职业")=="魔王"):
            return impossible
        if(player.status.get("职业")=="魔王军"):
            return f_calc_priority(1.1,prior)
        return impossible
    def encounter(self,player):
        mes=['%s跟着魔王烧杀抢掠，带恶人'%player.name]
        return mes
class event_encounter_hero(event):
    def __init__(self):
        super().__init__("师从魔王-被勇者打")
    def calc_priority(self, player):
        if(player.status.get("职业")=="魔王军"):
            return f_calc_priority(1.1,prior)
        return impossible
    def encounter(self,player):
        mes=["勇者要讨伐魔王军"]
        if(player.win_by_lvl(4.7)):
            mes.append("但他太菜了")
        else:
            player.hp=0
            mes.append("他好强")
        return mes
class event_maou_fighting_championship(event):
    def __init__(self):
        super().__init__("魔王眷属武斗会")
    def calc_priority(self,player):
        if(player.status.get("职业")!='魔王军'):
            return impossible
        return f_calc_priority(1.4,prior)
    def encounter(self,player):
        mes=[]
        mes.append("魔王军是个崇尚武力的地方")
        mes.append("举办了无规则武斗大会")
        if(not player.win_by_lvl(2)):
            mes.append("%s这么弱的菜鸡在武斗会上被魔王军其他人杀死了"%player.name)
            player.hp=0
            return mes
        elif(player.win_by_lvl(8)):
            mes.append("%s在其中脱颖而出"%player.name)
        elif(player.win_by_lvl(4)):
            mes.append("%s表现优异"%player.name)
        else:
            mes.append("%s好菜，打不过别的魔王军成员"%player.name)
        lvl_earn=0.4**(max(player.lvl-3.5,1))
        lvl_earn*=random.random()+0.3
        player.lvl+=lvl_earn
        mes.append("%s的能力值提升了%.1f"%(player.name,lvl_earn))
        return mes
class event_maou_decide_relation(event):
    def __init__(self):
        super().__init__("魔王决定友好性")
    def calc_priority(self,player):
        if(player.status.get("职业")!='魔王'):
            return impossible
        if("魔王友好性" in player.status):
            return impossible
        return inevitable
    def encounter(self,player):
        mes=[]
        if(random.random()<0.7):
            player.status['魔王友好性']="友好"
            mes.append("%s决定，从今以后，魔王军势力要和大家友好相处"%player.name)
        else:
            player.status['魔王友好性']="邪恶"
            mes.append("%s感到带领着魔王军可以所向披靡为所欲为了"%player.name)
        return mes
class event_maou_challenged_by_soldier(event):      
    def __init__(self):
        super().__init__("魔王手下挑战")
    def calc_priority(self,player):
        if(player.status.get("职业")!='魔王'):
            return impossible
        return f_calc_priority(1.4,prior)
    def encounter(self,player):
        mes=[]
        mes.append("有人觉得你不配做魔王、想要篡位、发起了挑战")
        if(player.win_by_lvl(6)):
            mes.append("他太天真了，根本打不过你")
        else:
            player.hp=0
            mes.append("他说的对。。。")
        return mes
#succubus events
class event_succubus_daily(event):
    def __init__(self):
        super().__init__("魅魔嗯喵")
    def calc_priority(self, player):
        if(player.species!='魅魔'):
            return impossible
        if(player.status.get("职业")=='魔王军'):
            return f_calc_priority(1.3,prior)
        return f_calc_priority(0.5)
    def encounter(self,player):
        mes=[]
        name=player.name
        mes.append("魅魔%s嗯喵嗯喵"%player.name)
        lvl_earn=0
        if(random.random()<0.1):
            mes.append("%s榨干了勇者，吸收了勇者的能力"%name)
            lvl_earn+=0.9**player.lvl
        if(lvl_earn>0.1):
            mes.append("能力值提升了%.1f"%lvl_earn)
        return mes

#slime events:
class event_slime_born(event):
    def __init__(self):
        super().__init__('史莱姆出生')
    def calc_priority(self,player):
        if(player.species!='史莱姆'):
            return impossible
        if('史莱姆出生' in player.status):
            return impossible
        return inevitable
    def encounter(self,player):
        mes=[]
        mes.append("%s穿越到了异世界"%player.name)
        mes.append("你作为史莱姆重生了")
        mes.extend(get_resource("史莱姆"))
        player.status['史莱姆出生']=True
        return mes
class event_slime_fight(event):
    def __init__(self):
        super().__init__("史莱姆战斗")
    def calc_priority(self,player):
        if(player.species!='史莱姆'):
            return impossible
        return f_calc_priority(1)
    def encounter(self,player):
        mes=[]
        name=player.name
        if(random.random()<0.3):
            mes.append("有一队冒险者来森林里收集史莱姆素材")
            if(player.win_by_lvl(2)):
                mes.append("他们没有料到%s是一只很强的史莱姆"%player.name)
                mes.append("他们被%s击退了"%name)
                lvl_earn=0.5**player.lvl
                mes.append("能力值提升了%.1f"%lvl_earn)
            else:
                mes.append("他们不怀好意地靠近你")
                player.hp=0
        else:#(random.random()<0.5):
            mes.append("%s驱动着圆滚滚的史莱姆身体到处乱逛"%name)
            mes.append("发现前面有一群哥布林")
            if(player.win_by_lvl(2)):
                mes.append("哥布林要打%s"%name)
                mes.append("%s驱动圆滚滚的身体滚滚滚滚滚下了山，逃跑了")
            elif(player.win_by_lvl(2)):
                mes.append("哥布林没想到%s是个聪明的史莱姆"%name)
                mes.append("打不过%s"%name)
            else:
                mes.append("你被装进了哥布林的热水锅里煮")
                player.hp=0
        return mes

#location ero dungeon events
#

class event_ero_dungeon(event):
    def __init__(self):
        super().__init__("工口地牢")
    def calc_priority(self, player):
        if(player.location!='工口地牢'):
            return impossible
        else:
            return f_calc_priority(1,prior)
    def encounter(self,player:cplayer):
        
        mes=[]
        stat_name=lambda n:"hidden-工口地牢visited-%s"%n
        name=player.name
        _impossible=114514
        calcp=lambda n:_impossible if (player.status.get(stat_name(n))) else f_calc_priority(1,prior)
        def level1():
            nonlocal mes
            player.status[stat_name('level1')]=True
            mes.append('%s遇到一片水池，对面有看起来像出口的门'%name)
            mes.append('里面都是黏糊糊的液体，看起来非常牙白')
            mes.append("水池上面有一根很细的桥")
            mes.append("%s走了上去"%name)
            mes.append("桥上伸出了许多绒毛触手，%s脚滑"%name)
            mes.append("嗯喵！%s的腿掉进水池，正好跨在桥上，踮着脚"%name)
            mes.append("水池里黏糊糊的液体原来是史莱姆，让%s行进缓慢"%name)
            mes.append("桥上的触手绒毛刺激着%s"%name)
            mes.append("非常艰难地通过了这片区域")
            player.numeric_status_count('经验次数')
            return
        def level2():
            nonlocal mes
            player.status[stat_name('level2')]=True
            mes.append('%s正在探路'%name)
            mes.append('前面遇到一扇关着的门')
            mes.append('地上有一根棒状物体，和一个液体容器')
            mes.append('%s想了想，坐了上去'%name)
            mes.append('嗯喵嗯喵嗯喵喵')
            mes.append('容器装满%s的液体的时候，门开了'%name)
            player.numeric_status_count('经验次数')
            return
        def level3():
            nonlocal mes
            player.status[stat_name('level3')]=True
            mes.append('%s看到路边有一个宝箱'%name)
            mes.append('毫无戒备心的笨比%s打开了宝箱'%name)
            mes.append('里面有一套散发着魔力之光的衣服')
            mes.append('“看起来是史诗级装备呀”')
            mes.append('%s穿了上去'%name)
            mes.append('恰到好处地包裹住了%s，发现怎么也脱不下来'%name)
            mes.extend(get_resource("触手服"))
            mes.append('衣服内部伸出了触手')
            mes.append('嗯喵嗯喵喵嗯喵')
            player.numeric_status_count('经验次数')
            return
        def level_boss():
            nonlocal mes
            mes.append('%s终于找到了出口'%name)
            player.location=player.born_location
            for i in ['level1','level2','level3']:
                player.status[stat_name(i)]=False
            player.earn_item('触手服')
            return
        az=list()
        az.append((calcp('level1'),random.random(),level1))
        az.append((calcp('level2'),random.random(),level2))
        az.append((calcp('level3'),random.random(),level3))
        az.append((_impossible-1,random.random(),level_boss))
        min(az)[-1]()
        player.old_speed=0.01
        return mes



#event get jobs
class event_become_shopkeeper(event):
    def __init__(self):
        super().__init__('开个商店')
    def calc_priority(self, player):
        if('职业' in player.status):
            return impossible
        if(player.yearold>20 and player.location=='城镇'):
            return f_calc_priority(1.4)
        return impossible
    def encounter(self,player):
        mes=[]
        name=player.name
        mes.append("%s在小镇上开了一家杂货店"%name)
        player.status['职业']='杂货店主'
        return mes
class event_become_venturer(event):
    def __init__(self):
        super().__init__("当个冒险者")
    def calc_priority(self, player: cplayer) -> float:
        if(player.status.get('职业')):
            return impossible
        if(player.yearold>20):
            return f_calc_priority(1.4)
        return impossible
    def encounter(self, player: cplayer) -> list:
        mes=[]
        name=player.name
        mes.append("%s打算去当冒险者")
        player.status['职业']='冒险者'
        return mes
#event job daily
class event_shop_keeper(event):
    def __init__(self):
        super().__init__("经营商店")
    def calc_priority(self, player):
        if(player.status.get('职业')=='杂货店主'):
            return f_calc_priority(1.5)
        return impossible
    def encounter(self,player):
        mes=[]
        name=player.name
        mes.append("%s经营着一家商店"%name)
        if(random.random()<0.3):
            mes.append("有一位冒险者前来买东西")
            mes.append("他说%s给他卖假货，吵起来了"%name)
            if(player.win_by_lvl(4)):
                mes.append("%s一拳把闹事者打晕了，丢出去"%name)
            elif(random.random()<0.2):
                mes.append("店里其他人觉得无语")
                mes.append("帮忙把闹事者赶走了")
            else:
                mes.append("他在店里到处打砸")
                hp_cost=(1-player.win_rate_by_lvl(3))*20*random.random()
                if(random.random()<0.2):
                    hp_cost=min(player.hp/2,hp_cost)
                
                hp=player.lose_hp(hp_cost)
                if(hp!=0):
                    mes.append("%s被找茬的人用刀砍，掉了%.1f HP"%(name,hp_cost))
                else:
                    mes.append("撒日朗！！！")
        elif(random.random()<0.5):
            money_earn=random.random()*70+10
            mes.append("%s赚了%.1f元"%(name,money_earn))
            player.status['金钱']=player.status.get("金钱",0)+money_earn
        
        return mes


#event misc
class event_sell_inventory(event):
    def __init__(self):
        super().__init__("卖东西")
    def calc_priority(self, player:cplayer) -> float:
        if(not player.inventory_num()):
            return impossible
        if(player.location not in '城镇,魔王领地'):
            return impossible
        if(player.inventory_num()>8):
            return f_calc_priority(0.5)
        return f_calc_priority(2)
    def encounter(self, player: cplayer) -> list:
        mes=[]
        name=player.name
        mes=["%s在商店"%name]
        earn=0
        value={"触手服":100,"史莱姆精华液":10}
        for i,j in value.items():
            if(player.inventory.get(i)):
                _earn=player.inventory[i]*j
                earn+=_earn
                mes.append("出售了%s，获得%d金钱"%(i,_earn))
                player.inventory[i]=0
        player.earn_money(earn)
        return mes
if(__name__=='__main__'):
    event('A',rarity=1)
    event('B',rarity=2)
    event('C',rarity=3)
    event('D',rarity=4)
    event('E',rarity=5)
    event('F',rarity=6)
    event('G',rarity=7)
    event('H',rarity=8)
    class I(event):
        def __init__(self):
            super().__init__(name='I',rarity=9)
    I()
    def choose_event(player):
        az=[]
        for name,inst in events.items():
            az.append(inst.try_encounter(player))
        return min(az)
    cnt=dict()
    for i in range(20000):
        evt=choose_event(None)[1]
        evt=str(evt)
        cnt[evt]=cnt.get(evt,0)+1
    for i in sorted(cnt.items(),key=lambda x:x[1]):
        print(i)
else:
    #general events
    event_born()
    event_farm_slime()
    event_farm_goblin()
    event_recover_hp()
    event_child_play()
    event_old_disease()
    #move place events
    event_goto_forest()
    event_goto_town()
    #elf events
    event_elf_raped()
    event_elf_daily()
    event_elf_akuochi()
    #neko events
    event_neko_catch_fish()
    event_neko_prpr()
    #disaster events
    event_forest_fire()
    event_maou_massacre()
    #school events
    event_enter_school()
    event_graduate()
    event_study()
    event_SIF()
    #maou envents
    event_invading()
    event_encounter_hero()
    event_maou_fighting_championship()
    event_maou_decide_relation()
    event_maou_challenged_by_soldier()
    #succubus events
    event_succubus_daily()
    
    #SIF events
    event_SIF_live()
    event_SIF_practice()
    
    #slime events
    event_slime_born()
    event_slime_fight()

    #ero dungeon events
    event_enter_ero_dungeon()
    event_ero_dungeon()
    

    #event get jobs
    event_become_shopkeeper()
    event_become_venturer()
    
    #event jobs daily
    event_shop_keeper()

    #event misc
    event_sell_inventory()