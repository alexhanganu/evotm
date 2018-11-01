from tkinter import Tk, ttk, Label, Button, Entry, Listbox, EXTENDED, END, simpledialog, StringVar, Menu
from os import listdir, rename, path
import time, re

from . import database

from . import tkSimpleDialog
MainDailyGroups = database.get_tasks_for_table_('MainDailyGroups')
Projects = database.get_tasks_for_table_('Projects')
Days_task_active = database.get_tasks_for_table_('Days_task_active')
MinDailyTaskDuration = database.get_tasks_for_table_('MinDailyTaskDuration')
Date_deadline = database.get_tasks_for_table_('Date_deadline')
PausedTasks = database.get_tasks_for_table_('PausedTasks')
MainDailyGroups_bg_color = database.get_tasks_for_table_('MainDailyGroups_bg_color')


class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        from . import ttkcalendar
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection

class HoverInfo(Menu):
    def __init__(self, parent, text, command=None):
       self._com = command
       Menu.__init__(self,parent, tearoff=0)
       if not isinstance(text, str):
          raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
       toktext=re.split('\n', text)
       for t in toktext:
          self.add_command(label = t)
          self._displayed=False
          self.master.bind("<Enter>",self.Display )
          self.master.bind("<Leave>",self.Remove )

    def __del__(self):
       self.master.unbind("<Enter>")
       self.master.unbind("<Leave>")

    def Display(self,event):
       if not self._displayed:
          self._displayed=True
          self.post(event.x_root, event.y_root)
       if self._com != None:
          self.master.unbind_all("<Return>")
          self.master.bind_all("<Return>", self.Click)

    def Remove(self, event):
     if self._displayed:
       self._displayed=False
       self.unpost()
     if self._com != None:
       self.unbind_all("<Return>")



class NewTask():
    def __init__(self):
        self.main = Tk()
        self.main.title("Add Task")

        ttk.Label(self.main, text='Main Daily Groups').grid(row=0, column=0)
        self.maindaily_listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.maindaily_listbox.grid(row=1, column=0)
        self.width = 5
        self.ls = []
        for project in MainDailyGroups:
            if project not in self.ls:
                self.ls.append(project)
        for item in self.ls:
            self.maindaily_listbox.insert(END, item)
            if len(item)>self.width:
                self.width = len(item)
        self.maindaily_listbox.config(width=self.width, height=len(self.ls))
        
        ttk.Label(self.main, text='Projects').grid(row=0, column=1)
        self.project_listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.project_listbox.grid(row=1, column=1)
        self.project_width = 5
        self.project_ls = []
        if len(Projects)>0:
            for project in Projects:
                if project not in self.project_ls:
                    self.project_ls.append(project)

            for item in self.project_ls:
                self.project_listbox.insert(END, item)
                if len(item)>self.project_width:
                    self.project_width = len(item)
        self.project_listbox.config(width=self.project_width, height=len(self.ls))

        self.EntryTask = Entry(self.main)
        self.EntryTask.grid(row=2, column=0)
        self.EntryTask.insert(0, 'task name')

        self.date_deadline = 'no date'
        ttk.Button(self.main, text="Set deadline", command=self.SetDate).grid(row=2, column=1)

        ttk.Button(self.main, text="Submit", command=self.select).grid(row=3, column=0)
        ttk.Button(self.main, text='New Project', command=self.NewProject).grid(row=3, column=1)

    def select(self):
        Task2Add = str(self.EntryTask.get())
        ls_selected_maindaily = list()
        ls_selected_projects = list()
        selected_maindaily = self.maindaily_listbox.curselection()
        selected_project = self.project_listbox.curselection()
        for i in selected_maindaily:
            entrada = self.maindaily_listbox.get(i)
            ls_selected_maindaily.append(entrada)
        for i in selected_project:
            entrada = self.project_listbox.get(i)
            ls_selected_projects.append(entrada)

        for maindailygroup in ls_selected_maindaily:
            database.__insert_in_table__('MainDailyGroups',maindailygroup, Task2Add)
        if len(ls_selected_projects)>0:
            for project in ls_selected_projects:
                database.__insert_in_table__('Projects',project, Task2Add)

        deadline = self.date_deadline
        if deadline != 'no date':
            print('adding deadline to db: ', deadline)
            database.__insert_in_table__('Date_deadline',Task2Add, deadline)
        self.main.destroy()

    def NewProject(self):
        project = simpledialog.askstring("askstring", "Enter New Project")
        database.__insert_in_table__('Projects',project, '')
        self.ls.append(project)
        self.project_listbox.insert(END, project)
        self.project_listbox.config(width=self.width, height=len(self.ls))

    def SetDate(self):
        cd = CalendarDialog(self.main)
        if len(str(cd.result))>0:
            self.date_deadline = str(cd.result)[:10].replace('-','')
        else:
            print('')
            self.date_deadline = 'no date'        


