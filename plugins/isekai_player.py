
class player_inbornskill:
    #base class, nothing is implemented
    pass



class player_status:
    def __init__(self,name,gender,species,yearold,lvl=1,status=None,skills=None,location='森林'):
        self.hp=50
        self.mp=mp
        self.lvl=1
        self.name=name
        self.species=species
        self.yearold=yearold
        self.location=location
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
        self.yearold+=1
    def lose_hp(self,n):
        self.hp=max(0,self.hp-n)
        return self.hp