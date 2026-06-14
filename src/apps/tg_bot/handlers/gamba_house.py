from apps.tg_bot.keyboards.callback_fabrics import DiceGameCF, GambaChoiceCF, GladiatorsCF, TrashLotoCF
from apps.tg_bot.keyboards.gamba_house_keyboard import GambaHouseKeyboard
from apps.tg_bot.providers.random_provider import TelegramRandomProvider
from domain.controllers.rights_controller import RightsController
from apps.tg_bot.keyboards.battle_keyboard import BattleKeyboard
from aiogram.types import FSInputFile, Message, CallbackQuery
from features.battles.battle_unit_entity import BattleUnit
from features.battles.battle_manager import BattleManager
from core.data.models.user_stats_model import UserStats
from core.utils.safe_edit import SafeEditMessage
from core.data.datasource import DataBase
from core.consts.dictionary import Dictionary
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.utils.enums import BattlePhases
from core.consts.consts import Consts
from aiogram.fsm.context import FSMContext
from typing import List, Optional, Tuple
from datetime import timedelta, datetime
from core.consts.config import Prefs
from core.utils.utils import Utils
from core.data.models.user_model import User
from aiogram.enums import ParseMode
from aiogram.types import Message
import asyncio
import random
import math
import os

from aiogram import Router, F
from aiogram import Bot

from features.gamba_house.domain.trash_loto_manager import TrashLotoManager
from features.gamba_house.domain.dice_manager import DiceGameManager

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
gamba_house_kb = GambaHouseKeyboard()
combat_kb = BattleKeyboard()
db = DataBase()
rt = Router()
rp = TelegramRandomProvider(bot)

dice_manager = DiceGameManager(db, dict)
trash_loto_manager = TrashLotoManager(db, dict)

###Открываем меню гамбы
@rt.message(StateFilter(None), Command(cn.gamba_house))
async def gamba_house(message: Message, state: FSMContext):
    user:User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await state.update_data(user=user)
    answer:Message
    await message.delete()

    users_stat:List[UserStats] = await db.get_users_stat_by_chat(message.chat.id)
    total:int = 0

    for stat in users_stat:
        total += stat.trash_loto_spins * 5 - stat.trash_loto_money_wins
        total += stat.gladiators_bet - stat.gladiators_bet_win

    photo = FSInputFile(os.path.join(Consts.IMAGES_DIR, f"gamba_house.webp"))

    answer = await bot.send_photo(user.chat_id, photo, caption=dict.gamba_house_description(total, user),
                                    reply_markup=gamba_house_kb.gamba_choice(user),
                                    parse_mode=ParseMode.HTML)
    
    await Utils.delete_old_message([answer], 15)

