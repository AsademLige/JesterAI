from src.data.dictionary import Dictionary
from aiogram.types import BotCommand
from src.data.config import Prefs
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
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

    ###Ссылка на актуальный набор стикеров бота
    sticker_pack = "sticker_pack"

    ###Информация о пользователе
    me = "me"

    ###Интерактивное действие с текущим размером пользователя
    pencil = "pencil"
    
    ###Команда отображения таблицы лидеров
    leaderboard = "leaderboard"

    ###Гамба!
    trash_loto = "trash_loto"

    ###Список активных запланированных на выполнение команд
    jobs = "jobs"

    @staticmethod
    async def setup_bot_commands():
        await bot.set_my_commands([
            BotCommand(command=Commands.me, description=dict.me),
            BotCommand(command=Commands.pencil, description=dict.pencil),
            BotCommand(command=Commands.leaderboard, description=dict.leaderboard_description),
            BotCommand(command=Commands.trash_loto, description=dict.trash_loto),
            BotCommand(command=Commands.sticker_pack, description=dict.sticker_pack),
            BotCommand(command=Commands.help, description=dict.help),
        ])