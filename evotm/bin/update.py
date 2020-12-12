from time import strptime, strftime
from datetime import datetime, timedelta

def send_to_thread_update(db):
    start_update = UpdateDaysTaskActive(db)
    start_update
    #threading.Thread(target=start_update).start()

class UpdateDaysTaskActive:
    
    def __init__ (self, db):
        # ls_keys = []
        # for key in Days_task_active:
            # if key not in MinDailyTaskDuration:
                # ls_keys.append(key)
        Days_task_active = db.get_tasks_for_table_('Days_task_active')
        MinDailyTaskDuration = db.get_tasks_for_table_('MinDailyTaskDuration')

        previous_day_start = (datetime.strptime(datetime.today().strftime("%Y%m%d"), "%Y%m%d")-timedelta(days=1)).strftime("%Y%m%d")

        for task in MinDailyTaskDuration:
            data = db.get_values_for_task_('Database',task,'date_id')
            if len(data)>0:
                if str(data[0][1]) == previous_day_start and str(data[0][3])>MinDailyTaskDuration[task]:
                    days_task_active = self.count_days(data, previous_day_start, True, MinDailyTaskDuration[task])
                elif str(data[0][1]) == previous_day_start and str(data[0][3])<MinDailyTaskDuration[task] or str(data[0][1]) != previous_day_start:
                    days_task_active = self.count_days(data, previous_day_start, False, MinDailyTaskDuration[task])
                if task in Days_task_active:
                    # print(days_task_active, task)
                    db.__update_table__('Days_task_active','days_task_active_id',days_task_active, 'task_id',task)
                else:
                    print('inserting in db 0 days active', task)
                    db.__insert_in_table__('Days_task_active',task, 0)
            else:
                print(len(data),' is zero', task)


    def count_days(self, data, previous_day, count, min_duration):
                days_task_active = 0
                if count:
                    for entry in data:
                        if entry[1] == str(previous_day) and entry[3] >min_duration:
                            days_task_active += 1
                            previous_day = (datetime.strptime(previous_day, "%Y%m%d")-timedelta(days=1)).strftime("%Y%m%d")
                        else:
                            break
                else:
                    if data[0][1] != previous_day:
                        while data[0][1] != previous_day:
                            days_task_active -= 1
                            previous_day = (datetime.strptime(previous_day, "%Y%m%d")-timedelta(days=1)).strftime("%Y%m%d")
                        if data[0][1] == str(previous_day):
                            for entry in data:
                                if entry[1] == str(previous_day) and entry[3] < min_duration:
                                    days_task_active -= 1
                                    previous_day = (datetime.strptime(previous_day, "%Y%m%d")-timedelta(days=1)).strftime("%Y%m%d")
                    else:
                        for entry in data:
                            if entry[1] == str(previous_day) and entry[3] < min_duration:
                                days_task_active -= 1
                                previous_day = (datetime.strptime(previous_day, "%Y%m%d")-timedelta(days=1)).strftime("%Y%m%d")
                            else:
                                print('False loop end of counting')
                                break
                return days_task_active

