from django.conf import settings
from django.db import connection

from functools import wraps

from ..models import UploadFileModel, ScriptList
from .view_helper import get_logs_dir

import datetime
import os
import re
import subprocess
import sys
import time


def get_next_run_time(name):
    # get the time of next task run
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT next_run_time FROM apscheduler_jobs where id = '{name}'")
        row = cursor.fetchone()

    if row is not None:
        epoch_time = int(row[0])
        return datetime.datetime.fromtimestamp(epoch_time).strftime('%a %b %d, %Y %-I:%M:%S %p')

    return None


def run_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ex: Thu Jul 22, 2021 12:55:00 PM
        current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
        f_current_time = datetime.datetime.now().strftime('%a_%b%d_%Y_%I%M%S%p')

        upload_file = args[0]
        script_path = upload_file.upload_file.path
        script_name = upload_file.script_name
        arguments = args[1]
        ext = script_path.split('.')[-1]
        log_location = f"{get_logs_dir()}{script_name}_{f_current_time}.txt"
        print('script name:', script_name, 'path', script_path, "@", f_current_time)

        t = open(log_location, 'w')
        if ext == 'sh':
            subprocess.call(['sh', script_path] + arguments, stdout=t)
        elif ext == 'py':
            subprocess.run([sys.executable, script_path] + arguments, text=True, stdout=t)
        t.close()

        # read the log output in the file
        t = open(log_location, 'r')
        log = t.read()
        t.close()

        # create a log in the database
        script_list_id = UploadFileModel.objects.get(pk=upload_file.id).script_list_id
        script_list = ScriptList.objects.get(pk=script_list_id)
        script_list.tasklog_set.create(task_id=script_name, time_ran=current_time, task_output=log)

        return func(*args, **kwargs)

    return wrapper


@run_task
def do_task(*args):
    time.sleep(.05)
    upload_file = args[0]

    # update the last_run and next_run values
    upload_file.filetask_set.filter(file_task_name=upload_file.script_name).update(
        last_run=datetime.datetime.now().strftime('%a %b %d, %Y %-I:%M:%S %p'),
        next_run=get_next_run_time(upload_file.script_name)
    )


def validate_dates(task_dates, context):
    # if any entry is left blank, replace it with a *
    for i, date in enumerate(task_dates):
        if date == '':
            if i != 7:
                task_dates[i] = '*'
            else:
                task_dates[i] = '0'

    month_min, month_max = 1, 12
    day_min, day_max = 1, 31
    week_min, week_max = 1, 53
    day_of_week_min, day_of_week_max = 0, 6
    hour_min, hour_max = 0, 23
    minute_min, minute_max = 0, 59
    second_min, second_max = 0, 59

    # task_date[i] is the input string for the field
    # task_scheduler[i] is the name of the input field (task_year, task_month, etc)
    for i, task in enumerate(context['task_scheduler']):
        if task_dates[i] == '*':
            context[task] = [True]
            continue

        task_dates[i] = parse_date(task_dates[i])

        if i == 0:  # year
            context[task] = check_year(task_dates[i], context['task_scheduler'][i])
        elif i == 1:  # month
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], month_min, month_max)
        elif i == 2:  # day
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], day_min, day_max)
        elif i == 3:  # week
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], week_min, week_max)
        elif i == 4:  # day of week
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], day_of_week_min,
                                             day_of_week_max)
        elif i == 5:  # hour
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], hour_min, hour_max)
        elif i == 6:  # minute
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], minute_min, minute_max)
        elif i == 7:  # second
            context[task] = check_date_range(task_dates[i], context['task_scheduler'][i], second_min, second_max)


def parse_date(date):
    # remove ending comma
    if date[-1] == ',':
        date = date[:len(date) - 1:]

    # split everything by comma
    date = date.split(',')

    while "" in date:
        date.remove("")
    # removing extra spaces, strip leading 0, remove empty strings
    date = [d.strip(' ') for d in date]
    date = [d.lstrip('0') or '0' for d in date]
    date = ['0' + d if d.startswith('-') else d for d in date]

    while "" in date:
        date.remove("")

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

    return date


def within_range(value, minVal, maxVal):
    if minVal <= value <= maxVal:
        return True

    return False


def check_date_range(date, task, minVal, maxVal):
    # pattern, must be a 1 or 2 digit integer
    # if it is a range of number, the two numbers must be separated by a dash
    pattern = re.compile(r'^\d{1,2}(?:\-\d{1,2})?$')
    values = date.split(',')
    error = ""

    bad_input, bad_range, bad_values = [], [], []

    for v in values:
        match = pattern.findall(v)
        if match:
            # range case x-y
            if '-' in v:
                nums = v.split('-')
                if int(nums[0]) > int(nums[1]):
                    bad_values.append(v)
                    continue

                if within_range(int(nums[0]), minVal, maxVal) and within_range(int(nums[1]), minVal, maxVal):
                    continue
                else:
                    bad_range.append(v)

            # single number case
            else:
                if within_range(int(v), minVal, maxVal):
                    continue
                else:
                    bad_range.append(v)
        else:
            bad_input.append(v)

    bad_input = ', '.join(bad_input)
    bad_range = ', '.join(bad_range)
    bad_values = ', '.join(bad_values)

    if bad_input:
        error += f"{bad_input} : invalid input. "
    if bad_range:
        error += f"{bad_range} : not in the correct range. "
    if bad_values:
        error += f"{bad_values} : first cannot be larger than second."

    if len(error) > 0:
        return [False, error]

    return [True]


# 4 digit year
def check_year(date, task):
    # must start and end with 4 digits
    pattern = re.compile(r'^\d{4}$')
    match = pattern.findall(date)

    if match:
        now = datetime.datetime.now()
        current_year = int(now.strftime("%Y"))

        if int(date) >= current_year:
            return [True]
        else:
            return [False, f"{date} LT {current_year}"]
    else:
        return [False, f"{date} is not a 4 digit number"]
