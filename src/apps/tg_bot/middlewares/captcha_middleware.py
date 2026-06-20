from domain.controllers.bot_settings_controller import SettingsController
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Any, Callable, Dict, Awaitable
from aiogram.types import TelegramObject, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apps.tg_bot.commands import Commands
from core.utils.utils import Utils
from aiogram import BaseMiddleware
from datetime import timedelta
import math

class CaptchaStates(StatesGroup):
    waiting_for_button = State()

class CaptchaMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if (not event.text or (isinstance(event, Message) and event.text and not event.text.startswith(f"/{Commands.pencil}"))):
            if (event): 
                return await handler(event, data) 
            else: return
        
        settings = await SettingsController.get_settings(event.chat)

        delta:timedelta = Utils.get_time_delta(settings.last_captcha_time, 0)

        if (math.floor(delta.total_seconds() / 3600) > 0):
            await self.send_button_captcha(event, data)
            return
        
        return await handler(event, data)

        
    async def send_button_captcha(self, event: Message, data: dict):
        builder = InlineKeyboardBuilder()
        
        builder.button(
            text="✅ Я не бот",
            callback_data="verify_human"
        )
        
        builder.adjust(1)
        
        captcha_text = (
            "🤖 **Проверка на бота (и Егора с отложкой)**\n"
        )
        
        captcha = await event.answer(
            captcha_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
        
        state: FSMContext = data['state']
        await state.set_state(CaptchaStates.waiting_for_button)
        await state.update_data(captcha_message_id=captcha.message_id)
        
        try:
            await event.delete()

            await Utils.delete_old_message([captcha], 10)
            await state.clear()
        except:
            print("event not found")