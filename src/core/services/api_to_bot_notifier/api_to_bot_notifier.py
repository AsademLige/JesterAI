from features.battles.data.repository.gino_battle_repository import GinoBattleRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.battles.game_controller import GameController
from features.user.data.dtos.user_dto import User
from aiogram.exceptions import TelegramBadRequest
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from redis.asyncio import Redis
from typing import Optional
from aiogram import Bot
import asyncio
import logging
import random
import json

logger = logging.getLogger(__name__)


class ApiToBotNotifier:
    _instance = None
    _initialized = False

    def __new__(cls, game_controller: GameController, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, game_controller: GameController):
        if not self._initialized:
            self.prefs = Prefs()
            self.bot = Bot(token=self.prefs.bot_token)
            self.battle_repo = GinoBattleRepository()
            self.user_repo = GinoUserRepository()
            self.game_controller = game_controller
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
            except Exception as e:
                logger.warning(f"Error closing pubsub: {e}")
            try:
                await redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing redis client: {e}")
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
        elif action == "battle_end":
            await self._handle_battle_end(user, log_data)
        else:
            logger.warning(f"Unknown action: {action}")

    async def _handle_battle_start(self, user: User):
        try:
            messages = self.game_controller.get_history(user)
            logger.info(f"Battle start: user={user.tg_id}, history_messages={len(messages) if messages else 0}")
            
            if messages:
                await Utils.delete_old_message(messages, 2)
            
            self.game_controller.clear_history(user)
        except Exception as e:
            logger.error(f"Error in battle_start handler: {e}", exc_info=True)

    async def _handle_battle_end(self, user: User, log_data: dict):
        try:
            validation = log_data.get('validation', {})
            is_valid = validation.get('valid', False)
            status = validation.get('status')
            
            if is_valid and status == "victory":
                await self._handle_victory(user, validation)
            elif is_valid and status == "death":
                await self._handle_death(user)
            else:
                logger.info(f"Battle end with invalid result: user={user.tg_id}, status={status}, valid={is_valid}")
                await self._send_message(user, "⚠️ Битва завершена с ошибкой валидации")
            
            await self.game_controller.delete_battle(user.tg_id)
            
        except Exception as e:
            logger.error(f"Error in battle_end handler: {e}", exc_info=True)

    async def _handle_victory(self, user: User, validation : dict):
        try:
            battle = self.game_controller.get_battle(user)
            if not battle:
                logger.warning(f"No battle found for victory: user={user.tg_id}")
                return
            
            monster = battle.get_opponent()
            if not monster:
                logger.warning(f"No opponent in battle: user={user.tg_id}")
                return
            
            if monster.inventory and len(monster.inventory) > 0:
                item_id = monster.inventory[0][0] if len(monster.inventory[0]) > 0 else None
                item_qty = monster.inventory[0][1] if len(monster.inventory[0]) > 1 else 1
                money_bonus = (validation["combo_max"] // 10) + (validation["crit_damage"])
                
                if item_id:
                    item_success = await self.user_repo.user_item_transaction(user, item_id, item_qty)
                else:
                    item_success = True
                
                money_success = await self.user_repo.update(
                    user,
                    money=user.money + (monster.inventory[1] if len(monster.inventory) > 1 else 0) + money_bonus,
                    good_hunting_count=user.good_hunting_count + 1
                )
                
                if item_success and money_success:
                    loot_text = Dictionary().hunt_loot(monster.inventory, money_bonus) if monster.inventory else ""
                    message_text = (
                        f'⚔️ <a href="tg://user?id={user.tg_id}">{user.tg_name}</a> убил монстра!\n\n'
                        f'📦 {loot_text}' if loot_text else
                        f'⚔️ <a href="tg://user?id={user.tg_id}">{user.tg_name}</a> убил монстра!'
                    )
                else:
                    message_text = f'⚔️ <a href="tg://user?id={user.tg_id}">{user.tg_name}</a> убил монстра, но награда не выдана'
            else:
                await self.user_repo.update(user, good_hunting_count=user.good_hunting_count + 1)
                message_text = f'⚔️ <a href="tg://user?id={user.tg_id}">{user.tg_name}</a> убил монстра!'
            
            await self._send_message(user, message_text, delete_after=60)
            
        except Exception as e:
            logger.error(f"Error in victory handler: {e}", exc_info=True)

    async def _handle_death(self, user: User):
        try:
            death_message = random.choice(Dictionary().battle_dead_description)
            message_text = f'💀 <a href="tg://user?id={user.tg_id}">{user.tg_name}</a> {death_message}'
            await self._send_message(user, message_text, delete_after=60)
        except Exception as e:
            logger.error(f"Error in death handler: {e}", exc_info=True)

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