from __future__ import print_function
from pytube import YouTube
from pprint import pprint

import Tkinter as tk
from Tkinter import *
 
class ExampleApp(tk.Frame):
    def __init__(self, master):
        self.yt = YouTube()
        
        # Initialize window using the parent's constructor
        tk.Frame.__init__(self,master,width=700,height=400)
        # Set the title
        self.master.title('PyTube: YouTube downloader')
 
        # This allows the size specification to take effect
        self.pack_propagate(0)
 
        # We'll use the flexible pack layout manager
        self.pack()

        # The recipient text entry control and its StringVar
        labelText=StringVar()
        labelText.set("Enter url ")
        labelDir=Label(self,textvariable=labelText, height=4)
        labelDir.grid(row=0)
        #labelDir.pack(side="left")
        #labelDir.pack();

        self.url=StringVar()
        self.urlname=Entry(self,textvariable=self.url,width=50)
        self.urlname.grid(row=0,column=1)
        #urlname.pack()
        #Fetch button
        self.fetch_button = tk.Button(self,text='Fetch',command=self.fetch_list).grid(row=1,column=0)

        #menu
        self.om_variable = tk.StringVar(self)
        self.om = OptionMenu(self, self.om_variable, ['select'])
        self.om.grid(row=2,column=0)
        self.om.configure(width=20)        
        
        #download
        self.download_button = tk.Button(self,text='Download',command=self.download).grid(row=2,column=1)

    def download(self):
        v = self.om_variable.get()
        self.yt.videos[0].download('/home/dorado/')
        

    def fetch_list(self):
        self.yt.url = self.url.get()
        options = self.yt.videos
        menu = self.om['menu']
        menu.delete(0,'end')
        for string in options:
            menu.add_command(label=string,command=lambda value=string:self.om_variable.set(value))
        self.om_variable.set(options[0])

          
    def fill_options(self):
        menu = self.om['menu']
        menu.delete(0,'end')
        options = ["red","orange","green","blue"]
        for string in options:
            menu.add_command(label=string,command=lambda value=string:self.om_variable.set(value))
        self.om_variable.set(options[0])

    def print_out(self):
        ''' Print a greeting constructed
            from the selections made by
            the user. '''
        print('%s, %s!' % (self.greeting_var.get().title(),
                           self.recipient_var.get()))
    def run(self):
        ''' Run the app '''
        self.mainloop()
 
app = ExampleApp(tk.Tk())
app.run()
