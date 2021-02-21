from PIL import Image
import random,re,math
#,workpathmanager
import pic2pic,myio,mymath
from dataStruct import segmentTree_count_2d
from glob import glob
from mytimer import timer
#import bot_shufflestr
import jieba
from PIL import ImageFont
#bot_shufflestr里面给jieba加了一些mea相关的词，自行换成jieba（
'''
自己写的词云，虽然Python有现成的库，但是不知道为什么我电脑上装不了

挑选颜色计数的熵较小的区域，也就是颜色相对比较单一的区域优先放字

为了加速，用四叉树维护图片矩形区域内的颜色统计
当图片分辨率为M，查询/更新区域分辨率为N，颜色总数为X的时候
建树时间复杂度XMlogM
查询时间复杂度XlogN
更新时间复杂度NXlogN

为了加速，预先减少图片颜色数
'''
# jieba=bot_shufflestr.jieba

def color2hex(c):
	return c[2]*65536 + c[1]*256 +c[0]
def hexCountDict2countColor(count):	#将“dict[0xRRGGBB]=数量”这样储存的
	ret=[]							#字典转换为(数量,(R,G,B))
	for hex,cou in count.items():	#tuple组成的list
		col=hex2color(hex)
		ret.append((cou,col))
	return ret
def hexData2Im(data):
	width=len(data)
	height=len(data[0])
	data_=[]
	for i in range(width):
		data_.append([])
		for j in range(width):
			data_[i].append(hex2color(data[i][j]))
	return Image.fromarray(data_)
def countColor2avgColor(cc):		#平均颜色
	countSum=sum([i[0] for i in cc])
	channelSum=[sum([i[1][channel] * i[0] for i in cc]) for channel in range(3)]
	return [int(i/countSum) for i in channelSum]
def gencd(th_):
	th=pic2pic.colorDis((0,0,0),(th_,th_,th_))
	return th

def imHexData(im):
	width,height=tuple([im.size[i] for i in [0,1]])
	data=[[]for i in range(width)]
	imdata=im.load()			#图片转为hex颜色组成的矩阵
	for i in range(width):
		for j in range(height):
			data[i].append(color2hex(imdata[i,j]))
	return data
def hex2color(h):
	c=[]
	for i in range(3):
		c.append(h%256)			#0xRRGGBB转为(R,G,B)
		h=int(h/256)
	return c
def getNearestColor(c,colors,f_colorDis=pic2pic.colorDis):
	bestC=colors[0]
	bestD=f_colorDis(bestC,c)
	for i in colors[1:]:
		dis=f_colorDis(c,i)
		if(dis<bestD):
			bestD=dis
			bestC=i
	return bestC,bestD
def paletteIm(im,palette=None,paletteSize=67,paletteMinTh=gencd(8),f_colorDis=pic2pic.colorDis):#减少图片的颜色
	t1=timer()
	t1.settime()
	im1=im.copy()
	data=im1.load()
	width=im1.size[0]		
	height=im1.size[1]
	if(palette is None):
		palette=[]
		for t in range(paletteSize*2):
			if(len(palette)>=paletteSize):
				break
			i,j=random.randrange(0,width),random.randrange(0,height)
			c=data[i,j]
			if(palette):
				bc,d=getNearestColor(c,palette,f_colorDis=f_colorDis)
				if(d<paletteMinTh):
					continue
			palette.append(data[i,j])
	palettegetmem={}
	def paletteGet(c):
		h=color2hex(c)
		if(h in palettegetmem):
			return palettegetmem[h]
		bestC,bestD=getNearestColor(c,palette,f_colorDis=f_colorDis)
		palettegetmem[h]=bestC
		return bestC
	
	
	for i in range(width):
		#print(i/width)
		for j in range(height):
			bestC=paletteGet(data[i,j])
			im1.putpixel((i,j),bestC)
	print('palette image time',t1.gettime())
	#im1age.fromarray(data).show()
	
	# im1.save(r'J:\new\temp\Palette_%s.png'%(int(paletteMinTh)),'PNG')
	return im1
