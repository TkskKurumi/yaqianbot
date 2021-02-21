from os import path
from PIL import Image
from glob import glob
import pic2pic,myio
pth=path.dirname(__file__)

def select_W_H(size):
	WS=[]
	HS=[]
	answers=[]
	rat=size[0]/size[1]
	for i in glob(path.join(pth,'W_*.json')):
		WS.append(int(path.basename(i)[2:-5]))
	for i in glob(path.join(pth,'H_*.json')):
		HS.append(int(path.basename(i)[2:-5]))
	for i in WS:
		for j in HS:
			rat1=i/j
			if(rat1>rat):
				answers.append((rat/rat1,i,j))
			else:
				answers.append((rat1/rat,i,j))
	return max(answers)[1:]
def enc(img,W,H):
	im=pic2pic.imBanner(img,(W,H)).convert("RGB")
	imnew=Image.new("RGB",(W,H))
	map_x=myio.loadjson(path.join(pth,"W_%d.json"%W))
	map_y=myio.loadjson(path.join(pth,"H_%d.json"%H))
	for i in range(W):
		for j in range(H):
			pix=im.getpixel((map_x[i],map_y[j]))
			imnew.putpixel((i,j),pix)
	return imnew
if(__name__=="__main__"):
	im=Image.open(r"D:\pyxyv\indexing\pics\0xcc9530cf9694.png")
	W,H=select_W_H(im.size)
	enc(im,W,H).show()