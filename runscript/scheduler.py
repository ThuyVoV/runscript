from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.events import JobExecutionEvent

from .helper_func.run_task import task_success_listener, task_missed_listener, task_exception_listener

import logging

# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

jobStores = {
    'default': SQLAlchemyJobStore(url='sqlite:///db.sqlite3')
}
executors = {
    'default': ThreadPoolExecutor(20)
}


def job_listener(event):
    # print("this this event", EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED)
    # print("stuff:", event.scheduled_run_time, event.retval, event.exception, event.traceback)
    print(f"{event.retval} ran ok")


def miss_job(event):
    print(f"THE EVENT AT {event.scheduled_run_time} WAS MISSED")
    print("more stuff:", event.scheduled_run_time, event.retval, event.exception, event.traceback, event.job_id)


scheduler = BackgroundScheduler(jobstores=jobStores, executors=executors)
scheduler.add_listener(task_success_listener, EVENT_JOB_EXECUTED)
scheduler.add_listener(task_exception_listener, EVENT_JOB_ERROR)
scheduler.add_listener(task_missed_listener, EVENT_JOB_MISSED)

scheduler.start()
