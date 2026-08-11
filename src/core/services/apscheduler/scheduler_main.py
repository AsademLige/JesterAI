from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.store.data.repository.store_repository import IStoreRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler, BaseScheduler
from features.user.data.repository.user_repository import IUserRepository
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from core.services.apscheduler.global_jobs import GlobalJobs
from core.services.data_base.db_config import POSTGRES_URI
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
import asyncio
import pytz

class Scheduler():
    _instance = None
    _lock = asyncio.Lock() 

    def __init__(self, scheduler:BaseScheduler, 
                 notification_handler,
                 user_repo:IUserRepository, 
                 store_repo:IStoreRepository, 
                 settings_repo:IBotSettingsRepository):
        
        self.notifier = notification_handler 
        self.game_core = GlobalJobs(
            user_repo=user_repo,
            store_repo=store_repo,
            settings_repo=settings_repo
        )
        self.core = scheduler

        self.core.start()

        print(f"Scheduler init, active jobs: {len(self.core.get_jobs())}")
        
        for job in self.core.get_jobs():
            print(f"job: {job}")
        pass

    @classmethod
    async def local(cls, notification_handler,
                        user_repo:IUserRepository, 
                        store_repo:IStoreRepository, 
                        settings_repo:IBotSettingsRepository):
        
        jobstores = {'default': MemoryJobStore()}
        scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=pytz.timezone('Europe/Moscow'))

        if cls._instance is None:
            cls._instance = cls(scheduler = scheduler,
                    notification_handler = notification_handler,
                    user_repo = user_repo,
                    store_repo = store_repo,
                    settings_repo = settings_repo)
    
        await cls._instance.init(scheduler)
        return cls._instance
    
    @classmethod
    async def sql_alchemy(cls, notification_handler,
                        user_repo:IUserRepository, 
                        store_repo:IStoreRepository, 
                        settings_repo:IBotSettingsRepository):
        
        jobstores = {'default': MemoryJobStore(),
                     'persistent': SQLAlchemyJobStore(url=POSTGRES_URI)}

        scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=pytz.timezone('Europe/Moscow'))

        if cls._instance is None:
            cls._instance = cls(scheduler = scheduler,
                    notification_handler = notification_handler,
                    user_repo = user_repo,
                    store_repo = store_repo,
                    settings_repo = settings_repo)
        
        await cls._instance.init(scheduler)
        return cls._instance
    
    @classmethod
    def get_current_instance(cls) -> "Scheduler":
        if cls._instance is None:
            raise RuntimeError("Scheduler еще не был инициализирован!")
        return cls._instance

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

    async def init(self, scheduler: BaseScheduler):
        # Команда без автоматического выполнения (проще дергать из одного списка задач в случае необходимости)
        # scheduler.add_job(self.run_tech_work_compensation, 'date', run_date=datetime.now() + timedelta(days=1000), id='tech_work_compensation', 
        #                         replace_existing=True)
                
        scheduler.add_job(self.run_day_draw, 'cron', id='day_draw', 
                               replace_existing=True, misfire_grace_time=15, hour=10, minute=30)
        
        scheduler.add_job(self.run_day_salary, 'cron', id='day_salary', 
                               replace_existing=True, misfire_grace_time=15, hour=18, minute=00)

        scheduler.add_job(self.run_warehouse_update, 'cron', id='warehouse_update', 
                               replace_existing=True, misfire_grace_time=15,
                               hour=9, minute=00)
        
        # self.scheduler.add_job(
        #     BotSchedulerJobs.event_trigger, 
        #     trigger='date', 
        #     run_date=datetime.now(),
        #     id='next_bot_action',
        #     replace_existing=True,
        #     args=[self] 
        # )