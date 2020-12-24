#!/usr/bin/python3
#updated 2018-03-18
time_zone = 'US/Eastern'

from os import listdir, getcwd, path, environ
from sys import version_info, platform
from datetime import date, datetime, timedelta
import time
from bin.utils import DEFAULT

environ['TZ'] = 'US/Eastern'
time.tzset()

if version_info[0] >=3:
    from tkinter import Tk, ttk, Frame, Label, Button, Menu, StringVar
else:
    from Tkinter import Tk, Frame, Label, Button, Menu, StringVar
    import ttk

from bin import database
from bin import update
from setup.get_credentials_home import _get_credentials_home
from bin.database import DB

cred_home = _get_credentials_home()
db = DB(cred_home)
try:
    from calendar_google.calendar_google import CalendarGoogle    
    cal = CalendarGoogle(cred_home, time_zone)
    print('Connection with Google Calendar is ready')
    google = True
except Exception as e:
    print('Importing Google Calendar didnt work. Please install: pip install googleapiclient google_auth_oauthlib', e)
    google = False

MainDailyGroups      = db.get_tasks_for_table_('MainDailyGroups')
Days_task_active     = db.get_tasks_for_table_('Days_task_active')
MinDailyTaskDuration = db.get_tasks_for_table_('MinDailyTaskDuration')
Tabs                 = db.get_tasks_for_table_('Tabs')

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

        self._start             = 0.0         
        self._elapsedtime       = 0.0
        self._running           = 0
        self._TotalTaskDuration = 0
        self._cal_starttime     = 0
        self._TimeLeftDailyMainGroup = StringVar()
        self._TaskTotalDailyDuration = StringVar()
        self._TotalProjectDuration = ['']
        self.Project_Duration_Now = {}
        for tab in Tabs:
            self.Project_Duration_Now[tab] = StringVar()
        self._taskrunning = ['']
        self._Projectrunning = ['']
        self._taskclosed = ['']

        self.mincal = 900 # 15 minutes minimal time to add to google calendar

        self.check_today()

        self.button_dict = {}
        self.button_days_task_active_dict = {}
        self.row_nr = 0
        self.col_nr = 1

        self.col_nr_4_stop_button = 2
        self.nr_of_col_4_widget = 1

        if len(ls_MainDailyGroups)>0:
            self.ListButtons()

        self.WidgetTaskDuration()
        self.SetProjectDuration()

    def check_today(self):
        today = datetime.today().strftime("%Y%m%d")
