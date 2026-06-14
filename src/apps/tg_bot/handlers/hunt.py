from features.battles.battle_unit_entity import BattleUnit, BodyParts, MemberStrategy
from features.items.data.models.user_inventory_item_model import UserInventoryItem
from features.battles.battle_manager import BattleManager, BattlePhases
from apps.tg_bot.keyboards.battle_keyboard import BattleKeyboard
from features.items.items_controller import ItemsController
from apps.tg_bot.keyboards.callback_fabrics import BattleCF
from aiogram.utils.deep_linking import create_deep_link
from features.items.data.models.item_model import Item
from typing import Any, Dict, List, Optional, Tuple
from core.utils.safe_edit import SafeEditMessage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.consts.dictionary import Dictionary
from core.data.models.user_model import User
from aiogram.fsm.context import FSMContext
from core.utils.enums import MemberStatus
from core.data.datasource import DataBase
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from aiogram.types import Message
from bot import game_controller
from datetime import timedelta
from aiogram import Router, F
from aiogram import Bot
import secrets
import asyncio
import math


prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
combat_kb = BattleKeyboard()
links_cache = {}
db = DataBase()
rt = Router()

###Отправиться на охоту
@rt.callback_query(StateFilter(None), F.data == "hub_hunt")
async def hunt_init(callback_query: CallbackQuery, state: FSMContext):
    message = callback_query.message
    
    user: User = await db.get_user_by_chat_id(callback_query.from_user.id, message.chat.id)

    await callback_query.answer()

    if (not message.chat.type == "private"):
        bot_info = await bot.me()
        await message.delete()

        payload = {
            "action" : "hunt",
            "user_id" : user.tg_id,
            "chat_id" : user.chat_id
        }

        token = secrets.token_urlsafe(8)

        asyncio.create_task(save_temp_data(token, payload))
        
        link = f"https://t.me/{bot_info.username}?start={token}"
        link_message = await bot.send_message(user.chat_id, f'⚔️ <a href="{link}">Вперед, в бой, {user.tg_name}, удачной охоты!</a>', 
                                            reply_markup=combat_kb.link_keyboard(link),
                                            parse_mode=ParseMode.HTML)

        await Utils.delete_old_message([link_message], 20)
    else:
        __hunt_init(message, state, message.chat.id) 

async def __hunt_init(message: Message, state: FSMContext, chat_id:int):
    user:User = await db.get_user_by_chat_id(message.from_user.id, chat_id)
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

    battle:Tuple[str, BattleManager] = await game_controller.prepare_hunt(user)
    await state.update_data(battle=battle[1])

    private_message = await bot.send_message(user.tg_id, battle[0],
                                    reply_markup=combat_kb.battle_keyboard(user, game_controller.get_battle(user)),
                                    parse_mode=ParseMode.HTML)

@rt.message(Command("start"))
async def hunt_deep_link(message: Message, state: FSMContext):
    if message.text and len(message.text.split()) > 1 \
        and message.text.split()[1] in links_cache:

        payload = links_cache[message.text.split()[1]]
        if (payload["action"] == "hunt"):
            await __hunt_init(message, state, payload["chat_id"])
            await Utils.delete_old_message([message], 0)
            return
        
async def save_temp_data(link_id, data, ttl=20):
    """Сохраняет данные и удаляет их через TTL секунд"""
    links_cache[link_id] = data
    await asyncio.sleep(ttl)
    links_cache.pop(link_id, None)

###Начало боя
@rt.callback_query(BattleCF.filter(F.action.in_([a.value for a in MemberStrategy])))
async def on_hunt_attack(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()

    if (not 'user' in state_data and not 'battle' in state_data): return
    global game_controller
    user: User = state_data["user"]
    battle: BattleManager = state_data["battle"]

    if (user.tg_id != callback_data.user_id):
        return
    
    if (battle.phase == BattlePhases.PREPARE):
        game_controller.start_battle(user, callback.message)

    battle.active_member.choice_strategy(MemberStrategy(callback_data.action))

    status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)
    if (status):
        await callback.answer()
        await bot.send_message(user.tg_id, status[0],
                            reply_markup=combat_kb.battle_keyboard(user, battle),
                            parse_mode=ParseMode.HTML)

###Действие атаки
@rt.callback_query(BattleCF.filter(F.action == "attack"))
async def on_turn_attack(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data and not 'battle' in state_data): return
    global game_controller
    user: User = state_data["user"]
    battle: BattleManager = state_data["battle"]

    if (user.tg_id != callback_data.user_id):
        return

    battle.active_member.take_aim(list(BodyParts)[callback_data.part])
    status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)

    if (status):
        await SafeEditMessage.safe_edit(callback, status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)

        if (status[1] == BattlePhases.BATTLE_END and callback.message.chat.type == "private"):
            result = await bot.send_message(user.chat_id, status[0],
                                parse_mode=ParseMode.HTML)
            await Utils.delete_old_message([result], 360)

###Действие защиты
@rt.callback_query(BattleCF.filter(F.action == "defense"))
async def on_turn_defense(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data and not 'battle' in state_data): return
    global game_controller
    user: User = state_data["user"]
    battle: BattleManager = state_data["battle"]
    items:List[Tuple[UserInventoryItem, Item]] = []

    if (user.tg_id != callback_data.user_id):
        return
    
    battle.active_member.protect(list(BodyParts)[callback_data.part])

    if (battle.active_member.status == MemberStatus.EXHAUSTED 
        and battle.active_member.strategy == MemberStrategy.DEFENSE):
        items = await db.get_user_heal_items(battle.active_member.entity)
        await state.update_data(items=items)

    status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)
    if (status):
        status_extended:str = status[0]

        if (items and not battle.phase == BattlePhases.BATTLE_END):
            status_extended += "\n\n<blockquote>🎒 В сумке охотника:</blockquote>\n"
            for item in items:
                status_extended += ItemsController.effects_description(item[1]) + "\n"
                
        await SafeEditMessage.safe_edit(callback, status_extended,
                                        reply_markup=combat_kb.battle_keyboard(user, battle, items) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)
        
        if (status[1] == BattlePhases.BATTLE_END and callback.message.chat.type == "private"):
            result = await bot.send_message(user.chat_id, status[0],
                                parse_mode=ParseMode.HTML)
            await Utils.delete_old_message([result], 360)
        
###Применение предмета лечения
@rt.callback_query(BattleCF.filter(F.action == "heal"))
async def on_hunter_heal(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data and not 'battle' in state_data): return
    global game_controller
    user: User = state_data["user"]
    battle: BattleManager = state_data["battle"]
    items:List[Tuple[UserInventoryItem, Item]] = state_data["items"]

    if (user.tg_id != callback_data.user_id):
        return
    
    old_hp:int = battle.active_member.hp
    heal_status:Optional[Tuple[str, int]] = await ItemsController.use_heal_item(user, items[callback_data.item_index], battle.active_member)
    items = await db.get_user_heal_items(battle.active_member.entity)
    message:str = ""

    if (heal_status):
        message += heal_status[0] + f"\nHP: {BattleManager.health_bar(old_hp, battle.active_member.max_hp, heal=heal_status[1])}"
    
    if (heal_status):
        await callback.answer()
        await bot.send_message(user.tg_id, message,
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
        await callback.answer()
        await bot.send_message(user.tg_id, status,
                                parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text("⛔️ Неожиданная ошибка...",
                                        parse_mode=ParseMode.HTML)
    
