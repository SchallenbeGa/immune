import tkinter as Tkinter
from PIL import Image, ImageTk

def update_image():
        global tkimg1
        tkimg1 = ImageTk.PhotoImage(Image.open('tweettest.png'))
        label.config( image = tkimg1)
        label.after(1000, update_image)
        print("Updated")
 
w = Tkinter.Tk()
im = Image.open('tweettest.png')
tkimg1 = ImageTk.PhotoImage(im)
label =  Tkinter.Label(w, image=tkimg1)
print("Loaded")
label.pack()
w.after(1000, update_image)
w.mainloop()