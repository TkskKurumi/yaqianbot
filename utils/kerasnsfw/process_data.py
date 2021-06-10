
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.layers import Dense
from os import path
import os
import random
import numpy as np
img_siz=48	#width=height=img_siz,RGB
n_input=img_siz*img_siz*3
n_hidden0=n_input//20
n_hidden1=int(n_hidden0/1.5)
n_classes=2	#sfw=0/nsfw=1
curpth=path.dirname(__file__)
def img2input(img,flatten=True,img_siz=img_siz):
    from PIL import Image
    if(isinstance(img,str)):
        img=Image.open(img)
    img=img.resize((img_siz,img_siz),Image.LANCZOS).convert("RGB")
    if(flatten):
        return np.asarray(img).astype(np.float32).flatten()
    else:
        return np.asarray(img).astype(np.float32)
def load_datas(**kwargs):
    from glob import glob
    poss=list(glob(path.join(curpth,'datas','pos','*')))
    negs=list(glob(path.join(curpth,'datas','neg','*')))
    xs=[]
    ys=[]
    for i in random.sample(list(poss),70):
    #for i in poss:
        xs.append(img2input(i,**kwargs))
        ys.append([0.0,1.0])
    for i in random.sample(list(negs),70):
    #for i in negs:
        xs.append(img2input(i,**kwargs))
        ys.append([1.0,0.0])
    az=list(range(len(xs)))
    random.shuffle(az)
    data=az[len(az)//3:]
    test=az[:len(az)//3]
    _xdata=np.array([xs[i] for i in data])
    _ydata=np.array([ys[i] for i in data])
    _xtest=np.array([xs[i] for i in test])
    _ytest=np.array([ys[i] for i in test])
    return _xdata,_ydata,_xtest,_ytest
