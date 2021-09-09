import random
class player_inbornskill:
    #base class, nothing is implemented
    pass
def f_calc_priority(rarity,delta=0):
    return random.normalvariate(rarity,rarity**0.5)+delta
def rand_profit(r):
    return max(random.normalvariate(r,r**0.5),0)

class player_status:
    def __init__(self,name,gender,species,yearold,lvl=1,status=None,skills=None,location='森林',born_location=None):
        self.hp=50
        self.lvl=1
        self.name=name
        self.species=species
        self.yearold=yearold
        self.mes=[]
        self.location=location
        self.born_location=born_location or location
        self.gender=gender
        self.old_speed=1
        if(skills is None):
            self.skills=list()
        else:
            self.skills=skills
        if(status is None):
            self.status=dict()
        else:
            self.status=status
    def is_alive(self):
        return self.hp>0
    def dump_mes(self):
        ret=self.mes
        self.mes=[]
        return ret
    def get_old(self,n=1):
        nn=n*self.old_speed
        if(self.yearold<15):
            if(random.random()<0.6):
                lvl_earn=rand_profit(1)/10
                self.lvl+=lvl_earn
                if(lvl_earn>0.1):
                    self.mes.append("随着年龄的增长，%s能力值变强了%.1f"%(self.name,lvl_earn))
        elif(self.yearold>40 and (self.species not in '魅魔精灵史莱姆')):
            lvl_lost=self.lvl*(1-(0.97**nn))
            self.lvl-=lvl_lost
            self.mes.append("随着衰老，%s能力值变弱了%.1f"%(self.name,lvl_lost))
        if(self.yearold>100):
            nn*=self.yearold/10
        self.yearold+=nn
        self.old_speed=1
        
    def lose_hp(self,n):
        self.hp=max(0,self.hp-n)
        return self.hp
    def strold(self):
        yint=int(self.yearold)
        m=(self.yearold-yint)*12
        mint=int(m)
        d=(m-mint)*30
        return "%d岁%d月%d天"%(yint,mint,d)
    def report_status(self):
        mes=[]
        mes.append("%s %s:"%(self.refine_species(),self.name))
        mes.append("%s, 能力值%.1f, HP%.1f"%(self.strold(),self.lvl,self.hp))
        for i in self.status:
            if(i=='史莱姆出生'):
                continue
            if(i in ['already_SIF']):
                continue
            j=self.status[i]
            j=str(j)
            if(j in 'TrueFalse'):
                j=''
            mes.append("  %s: %s"%(i,j))
        return mes
    def refine_species(self):
        if(self.species=='猫人'):
            if(self.gender=='女性'):
                return '猫娘'
            else:
                return '猫郎'
        elif(self.species=='史莱姆'):
            return '史莱姆'
        else:
            return self.gender+self.species
    def win_by_lvl(self,lvl):
        win_rate=1/(1+3**(lvl-self.lvl))
        return random.random()<win_rate
    def win_rate_by_lvl(self,lvl):
        win_rate=1/(1+3**(lvl-self.lvl))
        return win_rate
    def profit_by_lvl(self):
        return max(self.lvl/5,f_calc_priority(self.lvl))
    