from bot_backend import *
from pic2pic import zoomin_blur, txt2im_ml, txt2im
from make_gif import make_gif as _make_gif
from PIL import Image, ImageFilter
import random
import extract_gif
import mywc
import random_deform
import pic2pic
import mymath
import myGeometry
import math
import myio
import numpy as np
from PIL import ImageDraw
from myGeometry import point
from os import path
from glob import glob
from horror_gif import horror_gif


def make_gif(*args, **kwargs):
    kwargs['pth'] = path.join(mainpth, 'temppic')
    return _make_gif(*args, **kwargs)


def test_gif(img):
    try:
        img.seek(1)
        return True
    except Exception:
        return False


plugin_name_n = '沙雕图片生成器'


def report_status():
    ret = []
    ret.append('“/词云”   根据你群聊天记录生成词云')
    ret.append('“/缩放模糊”   将一张图缩放模糊产生动图')
    ret.append('“/随机扭曲”   将一张图随机扭曲产生动图')
    ret.append('“/扭扭”   将一张图左右扭扭')
    ret.append('“/扭扭1”   将一张图左右扭扭（另一种形式）')
    ret.append('“/恐怖”   将一张图进行扭曲、附加glitch效果')
    ret.append('“/抖文字”   将输入的文字化为抖来抖去的图片')
    ret.append('“/印象分型”   以图片色彩生成一个三角分型图片')
    return ret


def sample_by_cnt(sdic, n=100):
    #from bot_backend import lcg_eternal
    pth = sdic.pth
    ls = list(glob(path.join(pth, '*.json')))
    random.shuffle(ls)
    mx = (0, '')
    for i in ls:
        az = list(myio.loadjson(i).items())
        random.shuffle(az)
        for j, k in az:
            mx = max(mx, tuple(k))
            n -= 1
            if(n <= 0):
                return mx
    return mx


def sample_by_cnt1(sdic, n=100, k=5):
    from heapq import heappush, heappop
    pth = sdic.pth
    ls = list(glob(path.join(pth, '*.json')))
    random.shuffle(ls)
    mx = []
    for i in ls:
        az = list(myio.loadjson(i).items())
        random.shuffle(az)
        for j, _k in az:
            heappush(mx, _k)
            if(len(mx) > k):
                heappop(mx)
            n -= 1
            if(n <= 0):
                return mx
    return mx


@receiver
@threading_cnt('网友发了啥图')
@on_exception_send
@start_with(r'[!！/]网友发了啥图|[！!/]表情包|[！!/]啥图')
def cmd_random_pic(ctx, match, rest):
    from bot_backend import lcg_eternal, pic_cnt
    if(rest):
        mes = set()
        ls = sample_by_cnt1(pic_cnt, 400, 5)
        for mx in ls:
            cnt, url = mx
            f = lcg_eternal.get_path(url)
            f = fix_img_ext(f)
            mes.add(f)
        simple_send(ctx, list(mes))
        return
    mx = sample_by_cnt(pic_cnt, 80)
    cnt, url = mx
    f = lcg_eternal.get_path(url)
    f = fix_img_ext(f)
    if(random.random() < 0.3):
        mes = '网友们发了%d次' % cnt
    elif(random.random() < 0.5):
        mes = '菜菜看到了%d次' % cnt
    else:
        mes = '大家发了%d次' % cnt
    simple_send(ctx, [mes, f])


re_uflst = re.compile(r'[！!/]?u(\d+?)发了啥图')
re_gflst = re.compile(r'[！!/]?g(\d+?)发了啥图')
re_niqunflst = re.compile(r'[！!/]?你群爱发啥图')


@receiver
@threading_cnt('谁发了啥图')
# @on_exception_send
def cmd_specific_pic(ctx):
    try:
        from bot_backend import lcg_eternal
        sctx = simple_ctx(ctx)
        text = sctx.text
        if(re_uflst.match(text)):
            uid = re_uflst.findall(text)[0]
            counter = get_pic_cnt_byu(uid)
            mx = sample_by_cnt(counter, 5)

            cnt, url = mx
            if(cnt):
                f = lcg_eternal.get_path(url)
                f = fix_img_ext(f)
                simple_send(ctx, f)
            else:
                simple_send(ctx, '我还没见ta发图呢？')
        elif(re_gflst.match(text)):
            gid = re_gflst.findall(text)[0]
            counter = get_pic_cnt_byg(gid)
            mx = sample_by_cnt(counter, 20)
            cnt, url = mx
            if(cnt):
                f = lcg_eternal.get_path(url)
                f = fix_img_ext(f)
                simple_send(ctx, f)
            else:
                simple_send(ctx, '我还没见这群发图呢？')
        elif(re_niqunflst.match(text)):
            gid = sctx.group_id
            counter = get_pic_cnt_byg(gid)
            mx = sample_by_cnt(counter, 20)
            cnt, url = mx
            if(cnt):
                f = lcg_eternal.get_path(url)
                f = fix_img_ext(f)
                simple_send(ctx, f)
            else:
                simple_send(ctx, '我还没见这群发图呢？')
    except Exception as e:
        import traceback
        print(traceback.format_exc())


