from src.data.dictionary import Dictionary
from aiogram.types import BotCommand
from src.data.config import Prefs
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class Commands():
    ###Начать
    start = "start"

    ###Узнать возможности бота
    help = "help"

    ###Создать новый стикер-пак
    create_sticker_set = "create_sticker_set"

    ###Создать новый стикер-пак
    create_sticker_set = "create_sticker_set"

    ###Изменить стикер в пак
    edit_sticker_set = "edit_sticker_set"

    async def setup_bot_commands():
        bot_commands = [
        BotCommand(command="help", description=Dictionary.help),
        ]
        await bot.set_my_commands(bot_commands)