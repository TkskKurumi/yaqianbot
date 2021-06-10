import tensorflow.keras as keras
from tensorflow.keras.models import Sequential,load_model
from tensorflow.keras.layers import Dense,InputLayer,Dropout,Conv2D,MaxPooling2D,Flatten
from os import path
import os
from process_data import load_datas,img2input
import numpy as np
#import process_data
class predictor:
	def __init__(self,pth,img_siz):
		self.model=load_model(pth)
		self.img_siz=img_siz
	def predict(self,img):
		x=img2input(img,img_siz=self.img_siz,flatten=False)
		return self.model.predict(x=np.array([x]))[0]
	def default():
		return predictor(path.join(path.dirname(__file__),'95.22.h5'),72)
if(__name__=='__main__'):
	predictor.default().model.summary()
	exit()
	pd=predictor(r"C:\Users\TkskKurumi\learnkeras\6912_conv6,3,3_conv6,3,3_mp2,2_conv6,3,3_mp2,2_adagrad0.005\79.18.h5",48)
	print(pd.predict(r"C:\Users\TkskKurumi\learnkeras\datas\pos\$2S8$PUP6PBO35K3J~8({(H.jpg"))
	print(pd.predict(r"C:\Users\TkskKurumi\learnkeras\datas\pos\4d7e.jpg"))
	print(pd.predict(r"C:\Users\TkskKurumi\learnkeras\datas\neg\$)59$SKM3_LDF}VZD~M1NR2.gif"))
	print(pd.predict(r"C:\Users\TkskKurumi\learnkeras\datas\neg\$@($}MCTOFUMY}TWDFUXDU9.jpg"))