stop_words={',','.','<','>','，','。'}
def wordCloud(imMask,wordFrequencies=None,wordList=None,sizelimit=(567,567),wordMax=2048,bgcolor=pic2pic.colorWhite,stop_words=stop_words,vertical_posibility=0.1,random_rotate_posibility=0.05):
	imRet=pic2pic.im_sizelimitmin(Image.new('RGB',imMask.size,color=bgcolor),(1440,1440),rdeltamax=1.0)
	
	imMask_=pic2pic.im_sizelimitmax(imMask,sizelimit,rdeltamax=1.0)
	imMask_=paletteIm(imMask_)		#参考图片缩小为567x567以内，并且减少颜色
	data=imHexData(imMask_)			#但是输出图片仍然很大
	width,height=imMask_.size
	font=ImageFont.truetype('simhei.ttf',48)
	retRate=imRet.size[0]/imMask_.size[0]
	t1=timer()
	t1.settime()
	segTree=segmentTree_count_2d(data,width,height)
	print('线段树建树时间',t1.gettime())
	bgColorFilterTH=gencd(18)		#背景色不放东西
	t2=timer()
	if(not(wordFrequencies)and(wordList)):
		wordFrequencies={}
		for i in wordList:
			wordFrequencies[i]=wordFrequencies.get(i,0)+1
	def getWordsByFrequencyDict(wordFrequencies):
		#global wordFrequencies
	
		wordFrequencies=[(wordFrequencies[i],i)for i in wordFrequencies if not(i  in stop_words)]
		wordFrequencies.sort()
		wordFrequencies=wordFrequencies[::-1]
		if(len(wordFrequencies)>wordMax):
			wordFrequencies=wordFrequencies[:wordMax]
		wordNum=len(wordFrequencies)
		
		return wordFrequencies,wordNum
	def getWordsByFrequencyList(wordFrequencies):
		
	
		wordFrequencies=[(i[0],random.random(),i[-1])for i in wordFrequencies if not(i[-1] in stop_words)]
		wordFrequencies.sort()
		wordFrequencies=wordFrequencies[::-1]
		if(len(wordFrequencies)>wordMax):
			wordFrequencies=wordFrequencies[:wordMax]
		wordFrequencies=[(i[0],i[-1]) for i in wordFrequencies]
		wordNum=len(wordFrequencies)
		
		return wordFrequencies,wordNum
				
	def getWordSize(wordNum,wordFrequencies):
		wordSize=[]
		mode=0
		if(mode==0):
			for i in range(wordNum):
				ws=(100*wordNum)**((wordNum-i)/wordNum/3)
				maxRate=120		#最大的词是最小的词的120倍面积
				exp=0.67		#基本上是反比例，在来个指数
				ws=1/(i/wordNum+1/(maxRate**(1/exp)))
				wordSize.append(ws**exp)
		else:
			x=0.03
			b=1/wordNum
			r=100
			steps=15
			stepr=0.5**(1/steps)
			for i in range(wordNum):
				wordSize.append(r*x)
				r-=r*x
				x=(x**0.94)*(b**0.06)
				if((i+1)%(int(wordNum/steps))==0):
					x*=stepr
		totalTextSize=width*height
		print("图片大小",totalTextSize)
		for colorHex,count in segTree.count.items():
			color=hex2color(colorHex)
			if(pic2pic.colorDis(color,bgcolor)<bgColorFilterTH):
				totalTextSize-=count	#减去接近背景色的面积
		wordSizeSum=sum(wordSize)
		totalTextSize*=1.2				#留出一定空白，不然可能塞不下
		print("图片非背景色大小",totalTextSize)
		for i in range(wordNum):
			wordSize[i]*=totalTextSize/wordSizeSum	#词的面积
		return wordSize
	if(isinstance(wordFrequencies,dict)):
		wordFrequencies,wordNum=getWordsByFrequencyDict(wordFrequencies)
	elif(isinstance(wordFrequencies,list)):
		wordFrequencies,wordNum=getWordsByFrequencyList(wordFrequencies)
	wordSize=getWordSize(wordNum,wordFrequencies)
	print(wordFrequencies[:10])
	print(wordFrequencies[-10:])
	maxSize=wordSize[0]
	minSize=wordSize[-1]
	print('minSize',minSize)
	print('maxSize',maxSize)
	print('wordNum',wordNum)			#先放大字再放小字
	minEnum=35							#小字多随机位置，否则已经塞了很多字了要找不到了
	maxEnum=1/((wordNum/800)**0.4)+3	#大字少几次随机
	print('minEnum',minEnum,'maxEnum',maxEnum)	#又是拍脑袋定的玄学
	getEnumTime=lambda x:int((minEnum*(maxSize-x)+maxEnum*(x-minSize))/(maxSize+minSize))
	ents=[]			#记录每次的熵，用于最后统计平均的熵，评判颜色纯不纯
	buxing=0
	'''for i in range(5):
		print(wordSize[i],wordFrequencies[i])'''
	for i in range(wordNum):
		t2.settime()
		wsize=wordSize[i]
		if((wsize*retRate*retRate)<130):#字太小就不放了
			print('文字太小了',i)
			break
		if(wsize<16):
			print('参考图太小了',i)
			break
		
		word=wordFrequencies[i][1]
		if(random.random()<vertical_posibility):
			if(random.random()<0.5):
				rotate=90
			else:
				rotate=-90
		elif(random.random()<random_rotate_posibility):
			rotate=int(random.random()*360)
		else:
			rotate=0
		wordPic=pic2pic.txt2im(word,fill=pic2pic.colorBlackA,bg=pic2pic.colorWhiteA,font=font).convert('RGB')
		wordPic=pic2pic.im_sizeSquareSize(wordPic,wsize)
		if(rotate):
			wordPic=wordPic.rotate(rotate,expand=True,fillcolor=(255,255,255))
		wwidth,wheight=wordPic.size
		enumTime=getEnumTime(wsize)
		
		bestX,bestY,bestEnt,bestColor=-1,-1,-1,None
		for t in range(enumTime):
			x,y=random.randrange(0,width-wwidth),random.randrange(0,height-wheight)
			#ent=segTree.queryEnt(wwidth,wheight,x,y)
			count=segTree.query(wwidth,wheight,x,y)	#查询颜色统计
			cc=hexCountDict2countColor(count)
			ent=mymath.calcEnt([i[0] for i in cc])	#计算熵
			avg=countColor2avgColor(cc)
			if(pic2pic.colorDis(avg,bgcolor)<bgColorFilterTH):
				#print(x,y,wwidth,wheight,'is bgcolor,continue')
				continue
			if(-1 in count):						#在颜色统计里-1表示这里有字了
				#print(x,y,wwidth,wheight,'drawn,continue')
				continue
			if((ent<bestEnt)or(bestEnt==-1)):
				bestX,bestY,bestEnt=x,y,ent
				bestColor=avg
				if(bestEnt<1.18):
					break
		#print('枚举time',t2.gettime())
		if(bestEnt!=-1):
			x,y,color=bestX,bestY,bestColor
			ents.append(bestEnt)
			if(buxing>0):
				buxing-=1
			for dx in range(wwidth):
				for dy in range(wheight):
					c=wordPic.getpixel((dx,dy))
					if(pic2pic.colorDis(c,pic2pic.colorWhite)>bgColorFilterTH):
						data[bestX+dx][bestY+dy]=-1	#表示有字了
			
			color=tuple([int(i/1.3) for  i in color]+[255])	#调黑一点儿
			wsize_=(int(wwidth* retRate),int(wheight* retRate))
			wordPic=pic2pic.txt2im(word,fill=color,bg=pic2pic.colorWhiteA,font=font).convert('RGB')
			if(rotate):
				wordPic=wordPic.rotate(rotate,expand=True,fillcolor=(255,255,255))
			wordPic=wordPic.resize(wsize_,Image.LANCZOS)
			#wordPic.show()
			x_,y_=int(x*retRate),int(y*retRate)
			imRet.paste(wordPic,(x_,y_))
			segTree.update(wwidth,wheight,x,y)		#线段树更新数据
			#print(segTree.query(wwidth,wheight,x,y))
		else:
			buxing+=1
		#print(bestEnt,word,t2.gettime(),enumTime)
		if(buxing>12):
			print('没地方放了',i)
			break
	print('放图time',t1.gettime())
	print('平均的熵',sum(ents)/len(ents))
	return imRet
