from features.battles.data.repository.gino_monsters_repository import GinoMonstersRepository
from core.data.repository.gino_bot_settings_repository import GinoBotSettingsRepository
from features.store.data.repository.gino_store_repository import GinoStoreRepository
from apps.tg_bot.middlewares.registration_middleware import RegistrationMiddleware
from apps.tg_bot.providers.scheduler_provider import TelegramNotificationProvider
from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.middlewares.captcha_middleware import CaptchaMiddleware
import apps.tg_bot.handlers.create_sticker_set as create_sticker_set
import apps.tg_bot.handlers.edit_sticker_set as edit_sticker_set
from core.services.apscheduler.scheduler_main import Scheduler
from features.battles.game_controller import GameController
from core.services.data_base.db_model import on_startup
import apps.tg_bot.handlers.interactive as interactive
import apps.tg_bot.handlers.gamba_house as gamba_house
import apps.tg_bot.handlers.send_media as send_media
from core.consts.dictionary import Dictionary
import apps.tg_bot.handlers.captcha as captcha
import apps.tg_bot.handlers.system as system
import apps.tg_bot.handlers.store as store
import apps.tg_bot.handlers.start as start
from apps.tg_bot.commands import Commands
import apps.tg_bot.handlers.hunt as hunt
import apps.tg_bot.handlers.user as user
from apps.tg_bot.handlers import hub
from core.consts.config import Prefs
from aiogram import Bot, Dispatcher
import logging
import asyncio

###PYTHONPATH=src python3 bot.py - start bot
###Ctrl+c - stop bot

prefs = Prefs()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=prefs.bot_token)
dp = Dispatcher()
dict = Dictionary()
event_handler = TelegramNotificationProvider(bot)
monster_repository = GinoMonstersRepository()
user_repository = GinoUserRepository()
store_repository = GinoStoreRepository()
settings_repository = GinoBotSettingsRepository()

game_controller = GameController(user_repository, monster_repository)

async def main():
    dp.include_routers(create_sticker_set.rt,
                      edit_sticker_set.rt,
                      send_media.rt,
                      interactive.rt,
                      gamba_house.rt,
                      captcha.rt,
                      system.rt,
                      store.rt,
                      hunt.rt,
                      user.rt,
                      hub.rt,
                      ### /hunt имеет свой /start с параметрами, 
                      ### поэтому находиться выше
                      start.rt, 
                      )
    dp.message.outer_middleware(RegistrationMiddleware())
    dp.message.outer_middleware(CaptchaMiddleware())
    await on_startup(dp)
    await dict.init()
    await Scheduler.asyncIOS(event_handler.handle_event,
                             user_repo=user_repository,
                             store_repo=store_repository,
                             settings_repo=settings_repository)
    await Commands.setup_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())