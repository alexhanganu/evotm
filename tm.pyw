#!/usr/bin/python3
#updated 2018-03-18

from os import listdir, getcwd, path, environ
from sys import version_info, platform
from datetime import date, datetime
import time

if version_info[0] >=3:
    from tkinter import Tk, ttk, Frame, Label, Button, Menu, StringVar
else:
    from Tkinter import Tk, ttk, Frame, Label, Button, Menu, StringVar

from lib import database
from lib import update

MainDailyGroups = database.get_tasks_for_table_('MainDailyGroups')
Days_task_active = database.get_tasks_for_table_('Days_task_active')
MinDailyTaskDuration = database.get_tasks_for_table_('MinDailyTaskDuration')
Tabs = database.get_tasks_for_table_('Tabs')

ls_MainDailyGroups = []
ls_sorting_order_from_tabs = []
for tab in Tabs:
    ls_sorting_order_from_tabs.append(Tabs[tab])
for order in sorted(ls_sorting_order_from_tabs):
    for tab in Tabs:
        if Tabs[tab] == order:
            ls_MainDailyGroups.append(tab)


class TMApp(Frame):
    def __init__(self, parent, *args, **kwargs):  
        Frame.__init__(self, parent)

        menubar = Menu(self)
        filemenu=Menu(menubar, tearoff=0)
        menubar.add_cascade(label='tasks', menu=filemenu)
        filemenu.add_command(label="Edit task", command = lambda: self.EditTask())
        filemenu.add_command(label="Set/Edit Task Daily Duration", command = lambda: self.Edit_Task_Duration())
        filemenu.add_command(label="Unpause task", command = lambda: self.ActivateTask())
        filemenu.add_command(label="New task", command = lambda: self.NewTask())
        filemenu.add_command(label="Set/Edit Task Minimal Duration", command = lambda: self.SetEdit_MinimalDuration_Task())
        filemenu.add_command(label="Configure Tabs", command = lambda: self.Configure())
        filemenu.add_command(label="Statistics", command=lambda: self.Show_Stats())
        self.master.config(menu=menubar)

        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self._TotalTaskDuration = 0
        self._TimeLeftDailyMainGroup = StringVar()
        self._TaskTotalDailyDuration = StringVar()
        self._TotalProjectDuration = ['']
        self.Project_Duration_Now = {}
        for tab in Tabs:
            self.Project_Duration_Now[tab] = StringVar()
        self._taskrunning = ['']
        self._Projectrunning = ['']
        self._taskclosed = ['']


        self.check_today()

        self.button_dict = {}
        self.button_days_task_active_dict = {}
        self.maxlength = 5
        self.row_nr = 0
        self.col_nr = 1

        self.col_nr_4_stop_button = 2
        self.nr_of_col_4_widget = 1

        if len(ls_MainDailyGroups)>0:
            self.ListButtons()

        self.WidgetTaskDuration()
        self.SetProjectDuration()

    def check_today(self):
        today = datetime.strptime(datetime.today().strftime("%Y%m%d"), "%Y%m%d").strftime("%Y%m%d")
        d_tasks = database.get_tasks_for_table_('Dailydatabase')
        ls_tasks = []
        if len(d_tasks)>0:
            for key in d_tasks:
                ls_tasks.append(key)
            if d_tasks[ls_tasks[0]][0][1] != today:
                print('starting update', d_tasks[ls_tasks[0]][0][1], today)
                database.Update_DB()
                update.send_to_thread_update()


    def SetProjectDuration(self):
        if self._running == 1:
            for project in self.Project_Duration_Now:
                if project == self._Projectrunning:
                    self.Project_Duration_Now[project].set(time.strftime('%H:%M', time.gmtime(self._TotalProjectDuration+self._elapsedtime)))
                else:
                    self.Project_Duration_Now[project].set(self.Progress_Percent_Project_dict[project])
        else:
            self.Progress_Percent_Project_dict = {}
            for project in self.Project_Duration_Now:
                duration_per_daily_group = time.strftime('%H:%M', time.gmtime(self.ProjectDuration(project)))
                self.Project_Duration_Now[project].set(duration_per_daily_group)
                self.Progress_Percent_Project_dict[project] = duration_per_daily_group


    def ListButtons(self):
        Date_deadline = database.get_tasks_for_table_('Date_deadline')
        col=0
        for project in ls_MainDailyGroups:
            rownr = 2
            maxlength = 3
            task_in_minimum_daily = False
            task_in_date_deadline = False
            if len(MainDailyGroups[project])>0:
                Label(self, textvariable=self.Project_Duration_Now[project]).grid(row=1, column=col)

            for task in MainDailyGroups[project]:
                if len(task) > maxlength:
                    maxlength = len(task)
            self.maxlength = self.maxlength+maxlength
            for task in MainDailyGroups[project]:
                action = lambda x = task: self.SetTask(x)
                self.button_dict[task] = Button(self, height=1, width=maxlength, text=task, command=action)
                self.button_dict[task].grid(row=rownr, column=col)
                self.button_dict[task].configure(bg = self.SetButtonColor(task))
                if task in MinDailyTaskDuration:
                    task_in_minimum_daily = True
                    self.button_days_task_active_dict[task] = Button(self, height=1, width=2, text=Days_task_active[task])
                    self.button_days_task_active_dict[task].grid(row=rownr, column=col+1)
                if task in Date_deadline:
                    task_in_date_deadline = True
                    self.button_days_task_active_dict[task] = Button(self, height=1, width=2, text=(((date(int(Date_deadline[task][:4]), int(Date_deadline[task][4:6]), int(Date_deadline[task][6:])))-date.today()).days))
                    self.button_days_task_active_dict[task].grid(row=rownr, column=col+1)
                    if days_left < 10:
                        self.button_days_task_active_dict[task].configure(bg = 'firebrick')         
                    else:
                        self.button_days_task_active_dict[task].configure(bg = 'orange')
                rownr += 1
                if project == ls_MainDailyGroups[0]:
                    if task_in_minimum_daily or task_in_date_deadline:
                        self.nr_of_col_4_widget = 2
                    else:
                        self.nr_of_col_4_widget = 1
                elif project == ls_MainDailyGroups[-1]:
                    self.col_nr_4_stop_button = col
            if task_in_minimum_daily or task_in_date_deadline:
                col += 2
            else:
                col += 1

            if rownr > self.row_nr:
                self.row_nr = self.row_nr+rownr
        if col != 1:
            self.col_nr = col


    def WidgetTaskDuration(self):
        # if len(ls_MainDailyGroups)>2:
                # widget_task_text_row_nr = self.row_nr
                # widget_task_variable_row_nr = self.row_nr
                # widget_task_variable_col_nr = self.nr_of_col_4_widget
                # row_button = self.row_nr            
                # col_button = self.col_nr_4_stop_button
        # elif len(ls_MainDailyGroups)==1:
                # widget_task_text_row_nr = self.row_nr
                # widget_task_variable_row_nr = self.row_nr+1
                # widget_task_variable_col_nr = 0
                # row_button = self.row_nr+1
                # col_button = self.col_nr_4_stop_button-1
        # else:
                # widget_task_text_row_nr = self.row_nr
                # widget_task_variable_row_nr = self.row_nr+1
                # widget_task_variable_col_nr = 0
                # row_button = self.row_nr+1
                # col_button = self.col_nr_4_stop_button-1

        row_button, col_button = (self.row_nr+1, self.col_nr_4_stop_button-1)
        if len(MainDailyGroups)>0 and len(MainDailyGroups[ls_MainDailyGroups[0]])>0:
                row_button, col_button = (self.row_nr, self.col_nr_4_stop_button)

        Label(self, textvariable=self._TaskTotalDailyDuration).grid(row=widget_task_text_row_nr, column=0)

        Button(self, text='Stop', command=self.Stop).grid(row=row_button, column=col_button)


    def SetButtonColor(self, task):
        for key in MainDailyGroups:
            for value in MainDailyGroups[key]:
                if value == task:
                    Project = key
        if task in MinDailyTaskDuration:
            if database.task_in_table('Dailydatabase', task):
                    duration = float(database.ComputeTaskDuration(task))
                    if str(time.strftime('%H:%M:%S', time.gmtime(float(duration)))) > MinDailyTaskDuration[task]:
                        color_button = 'grey'
                    else:
                        color_button = 'firebrick'
            else:
                    color_button = 'firebrick'
        elif database.task_in_table('Dailydatabase', task):
                color_button = 'grey'
        else:
            if platform == 'win32':
                color_button = 'SystemButtonFace'
            elif platform == 'linux':
                color_button = 'snow4'
        return color_button


    def _update(self): 
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.after(500, self._update)
        if time.strftime('%H:%M:%S', time.localtime(time.time())) == ('23:59:55'):
            time.sleep(1)
            self.DayStart()


    def _setTime(self, elap):
        try:
            self.TaskDailyDuration = time.strftime('%H:%M:%S', time.gmtime(self._TotalTaskDuration+self._elapsedtime))
            self._TaskTotalDailyDuration.set(self.TaskDailyDuration)
        except:
            pass


    def Start(self):                                                     
        if not self._running:            
            self._start = time.time() - self._elapsedtime
            self._update()
            self._running = 1


    def Stop(self):                                    
        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = time.time() - self._start
            self._setTime(self._elapsedtime)
            self._running = 0
            database.UpdateDailyTask(self._taskrunning, self._elapsedtime)


    def Reset(self):                                  
        self._start = time.time()         
        self._elapsedtime = 0.0    
        self._setTime(self._elapsedtime)


    def SetTask(self, task):
        self.Stop()
        self.Reset()
        if len(self._taskclosed)>1:
            self.button_dict[self._taskclosed].configure(bg = self.SetButtonColor(self._taskclosed))
        for key in MainDailyGroups:
            ls = MainDailyGroups[key]
            if any(task in i for i in ls):
                self._Projectrunning = key
        self._TotalTaskDuration = database.ComputeTaskDuration(task)
        self.ProjectDuration(self._Projectrunning)
        self.SetProjectDuration()
        self._taskrunning = task
        database.UpdateStartTime(self._taskrunning, time.strftime('%H:%M:%S', time.localtime(time.time())))
        self.Start()
        self.button_dict[task].configure(bg = "green")
        self._taskclosed = self._taskrunning


    def ProjectDuration(self, project):
        self._TotalProjectDuration = database.ComputeProjectDuration(project)
        return  self._TotalProjectDuration


    def DayStart(self):
        self._taskclosed = self._taskrunning
        Project_closed = self._Projectrunning
        self.Stop()
        self.Reset()
        time.sleep(4)
        database.Update_DB()
        update.send_to_thread_update()

        for Group in MainDailyGroups:
            for task in MainDailyGroups[Group]:
                self.button_dict[task].configure(bg = self.SetButtonColor(task))
        self._Projectrunning = Project_closed
        self._TotalTaskDuration = 0
        self.ProjectDuration(self._Projectrunning)
        self.Start()
        self.button_dict[self._taskclosed].configure(bg = "green")

    def NewTask(self):
        from lib import task_config
        task_config.NewTask()

    def EditTask(self):
        from lib import task_config
        task_config.EditTask()

    def ActivateTask(self):
        from lib import task_config
        task_config.ActivateTask()

    def SetEdit_MinimalDuration_Task(self):
        from lib import task_config
        task_config.SetEdit_MinimalDuration_Task()

    def Configure(self):
        from lib import configuration
        configuration.Configuration()

    def SetDuration_MainDailyGroups(self):
        from lib import task_config
        task_config.SetDuration_MainDailyGroups()

    def Edit_Task_Duration(self):
        from lib import task_config
        task_config.Edit_Task_Duration()

    def Show_Stats(self):
        from lib import make_stats
        make_stats.Show_Stats()
        database.retrieve_all_data(path.join(environ["HOMEPATH"], "Desktop",'db_Database.csv'))

def on_closing():
        print('closing app and database')
        database.__close_db_()
        app.destroy()

app = Tk()
TMApp(app).pack(fill='both', expand=True)
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
