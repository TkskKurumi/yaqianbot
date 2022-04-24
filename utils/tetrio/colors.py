from PIL import ImageColor


class color:
    def fromany(x):
        if(isinstance(x, color)):
            return x
        elif(isinstance(x, tuple)):
            return color.RGBA(*x)
        else:
            raise Exception("Cannot convert %s to color" % x)

    def RGB(R, G, B):
        return color(R, G, B, 255)

    def HSV(H, S, V):
        RGB = HSV2RGB(H, S, V)
        return color(*RGB, 255)

    def RGBA(R, G, B, A):
        return color(R, G, B, A)

    def HSVA(H, S, V, A):
        RGBA = HSVA2RGBA(H, S, V, A)
        return color(*RGBA)

    def __init__(self, R=0, G=0, B=0, A=255):
        self.R = R
        self.G = G
        self.B = B
        self.A = A

    def astuple(self):
        return (int(self.R), int(self.G), int(self.B), int(self.A))

    def darken(self, rate=0.6):  # doesn't change self values when darken/lighten is called
        RGBA = darken(self.astuple(), rate=rate)
        return color(*RGBA)

    def lighten(self, rate=0.6):
        RGBA = lighten(self.astuple(), rate=rate)
        return color(*RGBA)
    brighten = lighten

    def alter(self, R=None, G=None, B=None, A=None):
        R = R or self.R
        G = G or self.G
        B = B or self.B
        A = A or self.A
        return color(R, G, B, A)

    def alterHSV(self, H=None, S=None, V=None, A=None):
        HH, SS, VV = RGB2HSV(self.R, self.G, self.B)
        H = H or HH
        S = S or SS
        V = V or VV
        A = A or self.A
        return color.HSVA(H, S, V, A)

    def __getattr__(self, name):

        H, S, V = RGB2HSV(self.R, self.G, self.B)
        if(name == 'H'):
            return H
        elif(name == 'S'):
            return S
        elif(name == 'V'):
            return V
        else:
            return AttributeError(name)

    def invert(self):
        R = 255-self.R
        G = 255-self.G
        B = 255-self.B
        return self.alter(R, G, B)

    def __str__(self):
        return str(self.astuple())

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return self.astuple().__iter__()

    def __getitem__(self, idx):
        if(idx in [0, 1, 2, 3]):
            return tuple(self)[idx]
        else:
            raise KeyError(idx)

    def __add__(self, other):
        if(isinstance(other, color)):
            ls = [i+other[idx] for idx, i in enumerate(self)]
            return color(*ls)
        else:
            return NotImplemented

    def __radd__(self, other):
        if(other == 0):
            return color(*self)
        else:
            return NotImplemented

    def __sub__(self, other):
        if(isinstance(other, color)):
            ls = [i-other[idx] for idx, i in enumerate(self)]
            return color(*ls)
        else:
            return NotImplemented

    def __mul__(self, other):
        if(isinstance(other, int) or isinstance(other, float)):
            return color(*[i*other for i in self])
        else:
            return NotImplemented

    def __truediv__(self, other):
        if(isinstance(other, int) or isinstance(other, float)):
            return color(*[i/other for i in self])
        else:
            return NotImplemented


def cat_alpha(RGB, A):
    RGBA = RGB+(A,)
    return RGBA


def HSV2RGB(H, S=None, V=None):
    if(isinstance(H, tuple)):
        H, S, V = H
    H = H % 360
    return ImageColor.getrgb('HSV(%d,%d%%,%d%%)' % (H, S, V))


def HSVA2RGBA(H, S=None, V=None, A=None):
    if(isinstance(H, tuple)):
        H, S, V, A = H
    return cat_alpha(HSV2RGB(H, S, V), A)


def RGB2HSV(r, g=None, b=None):
    if(isinstance(r, tuple)):
        r, g, b = r
    MAX = max([r, g, b])
    MIN = min([r, g, b])
    if(MAX == MIN):
        H = 0
    elif((MAX == r) and (g >= b)):
        H = 60*(g-b)/(MAX-MIN)
    elif((MAX == r) and (g < b)):
        H = 360-60*(b-g)/(MAX-MIN)
    elif(MAX == g):
        H = 120+60*(b-r)/(MAX-MIN)
    else:
        H = 240+60*(r-g)/(MAX-MIN)
    s = 1-MIN/MAX if MAX else 0
    v = MAX/255
    return (H, s*100, v*100)


def darken(RGBA, rate=0.5, *args):
    if(args):
        RGBA = (RGBA,)+args
    if(len(RGBA) == 4):
        R, G, B, A = RGBA
    else:
        R, G, B = RGBA
    H, S, V = RGB2HSV(R, G, B)
    V = V*(1-rate)
    S = S*(1-rate)+100*rate
    R, G, B = HSV2RGB(H, S, V)
    if(len(RGBA) == 4):
        return R, G, B, A
    else:
        return R, G, B


def lighten(RGBA, rate=0.5, *args):
    if(args):
        RGBA = (RGBA,)+args
    if(len(RGBA) == 4):
        R, G, B, A = RGBA
    else:
        R, G, B = RGBA
    H, S, V = RGB2HSV(R, G, B)
    V = V*(1-rate)+100*rate
    S = S*(1-rate)
    R, G, B = HSV2RGB(H, S, V)
    if(len(RGBA) == 4):
        return R, G, B, A
    else:
        return R, G, B


c_color_RED = color.HSV(0, 100, 100)
c_color_RED_half = c_color_RED.alter(A=128)
c_color_RED_lighten = c_color_RED.lighten()
c_color_RED_darken = c_color_RED.darken()

c_color_PINK = color.HSV(330, 55, 100)
c_color_PINK_half = c_color_PINK.alter(A=128)
c_color_PINK_lighten = c_color_PINK.lighten()
c_color_PINK_darken = c_color_PINK.darken()

c_color_GREEN = c_color_RED.alterHSV(H=120)
c_color_GREEN_half = c_color_RED_half.alterHSV(H=120)
c_color_GREEN_lighten = c_color_RED_lighten.alterHSV(H=120)
c_color_GREEN_darken = c_color_RED_darken.alterHSV(H=120)

c_color_BLUE = c_color_RED.alterHSV(H=240)
c_color_BLUE_half = c_color_RED_half.alterHSV(H=240)
c_color_BLUE_lighten = c_color_RED_lighten.alterHSV(H=240)
c_color_BLUE_darken = c_color_RED_darken.alterHSV(H=240)

c_color_MIKU = color.RGB(57, 197, 187)
c_color_MIKU_lighten = c_color_MIKU.lighten()
c_color_MIKU_darken = c_color_MIKU.darken()
c_color_MIKU_half = c_color_MIKU.alter(A=128)

c_color_TRANSPARENT = color(A=0)
c_color_WHITE = color(255, 255, 255, 255)
c_color_BLACK = color(0, 0, 0, 255)
if(__name__ == '__main__'):
    pass