def randomMaskPic():
	pth=workpathmanager.pathManager(appname='setubot').getpath(session='mainpth')+r'\mea\wcBG'
	
	im=list(glob(pth+r"\*.jpg"))
	im+=list(glob(pth+r"\*.png"))
	#im=list(glob(r"J:\new\setubot\mea\wcBG\meap3(1).jpg"))
	
	im=random.choice(im)
	im=Image.open(im)
	return im
def wordText2wordFrequencies(text):
	wordList=jieba.lcut(text,HMM=True)
	wordFrequencies={}
	for i in wordList:
		wordFrequencies[i]=wordFrequencies.get(i,0)+1
	return wordFrequencies
def temp1():
	im=list(glob(r"J:\new\setubot\2018*\*.jpg"))
	im=random.choice(im)
	im=Image.open(im)
	
	im=pic2pic.im_sizelimitmax(im,(600,600))
	#im.show()
	imp=paletteIm(im)
	#imp.show()
	data=imHexData(imp)
	t1=timer()
	width,height=imp.size
	segmentTree=segmentTree_count_2d(data,imp.size[0],imp.size[1])
	
	print('segmentTree_build_time',t1.gettime())
	countColor=hexCountDict2countColor(segmentTree.count)
	avg=countColor2avgColor(countColor)
	print(countColor,avg)
	
	be=114
	samplenum=114
	samplenum_=20
	for t in range(samplenum):
		
		qwidth,qheight=random.randint(20,114),random.randint(20,114)
		x,y=random.randrange(width-qwidth),random.randrange(height-qheight)	
		
		#print(x,y,qwidth,qheight)
		#print('Count',segmentTree.query(qwidth,qheight,x,y))
		ent=segmentTree.queryEnt(qwidth,qheight,x,y)
		#print('Ent',ent)
		#print('Ent',ent)
		if(random.random()<(samplenum_/samplenum)):
			p=imp.crop((x,y,x+qwidth-1,y+qheight-1))
			p.save(r'J:\new\temp\ent=%s.png'%(str(ent)[:5],),'PNG')
		if(ent<be):
			# continue
			print(x,y,qwidth,qheight)
			print('Count',segmentTree.query(qwidth,qheight,x,y))
			print('Ent',ent)
			p=imp.crop((x,y,x+qwidth-1,y+qheight-1))
			#p.save(r'J:\new\temp\ent=%s.png'%(str(ent)[:5],),'PNG')
			be=ent
		
	
	print('segmentTree_query_time',t1.gettime())
	#input()