class EditTask():
    def __init__(self):

        self.main = Tk()
        self.main.title("Edit Task")
        
        ttk.Label(self.main, text='Active Tasks').grid(row=0, column=0)    
        self.listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.listbox.grid(row=1, column=0)
        self.width = 10
        nr_symbol_count = 0
        for key in MainDailyGroups:
            self.listbox.insert(END, '=='+key+'==')
            for item in MainDailyGroups[key]:
                self.listbox.insert(END, item)
                self.listbox.itemconfig(nr_symbol_count,{'bg':MainDailyGroups_bg_color[key]})
                if len(item)>self.width:
                    self.width = len(item)
                nr_symbol_count += 1
            nr_symbol_count += 1
        self.listbox.config(width=self.width, height=10)#, justify=CENTER)
        
        ttk.Label(self.main, text='Projects').grid(row=0, column=1)
        self.project_listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.project_listbox.grid(row=1, column=1)
        self.project_width = 10
        if len(Projects)>0:
            for project in Projects:
                    self.project_listbox.insert(END, project)
                    if len(project)>self.project_width:
                        self.project_width = len(project)
            self.project_listbox.config(width=self.project_width, height=10)#, justify=CENTER)

        self.EntryNewTaskName = Entry(self.main)
        self.EntryNewTaskName.grid(row=2, column=0)
        self.EntryNewTaskName.insert(0, 'set new name')

        self.date_deadline = 'no date'        
        ttk.Button(self.main, text="Set deadline", command=self.SetDate).grid(row=3, column=0)

        # ttk.Label(self.main, text='Set minimal duration').grid(row=4, column=0)
        # self.EntryMinimumDailyTaskDuration = Entry(self.main)
        # self.EntryMinimumDailyTaskDuration.grid(row=4, column=1)
        # self.EntryMinimumDailyTaskDuration.insert(0, 'minutes, mm')

        ttk.Button(self.main, text="Update", command=self.Update).grid(row=4, column=0,)
        ttk.Button(self.main, text="Pause", command=self.Pause).grid(row=3, column=1)
        ttk.Button(self.main, text="Archive", command=self.Archive).grid(row=4, column=1)

    def Update(self):
        ls_Tasks2Update = list()
        selection = self.listbox.curselection()
        for i in selection:
            value = self.listbox.get(i)
            ls_Tasks2Update.append(value)

        ls_selected_projects = list()
        selected_project = self.project_listbox.curselection()
        for i in selected_project:
            value = self.project_listbox.get(i)
            ls_selected_projects.append(value)

        deadline = self.date_deadline
        if deadline != 'no date':
            for Task2Update in ls_Tasks2Update:
                print('adding deadline to db: ', deadline)
                if database.task_in_table('Date_deadline',Task2Update):
                    database.__update_table__('Date_deadline','date_id',deadline,'task_id',Task2Update)
                else:
                    database.__insert_in_table__('Date_deadline',Task2Update, deadline)

        RenameTask = str(self.EntryNewTaskName.get())
        if len(RenameTask)>0 and RenameTask != 'set new name':
            import pandas as pd
            for Task2Update in ls_Tasks2Update:
                for key in MainDailyGroups:
                    if Task2Update == ''=='+key+'=='':
                        pass
                    else:
                        for value in MainDailyGroups[key]:
                            if value == Task2Update:
                                database.__update_table__('MainDailyGroups','task_id',RenameTask, 'task_id',Task2Update)
                for key in Projects:
                            for value in Projects[key]:
                                if value == Task2Update:
                                    database.__update_table__('Projects','task_id',RenameTask, 'task_id',Task2Update)
                if Task2Update in MinDailyTaskDuration:
                            database.__update_table__('MinDailyTaskDuration', 'task_id',RenameTask,'task_id', Task2Update)
                            database.__update_table__('Days_task_active','task_id',RenameTask, 'task_id',Task2Update)
        self.main.destroy()

    def Pause(self):
        ls_Tasks2Update = list()
        selection = self.listbox.curselection()
        for i in selection:
            value = self.listbox.get(i)
            ls_Tasks2Update.append(value)
        for Task2Pause in ls_Tasks2Update:
            for key in MainDailyGroups:
                for value in MainDailyGroups[key]:
                    if value == Task2Pause:
                        project = key
            database.__delete_from_table__('MainDailyGroups',project, Task2Pause)
            database.__insert_in_table__('PausedTasks',project, Task2Pause)
            if Task2Pause in MinDailyTaskDuration:
                database.__update_table__('MinDailyTaskDuration','task_id',RenameTask,'task_id', Task2Pause)
                MinDailyTaskDuration[RenameTask] = MinDailyTaskDuration[Task2Pause]
            # self.ComputeTemporaryProjectDuration(Task2Pause, project)       
        self.main.destroy()

    def Archive(self):
        ArchivedTasks = database.get_tasks_for_table_('ArchivedTasks')
        ls_Tasks2Update = list()
        selection = self.listbox.curselection()
        for i in selection:
            value = self.listbox.get(i)
            ls_Tasks2Update.append(value)
        for Task2Archive in ls_Tasks2Update:
            for key in MainDailyGroups:
                for value in MainDailyGroups[key]:
                    if value == Task2Archive:
                        project = key
            database.__delete_from_table__('MainDailyGroups',project, Task2Archive)
            database.__insert_in_table__('ArchivedTasks',project, Task2Archive)
            if Task2Archive in Date_deadline:
                database.__delete_from_table__('Date_deadline',Task2Archive, Date_deadline[Task2Archive])
            if Task2Archive in MinDailyTaskDuration:
                database.__delete_from_table__('MinDailyTaskDuration',Task2Archive, MinDailyTaskDuration[Task2Archive])
            # self.ComputeTemporaryProjectDuration(Task2Archive, project)
        self.main.destroy()

    def ComputeTemporaryProjectDuration(self, task, project):
        import shutil, json
        from os import listdir
        for file in listdir(self.PATHapp+'proj/'):
            if task in file:
                with open(self.PATHapp+'proj/'+file,'r') as f:
                    for line in f:
                        duration = line.strip('\n')
                shutil.move(self.PATHapp+'proj/'+file, self.PATHapp+'archive/'+file)


                if path.exists(self.PATHapp+'proj/'+str(time.strftime('%Y%m%d', time.localtime()))+project+'_tmp.json'):
                    with open(self.PATHapp+'proj/'+str(time.strftime('%Y%m%d', time.localtime()))+project+'_tmp.json','r') as f:
                        for line in f:
                            newvalue = float(line)+int(duration)
                else:
                    newvalue = int(duration)
                with open(self.PATHapp+'proj/'+str(time.strftime('%Y%m%d', time.localtime()))+project+'_tmp.json','w') as f:
                    json.dump(newvalue, f)


    def SetDate(self):
        cd = CalendarDialog(self.main)
        if len(str(cd.result))>0:
            self.date_deadline = str(cd.result)[:10].replace('-','')
        else:
            print('')
            self.date_deadline = 'no date'        


    # def Update_order(self, MainDailyGroups):
        # for key in MainDailyGroups:
            # tmp_ls = MainDailyGroups[key]
            # for task2sort in MainDailyGroups[key]:
                # if task2sort in MinDailyTaskDuration:
                    # task2sort_value = MinDailyTaskDuration[task2sort]
                    # for task2change in tmp_ls:
                        # if task2change in MinDailyTaskDuration and task2change != task2sort:
                            # task2change_value = MinDailyTaskDuration[task2change]
                            # if task2change_value < task2sort_value and tmp_ls.index(task2change) >  tmp_ls.index(task2sort):
                                # tmp_ls.remove(task2change)
                                # tmp_ls.insert(tmp_ls.index(task2sort), task2change)
                        # elif task2sort != task2change and tmp_ls.index(task2change) <  tmp_ls.index(task2sort):
                                # tmp_ls.remove(task2sort)
                                # tmp_ls.insert(tmp_ls.index(task2change), task2sort)

