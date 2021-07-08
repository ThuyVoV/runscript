from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobStores = {
    'default': SQLAlchemyJobStore(url='sqlite:///db.sqlite3')
}

scheduler = BackgroundScheduler(jobstores=jobStores)
scheduler.start()
