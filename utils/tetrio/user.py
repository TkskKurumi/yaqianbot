from .requests import gettext, getimage
from .utils import save_temp
import json


class user:
    def __init__(self, user_id):
        url = "https://ch.tetr.io/api/users/%s" % user_id
        h = gettext(url)
        # print(save_temp(h, ext=".json"))
        j = json.loads(h)
        if(not j["success"]):
            raise Exception(j["error"])
        data = j["data"]
        user = data["user"]
        self.j = j
        self.user = user
        self._id = user["_id"]
        self.username = user["username"]
        self.league = user["league"]
        if(all([i in self.league for i in ["apm", "vs", "pps"]])):
            lpm = self.league["pps"]*24
            
            apm = self.league["apm"]
            pps = self.league["pps"]
            adpm = self.league["vs"]*0.6
            self.league["atk/line"] = apm/lpm
            self.league["dig/line"] = (adpm-apm)/lpm
            self.league["dpm"] = adpm-apm

    def get_avatar(self):

        try:
            url = r"https://tetr.io/user-content/avatars/%s.jpg" % self._id
            im = getimage(url)
        except Exception as e:
            return getimage(r"https://tetr.io/res/avatar.png")
        return im

    def get_flag(self):
        url = r"https://tetr.io/res/flags/%s.png" % self.user["country"].lower(
        )
        return getimage(url)

    def get_league_badge(self):
        url = r"https://tetr.io/res/league-ranks/%s.png" % self.league["rank"].lower(
        )
        return getimage(url)

    def get_relative_skills(self):
        skills = ["apm", "pps", "vs"]
        skills.extend(["atk/line", "dig/line", "dpm"])
        self_skill = {skill: self.league[skill] for skill in skills}
        other_skills = {}
        users = []

        url1 = r"https://ch.tetr.io/api/users/lists/league?limit=5&after=%d" % self.league["rating"]
        url2 = r"https://ch.tetr.io/api/users/lists/league?limit=5&before=%d" % self.league["rating"]
        for url in [url1, url2]:
            j = gettext(url)
            j = json.loads(j)
            if(not j["success"]):
                e = Exception(j["error"])
                continue
            users.extend(j["data"]["users"])
        if(not users):
            raise e
        for i in users:
            uname = i["username"]
            u = user(uname)

            for skill in skills:

                tot, num = other_skills.get(skill, (0, 0))
                if(skill not in u.league):
                    continue
                tot += u.league[skill]
                num += 1
                other_skills[skill] = (tot, num)
        rel_skills = {}
        for skill in skills:
            tot, num = other_skills[skill]
            avg = tot/num
            rel_skills[skill] = {
                "rvalue": self_skill[skill]/avg, "value": self_skill[skill]}

        return rel_skills


if(__name__ == "__main__"):   # test
    mura = user("murarin")
    yqq = user("tkskkurumi")
    # mura.get_avatar().show()
    print(mura.get_relative_skills())
    print(yqq.get_relative_skills())
