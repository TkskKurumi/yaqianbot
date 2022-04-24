from .paths import *
import os
base32_chrs = "01234567890abcdefghijklmnopqrstuvwxyz"


def shashi(s, length=24):
    ret = 0
    mask = (1 << length)-1
    for ch in s:
        i = ord(ch)
        ret = (ret << 7) ^ i
        ret = (ret & mask) ^ (ret >> length)
    return ret


def vhashi(v, length=24):
    ret = 0
    mask = (1 << length)-1
    for i in v:
        vi = int(i*1145141) % 256
        ret = (ret << 8) ^ vi
        ret = (ret & mask) ^ (ret >> length)
    return ret


def hashi(x, length=24):
    if(isinstance(x, str)):
        return shashi(x, length=length)
    elif(isinstance(x, list)):
        return vhashi(x, length=length)
    else:
        raise TypeError(type(x))


def base32(x, length=8):

    blength = length*5
    mask = (1 << blength)-1
    if(not isinstance(x, int)):
        x = hashi(x, length=blength)

    while(x >> blength):
        x = (x & mask) ^ (x >> blength)

    mask = 0b11111
    ret = []
    for i in range(length):
        ret.append(base32_chrs[x & mask])
        x >>= 5
    return ''.join(ret[::-1])


def ensure_dir(pth):
    if(not path.exists(path.dirname(pth))):
        os.makedirs(path.dirname(pth))


def savetext(filename, text):
    ensure_dir(filename)
    with open(filename, "w", encoding='utf-8') as f:
        f.write(text)
    return filename


def save_temp(text, ext=".html"):
    name = base32(text)+ext
    svpth = path.join(work_pth, name)
    savetext(svpth, text)
    return svpth
