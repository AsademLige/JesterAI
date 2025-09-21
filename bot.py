from src.domain.middlewares.registration_middleware import RegistrationMiddleware
import src.handlers.create_sticker_set as create_sticker_set
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
from src.models.db_model import on_startup
from src.handlers.commands import Commands
from src.data.config import Prefs
import src.handlers.start as start
import asyncio
import logging

###python3.9 bot.py - start bot
###Ctrl+c - stop bot

prefs = Prefs()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=prefs.bot_token)
dp = Dispatcher()

async def main():
    dp.include_routers(start.rt, 
                      create_sticker_set.rt,)
    dp.message.outer_middleware(RegistrationMiddleware())
    await on_startup(dp)
    await Commands.setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())