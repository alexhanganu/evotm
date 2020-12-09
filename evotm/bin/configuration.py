from tkinter import Tk, Label, Button, Listbox, Checkbutton, W, IntVar, END, Entry, simpledialog
from . import database

class Configuration():

    def __init__(self):

        self.main = Tk()
        self.main.title("Configuration")

        Button(self.main, text='New tab', command=self.NewTab).grid(row=0, column=0)

        self.maindaily_listbox = Listbox(self.main, exportselection=0)
        self.maindaily_listbox.grid(row=1, column=0)
        self.ls = []
        self.d_tabs = database.get_tasks_for_table_('Tabs')
        for tab in self.d_tabs:
                self.maindaily_listbox.insert(END, tab)
        self.maindaily_listbox.config(width=20, height=len(self.d_tabs)+1)
        
        self.EntryTask = Entry(self.main)
        self.EntryTask.grid(row=2, column=0)
        self.EntryTask.insert(0, 'new name')

        Button(self.main, text="Rename", command=self.Rename).grid(row=3, column=0)
        Button(self.main, text="Delete", command=self.Delete).grid(row=4, column=0)

    def Rename(self):
        NewName = str(self.EntryTask.get())
        Tab2Update = self.maindaily_listbox.get(self.maindaily_listbox.curselection())

        if len(NewName)>0 and NewName != 'new name':
            for tab in self.d_tabs:
                if tab == Tab2Update:
                    database.__update_table__('Tabs','tab_id',NewName, 'tab_id',Tab2Update)
        self.main.destroy()

    def Delete(self):
        Tab2Delete = self.maindaily_listbox.get(self.maindaily_listbox.curselection())
        database.__delete_from_table__('Tabs',Tab2Delete,self.d_tabs[Tab2Delete])
        self.main.destroy()

    def NewTab(self):
        tab = simpledialog.askstring("askstring", "Enter New Tab")
        position_id = 0
        for tab in self.d_tabs:
            if int(self.d_tabs[tab]) > position_id:
                position_id = int(self.d_tabs[tab])
        database.__insert_in_table__('Tabs',tab, str(position_id+1))
        self.maindaily_listbox.insert(END, tab)
        self.maindaily_listbox.config(width=20, height=len(self.d_tabs)+1)

'''checkbutton is an alternative
'''
        # Label(self.main, text="Pick active tab:").grid(row=0, sticky=W)
        # self.var1 = IntVar()
        # Checkbutton(self.main, text="Job", variable=self.var1).grid(row=1, sticky=W)
        # self.var2 = IntVar()
        # Checkbutton(self.main, text="Personal", variable=self.var2).grid(row=2, sticky=W)
        # self.var3 = IntVar()
        # Checkbutton(self.main, text="Daily", variable=self.var3).grid(row=3, sticky=W)
        # Button(self.main, text='Show', command=self.var_states).grid(row=4, sticky=W, pady=4)

    # def var_states(self):
       # print("Job: %d,\nPersonal: %d, \nDaily: %d" % (self.var1.get(), self.var2.get(), self.var3.get()))
       # self.main.destroy()