#        today = datetime.strptime(datetime.today().strftime("%Y%m%d"), "%Y%m%d").strftime("%Y%m%d")
        d_tasks = db.get_tasks_for_table_('Dailydatabase')
        ls_tasks = []
        if len(d_tasks)>0:
            for key in d_tasks:
                ls_tasks.append(key)
            if d_tasks[ls_tasks[0]][0][1] != today:
                print('starting update', d_tasks[ls_tasks[0]][0][1], today)
                db.Update_DB()
                update.send_to_thread_update(db)


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
        Date_deadline = db.get_tasks_for_table_('Date_deadline')
        col=0
        task_in_minimum_daily = False
        task_in_date_deadline = False
        for group in ls_MainDailyGroups:
            ls_tasks = MainDailyGroups[group]
            rownr = 2
            width = DEFAULT.tab_width
            if len(ls_tasks)>0:
                width = len(max(ls_tasks, key = len))
                Label(self, textvariable=self.Project_Duration_Now[group]).grid(row=1, column=col)
            Projects = db.get_tasks_for_table_('Projects')
            for task in ls_tasks:
                proj = '| '.join([i for i in Projects.keys() if task in Projects[i]])
                action = lambda x = task: self.SetTask(x)
                self.button_dict[task] = Button(self, height=1, width=width, text='{}| {}'.format(proj, task), command=action)
                self.button_dict[task].grid(row=rownr, column=col)
                self.button_dict[task].configure(bg = self.SetButtonColor(task))
                if task in MinDailyTaskDuration:
                    task_in_minimum_daily = True
                    self.button_days_task_active_dict[task] = Button(self, height=1, width=2, text=Days_task_active[task])
                    self.button_days_task_active_dict[task].grid(row=rownr, column=col+1)
                if task in Date_deadline:
                    task_in_date_deadline = True
                    days_left = (((date(int(Date_deadline[task][:4]), int(Date_deadline[task][4:6]), int(Date_deadline[task][6:])))-date.today()).days)
                    self.button_days_task_active_dict[task] = Button(self, height=1, width=2, text=days_left)
                    self.button_days_task_active_dict[task].grid(row=rownr, column=col+1)
                    if days_left < 10:
                        self.button_days_task_active_dict[task].configure(bg = 'firebrick')         
                    else:
                        self.button_days_task_active_dict[task].configure(bg = 'orange')
                rownr += 1
                if group == ls_MainDailyGroups[0]:
                    if task_in_minimum_daily or task_in_date_deadline:
                        self.nr_of_col_4_widget = 2
                    else:
                        self.nr_of_col_4_widget = 1
                elif group == ls_MainDailyGroups[-1]:
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
        if len(ls_MainDailyGroups)>2:
                widget_task_text_row_nr = self.row_nr
                widget_task_variable_row_nr = self.row_nr
                widget_task_variable_col_nr = self.nr_of_col_4_widget
                row_button = self.row_nr            
                col_button = self.col_nr_4_stop_button
        elif len(ls_MainDailyGroups)==1:
                widget_task_text_row_nr = self.row_nr
                widget_task_variable_row_nr = self.row_nr+1
                widget_task_variable_col_nr = 0
                row_button = self.row_nr+1
                col_button = self.col_nr_4_stop_button-1
        else:
                widget_task_text_row_nr = self.row_nr
                widget_task_variable_row_nr = self.row_nr+1
                widget_task_variable_col_nr = 0
                row_button = self.row_nr+1
                col_button = self.col_nr_4_stop_button-1

        row_button, col_button = (self.row_nr+1, self.col_nr_4_stop_button-1)
        if len(MainDailyGroups)>0 and len(MainDailyGroups[ls_MainDailyGroups[0]])>0:
                row_button, col_button = (self.row_nr, self.col_nr_4_stop_button)

        Label(self, textvariable=self._TaskTotalDailyDuration).grid(row=widget_task_text_row_nr, column=0)

        Button(self, text='Stop', command=self.Stop).grid(row=row_button, column=col_button)


    def SetButtonColor(self, task):
        color_button = "grey"
        for key in MainDailyGroups:
            for value in MainDailyGroups[key]:
                if value == task:
                    Project = key
        if task in MinDailyTaskDuration:
            if db.task_in_table('Dailydatabase', task):
                    duration = float(db.ComputeTaskDuration(task))
                    if str(time.strftime('%H:%M:%S', time.gmtime(float(duration)))) > MinDailyTaskDuration[task]:
                        color_button = 'grey'
                    else:
                        color_button = 'firebrick'
            else:
                    color_button = 'firebrick'
        elif db.task_in_table('Dailydatabase', task):
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
            db.UpdateDailyTask(self._taskrunning, self._elapsedtime)
            self.CalendarGoogleUpdate()


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
        self._TotalTaskDuration = db.ComputeTaskDuration(task)
        self.ProjectDuration(self._Projectrunning)
        self.SetProjectDuration()
        self._taskrunning = task
        db.UpdateStartTime(self._taskrunning, time.strftime('%H:%M:%S', time.localtime(time.time())))
        self.Start()
        self.button_dict[task].configure(bg = "green")
        self._taskclosed = self._taskrunning

    def CalendarGoogleUpdate(self):
        project = db.get_values_for_task_('Projects',self._taskrunning,'project_id')[0][0]
        if self._elapsedtime > self.mincal:
            cal_entrance = '{}| {}'.format(project, self._taskrunning)
            now = datetime.now()
            start_time = (now - timedelta(seconds = self._elapsedtime)).isoformat()
            if google:
                cal.create_event(cal_entrance, start_time, now.isoformat())

    def ProjectDuration(self, project):
        self._TotalProjectDuration = db.ComputeProjectDuration(project)
        return  self._TotalProjectDuration


    def DayStart(self):
        self._taskclosed = self._taskrunning
        Project_closed = self._Projectrunning
        self.Stop()
        self.Reset()
        time.sleep(4)
        db.Update_DB()
        update.send_to_thread_update(db)

        for Group in MainDailyGroups:
            for task in MainDailyGroups[Group]:
                self.button_dict[task].configure(bg = self.SetButtonColor(task))
        self._Projectrunning = Project_closed
        self._TotalTaskDuration = 0
        self.ProjectDuration(self._Projectrunning)
        self.Start()
        self.button_dict[self._taskclosed].configure(bg = "green")

    def NewTask(self):
        from bin.task_config import NewTask
        NewTask(db)
        self.ListButtons() #!!!!! intending to update the list of buttons after adding a New Task but does not work for now


    def EditTask(self):
        from bin import task_config
        task_config.EditTask(db)

    def ActivateTask(self):
        from bin import task_config
        task_config.ActivateTask(db)

    def SetEdit_MinimalDuration_Task(self):
        from bin import task_config
        task_config.SetEdit_MinimalDuration_Task(db)

    def Configure(self):
        from bin import configuration
        configuration.Configuration(db)

    def Edit_Task_Duration(self):
        from bin import task_config
        task_config.Edit_Task_Duration(db)

    def Show_Stats(self):
        from bin import make_stats
        make_stats.Show_Stats()
        db.retrieve_all_data(path.join(environ["HOMEPATH"], "Desktop",'db.csv'))

def on_closing():
        print('closing app and database')
        db.close_db()
        app.destroy()

app = Tk()
TMApp(app).pack(fill='both', expand=True)
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
