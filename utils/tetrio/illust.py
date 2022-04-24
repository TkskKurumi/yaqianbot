
from PIL import Image, ImageDraw
from pic2pic import txt2im, txt2im_ml, fixHeight
from math import sin, cos, pi, exp
from . import colors
from .requests import getimage
from .user import user as class_user
from typing import Tuple

def sigmoid(x):
    return 1/(1+exp(x))


def elu(x):
    if(x > 0):
        return x
    else:
        return exp(x)


def skill_polygon(size, skills, font_size=None, color: colors.color = colors.c_color_MIKU, style="light"):
    """ illustrates skill polygon
    Arguments:
    size --- image size
    skills --- dict of skill, skill: dict of value (abs value), rvalue (relative value)
    """
    if(font_size is None):
        font_size = int(size/3.8)
    skill_txt_images = []
    tmp = 0

    is_light = style == "light"
    if(isinstance(color, tuple)):
        color = colors.color(*color)
    if(is_light):
        color1 = color.lighten()
        color2 = color.darken()
    else:
        color1 = color.darken()
        color2 = color.lighten()
    color1a = color1.alter(A=100)
    color2a = color2.alter(A=100)

    for skill, values in skills.items():
        txt = "%s\n%.1f" % (skill, values['value'])
        im_d = txt2im_ml(txt, fixedHeight=font_size,
                         width=font_size*10, trim_width=True, align=0.5, fill=color2.astuple())
        im_l = txt2im_ml(txt, fixedHeight=font_size,
                         width=font_size*10, trim_width=True, align=0.5, fill=color.astuple())
        _w, _h = im_d.size
        tmptmp = (_w*_w+_h*_h)**0.5
        tmp = max(tmp, tmptmp)
        skill_txt_images.append((im_l, im_d))
    w = int((size + tmp)*2)
    h = w
    n = len(skills)
    le, ri, up, lo = w, 0, h, 0
    draw_width = int(w/100)

    def position(r=size, idx=None, angle=None):
        nonlocal n
        if(idx is not None):
            angle = (idx/n*2-0.5)*pi
        x = w/2+cos(angle)*r
        y = h/2+sin(angle)*r
        return x, y

    ls_skills = list(skills.items())

    def newlayer():
        nonlocal w, h
        return Image.new("RGBA", (w, h), (0,)*4)

    def newlayer_dr():
        nonlocal w, h
        layer = newlayer()
        dr = ImageDraw.Draw(layer)
        return layer, dr
    ret = newlayer()
    layer, dr = newlayer_dr()

    for i in range(n):
        im_l, im_d = skill_txt_images[i]
        _w, _h = im_l.size
        length = (_w*_w+_h*_h)**0.5
        x, y = position(size+length*0.4, i)
        x, y = int(x-_w/2), int(y-_h/2)
        layer.paste(im_l, box=(x+1, y+1), mask=im_d)
        layer.paste(im_d, box=(x, y))
        le = min(le, x)
        print(ls_skills[i][0], x, le)
        ri = max(ri, x+_w)
        up = min(up, y)
        lo = max(lo, y+_h)

    ret = Image.alpha_composite(ret, layer)

    layer, dr = newlayer_dr()
    for i in range(n):
        ctr = position(0, 0)
        u = position(size, idx=i)
        v = position(size, idx=i+1)
        dr.line((u, v), fill=color2.astuple(), width=draw_width)
        dr.line((u, ctr), fill=color2.astuple(), width=draw_width)
    ret = Image.alpha_composite(ret, layer)
    layer, dr = newlayer_dr()
    vertexes = []
    for i in range(n):
        # ctr = position(0, 0)
        skill, skillv = ls_skills[i]
        rv = skillv['rvalue']
        rv **= 2
        gate = 1.1
        mx = 1.3
        if(rv > gate):
            # print(rv,gate + (1-exp(gate-rv))*(mx-gate))
            rv = gate + (1-exp(gate-rv))*(mx-gate)
        u = position(size*rv, idx=i)
        vertexes.append(u)

    dr.polygon(vertexes, fill=color2a.astuple())
    dr.line(vertexes+[vertexes[0]], fill=color.astuple(), width=draw_width)

    ret = Image.alpha_composite(ret, layer)
    # ret.show()
    print((le, up, ri, lo))
    return ret.crop((le, up, ri, lo))


