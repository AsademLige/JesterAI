from core.providers.random_provider import IRandomProvider
from typing import Any, List, Tuple
from aiogram import Bot
import asyncio

class TelegramRandomProvider(IRandomProvider):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def roll_dice(self, chat_id: int) -> Tuple[List[int], List[Any]]:
        dice1 = await self.bot.send_dice(chat_id, emoji='🎲')
        dice2 = await self.bot.send_dice(chat_id, emoji='🎲')
        await asyncio.sleep(7)
        return [dice1.dice.value, dice2.dice.value], [dice1, dice2]

    async def spin_slot(self, chat_id: int) -> Tuple[int, Any]:
        result = await self.bot.send_dice(chat_id, emoji='🎰')
        await asyncio.sleep(3)
        return result.dice.value, result