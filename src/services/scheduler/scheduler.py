from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from src.services.scheduler.scheduler_jobs import SchedulerJobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.data_base.db_config import POSTGRES_URI   
from src.domain.utils.app_herald import AppHerald
from datetime import datetime, timedelta
from typing import Optional
import pytz

class Scheduler():
    _instance = None
    scheduler:Optional[AsyncIOScheduler] = None
    jobs:SchedulerJobs = SchedulerJobs()
    logger:AppHerald = AppHerald()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def init(self):
        self.logger.logs_init("apscheduler")

        jobstores = {
            'default': SQLAlchemyJobStore(url=POSTGRES_URI)
        }
        
        self.scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=pytz.timezone('Europe/Moscow'))

        # self.scheduler.add_job(self.jobs.weekly_top, 'cron', id='weekly_top', 
        #                        replace_existing=True, day_of_week='fri', hour=11, minute=30,
        #                        misfire_grace_time=15,)
        self.scheduler.add_job(self.jobs.day_draw, 'cron', id='day_draw', 
                               replace_existing=True, misfire_grace_time=15,
                               hour=10, minute=30)
        self.scheduler.add_job(self.jobs.day_salary, 'cron', id='day_salary', 
                               replace_existing=True, misfire_grace_time=15,
                               hour=18, minute=00)
        # Команда без автоматического выполнения (проще дергать из одного списка задач в случае необходимости)
        self.scheduler.add_job(self.jobs.tech_work_compensation, 'date', run_date=datetime.now() + timedelta(days=1000), id='tech_work_compensation', 
                               replace_existing=True)
    
        self.scheduler.start()
        
        #TODO(Илья): Убрать после релиза 0.0.3
        try:
            self.scheduler.remove_job('weekly_top')
            print("Job 'my_job_id' removed successfully.")
        except:
            print("Job not found or already removed.")

        print(f"Scheduler init, active jobs: {len(self.scheduler.get_jobs())}")
        
        for job in self.scheduler.get_jobs():
            print(f"job: {job}")