def profile(user: class_user, size=720, color: colors.color = colors.c_color_MIKU, style="dark"):
    # Meow!!! Meow! Meow!
    # 懒得写docstring
    w = size
    border = int(size/40)
    golden = (5**0.5 - 1)/2
    draw_width = int(border/5)

    # league skills
    # skills = ["apm", "pps", "vs"]
    # values = [user.league[i] for i in skills]
    # apm, pps, vs = values
    # rvalues = apm/40, pps/1.2, vs/83
    # mx = max(rvalues)
    # rvalues = [i/mx for i in rvalues]
    # skills_dict = dict()
    # for idx in range(3):
    #     skill_dict = dict()
    #     skill_dict["value"] = values[idx]
    #     skill_dict["rvalue"] = rvalues[idx]
    #     skills_dict[skills[idx]] = skill_dict
    skills_dict = user.get_relative_skills()
    # colors
    is_light = style == "light"
    if(is_light):
        color1 = color.lighten()
        color2 = color.darken()
    else:
        color1 = color.darken()
        color2 = color.lighten()
    color1a = color1.alter(A=100)
    color2a = color2.alter(A=100)

    # sizes
    size_avatar = int(size/4.3)
    size_badge = int(size_avatar/4.5)
    size_name = int((size_avatar+size_badge/2-border)/3)
    size_rank = size_name*2
    size_tr = int((size_rank-border)/(1+golden))
    size_glicko = int(size_tr*golden)
    size_poly = size_avatar*(golden**2)
    # images
    im_avatar = user.get_avatar().resize((size_avatar, size_avatar), Image.LANCZOS)
    im_username = txt2im(user.username.upper(),
                         fixedHeight=size_name, fill=color2.astuple())
    if(user.user["country"] is None):
        im_flag = Image.new("RGBA", (32, 32), (0,)*4)
    else:
        im_flag = user.get_flag()
    im_flag = fixHeight(im_flag, size_name)
    im_league_badge = user.get_league_badge()
    im_league_badge = fixHeight(im_league_badge, size_rank)
    im_tr = txt2im(
        "%.2f TR" % user.league["rating"], fixedHeight=size_tr, fill=color2.astuple())
    im_glicko = txt2im(
        "%.2f ± %d Glicko" % (user.league['glicko'], user.league["rd"]), fixedHeight=size_glicko, fill=color2.astuple())
    im_poly = skill_polygon(size_poly, skills_dict, color=color, style=style)
    # positions
    top_avatar = border
    left_avatar = border
    top_badge = top_avatar+size_avatar-size_badge//2
    top_username = border
    left_username = left_avatar+size_avatar+border
    top_league_badge = top_username+size_name+border
    left_league_badge = left_username
    left_flag = w-im_flag.size[0]-border
    top_flag = top_username
    left_tr = left_league_badge+im_league_badge.size[0]+border
    top_tr = top_league_badge
    top_glicko = top_tr+size_tr+border
    left_glicko = left_tr
    top_poly = top_badge+size_badge+border
    left_poly = border
    # draw
    h = top_poly+im_poly.size[1]+border

    def newlayer():
        nonlocal w, h
        return Image.new("RGBA", (w, h))
    ret = Image.new("RGBA", (w, h), color1.astuple())

    def newlayer_dr() -> Tuple[Image.Image, ImageDraw.Draw]:
        nonlocal w, h
        im = Image.new("RGBA", (w, h))
        dr = ImageDraw.Draw(im)
        return im, dr

    def commit_layer():
        nonlocal layer, ret
        ret = Image.alpha_composite(ret, layer)
        return ret
    layer = newlayer()
    layer.paste(im_avatar.convert("RGBA"), box=(left_avatar, top_avatar))
    layer.paste(im_username.convert("RGBA"), box=(left_username, top_username))
    layer.paste(im_flag.convert("RGBA"), box=(left_flag, top_flag))
    layer.paste(im_league_badge.convert("RGBA"), box=(left_league_badge, top_league_badge))  # nopep8
    layer.paste(im_tr, box=(left_tr, top_tr))
    layer.paste(im_glicko, box=(left_glicko, top_glicko))
    layer.paste(im_poly, box=(left_poly, top_poly))
    commit_layer()
    layer, dr = newlayer_dr()
    left = left_avatar+int(size_badge/3)
    for i in user.user.get("badges", list()):
        id = i["id"]
        url = r"https://tetr.io/res/badges/%s.png" % id

        ellipse_box = (left, top_badge, left+size_badge, top_badge+size_badge)
        expand = int(size_badge/7)
        box = [ellipse_box[idx] + (expand if idx < 2 else -expand)
               for idx in range(4)]
        _w, _h = box[2]-box[0], box[3]-box[1]
        im = getimage(url).resize((_w, _h), Image.LANCZOS).convert("RGBA")
        fill_color = color1a.astuple()
        bord_color = color2.astuple()
        dr.ellipse(ellipse_box, fill=fill_color,
                   outline=bord_color, width=draw_width)
        layer.paste(im, box=box[:2], mask=im)
        left += size_badge+int(size_badge/3)
    commit_layer()
    return ret


if(False and __name__ == "__main__"):
    # pps = {"value": 1.53, "rvalue": 1.3}
    # apm = {"value": 38.87, "rvalue": 0.97}
    # vs = {"value": 78.63, "rvalue": 0.9}
    # skills = {"pps": pps, "apm": apm, "vs": vs}
    # im = skill_polygon(100, skills)

    mura = class_user("murarin")
    # for color in [colors.c_color_BLUE, colors.c_color_MIKU, colors.c_color_PINK]:
    #     for style in ["light", "dark"]:
    #         profile(mura, color=color, style=style).show()
    profile(mura, style="light", color=colors.c_color_PINK).show()
    yqq = class_user("tkskkurumi")

    profile(yqq, style="dark", color=colors.c_color_PINK).show()
    cz = yqq = class_user("czsmall0402")
    profile(yqq, style="light", color=colors.c_color_BLUE).show()
if(__name__ == "__main__"):
    profiles = []
    for u in ["tkskkurumi", "murarin", "kazu", "ix1iv", "rdut_64", "doriko"]:
        user = class_user(u)
        prof = profile(user)
        profiles.append(prof)
    from pic2pic import picMatrix
    picMatrix(profiles).show()
    prof.show()
