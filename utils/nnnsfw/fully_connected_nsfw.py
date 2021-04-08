import tensorflow as tf
import tensorflow.contrib.layers as layers
from tensorflow.python import debug as tf_debug
from os import path
import numpy as np
import random
img_siz=25	#width=height=img_siz,RGB
n_input=img_siz*img_siz*3
n_hidden=n_input//6
n_classes=2	#sfw=0/nsfw=1


eta=0.001
max_epoch=10

pth=path.join(path.dirname(__file__),'multilayer_perceptron_nfsw','az')

def multilayer_perceptron(x):
	fc1=layers.fully_connected(x,n_hidden,activation_fn=tf.nn.relu,scope='fc1')
	tf.add_to_collection('fc1',fc1)
	
	#out=layers.fully_connected(fc1,n_classes,activation_fn=None,scope='out')
	#tf.add_to_collection('out',out)
	#return out
	
	fc2=layers.fully_connected(fc1,n_hidden,activation_fn=tf.nn.relu,scope='fc2')
	tf.add_to_collection('fc2',fc2)
	out=layers.fully_connected(fc2,n_classes,activation_fn=None,scope='out')
	tf.add_to_collection('out',out)
	#out=layers.fully_connected(fc1,n_classes,activation_fn=None,scope='out')
	return out

def img2input(img):
	from PIL import Image
	if(isinstance(img,str)):
		img=Image.open(img)
	img=img.resize((img_siz,img_siz),Image.LANCZOS).convert("RGB")
	return np.asarray(img).astype(np.float32).flatten()
def load_datas():
	from glob import glob
	poss=list(glob(r'M:\pic\colornsfw\pos\*'))
	negs=list(glob(r'M:\pic\colornsfw\neg\*'))
	xs=[]
	ys=[]
	#for i in random.sample(list(poss),40):
	for i in poss:
		xs.append(img2input(i))
		ys.append([0.0,1.0])
	#for i in random.sample(list(negs),40):
	for i in negs:
		xs.append(img2input(i))
		ys.append([1.0,0.0])
	az=list(range(len(xs)))
	random.shuffle(az)
	data=az[len(az)//5:]
	test=az[:len(az)//5]
	_xdata=[xs[i] for i in data]
	_ydata=[ys[i] for i in data]
	_xtest=[xs[i] for i in test]
	_ytest=[ys[i] for i in test]
	return _xdata,_ydata,_xtest,_ytest
x=tf.placeholder(tf.float32,[None,n_input],name='placeholder_x')
y=tf.placeholder(tf.float32,[None,n_classes],name='placeholder_y')
y_hat=multilayer_perceptron(x)
tf.add_to_collection('y_hat',y_hat)
# loss=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y_hat,labels=y))
loss=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=y_hat,labels=y))
train=tf.train.AdamOptimizer(learning_rate=eta).minimize(loss)
init=tf.global_variables_initializer()

with tf.Session() as sess:
	sess.run(init)
	xdata,ydata,xtest,ytest=load_datas()
	for epoch in range(114514):
		epoloss=0
		
		_,epoloss=sess.run([train,loss],feed_dict={x:xdata,y:ydata})
		correct_prediction=tf.equal(tf.argmax(y_hat,1),tf.argmax(y,1))
		accuracy=tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
		acc=accuracy.eval({x:xtest,y:ytest})
		#print("Accuracy%.3f"%(acc*100))
		print('epoch%d,loss=%.3f,acc=%d%%'%(epoch,epoloss,acc*100),end='\r')
		
		if((epoch+1)%150 == 0):
			saver = tf.train.Saver()
			saver.save(sess, pth)
			'''graph=tf.get_default_graph()
			out=graph.get_collection('out')
			test_img=img2input(r"M:\pic\colornsfw\pos\141.png")
			print('\n',sess.run(out,feed_dict={x:[test_img]}))'''