@receiver
@threading_cnt('词云')
@on_exception_send
@start_with(r'[!！/]wc|[!！/]word_clud|[!！/]词云')
def cmd_word_cloud(ctx):
    @timing('词云')
    def f(ctx):
        sctx = simple_ctx(ctx)
        if(sctx.rpics):
            img = Image.open(sctx.get_rpics()[0])
        else:
            img = Image.open(plugins['plg_setu'].rand_img())
        gid = sctx.group_id
        pth = path.join(mainpth, 'saves', 'message_record', '%s.log' % gid)
        if(not path.exists(pth)):
            simple_send(ctx, '还没攒够聊天记录呐！')
            return
        text = myio.opentext(pth)
        if(len(text) < 700):
            simple_send(ctx, '还没攒够聊天记录呐！')
            return
        simple_send(ctx, '正在生成词云图..')
        wordFrequencies = mywc.wordText2wordFrequencies(text)
        wcpic = mywc.wordCloud(
            img, wordFrequencies=wordFrequencies, wordMax=500).convert("RGB")
        simple_send(ctx, wcpic, im_size_limit=1 << 20, img_type="JPEG")
    f(ctx)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]缩放模糊')
def cmd_zoomin_blur(ctx):
    @timing('缩放模糊')
    def f(ctx):
        sctx = simple_ctx(ctx)
        rpics = sctx.get_rpics()
        if(not rpics):
            simple_send(ctx, '您还没有发送图片呐！')
            return
        img = Image.open(rpics[0])
        is_gif = test_gif(img)
        fps = 24
        if(is_gif):
            imgs = extract_gif.extract_gif(rpics[0])
            fps = int(extract_gif.get_fps(rpics[0]))
        _ = []
        for i in range(len(imgs) if is_gif else 10):
            if(is_gif):
                _.append(zoomin_blur(imgs[i].convert(
                    "RGB"), dist=random.random()*0.3))
            else:
                _.append(zoomin_blur(img.convert(
                    "RGB"), dist=random.random()*0.3))
        gif = make_gif(_, ss=50000, fps=fps)
        simple_send(ctx, gif)
    f(ctx)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?parrot')
def parrot(ctx):

    a = glob(path.join(mainpth, 'parrot_hd', '*.gif'))
    a = random.choice(a)
    # await session.send([img2dic(a)])
    simple_send(ctx, a)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?随机扭曲$')
def cmd_random_deform(ctx):
    @timing('随机扭曲')
    def _f(ctx=ctx):
        sctx = simple_ctx(ctx)
        # sstr=senderstr(session.ctx,group_with_uid=True)
        # imgs=get_recent_sent_img_file(sstr)
        imgs = sctx.get_rpics()
        if(not imgs):
            img = plugins['plg_setu'].rand_img()
        else:
            img = imgs[0]
        img = Image.open(img)
        img = pic2pic.im_sizeSquareSize(img, 23004)
        imgs = [random_deform.random_deform(
            img, cnt=500, x_range=0.0, y_range=0.0, neibour_cnt=3) for _ in range(5)]
        gif = make_gif(imgs, fps=10, ss=23004)
        # non_async_send(session.bot,session.ctx,[img2dic(gif)])
        simple_send(ctx, gif)
    _f(ctx)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?扭扭')
def cmd_niuniu(ctx, match, rest):

    rest = rest.strip() == 'debug'
    sctx = simple_ctx(ctx)
    if('扭扭1' in sctx.text):
        return
    imgs = sctx.get_rpics()
    if(not imgs):
        img = plugins['plg_setu'].rand_img()
    else:
        img = imgs[0]
    img = Image.open(img)
    img = pic2pic.squareSize(img, 23333)
    w, h = img.size
    imgs = []
    def npa(_): return np.array(_, np.float64)
    if(rest):
        simple_send(ctx, '开始了')
    for i in range(-4, 5):
        if(rest and (i & 1)):
            simple_send(ctx, "%d/%d" % (i+5, 10))
        i = i/4
        i = mymath.asgn(i)*(abs(i)**0.5)
        qd = {}
        for x in range(w):
            for y in range(h):
                temp = (y/h-0.5)*2
                temp = (1-temp*temp)**0.3
                temp = temp*i*w/3
                qd[(x, y)] = (npa((x-temp, y)))
        imgs.append(random_deform.random_deform(
            img, cnt=0, neibour_cnt=3, qd=qd, method=0))
    gif = make_gif(imgs+imgs[-1:0:-1], fps=24, ss=23333)
    # non_async_send(session.bot,session.ctx,[img2dic(gif)])
    simple_send(ctx, gif)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?扭扭1')
