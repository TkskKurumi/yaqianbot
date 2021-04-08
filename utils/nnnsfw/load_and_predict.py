import tensorflow as tf
import tensorflow.contrib.layers as layers
from tensorflow.python import debug as tf_debug
from os import path
import numpy as np
import random
img_siz=25	#width=height=img_siz,RGB
n_input=img_siz*img_siz*3
n_hidden=n_input//8
n_classes=2	#sfw=0/nsfw=1

def img2input(img):
	from PIL import Image
	if(isinstance(img,str)):
		img=Image.open(img)
	img=img.resize((img_siz,img_siz),Image.LANCZOS).convert("RGB")
	return np.asarray(img).astype(np.float32).flatten()
pth=path.join(path.dirname(__file__),'multilayer_perceptron_nfsw','az')


'''with tf.Session() as sess:
	saver=tf.train.import_meta_graph(pth+'.meta')
	saver.restore(sess,tf.train.latest_checkpoint(path.join(path.dirname(__file__),'multilayer_perceptron_nfsw')))
	graph=tf.get_default_graph()
	#print(graph.get_all_collection_keys())
	#print(graph.get_operations())
	#exit()
	#X=tf.placeholder(tf.float32,name='X')
	out=graph.get_collection('out')
	X=graph.get_tensor_by_name('placeholder_x:0')
	test_img0=img2input(r"M:\pic\colornsfw\pos\141.png")
	test_img1=img2input(r"M:\pic\colornsfw\pos\69.png")
	#print(out.eval({X:test_img}))
	#az=tf.argmax(out,2)
	az=tf.nn.softmax(out)
	print(sess.run(az,feed_dict={X:[test_img0,test_img1]}))
	print(sess.run(out,feed_dict={X:[test_img0,test_img1]}))'''


class predictor:
	def __init__(self):
		self.sess=tf.Session()
		saver=tf.train.import_meta_graph(pth+'.meta')
		saver.restore(self.sess,tf.train.latest_checkpoint(path.join(path.dirname(__file__),'multilayer_perceptron_nfsw')))
		graph=tf.get_default_graph()
		out=graph.get_collection('out')
		self.softmaxout=tf.nn.softmax(out[0])
		self.x=graph.get_tensor_by_name('placeholder_x:0')
	def predict(self,im):
		return self.sess.run(self.softmaxout,feed_dict={self.x:[img2input(im)]})[0] 
if(__name__=='__main__'):
	from glob import glob
	from pic2pic import fixWidth,pinterest,addTitle
	from PIL import Image
	import random
	pd=predictor()
	poss=list(glob(r'M:\pic\colornsfw\pos\*'))
	negs=list(glob(r'M:\pic\colornsfw\neg\*'))
	def redim(im):
		return Image.blend(im,Image.new("RGB",im.size,(255,0,0)),0.3)
	pos_im=[]
	neg_im=[]
	for i in random.sample(poss,20):
		az=Image.open(i)
		az=fixWidth(az,233).convert("RGB")
		buse,hso=pd.predict(az)
		if(hso>buse):
			pos_im.append(az)
		else:
			neg_im.append(redim(az))
	for i in random.sample(negs,20):
		az=Image.open(i)
		az=fixWidth(az,233).convert("RGB")
		buse,hso=pd.predict(az)
		if(hso>buse):
			pos_im.append(redim(az))
		else:
			neg_im.append(az)
	pinterest(pos_im,int(len(pos_im)**0.5)).show()
	pinterest(neg_im,int(len(neg_im)**0.5)).show()
	