from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

import logging

# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

jobStores = {
    'default': SQLAlchemyJobStore(url='sqlite:///db.sqlite3')
}
executors = {
    'default': ThreadPoolExecutor(20)
}

scheduler = BackgroundScheduler(jobstores=jobStores, executors=executors)
scheduler.start()