def test1():
	t=timer()
	stept=timer()
	im=randomMaskPic()
	im=Image.open(r"M:\pic\setubot\mea\wcBG\mea_.jpg")
	#im.show()
	words=myio.opentext(r"M:\pic\setubot\saves\message_record\Group580098100.log")
	words=re.sub(r'\n\d\d\d\d-\d\d-\d\d[\s\S]+?\n','',words)
	wordFrequencies=wordText2wordFrequencies(words)
	wordFrequencies['あくあ']=wordFrequencies['阿夸']
	wordFrequencies.pop('阿夸')
	wordFrequencies['YouTube']=wordFrequencies['油管']
	wordFrequencies['Meaqua']=wordFrequencies['Meaqua']*1.5
	wordFrequencies.pop('油管')
	
	
	'''wordFrequencies=[(random.random(),'你妈')for i in range(300)]
	wordFrequencies+=[(random.random(),'你妈的')for i in range(700)]
	wordFrequencies+=[(random.random(),'v3')for i in range(30)]
	
	wordFrequencies+=[(random.random(),'你妈的为什么')for i in range(100)]
	wordFrequencies+=[(random.random(),'为什么')for i in range(1000)]
	wordFrequencies=[(random.random()*0.8,c)for c in '你妈的为什么' for i in range(800)]
	wordFrequencies+=[(1+random.random(),c)for c in '你妈的为什么']'''
	stop_words=bot_shufflestr.stop_words
	stop_words['真名']=1
	
	stop_words['1']=1
	stop_words['8']=1
	a=wordCloud(im,wordFrequencies=wordFrequencies,wordMax=1200)
	a.show()
	a.save(r"M:\pic\temp\mywc.png")
	print(t.gettime())
def testLijie():
	t=timer()
	im=list(glob(r"J:\new\setubot\2018*\*.jpg"))
	#im=list(glob(r"J:\new\pic\mtr.jpg"))
	#im=list(glob(r"J:\new\pic\mea__.jpg"))
	im=list(glob(r"J:\new\setubot\mea\wcBG\*.jpg"))
	im+=list(glob(r"J:\new\setubot\mea\wcBG\*.png"))
	im=list(glob(r"J:\new\setubot\mea\wcBG\QQ图片20181230202743.jpg"))
	im=random.choice(im)
	im=Image.open(im)
	#im.show()
	words=[(i,'理解') for i in range(2000)]
	#words=re.sub(r'\n\d\d\d\d-\d\d-\d\d[\s\S]+?\n','',words)
	
	wordCloud(im,wordFrequencies=words,wordMax=2000).show()
	
def testGachiKimo():
	t=timer()
	im=r"C:\Users\78716\Downloads\Telegram Desktop\photo_2018-11-21_22-06-58.jpg"
	im=Image.open(im)
	words=[(random.random(),j) for i in range(500) for j in 'ガチキモ']
	a=wordCloud(im,wordFrequencies=words,wordMax=2048)
	a.save(r'd:\temp.png')
	print(t.gettime())
	
def colorDis1(s=1.5):
	def colorDis(a,b):
		temp=0
		for idx,a_ in enumerate(a):
			temp=temp+(abs(a_-b[idx]))**s
		return temp
	return colorDis
if(__name__=="__main__"):
	i=Image.open(r"C:\Users\TokisakiKurumi\Downloads\Telegram Desktop\mea.png")
	
	palette=[]
	for x,y in[(576,551),(501,646),(448,517),(932,495),(1115,398),(318,732),(594,695)]:
		palette.append(i.getpixel((x,y)))
	paletteIm(i,palette=palette,f_colorDis=colorDis1(s=1.2)).show()
	i1,g=__import__("christmas_hat").floodfill(Image.open(r"C:\Users\TokisakiKurumi\Downloads\Telegram Desktop\mea.png"),th=gencd(8))
	i=i.convert("RGB")
	i1.show()
	palette=[]
	for x,y in[(576,551),(501,646),(448,517),(932,495),(1115,398),(318,732),(594,695)]:
		palette.append(i.getpixel((x,y)))
	paletteIm(i1,palette=palette,f_colorDis=colorDis1(s=1.2)).show()