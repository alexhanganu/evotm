import pandas as pd
import time
from . import database

class Show_Stats():

    def __init__(self):
        conn = database.__connect_db__()
        c = conn.cursor()
        frame = [{'date':time.strftime('%Y%m%d', time.localtime())}]
        df = pd.DataFrame(frame)
        tasksindf = df.columns.values.tolist()
        ls = ['day_of_week_id', 'date_id', 'task_id', 'duration_id']
        for row in c.execute('''SELECT * from Database'''):
                    date = row[1]
                    task = row[2]
                    duration = row[3]
                    for taskindf in tasksindf:
                        if taskindf == task:
                            addtask = 1
                            break
                        else:
                            addtask = 0
                    if addtask == 0:
                        df[task] = ('')
                        tasksindf = df.columns.values.tolist()
                    for dateindf in df['date']:
                        if int(float(dateindf)) == int(date):
                            index = df.date[df.date == dateindf].index.tolist()
                            df.at[index, task] = duration
                            break
                        elif int(float(dateindf)) < int(date):
                            df.loc[-1] = df.columns.values
                            df.index = df.index+1
                            df = df.sort_index()
                            for taskindf in tasksindf:
                                df.at[0,taskindf] =''
                            df.at[0,'date'] = date
                            df.at[0, task] = duration
                            break
                        elif int(float(dateindf)) > int(date) and dateindf != df['date'][len(df['date'])-1]:
                            pass

                        elif dateindf == df['date'][len(df['date'])-1] and int(float(dateindf)) > int(date):
                            df.loc[-1] = df.columns.values
                            for taskindf in tasksindf:
                                df.at[-1, taskindf] = ''
                            df.at[-1, 'date'] = date
                            df.at[-1, task] = duration
                            df.index = range(len(df['date']))
                            break
                        else:
                            print('ERROR')
        df[sorted(df.columns)]
        df.to_csv('C:/Users/Alex/Desktop/tm_db.csv', encoding='utf-8', index=False)