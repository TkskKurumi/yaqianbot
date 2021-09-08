import random
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
    def judge_possible(self,player):
        return True
    def calc_priority(self,player):
        return random.normalvariate(self.rarity,self.rarity**0.5)+self.priority_delta
    def try_encounter(self,userinfo):
        return self.calc_priority(userinfo),self
    def __str__(self):
        return "Event(%s)"%self.name
    def __repr__(self):
        return self.__str__()
    def __lt__(self,other):
        return self.name<other.name
class event_born(event):
    def __init__(self):
        super().__init__('出生')
    def calc_priority(self,player):
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
        player.get_old()
        return mes

class event_farm_slime(event):
    #刷小怪
    def __init__(self):
        super().__init__(name='打小怪',rarity=1)
    def calc_priority(self,player):
        if(player.location=='城镇'):
            return impossible
        if(player.yearold<11):
            return f_calc_priority(3)
        else:
            return f_calc_priority(0.5+25/player.hp)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_cost=15/player.lvl
        lvl_earn=0.7**player.lvl
        
        hp=player.lose_hp(hp_cost)
        player.lvl+=lvl_earn
        
        mes.append("%s在打史莱姆"%player.name)
        if(hp==0):
            if(player.yearold<11):
                mes.append("幼小的%s根本不知道怪物的可怕，作死了"%name)
            else:
                monster_name=random.choice(['史莱姆'])
                mes.append("%s真是杂鱼，居然%s都打不过"%(name,monster_name))
            return mes
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
        
        return f_calc_priority(0.8+hp_cost/20)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_cost=15/(player.lvl-1)
        hp=player.lose_hp(hp_cost)
        lvl_earn=0.7**(player.lvl-0.5)
        player.lvl+=lvl_earn
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
        return f_calc_priority(player.hp/30)
    def encounter(self,player):
        mes=[]
        name=player.name
        hp_recover=min(player.lvl/2,1)*((50-player.hp)**0.3)
        rnd=(random.random()*0.7+0.15)
        hp_recover*=rnd
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
        if(player.species=='精灵'):
            return f_calc_priority(1.7)
        else:
            return f_calc_priority(2)
    def encounter(self,player):
        mes=[]
        player.location='森林'
        if(player.species=='精灵'):
            mes.append("%s回到了故乡，大森林"%player.name)
        else:
            mes.append("%s来到了大森林"%player.name)
        return mes


#female elf events
class event_elf_raped(event):
    def __init__(self):
        super().__init__(name='精灵被嗯喵',rarity=1.5)
    def calc_priority(self,player):
        if(player.gender=='女性' and player.species=='精灵' and player.location=='森林' and player.yearold>14):
            return super().calc_priority(player)
        else:
            return impossible
    def encounter(self,player):
        mes=[]
        mes.append("%s被兽人抓住了"%player.name)
        hp=player.lose_hp(10)
        if(hp==0):
            mes.append("%s被关起来变成了兽人的RBQ，被雷普到死"%player.name)
        else:
            mes.append("%s被关起来嗯喵❤嗯喵喵❤喵喵呜呜❤"%player.name)
            mes.append("掉了%.1fHP"%10)
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
        mes.append("%s在精灵村寨生活，能力值提升了%.1f"%(name,lvl_earn))
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
        super().__init__(name='森林大火',rarity=3.6)
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
class event_maou_massacre(event):
    def __init__(self):
        super().__init__(name="魔王大屠杀",rarity=3.8)
    def calc_priority(self, player):
        if(player.location=='学校'):
            return f_calc_priority(3.8,prior)
        return super().calc_priority(player)
    def encounter(self,player):
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
        else:
            return f_calc_priority(1.8)
    def encounter(self,player):
        prev_loc=player.location
        mes=[]
        mes.append("%s从%s来到学校"%(player.name,prev_loc))
        player.location='学校'
        pass
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
        mes.append("%s在学校学习战斗，能力值提升了%.1f"%lvl_earn)
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
    #move place events
    event_goto_forest()
    #elf events
    event_elf_raped()
    event_elf_daily()
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