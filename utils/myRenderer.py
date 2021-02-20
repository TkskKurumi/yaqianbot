import pic2pic
from PIL import Image
import numpy as np
import copy
class renderer:
	type_txt=0
	type_img=1
	type_verticle=2
	type_horizontal=3
	type_txt_value=4
	
	border_type_absolute=0
	border_type_relative=1
	def __init__(self,type,border=None,contents_gap=0,bg=None,fill=(0,0,0),align_contents_size=False,contents=None,fixedHeight=None,align_contents_pos=None,align_pos_default=0):
		if(isinstance(type,str)):
			#print('exec type')
			self.type=eval("renderer.type_%s"%type)
		else:
			self.type=type
		#print(self.type)
		self.contents=contents or list()
		self.align_contents_size=align_contents_size
		self.align_pos_default=align_pos_default
		self.bg=bg
		self.fill=fill
		self.fixedHeight=fixedHeight
		self.border=border
		self.contents_gap=contents_gap
		self.align_contents_pos=align_contents_pos or {}
	def add_content(self,content):
		self.contents.append(content)
	def render(self,father_bg=None,father_fill=None):
		if(self.type==renderer.type_txt):
			t=self.contents[0]
			bg=self.bg or father_bg or (255,255,255,0)
			fill=self.fill or father_fill or (0,0,0,255)
			im=pic2pic.txt2im(t,bg=bg,fill=fill,fixedHeight=self.fixedHeight)
			if(self.contents_gap):
				im=add_border(im,{"color":bg,"type":renderer.border_type_absolute,"width":self.contents_gap})
			return add_border(im,self.border)
		elif(self.type==renderer.type_img):
			im=self.contents[0]
			if(self.contents_gap):
				im=add_border(im,{"color":bg,"type":renderer.border_type_absolute,"width":self.contents_gap})
			return add_border(im,self.border)
		elif(self.type == renderer.type_horizontal):
			cts=self.get_rendered_contents()
			gap=self.contents_gap
			if(self.align_contents_size):
				height=min([i.size[1] for i in cts])
				for idx,c in enumerate(cts):
					cts[idx]=pic2pic.fixHeight(c,height)
			height=max([i.size[1] for i in cts])+gap*2
			width=sum([i.size[0] for i in cts])+gap*(1+len(cts))
			bg=self.bg or (255,255,255,0)
			fill=self.fill or (0,0,0,255)
			ret=Image.new("RGBA",(width,height),bg)
			left=gap
			for idx,content in enumerate(cts):
				algn=self.align_contents_pos.get(idx,self.align_pos_default)
				top=gap+int(algn*(height-content.size[1]))
				ret.paste(content,(left,top))
				left+=content.size[0]
			ret=add_border(ret,self.border)
			return ret
		elif(self.type == renderer.type_verticle):
			cts=self.get_rendered_contents()
			gap=self.contents_gap
			if(self.align_contents_size):
				width=min([i.size[0] for i in cts])
				for idx,c in enumerate(cts):
					cts[idx]=pic2pic.fixWidth(c,width)
			width=max([i.size[0] for i in cts])+gap*2
			height=sum([i.size[1] for i in cts])+gap*(1+len(cts))
			bg=self.bg or (255,255,255,0)
			fill=self.fill or (0,0,0,255)
			ret=Image.new("RGBA",(width,height),bg)
			top=gap
			for idx,content in enumerate(cts):
				algn=self.align_contents_pos.get(idx,self.align_pos_default)
				left=gap+int(algn*(width-content.size[0]))
				ret.paste(content,(left,top))
				top+=content.size[1]+gap
			ret=add_border(ret,self.border)
			return ret
	def get_rendered_contents(self):
		cts=[]
		for i in self.contents:
			if(isinstance(i,renderer)):
				cts.append(i.render(father_bg=self.bg,father_fill=self.fill))
			elif(isinstance(i,str)):
				cts.append(renderer(type=renderer.type_txt,bg=self.bg,fill=self.fill,fixedHeight=self.fixedHeight).render())
			elif(isinstance(i,Image.Image)):
				cts.append(i)
		return cts
def add_border(im,border):
	if(not(border)):
		return im
	type=border.get('type',renderer.border_type_relative)
	if(type==renderer.border_type_relative):
		border_width=int(((im.size[0]*im.size[1])**0.5)*border.get('width',0.1))
	else:
		border_width=border.get('width',5)
	color=border.get("color",(0,0,0))
	ret=Image.new('RGBA',(im.size[0]+border_width*2,im.size[1]+border_width*2),color)
	ret.paste(im,(border_width,border_width))
	return ret
class json_renderer():
	def __init__(self,layout):
		self.layout=layout
	def render(self,contents):
		lyout=json_renderer.load_contents(self.layout,contents)
		return json_renderer.render_(lyout)
	def render_(lyout):
		if(isinstance(lyout,dict)):
			if(lyout['type']in[renderer.type_horizontal,renderer.type_verticle,'horizontal','verticle']):
				for idx,i in enumerate(lyout['contents']):
					if(isinstance(i,dict)):
						lyout['contents'][idx]=json_renderer.render_(i)
			return renderer(**lyout).render()
		else:
			return lyout
	def load_contents(layout,contents):
		lyout=copy.deepcopy(layout)
		if(isinstance(layout,dict)):
			
			for i,j in lyout.items():
				if(isinstance(j,str)):
					for i1,j1 in contents.items():
						if(j=="%"+i1+"%"):
							lyout[i]=k1
				elif(isinstance(j,dict) or isinstance(j,list)):
					lyout[i]=json_renderer.load_contents(j,contents)
			return lyout
		elif(isinstance(lyout,list)):
			for idx,i in enumerate(lyout):
				if(isinstance(i,str)):
					for i1,j1 in contents.items():
						if(i=="%"+i1+"%"):
							lyout[idx]=j1
				elif(isinstance(i,dict) or isinstance(i,list)):
					lyout[idx]=json_renderer.load_contents(i,contents)
			return lyout
		return lyout
if(__name__=="__main__"):
	bg_color=np.array([11,140,185])
	bg_color_dark=(bg_color/2.2).astype('int32')
	bg_color_bright=((bg_color+255*3)/4).astype('int32')
	#font_color1=((bg_color+255*6)/7).astype('int32')
	bg_color=tuple(bg_color)
	bg_color_dark=tuple(bg_color_dark)
	bg_color_bright=tuple(bg_color_bright)
	wtt=115
	r=renderer(type=renderer.type_txt,fill=bg_color_bright,bg=bg_color_dark,contents=["“手艺工坊”正繁忙，没时间给你做工艺品啦！请等待%.2f秒。"%wtt],contents_gap=3,fixedHeight=32,border={"width":5,"type":renderer.border_type_absolute,"color":bg_color_dark})
	r.render().show()