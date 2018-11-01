import json
from sqlite3 import connect, OperationalError
from os import environ, listdir, path
import pandas.io.sql as pdsql
import pandas as pd
from time import strftime, localtime, gmtime
import pathlib 

def __connect_db__():
    conn = connect(str(pathlib.Path().absolute())+'/lib/'+environ['COMPUTERNAME']+'.db', check_same_thread=False)
    try:
        __get_table_(conn)
    except OperationalError:
        __create_table__(conn)
    return conn


def Update_DB():
    conn = __connect_db__()
    for row in conn.execute('''SELECT * FROM Dailydatabase''').fetchall():
        data = [(row[0], row[1], row[2], str(strftime('%H:%M:%S', gmtime(float(row[3])))))]
        date = row[1]
        print('inserting into Database values: ',data)
        conn.executemany('''INSERT INTO Database VALUES(?,?,?,?)''', data)
    conn.execute('''DELETE FROM Dailydatabase''')
    conn.commit()


def get_tasks_duration_for_Dailydatabase():
    conn = __connect_db__()
    table = {}
    for task in conn.execute('''SELECT task_id FROM Dailydatabase''').fetchall():
        table[task] = conn.execute('''SELECT duration_id FROM Dailydatabase''').fetchone()[0]
    return table


def UpdateDailyTask(task, duration):
    conn = __connect_db__()
    if conn.execute('''select count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
        time_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
        new_time = time_in_db+ duration
        conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(new_time, task))
    else:
        new_time = duration
        data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, new_time)]
        conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
    conn.commit()


def SetDailyTaskDuration(task, duration):
    conn = __connect_db__()
    if conn.execute('''select count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
        conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(duration, task))
    else:
        new_time = duration
        data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, new_time)]
        conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
    conn.commit()

	
def ComputeTaskDuration(task):
    conn = __connect_db__()
    date = str(strftime('%Y%m%d', localtime()))
    _TotalTaskDuration = 0
    if task_in_table('Dailydatabase', task):
        duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
        _TotalTaskDuration = float(duration_in_db)+ _TotalTaskDuration
    return (_TotalTaskDuration)



def ComputeProjectDuration(project):
    MainDailyGroups = get_tasks_for_table_('MainDailyGroups')
    conn = __connect_db__()
    _TotalProjectDuration_in_db = 0
    for task in MainDailyGroups[project]:
        if task == 'sleep':
            pass
        else:
            if task_in_table('Dailydatabase', task):
                duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
                _TotalProjectDuration_in_db = float(duration_in_db)+ _TotalProjectDuration_in_db
    return _TotalProjectDuration_in_db
	

def task_in_table(table, task):
    conn = __connect_db__()
    exists = conn.execute('''select count(*) from {0} where task_id="{1}"'''.format(table,task)).fetchone()[0] != 0
    return exists

def task_and_date_in_table(table, task, date):
    conn = __connect_db__()
    exists = conn.execute('''select count(*) from {0} where task_id="{1}" and date_id="{2}"'''.format(table,task,date)).fetchone()[0] != 0
    return exists


def get_tasks_for_table_(table_name):
    conn = __connect_db__()
    cursor = conn.execute('''SELECT * FROM {0}'''.format(table_name,))
    all_data_for_table = cursor.fetchall()
    table = {}
    tables_with_lists = ['MainDailyGroups','PausedTasks','ArchivedTasks','Projects',]
    for Group in all_data_for_table:
        if table_name in tables_with_lists:
            if Group[0] not in table:
                table[Group[0]] = []
            table[Group[0]].append(Group[1])
        elif table_name == 'Dailydatabase':
            table[Group[2]] = []
            table[Group[2]].append(Group)
        else:
            table[Group[0]] = Group[1]
    return table


def update_db_from_pandas(dfsql):
    conn = __connect_db__()
    pdsql.to_sql(dfsql, 'Database', conn, if_exists='append', index=False)
    print('dfsql added to database')
    conn.commit()


def get_values_for_task_(table, task, column):
    conn = __connect_db__()
    data = conn.execute('''SELECT * from {0} WHERE task_id="{1}" ORDER BY {2} DESC'''.format(table, task, column))
    return data.fetchall()


def retrieve_all_data(file_2save):
    conn = __connect_db__()
    df = pd.read_sql('''SELECT * from Database''',conn)
    df.to_csv(file_2save, encoding='utf-8', index=False)


def __insert_in_table__(table, group, task):
    conn = __connect_db__()
    values = [group, task,]
    conn.execute("INSERT INTO {0} VALUES ({1})".format(table,','.join('\"' + str(x) + '\"'for x in values)))
    conn.commit()
   

def __update_table__(table, col2update, new_value, where2update, where_value):
    conn = __connect_db__()
    conn.execute("UPDATE {0} SET {1} = '{2}' WHERE {3}='{4}'".format(table, col2update, new_value, where2update, where_value))
    conn.commit()


def __delete_from_table__(table, value1, value2):
    conn = __connect_db__()
    if table == 'MainDailyGroups' or table == 'PausedTasks' or table == 'ArchivedTasks':
        col1 = 'dailygroup_id'
        col2 = 'task_id'
    elif table == 'Projects':
        col1 = 'project_id'
        col2 = 'task_id'
    elif table == 'Date_deadline':
        col1 = 'task_id'
        col2 = 'date_id'
    elif table == 'Days_task_active':
        col1 = 'task_id'
        col2 = 'days_task_active_id'
    elif table == 'MinDailyTaskDuration':
        col1 = 'task_id'
        col2 = 'min_duration_id'
    elif table == 'MainDailyGroups_bg_color':
        col1 = 'dailygroup_id'
        col2 = 'color_id'
    conn.execute("DELETE from {0} WHERE {1}='{2}' AND {3}='{4}'".format(table, col1, value1, col2, value2))
    conn.commit()


def __close_db_():
    conn = __connect_db__()
    conn.commit()
    conn.close()
    print('database closed')


def __get_table_(conn):
    ls_tables = []
    for table in conn.execute('''SELECT * FROM sqlite_master WHERE type='table' ''').fetchall():
        ls_tables.append(table[1])
    if len(ls_tables) == 10:
        pass
    else:
        __create_table__(conn)
    return ls_tables


def __create_table__(conn):
    conn.execute('''CREATE TABLE if not exists Database (day_of_week_id, date_id, task_id, duration_id)''')
    conn.execute('''CREATE TABLE if not exists MainDailyGroups (dailygroup_id, task_id)''')
    conn.execute('''CREATE TABLE if not exists Projects (project_id, task_id)''')
    conn.execute('''CREATE TABLE if not exists Days_task_active (task_id, days_task_active_id)''')
    conn.execute('''CREATE TABLE if not exists MinDailyTaskDuration (task_id, min_duration_id)''')
    conn.execute('''CREATE TABLE if not exists Date_deadline (task_id, date_id)''')
    conn.execute('''CREATE TABLE if not exists PausedTasks (dailygroup_id, task_id)''')
    conn.execute('''CREATE TABLE if not exists ArchivedTasks (dailygroup_id, task_id)''')
    conn.execute('''CREATE TABLE if not exists Dailydatabase (day_of_week_id, date_id, task_id, duration_id)''')
    conn.execute('''CREATE TABLE if not exists MainDailyGroups_bg_color (dailygroup_id, color_id)''')
    conn.commit()
