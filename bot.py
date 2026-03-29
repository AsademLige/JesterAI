from src.domain.middlewares.registration_middleware import RegistrationMiddleware
from src.domain.middlewares.captcha_middleware import CaptchaMiddleware
from src.domain.controllers.game_controller import GameController
import src.handlers.create_sticker_set as create_sticker_set
import src.handlers.edit_sticker_set as edit_sticker_set
from src.services.scheduler.scheduler import Scheduler
import src.handlers.interactive as interactive
import src.handlers.gamba_house as gamba_house
import src.handlers.send_media as send_media
from src.data.dictionary import Dictionary
from src.models.db_model import on_startup
from src.handlers.commands import Commands
import src.handlers.captcha as captcha
import src.handlers.system as system
from aiogram import Bot, Dispatcher
import src.handlers.store as store
import src.handlers.start as start
from src.data.config import Prefs
import src.handlers.hunt as hunt
import src.handlers.user as user
import logging
import asyncio

###python3.9 bot.py - start bot
###Ctrl+c - stop bot

prefs = Prefs()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=prefs.bot_token)
dp = Dispatcher()
dict = Dictionary()
scheduler = Scheduler()

game_controller = GameController()

async def main():
    dp.include_routers(start.rt, 
                      create_sticker_set.rt,
                      edit_sticker_set.rt,
                      interactive.rt,
                      gamba_house.rt,
                      send_media.rt,
                      captcha.rt,
                      system.rt,
                      store.rt,
                      hunt.rt,
                      user.rt,
                      )
    dp.message.outer_middleware(RegistrationMiddleware())
    dp.message.outer_middleware(CaptchaMiddleware())
    await on_startup(dp)
    await dict.init()
    await scheduler.init()
    await Commands.setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())