def cmd_niuniu1(ctx, match, rest):
    sctx = simple_ctx(ctx)
    dbg = rest.strip() == 'debug'

    imgs = sctx.get_rpics()
    if(not imgs):
        img = plugins['plg_setu'].rand_img()
    else:
        img = imgs[0]
    img = Image.open(img)
    img = pic2pic.im_sizeSquareSize(img, 23004)
    w, h = img.size

    def npa(_): return np.array(_, np.float64)

    imgs = []
    if(dbg):
        simple_send(ctx, '开始了')
    for t in range(-1, 5):
        qd = {}
        if(dbg and (t & 1)):
            simple_send(ctx, '%.2f%%' % ((t+1)/12*100))
        p = myGeometry.point(-w*(2**t), h)
        for i in range(w):
            for j in range(h):
                pp = myGeometry.point(i, j)
                pp = p+(pp-p).unit()*abs((pp-p).x)
                qd[pp.xy] = npa((i, j))
        imgs.append(random_deform.random_deform(
            img, cnt=0, neibour_cnt=4, qd=qd, method=0))
    for t in range(4, -2, -1):
        qd = {}
        p = myGeometry.point(w+w*(2**t), h)
        if(dbg and (t & 1)):
            simple_send(ctx, '%.2f%%' % ((10-t)/12*100))
        for i in range(w):
            for j in range(h):
                pp = myGeometry.point(i, j)
                pp = p+(pp-p).unit()*abs((pp-p).x)
                qd[pp.xy] = npa((i, j))
        imgs.append(random_deform.random_deform(
            img, cnt=0, neibour_cnt=4, qd=qd, method=0))
    gif = make_gif(imgs+imgs[::-1], ss=23004, fps=18)
    # non_async_send(session.bot,session.ctx,[img2dic(gif)])
    simple_send(ctx, gif)


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?恐怖')
def cmd_horror_gif(ctx, match, rest):
    sctx = simple_ctx(ctx)
    imgs = sctx.get_rpics()
    if(not imgs):
        img = plugins['plg_setu'].rand_img()
    else:
        img = imgs[0]
    img = Image.open(img)
    gif = horror_gif(img, resolution=14000)
    simple_send(ctx, gif)


@receiver
@threading_cnt('抖文字')
@on_exception_send
@start_with(r'[!！/]?抖文字')
def cmd_shake_words(ctx, match, rest):
    imgs = [[]]
    area = 0
    cnt = 0
    for i in rest.strip(' \r\n'):
        if(i == '\n' or i == '\r'):
            imgs.append([])
            continue
        img = pic2pic.txt2im(i)
        imgs[-1].append(img)
        area += img.size[0]*img.size[1]
        cnt += 1
    border = int(math.sqrt(area/cnt/7))
    top = border
    left = border
    height = border
    width = 0
    tops = list()
    lefts = list()
    for i in imgs:
        top = height
        left = border
        tops.append(list())
        lefts.append(list())
        for j in i:
            tops[-1].append(top)
            lefts[-1].append(left)

            height = max(top+j.size[1], height)
            width = max(left+j.size[0], width)
            left += j.size[0]
    rets = []
    width += border
    height += border
    for frame in range(10):
        im = Image.new("RGBA", (width, height), (255,)*4)
        for i in range(len(imgs)):
            for j in range(len(imgs[i])):
                img = imgs[i][j]
                top = int(tops[i][j]+(random.random()-random.random())*border)
                left = int(
                    lefts[i][j]+(random.random()-random.random())*border)
                im.paste(img, box=(left, top), mask=img)
        rets.append(im)
    simple_send(ctx, make_gif(rets, ss=23333, fps=15))


@receiver
@threading_run
@on_exception_send
@start_with(r'[!！/]?运动模糊')
def mb(ctx, match, rest):
    sctx = simple_ctx(ctx)
    # sstr=senderstr(session.ctx,group_with_uid=True)
    # imgs=get_recent_sent_img_file(sstr)
    imgs = sctx.get_rpics()
    try:
        rrr = min(float(rest.strip()), 12)
    except Exception as e:
        rrr = 1
    if(path.splitext(imgs[0])[1] != '.gif'):
        img = Image.open(imgs[0]).convert("RGBA")
        img = pic2pic.im_sizeSquareSize(img, 23333)
        frames = 30
        fps = 30
        rr = img.size
        rr = ((rr[0]*rr[1])**0.5)*rrr
    else:
        img = extract_gif.extract_gif(imgs[0])
        fps = extract_gif.get_fps(imgs[0])
        frames = len(img)
        rr = img[0].size
        rr = ((rr[0]*rr[1])**0.5)*rrr

    imgs = []

    angle1 = angle = 0
    r1 = int(random.random()*rr*0.15+1.5)
    for i in range(frames):

        r = int(random.random()*rr*0.15+1.5)
        angle += random.random()*360/frames*6
        x, y = myGeometry.point.rarg(r, angle).xy
        if(isinstance(img, list)):
            img_ = img[i].copy()
            img_.paste(img[i].copy(), (int(x), int(y)))
        else:
            img_ = img.copy()
            img_.paste(img, (int(x), int(y)))
        img_ = img_.rotate(random.random()*36*rrr-18*rrr,
                           fillcolor=pic2pic.get_border_color(img_))
        img_ = pic2pic.motion_blur(img_, r, angle)
        if(r1 >= 2):
            img_ = pic2pic.motion_blur(img_, r1, angle1)
        imgs.append(img_)
        r1 = r//2
        angle1 = angle
    gif = make_gif(imgs, ss=2200000//frames, fps=int(fps),
                   pth=path.join(mainpth, 'temppic'))
    simple_send(ctx, gif)


