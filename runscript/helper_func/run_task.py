import re, subprocess, sys

from .view_helper import get_temp
from datetime import datetime


def run_task(*args):
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    path = args[0]
    arguments = args[1]
    ext = args[2]
    print('path', path)
    print('arg', arguments)
    print("date and time =", dt_string)

    t = open(get_temp(), 'w')

    if ext == 'sh':
        subprocess.call(['sh', path] + arguments, stdout=t)
    elif ext == 'py':
        subprocess.run([sys.executable, path] + arguments, text=True, stdout=t)
    t.close()


def validate_dates(task_dates, context):
    task_scheduler = [
        "task_year", "task_month", "task_day",
        "task_week", "task_day_of_week",
        "task_hour", "task_minute", "task_second"
    ]

    # print(task_scheduler)

    # creates context for each date input and assumes false before validations
    for task in task_scheduler:
        context[task] = [False, '']  # f"this is the task_scheduler for: {task}"]

    # for task in task_scheduler:
    #     print(context[task][1])

    # if any entry is left blank, replace it with a *
    for i, date in enumerate(task_dates):
        if date == '':
            task_dates[i] = '*'

    # for i,s in enumerate(task_scheduler):
    #     print(i,s[0], s[1])

    # for i, task in enumerate(task_scheduler):
    #     if i == 0:
    #         context[task] = check_year(task_dates[i], task_scheduler[i])
    #     elif i == 1:
    #         context[task] = check_month(task_dates[i], task_scheduler[i])
    #     elif i == 2:
    #         context[task] = check_day(task_dates[i], task_scheduler[i])
    #     elif i == 3:
    #         context[task] = check_week(task_dates[i], task_scheduler[i])
    #     elif i == 4:
    #         context[task] = check_day_of_week(task_dates[i], task_scheduler[i])
    #     elif i == 5:
    #         context[task] = check_hour(task_dates[i], task_scheduler[i])
    #     elif i == 6:
    #         context[task] = check_minute(task_dates[i], task_scheduler[i])
    #     elif i == 7:
    #         context[task] = check_second(task_dates[i], task_scheduler[i])

    # task_date[i] is the input string for the field
    # task_scheduler[i] is the name of the input field (task_year, task_month, etc)
    for i, task in enumerate(task_scheduler):
        if task_dates[i] == '*':
            context[task] = [True, 'from *']
            continue

        if i == 0:  # year
            context[task] = check_year(task_dates[i], task_scheduler[i])
        elif i == 1:  # month
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 1, 12)
        elif i == 2:  # day
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 1, 31)
        elif i == 3:  # week
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 1, 53)
        elif i == 4:  # day of week
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 0, 6)
        elif i == 5:  # hour
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 0, 23)
        elif i == 6:  # minute
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 0, 59)
        elif i == 7:  # second
            context[task] = check_date_range(task_dates[i], task_scheduler[i], 0, 59)

    return task_scheduler


def within_range(value, minVal, maxVal):
    if minVal <= value <= maxVal:
        return True

    return False


def check_date_range(date, task, minVal, maxVal):

    values = date.split('-')
    print("length of values", len(values))
    if len(values) == 1:
        if within_range(int(values[0]), minVal, maxVal):
            return [True, "within range for 1 argument"]
        else:
            return [False, "Not within range"]
    elif len(values) == 2:
        pass
    else:
        return [False, "Invalid input"]

    print("check date range:", date, task)

    print("made it to default true")
    return [True]


# 4 digit year
def check_year(date, task):

    # must start and end with 4 digits
    pattern = re.compile(r'^\d{4}$')
    match = pattern.findall(date)
    print("this is match:", match)

    if match:
        now = datetime.now()
        current_year = int(now.strftime("%Y"))

        if int(date) >= current_year:
            return [True, f"{date} GE {current_year}"]
        else:
            return [False, f"{date} LT {current_year}"]
    else:
        return [False, "Not 4 digits"]


# 1-12
def check_month(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 1-31
def check_day(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 1-53
def check_week(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 0-6 starts on monday
def check_day_of_week(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 0-23
def check_hour(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 0-59
def check_minute(task_dates, task_scheduler):
    print(task_dates, task_scheduler)


# 0-59
def check_second(task_dates, task_scheduler):
    print(task_dates, task_scheduler)
