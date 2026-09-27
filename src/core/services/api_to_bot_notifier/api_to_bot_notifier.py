import json

from redis import Redis

from core.consts.config import Prefs
from aiogram import Bot
from aiohttp import web

class ApiToBotNotifier():
    prefs = Prefs()
    bot = Bot(token=prefs.bot_token)
    redis_client = Redis(host='redis-broker', port=6379, decode_responses=True)
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            
    async def redis_listener(self):
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("bot_notifications")
        
        try:
            async for message in pubsub.listen():
                if message['type'] != 'message':
                    continue
                    
                try:
                    data = json.loads(message['data'])

                    print(f"cdlog {data}")
                        
                except Exception as e:
                    print(f"Ошибка при обработке сообщения из Redis: {e}")
        finally:
            await pubsub.unsubscribe("bot_notifications")
            await self.redis_client.close()