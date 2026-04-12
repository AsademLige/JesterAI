from src.data.dictionary import Dictionary
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
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

    ###Оставь надежду, всяк сюда входящий!
    gamba_house = "gamba_house"

    ###Магазин
    store = "store"

    ###Список активных запланированных на выполнение команд
    jobs = "jobs"

    ###Данные о выигрышах пользователей
    winners_log = "winners_log"

    ###Охота на монстров
    hunt = "hunt"

    @staticmethod
    async def setup_bot_commands():
        await bot.set_my_commands([
            BotCommand(command=Commands.me, description=dict.me),
            BotCommand(command=Commands.pencil, description=dict.pencil),
            BotCommand(command=Commands.gamba_house, description=dict.gamba_house),
            BotCommand(command=Commands.hunt, description=dict.hunt),
            BotCommand(command=Commands.store, description=dict.store),
            BotCommand(command=Commands.leaderboard, description=dict.leaderboard_description),
            BotCommand(command=Commands.winners_log, description=dict.winners_log_description),
            BotCommand(command=Commands.sticker_pack, description=dict.sticker_pack),
            BotCommand(command=Commands.help, description=dict.help),
        ], scope=BotCommandScopeAllGroupChats())

        await bot.set_my_commands([], scope=BotCommandScopeAllPrivateChats())