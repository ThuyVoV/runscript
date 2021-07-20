import re
import subprocess
import sys
from datetime import datetime

from .view_helper import get_temp


def run_task(*args):
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    path = args[0]
    arguments = args[1]
    ext = args[2]
    print('path', path, "@", dt_string)

    t = open(get_temp(), 'w')

    if ext == 'sh':
        subprocess.call(['sh', path] + arguments, stdout=t)
    elif ext == 'py':
        subprocess.run([sys.executable, path] + arguments, text=True, stdout=t)
    t.close()


def validate_dates(task_dates, context):
    # task_scheduler = [
    #     "task_year", "task_month", "task_day",
    #     "task_week", "task_day_of_week",
    #     "task_hour", "task_minute", "task_second"
    # ]
    #
    # # creates context for each date input and assumes false before validations
    # for task in task_scheduler:
    #     context[task] = [False, '']  # f"this is the task_scheduler for: {task}"]

    # for task in task_scheduler:
    #     print(context[task][1])

    # if any entry is left blank, replace it with a *
    for i, date in enumerate(task_dates):
        if date == '':
            task_dates[i] = '*'

    # task_date[i] is the input string for the field
    # task_scheduler[i] is the name of the input field (task_year, task_month, etc)
    for i, task in enumerate(context['task_scheduler']):
        if task_dates[i] == '*':
            context[task] = [True, 'from *']
            continue

        task_dates[i] = parse_date(task_dates[i])

        if i == 0:  # year
            context[task] = check_year(task_dates[i], context['task_scheduler'][i])
        elif i == 1:  # month
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 1, 12)
        elif i == 2:  # day
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 1, 31)
        elif i == 3:  # week
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 1, 53)
        elif i == 4:  # day of week
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 0, 6)
        elif i == 5:  # hour
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 0, 23)
        elif i == 6:  # minute
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 0, 59)
        elif i == 7:  # second
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], 0, 59)


# 1,,,,2-3,,,5-6, 00,002,02, 3,3,5,7,7,0007,14 , 200, -1,           ,
# 00,002,02, 3,3,5,7,7,0007
def parse_date(date):
    # remove ending comma
    if date[-1] == ',':
        date = date[:len(date) - 1:]

    # split everything by comma
    date = date.split(',')
    # print("values before:", date)
    while "" in date:
        date.remove("")
    # removing extra spaces, strip leading 0
    date = [d.strip(' ') for d in date]
    date = [d.lstrip('0') or '0' for d in date]
    date = ['0' + d if d.startswith('-') else d for d in date]

    # remove empty strings (e,g user input ,,,,)
    while "" in date:
        date.remove("")
    # print("values after:", date)

    # remove duplicates
    date = list(set(date))
    date.sort()

    # sort inputs based on integer or range
    single, double = [], []
    for d in date:
        if '-' in d:
            double.append(d)
        else:
            single.append(d)

    # concatenate everything back
    date = single + double
    date = ",".join(date)
    print("this is date", date)

    return date


def within_range(value, minVal, maxVal):
    if minVal <= value <= maxVal:
        return True

    return False


# 0,1,5,8,13,14

# 1,,,2-3,,,5-6, 00,002,02, 3,3,5,7,7,0007,14 , 200, -1, !,@,#,$,lmao, 8-4 ,123-577 , 11-14//,10-12,// ,   0-6    ,
# ^\d{1,2}(\-\d{1,2})?$
def check_date_range(date, task, minVal, maxVal):
    # pattern, must be a 1 or 2 digit integer
    # if it is a range of number, the two numbers must be separated by a dash
    pattern = re.compile(r'^\d{1,2}(?:\-\d{1,2})?$')

    values = date.split(',')

    error = ""
    goodv = []
    badv = []
    bad_input = []
    bad_range = []
    bad_values = []

    print("values", values)

    for v in values:
        match = pattern.findall(v)

        if match:
            # range case x-y
            if '-' in v:
                nums = v.split('-')
                if int(nums[0]) > int(nums[1]):
                    badv.append(v)
                    bad_values.append(v)
                    # error = error + f"{v} incorrect input, first number cannot be larger than the second."
                    continue

                if within_range(int(nums[0]), minVal, maxVal) and within_range(int(nums[1]), minVal, maxVal):
                    goodv.append(v)
                else:
                    badv.append(v)
                    bad_range.append(v)
                    # error = error + f"{v} not in the correct range. "

            # single number case
            else:
                if within_range(int(v), minVal, maxVal):
                    goodv.append(v)
                else:
                    badv.append(v)
                    bad_range.append(v)
                    # error = error + f"{v} not in the correct range. "
        else:
            badv.append(v)
            bad_input.append(v)
            # error = error + f"{v} is invalid. "

    bad_input = ', '.join(bad_input)
    bad_range = ', '.join(bad_range)
    bad_values = ', '.join(bad_values)

    if bad_input:
        error += f"{bad_input} : invalid input. "
    if bad_range:
        error += f"{bad_range} : not in the correct range. "
    if bad_values:
        error += f"{bad_values} : first cannot be larger than second."

    # error = f"{bad_input} : invalid input. {bad_range} : not in the correct range. " \
    #         f"{bad_values} : first cannot be larger than second."

    # print("this is error:", error)
    # print("goodv", goodv, len(goodv), "\nbadv", badv, len(badv))
    # print("task:", task, "values:", values, "length of values", len(values))

    if len(error) > 0:
        return [False, error]
    print("made it to bottom true for:", task)
    return [True]


# 4 digit year
def check_year(date, task):
    # must start and end with 4 digits
    pattern = re.compile(r'^\d{4}$')
    match = pattern.findall(date)

    if match:
        now = datetime.now()
        current_year = int(now.strftime("%Y"))

        if int(date) >= current_year:
            return [True]
        else:
            return [False, f"{date} LT {current_year}"]
    else:
        return [False, f"{date} is not a 4 digit number"]
