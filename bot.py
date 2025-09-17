from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
from src.models.db_model import on_startup
from src.config_reader import Prefs
import asyncio
import logging

prefs = Prefs()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=prefs.bot_token)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

async def main():
    await on_startup(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())