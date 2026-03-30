from src.domain.utils.safe_edit import SafeEditMessage
from src.domain.controllers.battle_controller import BattleController, BattlePhases
from src.models.battle_member_model import BattleMember, BodyParts, MemberStrategy
from src.domain.controllers.items_controller import ItemsController
from src.models.user_inventory_item_model import UserInventoryItem
from src.keyboards.battle_keyboard import BattleKeyboard
from src.keyboards.callback_fabrics import BattleCF
from typing import Any, Dict, List, Optional, Tuple
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.domain.utils.enums import MemberStatus
from src.services.data_base.db import DataBase
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from src.domain.utils.utils import Utils
from src.models.user_model import User
from src.models.item_model import Item
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from bot import game_controller
from datetime import timedelta
import math

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

    delta:timedelta = Utils.get_time_delta(user.last_hunt, 1)

    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.hunt_timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

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
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    if (battle and battle.phase == BattlePhases.PREPARE):
        game_controller.start_battle(user, callback.message)

    battle.active_member.choice_strategy(MemberStrategy(callback_data.action))

    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)
    if (status):
        await SafeEditMessage.safe_edit(callback, status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle),
                                        parse_mode=ParseMode.HTML)

###Действие атаки
@rt.callback_query(BattleCF.filter(F.action == "attack"))
async def on_turn_attack(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    if (not battle): return

    battle.active_member.take_aim(list(BodyParts)[callback_data.part])
    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)

    if (status):
        await SafeEditMessage.safe_edit(callback, status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)

###Действие защиты
@rt.callback_query(BattleCF.filter(F.action == "defense"))
async def on_turn_defense(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]
    items:List[Tuple[UserInventoryItem, Item]] = []

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    if (not battle): return
    battle.active_member.protect(list(BodyParts)[callback_data.part])

    if (battle.active_member.status == MemberStatus.EXHAUSTED 
        and battle.active_member.strategy == MemberStrategy.DEFENSE):
        items = await db.get_user_heal_items(battle.active_member.entity)
        await state.update_data(items=items)

    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)
    if (status):
        status_extended:str = status[0]

        if (items):
            status_extended += "\n\n<blockquote>🎒 В сумке охотника:</blockquote>\n"
            for item in items:
                status_extended += ItemsController.effects_description(item[1]) + "\n"

        await SafeEditMessage.safe_edit(callback, status_extended,
                                        reply_markup=combat_kb.battle_keyboard(user, battle, items) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)
        
###Применение предмета лечения
@rt.callback_query(BattleCF.filter(F.action == "heal"))
async def on_hunter_heal(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]
    items:List[Tuple[UserInventoryItem, Item]] = state_data["items"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleController = game_controller.get_battle(user)
    if (not battle): return
    
    old_hp:int = battle.active_member.hp
    heal_status:Optional[Tuple[str, int]] = await ItemsController.use_heal_item(user, items[callback_data.item_index], battle.active_member)
    items = await db.get_user_heal_items(battle.active_member.entity)
    message:str = ""

    if (heal_status):
        message += heal_status[0] + f"\nHP: {BattleController.health_bar(old_hp, battle.active_member.max_hp, heal=heal_status[1])}"
    
    if (heal_status):
        await SafeEditMessage.safe_edit(callback, message,
                                        reply_markup=combat_kb.battle_keyboard(user, battle, items),
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
    status:str = await game_controller.escape_battle(user)
    if (status):
        await callback.message.edit_text(status,
                                        parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text("⛔️ Неожиданная ошибка...",
                                        parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([callback.message], 10)
    