class ActivateTask():
    def __init__(self):
        self.main = Tk()
        self.main.title("Activate Task")
        
        ttk.Label(self.main, text='Paused Tasks').grid(row=0, column=0)
        self.listbox = Listbox(self.main, selectmode=EXTENDED)
        self.listbox.grid(row=1, column=0)
        self.width = 5
        for key in PausedTasks:
            self.listbox.insert(END,  '=='+key+'==')
            for value in PausedTasks[key]:
                self.listbox.insert(END, value)
                if len(value)>self.width:
                    self.width = len(value)
        self.listbox.config(width=self.width, height=10)#, justify=CENTER)

        ttk.Button(self.main, text="Activate", command=self.select).grid(row=2, column=0)

    def select(self):
        selection = self.listbox.curselection()
        for i in selection:
            Task2Activate = self.listbox.get(i)
            for key in PausedTasks:
                if Task2Activate == '=='+key+'==':
                    pass
                else:
                    for value in PausedTasks[key]:
                        if value == Task2Activate:
                            project = key
            database.__insert_in_table__('MainDailyGroups',project, Task2Activate)
            database.__delete_from_table__('PausedTasks',project, Task2Activate)
        self.main.destroy()

class SetEdit_MinimalDuration_Task():
    def __init__(self):
        self.main = Tk()
        self.main.title("Set/Edit Minimal Task Duration")
        
        ttk.Label(self.main, text='Active Tasks').grid(row=0, column=0)    
        self.listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.listbox.grid(row=1, column=0)
        self.width = 10
        for key in MainDailyGroups:
            self.listbox.insert(END, '=='+key+'==')
            for item in MainDailyGroups[key]:
                self.listbox.insert(END, item)
                if len(item)>self.width:
                    self.width = len(item)
        self.listbox.config(width=self.width, height=10)#, justify=CENTER)

        ttk.Label(self.main, text='Tasks with Minimal Duration').grid(row=0, column=1)
        self.tasks_min_duration_listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.tasks_min_duration_listbox.grid(row=1, column=1)
        self.tasks_min_duration_width = 10

        if len(MinDailyTaskDuration)>0:
            for key in MinDailyTaskDuration:
                    self.tasks_min_duration_listbox.insert(END, key+'    '+MinDailyTaskDuration[key])
                    if len(key)+len(MinDailyTaskDuration[key])>self.tasks_min_duration_width:
                        self.tasks_min_duration_width = len(key)+len(MinDailyTaskDuration[key])
            self.tasks_min_duration_listbox.config(width=self.tasks_min_duration_width, height=10)#, justify=CENTER)

        ttk.Label(self.main, text='Set/Edit Minimal Task Duration').grid(row=2, column=0)
        self.EntryTaskDuration = Entry(self.main)
        self.EntryTaskDuration.grid(row=2, column=1)
        self.EntryTaskDuration.insert(0, 'HH:MM')

        ttk.Button(self.main, text="Update", command=self.Set_Duration).grid(row=3, column=0, columnspan=2)

    def Set_Duration(self):
        ls_Tasks2Update = list()
        selection = self.listbox.curselection()
        for i in selection:
            value = self.listbox.get(i)
            ls_Tasks2Update.append(value)
            for Task2Edit in ls_Tasks2Update:
                duration = str(self.EntryTaskDuration.get())
                if len(duration)>0 and duration != 'HH:MM':
                    if Task2Edit not in MinDailyTaskDuration:
                        database.__insert_in_table__('MinDailyTaskDuration',Task2Edit, str(duration))
                        MinDailyTaskDuration[Task2Edit] = str(duration)
                        database.__insert_in_table__('Days_task_active',Task2Edit, 0)
                    else:
                        database.__update_table__('MinDailyTaskDuration','min_duration_id', str(duration), 'task_id', Task2Edit)

    def Update_order(self, MainDailyGroups):
        for key in MainDailyGroups:
            tmp_ls = MainDailyGroups[key]
            for task2sort in MainDailyGroups[key]:
                if task2sort in MinDailyTaskDuration:
                    task2sort_value = MinDailyTaskDuration[task2sort]
                    for task2change in tmp_ls:
                        if task2change in MinDailyTaskDuration and task2change != task2sort:
                            task2change_value = MinDailyTaskDuration[task2change]
                            if task2change_value < task2sort_value and tmp_ls.index(task2change) >  tmp_ls.index(task2sort):
                                tmp_ls.remove(task2change)
                                tmp_ls.insert(tmp_ls.index(task2sort), task2change)
                        elif task2sort != task2change and tmp_ls.index(task2change) <  tmp_ls.index(task2sort):
                                tmp_ls.remove(task2sort)
                                tmp_ls.insert(tmp_ls.index(task2change), task2sort)
            MainDailyGroups[key] = tmp_ls
        self.main.destroy()

