from apps.tg_bot.providers.scheduler_provider import TelegramNotificationProvider
from core.services.apscheduler.scheduler_main import Scheduler
from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.system_keyboard import SystemKeyboard
from apps.tg_bot.keyboards.callback_fabrics import JobsCF
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from apps.tg_bot.states.system import EditJob
from core.consts.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from aiogram.types import Message
from apscheduler.job import Job
from datetime import datetime
from typing import List

from aiogram import Router, F
from aiogram import Bot


prefs = Prefs()
system_kb = SystemKeyboard()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
event_handler = TelegramNotificationProvider(bot)
user_repo = GinoUserRepository()
rt = Router()

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.jobs))
async def get_all_jobs(message: Message, state: FSMContext):
    if (not await user_repo.is_admin(message.from_user.id)):
        await message.answer("Не по масти тебе такие команды мне давать... ")    
        return

    jobs: List[Job] = Scheduler.get_current_instance().core.get_jobs()
    jobs_text:str = ""
    
    for job in jobs:
        jobs_text += f"<blockquote>📅 Задача - {job.id};</blockquote>\n"\
        f"<b>Триггер:</b> <code>{job.trigger}</code>;\n"\
        f"<b>Следующий запуск:</b> <code>{job.next_run_time}</code>\n\n"

    await state.set_state(EditJob.edit_job)
        
    await message.answer(jobs_text,
                reply_markup = system_kb.jobs_list_button(jobs),
                parse_mode=ParseMode.HTML)
    
### Выбор действия
@rt.callback_query(EditJob.edit_job, JobsCF.filter())
async def edit_sticker_set_handler(callback: CallbackQuery, callback_data: JobsCF, state: FSMContext):
    if (callback_data.action == "choice"):
        await state.update_data(job_id = callback_data.job_id)
        await callback.message.edit_text(f"📅 <b>Задача</b> - <code>{callback_data.job_id}</code>", 
                                         reply_markup = system_kb.job_edit_button_list(),
                                         parse_mode=ParseMode.HTML)
    elif (callback_data.action == "trigger"):
        state_data = await state.get_data()
        
        scheduler = Scheduler.get_current_instance()
        job:Job = scheduler.core.get_job(state_data["job_id"])
        scheduler.core.add_job(job.func, 'date', 
                                    run_date=datetime.now(), 
                                    misfire_grace_time=15)
        
        await callback.message.edit_text("🟢 Запускаем задачу...")
        await state.clear()
    elif (callback_data.action == "exit"):
        await callback.message.delete()
        await state.clear()

            