@rt.callback_query(GambaChoiceCF.filter(F.action == "exit"))
async def gamba_house_exit(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    try:
        await callback.message.delete()
    except:
        return

###Дайсы крутятся, монетки мутятся
@rt.callback_query(DiceGameCF.filter(F.action == "dice_game"))
async def dice_game(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    delta = await dice_manager.check_cool_down(user)
    if delta:
        answer = await bot.send_message(user.chat_id, dict.timer_message(user, Utils.timedelta_to_hhmm(delta)),
                                        parse_mode=ParseMode.HTML)
        return await Utils.delete_old_message([answer], 10)

    await callback.message.edit_caption( dict.dice_game_start, 
                     reply_markup = gamba_house_kb.dice_choice(user),
                     parse_mode=ParseMode.HTML)
    await state.update_data(user = user)

    await Utils.delete_old_message([callback.message], 15)

###Дайсы крутятся, монетки мутятся
@rt.callback_query(DiceGameCF.filter(F.action))
async def dice_game_start(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    
    user = state_data["user"]
    
    delta = await dice_manager.check_cool_down(user)
    if delta:
        answer = await bot.send_message(user.chat_id, dict.timer_message(user, Utils.timedelta_to_hhmm(delta)),
                                        parse_mode=ParseMode.HTML)
        return await Utils.delete_old_message([answer], 10)

    result = await dice_manager.play(user, callback_data.action, rp)
    
    if result["is_minor_win"]:
        msg = await bot.send_message(user.chat_id, dict.dice_minor_win(user, result["dice_values"], result["award"]), 
                                     parse_mode=ParseMode.HTML)
    elif result["is_major_win"]:
        msg = await bot.send_message(user.chat_id, dict.dice_major_win(user, result["dice_values"], result["award"]),
                                     parse_mode=ParseMode.HTML)
    else:
        msg = await bot.send_message(user.chat_id, dict.dice_lose(user, result["dice_values"]),
                                     parse_mode=ParseMode.HTML)
        
    messages_to_delete = result["sent_messages"] + [msg]
    await Utils.delete_old_message(messages_to_delete, 10)

###Бесполезная трата денег
@rt.callback_query(TrashLotoCF.filter(F.action == "trash_loto"))
async def trash_loto(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    have_delete_rights = (await RightsController.check_is_admin(callback.message.chat.id) and
        await RightsController.check_delete_messages_rights(callback.message.chat.id))
    await callback.message.delete()
    
    user: User = await db.get_user_by_chat_id(callback.from_user.id, callback.message.chat.id)
    
    loto_cost:int = 5

    if (user.money < loto_cost):
        answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                            parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([callback.message, answer])
        return
    
    result = await trash_loto_manager.play(user, loto_cost, rp)
        
    await asyncio.sleep(3) 

    if (result["error"]):
        msg = await bot.send_message(user.chat_id, dict.trash_loto_error, 
                                        parse_mode=ParseMode.HTML)
    else:
        msg = await bot.send_message(user.chat_id, result["slot_result_msg"],
                                        parse_mode=ParseMode.HTML)
    
    if (have_delete_rights):
        await Utils.delete_old_message([] if (result["is_major_win"] or result["is_jackpot"]) 
                                       else [result["slot_msg"], msg], 5)
        
###Гладиаторы!
@rt.callback_query(GladiatorsCF.filter(F.action == "gladiators"))
async def gladiators(callback: CallbackQuery, callback_data: GladiatorsCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    await callback.message.delete()

    delta:timedelta = Utils.get_time_delta(user.last_gladiators_bet, 1)
    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return
    
    global game_controller
    from bot import game_controller
    if (game_controller.get_battle(user)):
        answer = await callback.message.answer("⚔️ Ставка уже сделана!")
        await Utils.delete_old_message([answer], 5)
        return
    
    await state.update_data(user=user)

    answer = await bot.send_message(user.chat_id, await game_controller.prepare_gladiators(user),
                                    reply_markup=combat_kb.battle_keyboard(user, game_controller.get_battle(user)),
                                    parse_mode=ParseMode.HTML)
    
###Ставка на гладиатора
@rt.callback_query(GladiatorsCF.filter(F.action == "bet"))
async def gladiators_bet(callback: CallbackQuery, callback_data: GladiatorsCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]
    global game_controller

    if (user.tg_id != callback_data.user_id or not callback_data.bet):
        return

    if (user.money < callback_data.bet):
        await game_controller.delete_battle(user.tg_id)
        await callback.message.delete()
        answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                            parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([callback.message, answer])
        return
    
    if (not await db.update_user(user, {User.money.name : User.money - callback_data.bet})):
        await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        return
    
    await db.update_user_status(user.id, 
        {UserStats.gladiators_bet.name :  UserStats.gladiators_bet + callback_data.bet})
    
    battle:BattleManager = game_controller.get_battle(user)

    if (battle.phase == BattlePhases.PREPARE):
        game_controller.start_battle(user, callback.message)

    if (type(callback_data.gladiator_id) is int):
        battle.members[callback_data.gladiator_id].bet(callback_data.bet)
    
    status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)
    if (status):
        await callback.message.edit_text(status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)
    
###Бой гладиаторов
@rt.callback_query(GladiatorsCF.filter(F.action == "gladiators_fight"))
async def gladiators_fight(callback: CallbackQuery, callback_data: GladiatorsCF, state: FSMContext):
    if (await SafeEditMessage.is_locked(callback)): return
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    global game_controller
    battle:BattleManager = game_controller.get_battle(user)
    status:Optional[Tuple[str, BattlePhases, Optional[BattleUnit]]] = await game_controller.get_battle_status(user)

    if (status):
        await SafeEditMessage.safe_edit(callback,status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)