class Edit_Task_Duration():
    def __init__(self):
        self.main = Tk()
        self.main.title("Edit Task Duration")
        
        ttk.Label(self.main, text='Active Tasks').grid(row=0, column=0)    
        self.listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.listbox.grid(row=1, column=0)
        self.width = 10
        for key in MainDailyGroups:
            self.listbox.insert(END, '=='+key+'==')
            for item in MainDailyGroups[key]:
                self.listbox.insert(END, item)
                if len(item)>self.width:
                    self.width = len(item)
        self.listbox.config(width=self.width, height=10)#, justify=CENTER)

        today_tasks_and_durations = {}
        all_tasks = database.get_tasks_duration_for_Dailydatabase()
        for task in all_tasks:
            today_tasks_and_durations[task[0]] = str(time.strftime('%H:%M:%S', time.gmtime(float(all_tasks[task]))))
        print('READ THIS',today_tasks_and_durations)

        ttk.Label(self.main, text='Tasks Used today').grid(row=0, column=1)
        self.today_tasks_listbox = Listbox(self.main, selectmode=EXTENDED, exportselection=0)
        self.today_tasks_listbox.grid(row=1, column=1)
        self.today_tasks_width = 10

        if len(today_tasks_and_durations)>0:
            for task_active_today in today_tasks_and_durations:
                    self.today_tasks_listbox.insert(END, task_active_today+'    '+today_tasks_and_durations[task_active_today])
                    if len(task_active_today)+len(today_tasks_and_durations[task_active_today])>self.today_tasks_width:
                        self.today_tasks_width = len(task_active_today)+len(today_tasks_and_durations[task_active_today])
            self.today_tasks_listbox.config(width=self.today_tasks_width, height=10)#, justify=CENTER)

        ttk.Label(self.main, text='Set Hours:').grid(row=2, column=0)
        self.SetHour = Entry(self.main)
        self.SetHour.grid(row=2, column=1)
        self.SetHour.insert(0, 'hours')
        ttk.Label(self.main, text='Set Minutes:').grid(row=3, column=0)
        self.SetMinutes = Entry(self.main)
        self.SetMinutes.grid(row=3, column=1)
        self.SetMinutes.insert(0, 'MM')

        ttk.Button(self.main, text="Set", command=lambda: self.Set_Duration('set')).grid(row=4, column=0)
        ttk.Button(self.main, text="Add to previous", command=lambda: self.Set_Duration('add')).grid(row=4, column=1)

    def Set_Duration(self, type):
        ls_Tasks2Update = list()
        selection = self.listbox.curselection()
        for i in selection:
            value = self.listbox.get(i)
            ls_Tasks2Update.append(value)
        duration = str(self.SetHour.get())
        duration_min = str(self.SetMinutes.get())
        if len(duration)>0 and duration != 'hours':
            if duration_min == 'MM':
                duration_min = 0
            print(duration, duration_min)
            duration2set = (int(duration)*60+int(duration_min))*60
        elif duration == 'hours':
            if len(duration_min)>0 and duration_min != 'MM':
                print(duration_min)
                duration2set = int(duration_min)*60
        for Task2Edit in ls_Tasks2Update:
            self.EditDuration(Task2Edit, duration2set, type)

    def EditDuration(self, task, duration2set, type):
        print(task, type, duration2set)
        if type == 'add':
            duration = database.ComputeTaskDuration(task)
            new_duration = duration2set+float(duration)
            database.UpdateDailyTask(task, new_duration)
        else:
            database.SetDailyTaskDuration(task, duration2set)

        self.main.destroy()


