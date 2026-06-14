from aiogram.enums.chat_member_status import ChatMemberStatus
from core.data.datasource import DataBase
from core.consts.config import Prefs
from aiogram import Bot

db = DataBase()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class RightsController():
    @staticmethod
    async def check_is_admin(chat_id:int):
        member = await bot.get_chat_member(chat_id, bot.id)
        return member.status == ChatMemberStatus.ADMINISTRATOR

    @staticmethod
    async def check_delete_messages_rights(chat_id:int):
        member = await bot.get_chat_member(chat_id, bot.id)
        admin_member = member.model_dump()
        return admin_member.get('can_delete_messages')
        