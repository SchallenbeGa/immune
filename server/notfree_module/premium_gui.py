from tkinter import *

class home:
    def __init__(self, win):
        self.lbl1=Label(win, text='PAIR')
        self.lbl2=Label(win, text='Stable')
        self.lbl3=Label(win, text='Margin')
        self.t1=Entry(bd=3)
        self.t2=Entry()
        self.t3=Entry()
        self.btn1 = Button(win, text='TRADE')
        self.lbl1.place(x=100, y=50)
        self.t1.place(x=200, y=50)
        self.b1=Button(win, text='lower', command=self.low_margin)
        self.b1.place(x=100, y=150)
        self.lbl3.place(x=100, y=200)
        self.t3.place(x=200, y=200)
    def low_margin(self):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=2*(num1/num2*3.2)
        self.t3.insert(END, str(result))
 
window=Tk()
homepage=home(window)
window.title('Home')
window.geometry("400x300+10+10")
window.mainloop()