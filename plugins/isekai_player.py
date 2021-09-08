
class player_inbornskill:
    #base class, nothing is implemented
    pass



class player_status:
    def __init__(self,name,gender,species,yearold,lvl=1,status=None,skills=None,location='森林',born_location=None):
        self.hp=50
        self.lvl=1
        self.name=name
        self.species=species
        self.yearold=yearold
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
    def get_old(self,n=1):
        self.yearold+=n*self.old_speed
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
        mes.append("%s:"%self.name)
        mes.append("%s, 能力值%.1f, HP%.1f"%(self.strold(),self.lvl,self.hp))
        return mes
    def refine_species(self):
        if(self.species=='猫人'):
            if(self.gender=='女性'):
                return '猫娘'
            else:
                return '猫郎'
        else:
            return self.gender+self.species