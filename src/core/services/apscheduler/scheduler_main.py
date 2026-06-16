from core.services.apscheduler.global_jobs import GlobalJobs
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from features.bots.bot_scheduler_jobs import BotSchedulerJobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.services.data_base.db_config import POSTGRES_URI
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
from typing import Optional
import pytz

class Scheduler():
    _instance = None
    scheduler: Optional[AsyncIOScheduler] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, notification_handler):
        if not hasattr(self, 'initialized'):
            self.initialized = True
        
            self.notifier = notification_handler 
            self.game_core = GlobalJobs()

    async def run_day_draw(self):
        await self.game_core.day_draw(self.notifier)

    async def run_day_salary(self):
        await self.game_core.day_salary(self.notifier)

    async def run_tech_work_compensation(self):
        await self.game_core.tech_work_compensation(self.notifier)

    async def run_day_salary(self):
        await self.game_core.day_salary(self.notifier)

    async def run_warehouse_update(self):
        await self.game_core.warehouse_update(self.notifier)

    async def init(self):
        jobstores = {'default': MemoryJobStore(),
                     'persistent': SQLAlchemyJobStore(url=POSTGRES_URI)}

        self.scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=pytz.timezone('Europe/Moscow'))

        self.scheduler.add_job(self.run_day_draw, 'cron', id='day_draw', 
                               replace_existing=True, misfire_grace_time=15, hour=10, minute=30)
        
        self.scheduler.add_job(self.run_day_salary, 'cron', id='day_salary', 
                               replace_existing=True, misfire_grace_time=15, hour=18, minute=00)

        self.scheduler.add_job(self.run_warehouse_update, 'cron', id='warehouse_update', 
                               replace_existing=True, misfire_grace_time=15,
                               hour=9, minute=00)
        
        # Команда без автоматического выполнения (проще дергать из одного списка задач в случае необходимости)
        self.scheduler.add_job(self.run_tech_work_compensation, 'date', run_date=datetime.now() + timedelta(days=1000), id='tech_work_compensation', 
                               replace_existing=True)
        
        # self.scheduler.add_job(
        #     BotSchedulerJobs.event_trigger, 
        #     trigger='date', 
        #     run_date=datetime.now(),
        #     id='next_bot_action',
        #     replace_existing=True,
        #     args=[self] 
        # )

        self.scheduler.start()

        print(f"Scheduler init, active jobs: {len(self.scheduler.get_jobs())}")
        
        for job in self.scheduler.get_jobs():
            print(f"job: {job}")