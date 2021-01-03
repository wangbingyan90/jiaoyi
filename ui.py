import tkinter
from tkinter import messagebox
class Login(object): 
 def __init__(self): 
  
  # 创建主窗口,用于容纳其它组件 
  self.root = tkinter.Tk() 
  # 给主窗口设置标题内容 
  self.root.geometry('500x900') 
  self.b1=tkinter.Button(self.root, text="置顶", command=self.switch)
  self.run = tkinter.Button(self.root, text='启动',command = lambda : self.runf()) 
  self.sa = tkinter.Scale(self.root,label='透明度',   #设置显示的标签
      from_=0.4,to=1,  		# 设置最大最小值
      #注意设置最大值的属性不是'from'，而是'from_'，这是因为python中已经有了from关键字啦
      resolution=0.1,  		# 设置步距值
      orient=tkinter.HORIZONTAL,  	# 设置水平方向
      #如果我们想设置成垂直方向改怎么办呢？直接缺省这个属性就可以啦，默认就是垂直哒
      command=self.setalpha
      ).pack()
  self.bt = False



  self.sharee1 = tkinter.Entry(self.root) 
  self.shareb1 = tkinter.Button(self.root, text='买',command = lambda : self.buy(self.sharee1.get())) 
  self.shares1 = tkinter.Button(self.root, text='卖',command = lambda : self.sel(self.sharee1.get())) 

  self.sharee2 = tkinter.Entry(self.root) 
  self.shares2 = tkinter.Button(self.root, text='卖',command = lambda : self.sel(self.sharee2.get()))
  self.shareb2 = tkinter.Button(self.root, text='买',command = lambda : self.buy(self.sharee2.get())) 


  self.sharee3 = tkinter.Entry(self.root) 
  self.shareb3 = tkinter.Button(self.root, text='买',command = lambda : self.buy(self.sharee3.get())) 
  self.shares3 = tkinter.Button(self.root, text='卖',command = lambda : self.sel(self.sharee3.get())) 

  self.sharee4 = tkinter.Entry(self.root) 
  self.shares4 = tkinter.Button(self.root, text='卖',command = lambda : self.sel(self.sharee4.get()))
  self.shareb4 = tkinter.Button(self.root, text='买',command = lambda : self.buy(self.sharee4.get())) 




 def setalpha(self,text):
    self.root.attributes("-alpha",text)

 def switch(self):
  self.bt = not self.bt
  if self.bt:
    self.b1['text'] = "取消置顶"
  else:
    self.b1['text'] = "置顶"
  
  self.root.wm_attributes('-topmost',self.bt)

  # 完成布局 
 def gui_arrang(self): 
  

  self.run.place(x=100, y= 20)
  self.b1.place(x=20, y= 20)
  # self.sa.place(x=190, y= 20)

  
  self.shareb1.place(x=20,  y= 70)
  self.shares1.place(x=350, y=70) 
  self.sharee1.place(x=70,  y=70,height=30, width=90) 
  self.shareb2.place(x=20,  y=120)
  self.shares2.place(x=350, y=120) 
  self.sharee2.place(x=70,  y=120,height=30, width=90) 
  self.shareb3.place(x=20,  y=170)
  self.shares3.place(x=350, y=170) 
  self.sharee3.place(x=70,  y=170,height=30, width=90) 
  self.shareb4.place(x=20,  y=220)
  self.shares4.place(x=350, y=220) 
  self.sharee4.place(x=70,  y=220,height=30, width=90) 

 
 def runf(self):
  # self.c = text.getUser()
  self.switch()

 # 进入注册界面 
 def buy(self,x):
  # self.c.buy(x,x,x) 
  print(x)


 def sel(self,x): 
  print(x)
  # self.c.sell(x,x,x) 

def main(): 
 # 初始化对象 
 L = Login() 
 # 进行布局 
 L.gui_arrang() 
 # 主程序执行 
 tkinter.mainloop() 
if __name__ == '__main__': 
 main()