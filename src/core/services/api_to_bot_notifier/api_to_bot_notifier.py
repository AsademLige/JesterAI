from features.battles.data.repository.gino_battle_repository import GinoBattleRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.user.data.dtos.user_dto import User
from aiogram.exceptions import TelegramBadRequest
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from redis.asyncio import Redis
from typing import Optional
from aiogram import Bot
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class ApiToBotNotifier:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.prefs = Prefs()
            self.bot = Bot(token=self.prefs.bot_token)
            self.battle_repo = GinoBattleRepository()
            self.user_repo = GinoUserRepository()
            # Формат: { user_tg_id: {"message_id": int, "chat_id": int} }
            self.pending_messages = {}
            self._initialized = True

    async def redis_listener(self):
        redis_client = Redis(host='redis-broker', port=6379, decode_responses=True)
        pubsub = redis_client.pubsub()
        
        try:
            await pubsub.subscribe("bot_notifications")
            logger.info("Redis listener started, subscribed to 'bot_notifications'")
            
            async for message in pubsub.listen():
                if message['type'] != 'message':
                    continue
                
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled, cleaning up...")
        except Exception as e:
            logger.error(f"Redis listener error: {e}", exc_info=True)
        finally:
            try:
                await pubsub.unsubscribe("bot_notifications")
                await pubsub.close()
                await redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing pubsub/redis: {e}")
            logger.info("Redis listener stopped")

    async def _process_message(self, message: dict):
        raw_data = message["data"]
        try:
            log_data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, raw data: {raw_data}")
            return
        
        action = log_data.get("action")
        user_tg_id = log_data.get("user_tg_id")
        
        if not user_tg_id:
            logger.warning(f"No user_tg_id in message: {log_data}")
            return
        
        user = await self.user_repo.get_user(tg_id=user_tg_id)
        if not user:
            logger.warning(f"User {user_tg_id} not found in DB")
            return
        
        if action == "battle_start":
            await self._handle_battle_start(user)
        elif action == "battle_end_message":
            await self._handle_battle_end_message(user, log_data)
        elif action == "notification":
            await self._handle_notification(user, log_data)
        else:
            logger.warning(f"Unknown action: {action}")

    async def _handle_battle_start(self, user: User):
        """Удаляем отслеживаемое сообщение при старте боя"""
        try:
            tracked = self.pending_messages.pop(user.tg_id, None)
            
            if tracked:
                try:
                    await self.bot.delete_message(
                        chat_id=tracked["chat_id"], 
                        message_id=tracked["message_id"]
                    )
                    logger.info(f"Deleted pending message for user {user.tg_id}")
                except Exception as e:
                    logger.warning(f"Could not delete tracked message for {user.tg_id}: {e}")
            else:
                logger.info(f"Battle start: no pending message to delete for user {user.tg_id}")
                
        except Exception as e:
            logger.error(f"Error in battle_start handler: {e}", exc_info=True)

    async def _handle_battle_end_message(self, user: User, log_data: dict):
        """Просто отправляет готовое сообщение, сформированное в API"""
        text = log_data.get("text", "Бой завершен!")
        await self._send_message(user, text, delete_after=30)

    async def _handle_notification(self, user: User, log_data: dict):
        if (log_data.get("text")):
            await self._send_message(user, log_data["text"], delete_after=log_data["delete_delay"])

    async def _send_message(self, user: User, text: str, delete_after: Optional[int] = None):
        try:
            message = await self.bot.send_message(
                user.chat_id,
                text,
                parse_mode=ParseMode.HTML
            )
            
            if delete_after:
                asyncio.create_task(self._delete_message_delayed(message, delete_after))
                
        except TelegramBadRequest as e:
            logger.warning(f"Telegram bad request for user {user.tg_id}: {e}")
        except Exception as e:
            logger.error(f"Error sending message to user {user.tg_id}: {e}", exc_info=True)

    async def _delete_message_delayed(self, message, delay: int):
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except Exception as e:
            logger.debug(f"Could not delete message: {e}")