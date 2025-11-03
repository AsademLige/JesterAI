from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from src.services.data_base.db_config import POSTGRES_URI
from typing import Optional
import gino

class Scheduler():
    _instance = None

    scheduler:Optional[BackgroundScheduler] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def init(self):
        jobstores = {
            'default': SQLAlchemyJobStore(engine=await gino.create_engine(POSTGRES_URI))
        }
        
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        
