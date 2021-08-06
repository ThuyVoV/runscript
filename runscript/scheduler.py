from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from .helper_func.run_task import task_success_listener, task_missed_listener, task_exception_listener

jobStores = {
    'default': SQLAlchemyJobStore(url='sqlite:///db.sqlite3')
}
executors = {
    'default': ThreadPoolExecutor(20)
}

scheduler = BackgroundScheduler(jobstores=jobStores, executors=executors)
scheduler.add_listener(task_success_listener, EVENT_JOB_EXECUTED)
# scheduler.add_listener(task_exception_listener, EVENT_JOB_ERROR)
scheduler.add_listener(task_missed_listener, EVENT_JOB_MISSED | EVENT_JOB_ERROR)
scheduler.remove_listener(task_exception_listener)

scheduler.start()