class SetDuration_MainDailyGroups():
    def __init__(self):
        self.main = Tk()
        self.main.title("Set Duration for Main Daily Groups")
        
        ttk.Label(self.main, text='Main Daily Groups').grid(row=0, column=0, columnspan=2)
        self.maindaily_listbox = Listbox(self.main, selectmode=SINGLE)
        self.maindaily_listbox.grid(row=1, column=0, columnspan=2)
        self.width = 5
        self.ls = []
        for project in MainDailyGroups:
            if project not in self.ls:
                self.ls.append(project)
        for item in self.ls:
            self.maindaily_listbox.insert(END, item)
            if len(item)>self.width:
                self.width = len(item)
        self.maindaily_listbox.config(width=self.width, height=len(self.ls))#, justify=CENTER)
        #scrollbar = Scrollbar(self.maindaily_listbox, orient=VERTICAL)
        #scrollbar.grid(column=1)#, sticky=N+S)

        ttk.Label(self.main, text='Enter duration:').grid(row=2, column=0, columnspan=2)
        self.EntryDurationHours = Entry(self.main)
        self.EntryDurationHours.grid(row=3, column=0)
        self.EntryDurationHours.insert(0, 'hours')
        self.EntryDurationMinutes = Entry(self.main)
        self.EntryDurationMinutes.grid(row=3, column=1)
        self.EntryDurationMinutes.insert(0, 'minutes')

        ttk.Button(self.main, text="Submit", command=self.select).grid(row=4, column=0, columnspan=2)

    def select(self):
        DurationHours2Get = str(self.EntryDurationHours.get())
        DurationMinutes2Get = str(self.EntryDurationMinutes.get())
        reslist = list()
        if DurationHours2Get != 'hours':
            Duration2Add = (int(DurationHours2Get)*3600)+(int(DurationMinutes2Get)*60)
            selected_maindaily = self.maindaily_listbox.curselection()
            for i in selected_maindaily:
                entrada = self.maindaily_listbox.get(i)
                reslist.append(entrada)
            for maindailygroup in reslist:
                database.__insert_in_table__('MainDailyGroupDuration',maindailygroup, Duration2Add)

        else:
            pass

        self.main.destroy()


def popupmsg(msg):
    popup = Tk()
    popup.wm_title("!")
    label = Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