@receiver
@threading_cnt('lumin2d')
@on_exception_send
@start_with(r'[!！/]?光照')
def cmd_lumin(ctx, match, rest):
    rest = rest.strip()
    if(re.match(r'\d+(\.\d+)?', rest)):
        mtch = re.match(r'\d+(\.\d+)?', rest).group()
        rate = float(mtch)
        if(rate <= 0):
            rate = 1
    else:
        rate = 1
    sctx = simple_ctx(ctx)
    rpics = sctx.get_rpics()
    pic = rpics[0]
    pic = Image.open(pic)
    pic = pic2pic.squareSize(pic, 8e4)
    import lumin2d
    gr = lumin2d.gray(pic.filter(ImageFilter.GaussianBlur(2)))
    vn = lumin2d.vec_n(gr)

    def fuc1(x0, y0, x1, y1):
        k = (y1-y0)/(x1-x0)
        b = y0-k*x0

        def f(x, k=k, b=b):
            return k*x+b
        return f

    def fuc(l_min, l_max, d_min, d_max, l_a, d_a):
        f_l_a = fuc1(0.5, 1, 1, l_a)
        f_d_a = fuc1(0, d_a, 0.5, 1)

        def func(c, ss):
            if(ss < 0.5):
                return (c**(d_min-(d_min-d_max)*2*ss))*f_d_a(ss)
            else:
                c = c**(l_min-(l_min-l_max)*2*(ss-0.5))
                c = 1-c
                c = c*f_l_a(ss)
                c = 1-c
                return c
        return func
    f = fuc(1.3**rate, 0.7**rate, 1.4**rate, 1.3**rate, 0.7**rate, 0.7**rate)
    v1 = np.array(lumin2d.illuminate(pic, (0, 1, 0.5), vn=vn,
                  gr=gr, func_newc=f)).astype(np.float32)
    v2 = np.array(lumin2d.illuminate(pic, (1, 0, 0.5), vn=vn,
                  gr=gr, func_newc=f)).astype(np.float32)
    v3 = np.array(lumin2d.illuminate(pic, (0, -1, 0.5), vn=vn,
                  gr=gr, func_newc=f)).astype(np.float32)
    v4 = np.array(lumin2d.illuminate(pic, (-1, 0, 0.5), vn=vn,
                  gr=gr, func_newc=f)).astype(np.float32)
    rets = []
    for i in range(10):
        a = i/10
        v = v1*(1-a)+v2*a
        rets.append(Image.fromarray(v.astype(np.uint8)))
    for i in range(10):
        a = i/10
        v = v2*(1-a)+v3*a
        rets.append(Image.fromarray(v.astype(np.uint8)))
    for i in range(10):
        a = i/10
        v = v3*(1-a)+v4*a
        rets.append(Image.fromarray(v.astype(np.uint8)))
    for i in range(10):
        a = i/10
        v = v4*(1-a)+v1*a
        rets.append(Image.fromarray(v.astype(np.uint8)))

    simple_send(ctx, make_gif(rets, fps=12, ss=7e4))


