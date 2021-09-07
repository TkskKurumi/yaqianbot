import random
events=dict()
inevitable=float('-inf')
impossible=float('inf')
prior=-10
def f_calc_priority(rarity,delta=0):
    return random.normalvariate(rarity,rarity**0.5)+delta
class event:
    def __init__(self,name,rarity=1,priority_delta=0):
        self.rarity=rarity
        self.name=name
        self.priority_delta=priority_delta
        global events
        events[name]=self
    def calc_priority(self,userinfo):
        return random.normalvariate(self.rarity,self.rarity**0.5)+self.priority_delta
    def try_encounter(self,userinfo):
        return self.calc_priority(userinfo),self
    def __str__(self):
        return "Event(%s)"%self.name
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
        mes.append('你是一位%s%s'%(gender,player.species))
        mes.append('出生在%s'%player.location)
        player.get_old()
        return mes

class event_elf_raped(event):
    def __init__(self):
        super().__init__(name='精灵被嗯喵',rarity=1.7)
    def calc_priority(self,player):
        if(player.gender=='女性' and player.species=='精灵' and player.location=='森林'):
            return super().calc_priority(player)
        else:
            return impossible
    def encounter(self,player):
        mes=[]
        mes.append("%s被兽人抓住了"%player.name)
        hp=player.lose_hp(10)
        if(hp==0):
            mes.append("%s被关起来变成了兽人的RBQ"%player.name)
        else:
            mes.append("%s被关起来嗯喵嗯喵喵喵喵呜呜")
        return mes
class event_farm_slime(event):
    #刷小怪
    def __init__(self):
        super().__init__(name='打小怪',rarity=1):
    def calc_priority(self,player):
        if(player.yearold<11):
            return f_calc_priority(5)
        else:
            return f_calc_priority(0.5+25/player.hp)
    def encounter(self,player):
        mes=[]
        hp=player.lose_hp(15/player.lvl)
        player.lvl+=0.5**player.lvl
if(__name__=='__main__'):
    event('A',rarity=1)
    event('B',rarity=2)
    event('C',rarity=3)
    event('D',rarity=4)
    event('E',rarity=5)
    event('F',rarity=6)
    event('G',rarity=7)
    event('H',rarity=8)
        
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