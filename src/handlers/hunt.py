from src.models.battle_member_model import BattleMember, BodyParts, MemberStrategy
from src.domain.controllers.battle_controller import BattleController, BattlePhases
from src.keyboards.battle_keyboard import BattleKeyboard
from src.keyboards.callback_fabrics import BattleCF
from typing import Any, Dict, List, Optional, Tuple
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from bot import game_controller

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
combat_kb = BattleKeyboard()
db = DataBase()
rt = Router()

###Отправиться на охоту
@rt.message(StateFilter(None), Command(cn.hunt))
async def hunt_init(message: Message, state: FSMContext):
    user:User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    answer:Message

    await message.delete()

    global game_controller
    if (game_controller.get_battle(user)):
        answer = await message.answer("⚔️ Ты уже в бою!")
        await Utils.delete_old_message([answer], 5)
        return

    await state.update_data(user=user)

    answer = await bot.send_message(user.chat_id, await game_controller.prepare_hunt(user),
                                    reply_markup=combat_kb.battle_keyboard(user, game_controller.get_battle(user)),
                                    parse_mode=ParseMode.HTML)

###Начало боя
@rt.callback_query(BattleCF.filter(F.action.in_([a.value for a in MemberStrategy])))
async def on_hunt_attack(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    if (battle.phase == BattlePhases.PREPARE):
        game_controller.start_battle(user, callback.message)

    battle.active_member.choice_strategy(MemberStrategy(callback_data.action))

    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)
    if (status):
        await callback.message.edit_text(status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle),
                                        parse_mode=ParseMode.HTML)

###Действие атаки
@rt.callback_query(BattleCF.filter(F.action == "attack"))
async def on_turn_attack(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    battle.active_member.take_aim(list(BodyParts)[callback_data.part])
    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)

    if (status):
        await callback.message.edit_text(status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)

###Действие защиты
@rt.callback_query(BattleCF.filter(F.action == "defense"))
async def on_turn_defense(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    battle.active_member.protect(list(BodyParts)[callback_data.part])
    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)
    if (status):
        await callback.message.edit_text(status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)

###Побег от монстра
@rt.callback_query(BattleCF.filter(F.action == "escape"))
async def on_hunt_escape(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    status:str = game_controller.escape_battle(user)
    if (status):
        await callback.message.edit_text(status,
                                        parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text("⛔️ Неожиданная ошибка...",
                                        parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([callback.message], 10)
    