def cmd_fl_gif(ctx, rest):
    tmr = receiver_timer('花')

    def gcd(a, b, eps=1e-6):
        if(b < eps):
            return a
        else:
            return gcd(b, a % b)

    def lcm(a, b, eps=1e-6):
        return a*b/gcd(a, b)
    abc = [37, 53, 103, 10, 10, 10]
    for j, i in enumerate(rest.strip().split()):
        if(j < len(abc)):
            if(i.isnumeric() or (i[0] == '-' and i[1:].isnumeric())):
                abc[j] = int(i)
        else:
            break
    a, b, c, l1, l2, l3 = abc
    sm = l1+l2+l3
    le = 500/2.3
    l1, l2, l3 = [l1/sm*le, l2/sm*le, l3/sm*le]
    frame_num = 120
    _lcm = lcm(abs(a*b*360), lcm(abs(b*c*360), abs(c*a*360)))
    sctx = simple_ctx(ctx)
    rpics = sctx.get_rpics()
    if(rpics):
        im2 = Image.open(rpics[0])
    else:
        im2 = Image.open(plugins['plg_setu'].rand_img())
    cc = pic2pic.get_main_color(im2)
    if(cc[1]+cc[2]+cc[0] < 128*3):
        br = 1
        im1 = Image.new('RGB', (500, 500), (255, 255, 255))
    else:
        br = 0
        im1 = Image.new('RGB', (500, 500), (0,)*3)
    dr = ImageDraw.Draw(im1)
    im2 = pic2pic.imBanner(im2, (500, 500)).convert("RGB")

    steps = 30000

    mo = steps//frame_num
    frames = []
    center = point(255, 255)

    last = center+point.rarg(l1+l2+l3, 0)
    for i in range(steps+1):
        angle = _lcm/steps*i/180*math.pi
        p1 = center+point.rarg(l1, angle/b/c)
        p2 = p1+point.rarg(l2, angle/a/c)
        p3 = p2+point.rarg(l3, angle/a/b)
        x, y = p3.xy
        co = im2.getpixel((int(x), int(y)))
        dr.line([*last.xy, *p3.xy], fill=co)
        last = p3
        if(i//mo >= len(frames)):
            if(br):
                cpy = im1.copy()
                dr1 = ImageDraw.Draw(cpy)
                dr1.line([*center.xy, *p1.xy], fill=(177, 0, 0), width=2)
                dr1.line([*p2.xy, *p1.xy], fill=(0, 177, 0), width=2)
                dr1.line([*p2.xy, *p3.xy], fill=(0, 0, 177), width=2)
                frames.append(cpy)
            else:
                cpy = im1.copy()
                dr1 = ImageDraw.Draw(cpy)
                dr1.line([*center.xy, *p1.xy], fill=(255, 120, 120), width=2)
                dr1.line([*p2.xy, *p1.xy], fill=(120, 255, 120), width=2)
                dr1.line([*p2.xy, *p3.xy], fill=(120, 120, 255), width=2)
                frames.append(cpy)
    simple_send(ctx, im1)
    simple_send(ctx, make_gif(frames, fps=12, ss=5e6/frame_num))


@receiver
@threading_cnt('花')
@on_exception_send
@start_with(r'[!！/]花')
def cmd_fl(ctx, match, rest):
    tmr = receiver_timer('花')
    if(rest.strip()[:3] == 'gif'):
        cmd_fl_gif(ctx, rest.strip()[3:])
        tmr.finish()
        return

    def gcd(a, b, eps=1e-6):
        if(b < eps):
            return a
        else:
            return gcd(b, a % b)

    def lcm(a, b, eps=1e-6):
        return a*b/gcd(a, b)

    def az(a, b, c, step=10000, size=None, wid=None):
        if(size is None):
            size = 200
        if(wid is None):
            wid = 1
        le = size/8
        center = point(size/2, size/2)
        _lcm = lcm(abs(a*b*360), lcm(abs(b*c*360), abs(c*a*360)))
        ps = []
        for i in range(step+1):
            angle = _lcm/step*i/180*math.pi
            p1 = center+point.rarg(le, angle/b/c)
            p2 = p1+point.rarg(le, angle/a/c)
            p3 = p2+point.rarg(le, angle/a/b)
            ps.append(p3.xy)
        im = Image.new("L", (size, size), 255)
        dr = ImageDraw.Draw(im)
        dr.line(ps, fill=0, width=wid, joint="curve")
        # print(_lcm)
        return im
    abc = [37, 53, 103]
    for j, i in enumerate(rest.strip().split()):
        if(j < 3):
            if(i.isnumeric() or (i[0] == '-' and i[1:].isnumeric())):
                abc[j] = int(i)
        else:
            break
    a, b, c = abc
    imm = az(a, b, c, size=500, wid=1)

    sctx = simple_ctx(ctx)
    rpics = sctx.get_rpics()
    if(rpics):
        im2 = Image.open(rpics[0])
    else:
        im2 = Image.open(plugins['plg_setu'].rand_img())
    c = pic2pic.get_main_color(im2)
    if(c[1]+c[2]+c[0] < 128*3):
        im1 = Image.new('RGB', (500, 500), (255, 255, 255))
    else:
        im1 = Image.new('RGB', (500, 500), (0,)*3)
    im2 = pic2pic.imBanner(im2, (500, 500)).convert("RGB")
    im2.paste(im1, (0, 0), mask=imm)
    simple_send(ctx, im2)
    tmr.finish()


@receiver
@threading_cnt('旋转')
@on_exception_send
@start_with(r'[!！/]旋转')
def cmd_rotate(ctx):
    tmr = receiver_timer('旋转')
    sctx = simple_ctx(ctx)
    rpics = sctx.get_rpics()
    pic = rpics[0]
    if(pic[-3:] != 'gif'):
        pics = [Image.open(pic)]

        fps = 30
        fnum = 15
    else:
        pics = extract_gif.extract_gif(pic)
        fnum = len(pics)*2
        # fps=extract_gif.get_fps(pic)
        fps = int(fnum/0.8)
    pics = [_.convert("RGB") for _ in pics]
    rets = []
    bg = pic2pic.get_border_color(pics[0])
    def cuberoot(x): return abs(x**(1/3))*(x/abs(x)) if x != 0 else 0
    def fuc(i): return cuberoot(i-fnum/2)
    d = fuc(fnum)-fuc(0)
    d1 = -fuc(0)/d*360
    def fuc1(i): return cuberoot(i-fnum/2)/d*1080+d1
    for i in range(fnum):
        p = pics[i % len(pics)]
        # print(fuc1(i))
        rets.append(p.rotate(fuc1(i), fillcolor=bg))
    simple_send(ctx, make_gif(rets, fps=fps, ss=7e4))


@receiver
@threading_cnt('pet')
@on_exception_send
@start_with(r'[!！/]pet|[!！/]摸摸')
def cmd_pet(ctx, match, rest):
    pth = path.join(mainpth, 'static_pics', 'pet')

    def pet(img, pth=pth, size=720, ss=5e6, high_frame_rate=False):
        img = img.convert("RGBA")
        imgs = [Image.open(_).resize((size, size))
                for _ in glob(path.join(pth, '*.png'))]
        if(high_frame_rate):
            imgs = [imgs[_//2] for _ in range(len(imgs)*2)]
            fps = 24
        else:
            fps = 12
        _ = min(img.size)
        img = img.crop((0, 0, _, _))
        # lucenter_ratio=0.15
        move_len_y = 0.06*size
        move_len_x = 0.02*size
        # center_ratio=(1+lucenter_ratio+move_ratio)/2
        center = point(size*0.65, size*0.8)
        lucenter = point(size*0.15, size*0.17)
        _ = lucenter.x+move_len_x
        w_ratio = (size-_)/(center.x-_)
        _ = lucenter.y+move_len_y
        h_ratio = (size-_)/(center.y-_)

        frame_num = len(imgs)
        rets = []
        for i in range(frame_num):
            angle = math.pi*2/frame_num*i-math.pi*0.6
            delta = point.rarg(1, angle)
            delta = point(delta.x*move_len_x, delta.y*move_len_y)
            lu = lucenter+delta
            le, up = [int(_) for _ in lu.xy]
            #w,h=[int(_*2) for _ in (center-lu).xy]
            w = int(w_ratio*(center-lu).x)
            h = int(h_ratio*(center-lu).y)
            ret = Image.new("RGBA", (size, size), (255,)*4)
            ret.paste(img.resize((w, h)), box=(le, up))
            ret.paste(imgs[i], (0, 0), imgs[i])
            rets.append(ret)
        return make_gif(rets, fps=fps, ss=ss/frame_num)

    rpics = simple_ctx(ctx).get_rpics()
    pic = rpics[0]
    pic = Image.open(pic)
    simple_send(ctx, pet(pic, high_frame_rate=bool(rest.strip())))


@receiver
@threading_cnt('font')
@on_exception_send
def cmd_font(ctx):
    sctx = simple_ctx(ctx)
    text = sctx.text
    splited = text.split()
    if(len(splited) < 2):
        return
    font, text = splited[0], ' '.join(splited[1:])
    _ = glob(path.join(mainpth, 'ttfs', '*%s*' % font))
    if(not _):
        #    print(no font)
        return
    fnt = list(_)[0]
    #from pic2pic import txt2im_ml
    p = txt2im_ml(text, font=fnt, width=512, fixedHeight=36,
                  trim_width=True, bg=(255,)*4)
    simple_send(ctx, p)


@receiver
@threading_cnt('fnt_list')
@on_exception_send
@start_with(r'字体列表')
def cmd_font_list(ctx):
    pics = []
    from os.path import basename, splitext
    for i in glob(path.join(mainpth, 'ttfs', '*')):
        name = splitext(basename(i))[0]
        p = txt2im(name, font=i, bg=(255,)*4)
        pics.append(p)
    mat = pic2pic.picMatrix(pics, column_num=1)
    simple_send(ctx, mat)


@receiver
@threading_cnt('扭曲gif')
@on_exception_send
@start_with(r'[/!！]?扭曲gif')
def cmd_bend_gif(ctx):
    sctx = simple_ctx(ctx)
    rpics = sctx.get_rpics()
    if(rpics is None):
        simple_send(ctx, '你没有发图片耶')
        return
    rpic = rpics[0]
    if(rpic[-3:] == 'gif'):
        frames = extract_gif.extract_gif(rpic)
        fps = extract_gif.get_fps(rpic)
    else:
        frames = [Image.open(rpic)]*30
        fps = 18
    framenum = len(frames)
    frames = [pic2pic.im_sizeSquareSize(
        im, 2e6/min(framenum, 200)) for im in frames]
    if(framenum > 200):
        rate = framenum/200
        frames = [frames[int(i*rate)] for i in range(200)]
        fps = fps/rate
        framenum = 200
    sin = math.sin
    _2pi = math.pi*2

    width, height = frames[0].size
    ret = []
    def ft(t): return sin(t*_2pi*3)

    def fyt(y, t): return (ft(t)-0.5)*(y-height/2)/12 + \
        width/9*sin(ft(t)*_2pi+y/height*(4+ft(t)))

    def get(im, x, y):
        return im.getpixel((int(x) % width, int(y) % height))
    for f in range(framenum):
        #print('    ln734',f)
        im = Image.new("RGB", (width, height))
        for x in range(width):
            for y in range(height):
                _x = x+fyt(y, f/framenum)
                im.putpixel((x, y), get(frames[f], _x, y))
        ret.append(im)
    simple_send(ctx, make_gif(ret, ss=2e6/framenum, fps=int(fps)))


@receiver
@threading_run
@on_exception_send
@start_with('[!！/]?印象分型')
def cmd_az(ctx):
    sctx = simple_ctx(ctx)
    from myGeometry import point
    from myMesh import mesh as Mesh
    from PIL import Image
    from random import random as rnd
    from random import shuffle
    from pic2pic import kmeans
    rpic = sctx.get_rpics()
    if(rpic):
        rpic = rpic[0]
    else:
        simple_send(ctx, '您没有发送图片')
    im = Image.open(rpic).convert("RGB")
    im_new = Image.new(im.mode, im.size)

    def get(im, x, y):
        return im.getpixel((int(x) % im.size[0], int(y) % im.size[1]))
    width, height = im.size
    colors = []
    points = []
    points.append(point(0, 0))
    points.append(point(0, height-1))
    points.append(point(width-1, 0))
    points.append(point(width-1, height-1))
    for i in range(50):
        points.append(point(width*rnd(), height*rnd()))
        colors.append(get(im, width*rnd(), height*rnd()))
    colors, gn = kmeans(colors, 7)
    mesh = Mesh.generate_mesh_by_points1(points)
    for abc, xy in mesh.get_tri_integral_point().items():
        A, B, C = abc
        A, B, C = mesh.points[A], mesh.points[B], mesh.points[C]
        ctr = (A+B+C)/3
        shuffle(colors)
        c = colors[1]+rnd()*(colors[0]-colors[1])
        c = int(c[0]), int(c[1]), int(c[2])
        for x, y in xy:
            im_new.putpixel((x, y), c)
    simple_send(ctx, im_new)


@receiver_nlazy
@threading_run
@on_exception_send
@start_with('[!！/]二维码')
def cmd_makeqr(ctx, match, rest):
    import myqr
    rest = rest.strip()
    if(not rest):
        rest = 'https://b23.tv/BV1GJ411x7h7'
    qr = myqr.make(rest).convert("RGB")
    sctx = simple_ctx(ctx)
    if(sctx.get_rpics()):
        bg = sctx.get_rpics()[0]
    elif('plg_setu' in plugins):
        bg = plugins['plg_setu'].rand_img(ctx)
    else:
        simple_send(ctx, qr)
        return
    bg = Image.open(bg)
    bg = pic2pic.imBanner(bg, qr.size).convert("RGB")
    bsiz = myqr.boxsiz
    w, h = qr.size
    def inb(x, y, le, ri, up, lo): return (le <= x <= ri) and (up <= y <= lo)
    dots = 0.2
    for x in range(w):
        for y in range(h):
            if(inb(x, y, 0, bsiz*8, 0, bsiz*8) or
               inb(x, y, 0, bsiz*8, h-1-bsiz*8, h-1) or
               inb(x, y, w-bsiz*8-1, w-1, 0, bsiz*8) or
               inb(x, y, w-1-bsiz*9, w-1-bsiz*4, h-1-bsiz*9, h-1-bsiz*4)):
                bg.putpixel((x, y), qr.getpixel((x, y)))
                continue
            xx = (x % bsiz)/bsiz
            yy = (y % bsiz)/bsiz
            if((1-dots)/2 <= xx <= (1+dots)/2 and
               (1-dots)/2 <= yy <= (1+dots)/2):
                bg.putpixel((x, y), qr.getpixel((x, y)))
    simple_send(ctx, bg)


qunpintu = dict()


@receiver
@threading_run
@on_exception_send
@start_with('[!！/]群拼图')
def cmd_grou_pintu(ctx, match, rest):
    # print('ln866')
    sctx = simple_ctx(ctx)
    gid = sctx.group_id
    if(rest):
        if(gid not in qunpintu):
            simple_send(ctx, '生成一下群拼图再查自己在哪吧！')
            return
        info = qunpintu[gid]
        uid = int(sctx.user_id)
        img = info['img']
        w, h = img.size
        x, y = info[uid]
        siz = info['siz']

        rng = int((info['area']**0.5)*0.3)
        le = max((x-rng)*siz, 0)
        ri = min((x+rng+1)*siz, w)-1
        up = max((y-rng)*siz, 0)
        lo = min((y+rng+1)*siz, h)-1
        simple_send(ctx, img.crop((le, up, ri, lo)))
        return
    from bot_backend import _bot
    from bot_backend import lcg_l as getter
    from annoy import AnnoyIndex
    from pic_indexing_RGB_img2vecs import img2vec_rgb
    import numpy as np
    if(sctx.get_rpics()):
        bg = Image.open(sctx.get_rpics()[0]).convert("RGB")
    else:
        bg = getter.get_image(r'http://p.qlogo.cn/gh/%s/%s/0' %
                              (gid, gid)).convert("RGB")
    memblist = _bot.sync.get_group_member_list(
        self_id=int(sctx.self_id), group_id=int(sctx.group_id))
    imgs = []
    uids = []
    siz = 20
    index = AnnoyIndex(siz*siz*3, 'euclidean')
    for i in memblist:
        # print('ln901')
        uid = i['user_id']
        uids.append(int(uid))
        url = r'http://q.qlogo.cn/g?b=qq&s=640&nk=%s' % uid
        imgs.append(lcg_l.get_image(url).convert("RGB"))
        index.add_item(len(imgs)-1, img2vec_rgb(imgs[-1], siz))
    index.build(2)
    le = len(memblist)
    grid_w, grid_h = bg.size
    rate = (max(le*12, 100)/grid_w/grid_h)**0.5
    grid_w, grid_h = int(grid_w*rate+1), int(grid_h*rate+1)
    ret = Image.new("RGB", (grid_w*siz, grid_h*siz))
    bg = bg.resize(ret.size)
    arr = np.asarray(bg).swapaxes(0, 1)
    visited = dict()
    index1 = AnnoyIndex(siz*siz*3, 'euclidean')
    for x in range(grid_w):
        for y in range(grid_h):
            vec = img2vec_rgb(arr[x*siz:(x+1)*siz, y*siz:(y+1)*siz], siz)
            index1.add_item(x*grid_h+y, vec)
            # print((x*grid_h+y)/(grid_w*grid_h-1))
            idx = index.get_nns_by_vector(vec, 4)
            idx = min(idx, key=lambda x: visited.get(x, 0))
            ret.paste(imgs[idx].resize((siz, siz)), (x*siz, y*siz))
            visited[idx] = visited.get(idx, 0)+1
    index1.build(2)
    visited1 = dict()
    info = dict()
    for idx, i in enumerate(imgs):
        vec = img2vec_rgb(i, siz)
        j = 1
        while(True):
            idx1 = index1.get_nns_by_vector(vec, j)[-1]
            if(idx1 not in visited1):
                break
            j += 1
            if(j >= grid_w*grid_h):
                print('ln939')
                break
        x, y = idx1//grid_h, idx1 % grid_h
        ret.paste(i.resize((siz, siz)), (x*siz, y*siz))
        visited1[idx1] = uids[idx]
        info[uids[idx]] = (x, y)
        '''if(uids[idx]==int(sctx.user_id)):
            simple_send(ctx,[str((x,y)),i])'''
    ret = Image.blend(ret, bg, 0.1)
    info['img'] = ret
    info['siz'] = siz
    info['grid_h'] = grid_h
    info['area'] = grid_h*grid_w
    # info['visited1']=visited1
    qunpintu[gid] = info
    simple_send(ctx, ret, im_size_limit=3 << 20)
    index.unload()
    index1.unload()


@receiver
@on_exception_send
@start_with("[!！/]响指")
def cmd_xiaosan1(ctx):
    import random
    import math
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    sctx = simple_ctx(ctx)
    pic = sctx.get_rpics()[0]

    im = Image.open(pic).convert("RGB")
    # im_arr = np.asarray(im)
    rnd = random.random
    w, h = im.size
    colors = list()
    dotnum = 6000
    for x in range(w):
        for y in [0, h-1]:
            colors.append(im.getpixel((x, y)))

    for y in range(h):
        for x in [0, w-1]:
            colors.append(im.getpixel((x, y)))

    def arr2color(arr):
        return tuple([int(i) for i in arr])
    bg_color = np.mean(colors, axis=0)
    bg_color = arr2color(bg_color)

    color = list()
    velocity = list()
    location = list()
    frame_num = 40
    dots = 8000
    dotsize = max(w*h/dots/10,1)
    for i in range(dots):
        x, y = random.randrange(w), random.randrange(h)
        color.append(im.getpixel((x, y)))
        speed = random.random()+1
        angle = (random.random()-0.5)*40/180*math.pi
        velocity.append(
            np.array([math.cos(angle)*speed, math.sin(angle)*speed]))
        location.append(np.array([x, y]))
    frames = []
    for f in range(frame_num):
        frame = Image.new("RGBA", (w, h), bg_color)
        rate = f/frame_num*1.2
        rate2 = rate*rate
        left = int(rate*w)
        tmp = int((1-rate**0.5)*255)
        if(0<tmp and tmp<256):
            frame.paste(im, mask = Image.new("L",(w, h), tmp))
        if(left < w):
            tmp = im.crop((left, 0, w, h))
            frame.paste(tmp, (left, 0))
            
        dot_frame = Image.new("RGBA", (w, h), bg_color+(0,))
        dr = ImageDraw.Draw(dot_frame)
        for i in range(dots):
            loc = location[i]
            vec = velocity[i]
            col = color[i]
            loc = vec*(w, h)*rate2*1.2 + loc
            ll = loc - (dotsize, dotsize)
            ur = loc + (dotsize, dotsize)
            dr.ellipse([*ll,*ur],fill = col+(170, ))
        frame.alpha_composite(dot_frame)
        frames.append(frame.convert("RGB"))
    gif = make_gif(frames, fps = 18, ss=1e5)
    simple_send(ctx, gif)


@receiver
@threading_run
@start_with("/3d转")
def cmd_3drotate(ctx):
    from PIL import Image
    from mesh_deform import mesh_deform, point
    import math
    from pic2pic import squareSize
    im = Image.open(simple_ctx(ctx).get_rpics()[0])
    ss = 1e4
    im = squareSize(im, ss)
    w, h = im.size
    lu = [0,0]
    ru = [w-1,0]
    ll = [0,h-1]
    rl = [w-1,h-1]
    mid = [w/2,h/2]
    md = mesh_deform(im,qdpoints=[lu,ru,ll,rl,mid],mesh_cnt=0,ensure_corner=False)
    n_frames = 15
    frames = []
    print(md.points, md.mesh.edges)
    for i in range(n_frames):

        meow = i/n_frames*2*math.pi
        md.points[0] = point(w/2,0)+point(w/2*math.cos(meow),w/4*math.sin(meow))
        md.points[3] = point(w/2,0)+point(w/2*math.cos(meow+math.pi),w/4*math.sin(meow+math.pi))
        md.points[2] = point(w/2,h/2)
        md.points[1] = point(w/2,h)+point(w/2*math.cos(meow),-w/4*math.sin(meow))
        md.points[4] = point(w/2,h)+point(w/2*math.cos(meow+math.pi),-w/4*math.sin(meow+math.pi))
        for idx, p in enumerate(md.points):
            md.points[idx] = point(w/2,h/2)+(p-point(w/2,h/2))*0.85
        print(i/n_frames,md.points)
        im=md.render1()
        frames.append(im)
    mg = plugins['plg_facegen'].make_gif
    simple_send(ctx,mg(frames,fps=18,ss=ss))