from src.keyboards.callback_fabrics import DiceGameCF, GambaChoiceCF, GladiatorsCF, TrashLotoCF
from src.domain.controllers.battle_controller import BattleController
from src.domain.controllers.rights_controller import RightsController
from src.keyboards.gamba_house_keyboard import GambaHouseKeyboard
from aiogram.types import FSInputFile, Message, CallbackQuery
from src.keyboards.battle_keyboard import BattleKeyboard
from src.models.battle_member_model import BattleMember
from src.domain.utils.safe_edit import SafeEditMessage
from src.models.user_stats_model import UserStats
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.domain.utils.enums import BattlePhases
from src.services.data_base.db import DataBase
from src.domain.utils.consts import Consts
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from typing import List, Optional, Tuple
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
import asyncio
import random
import math
import os

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
gamba_house_kb = GambaHouseKeyboard()
combat_kb = BattleKeyboard()
db = DataBase()
rt = Router()

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
    
    delta:timedelta = Utils.get_time_delta(user.last_dice_play, 1)
    if (math.floor(delta.total_seconds() / 3600) < 0):
        await callback.message.delete()
        answer = await bot.send_message(user.chat_id, dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

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
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    await callback.message.delete()

    if (callback_data.action == "exit"): return

    if (callback_data.action == "rules"):
        message = await bot.send_message(user.chat_id, dict.dice_game_rules, 
                                                    parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([message], 60)
        return

    if (not await db.update_user(user, 
            {User.last_dice_play.name: datetime.now() })):
        await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)


    dice1 = await bot.send_dice(user.chat_id, emoji='🎲')
    dice2 = await bot.send_dice(user.chat_id, emoji='🎲')

    result = dice1.dice.value + dice2.dice.value
    
    is_minor_win:bool = (result > 7 and callback_data.action == "bigger")\
        or (result < 7 and callback_data.action == "smaller")
    
    is_major_win:bool = result == 7 and callback_data.action == "equal"

    minor_win_award = 5
    major_win_award = 15

    await asyncio.sleep(7) 

    if (is_minor_win):
        message = await bot.send_message(user.chat_id, 
                                         dict.dice_minor_win(user, [dice1.dice.value, 
                                                                    dice2.dice.value],
                                                                    minor_win_award), 
                                                    parse_mode=ParseMode.HTML)
    elif (is_major_win):
        message = await bot.send_message(user.chat_id, 
                                         dict.dice_major_win(user, [dice1.dice.value, 
                                                                    dice2.dice.value],
                                                                    major_win_award), 
                                                    parse_mode=ParseMode.HTML)
    else:
        message = await bot.send_message(user.chat_id, 
                                         dict.dice_lose(user, [dice1.dice.value, 
                                                               dice2.dice.value]), 
                                                    parse_mode=ParseMode.HTML)
    if (is_minor_win or is_major_win):
        if (not await db.update_user(user, 
                {User.money.name : User.money + (minor_win_award if is_minor_win else major_win_award),
                    })):
            await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)

        await db.add_win_log(user.id, 
                                event_type=4 if is_minor_win else 5, 
                                money=5 if is_minor_win else 15)
        
    await db.update_user_status(user.id, 
        {UserStats.dice_games.name : UserStats.dice_games + 1, 
          UserStats.dice_minor_wins.name :  UserStats.dice_minor_wins + (1 if is_minor_win else 0),
          UserStats.dice_major_wins.name :  UserStats.dice_major_wins + (1 if is_major_win else 0),
        })
    
    await Utils.delete_old_message([dice1, dice2, message], 10)

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
    
    if (not await db.update_user(user, {"money" : User.money - loto_cost})):
        await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        return
        
    result = await bot.send_dice(user.chat_id, emoji='🎰')
    await asyncio.sleep(3) 
    
    value = result.dice.value - 1

    # Индексы: 0=BAR, 1=🍒, 2=🍋, 3=777
    left = value % 4
    middle = (value // 4) % 4
    right = value // 16

    is_minor_win = (left == middle or middle == right)
    is_major_win = (left == middle == right)
    is_consolation = (left == right)
    is_jackpot = value == 63
    is_lose = not (is_jackpot or is_major_win or is_minor_win or is_consolation)

    award = 0
    length = 0

    # 777
    if is_jackpot:
        award =  random.randrange(20, 30)
        if (await db.update_user(user, {"money" : User.money + award})):
            answer = await bot.send_message(user.chat_id, dict.trash_loto_jackpot_money_award(user.tg_name, user.tg_id, award),
                                parse_mode=ParseMode.HTML)
            await db.add_win_log(user.id, event_type=0, money=award)
        else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
    #тройная комбинаций
    elif is_major_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = random.randrange(2, 3)
            if (await db.update_user(user, {"length": User.length + length, "money" : user.money})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_major_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
                await db.add_win_log(user.id, event_type=2, length=length)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(10, 15)
            if (await db.update_user(user, {"money" : User.money + award})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_major_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
                await db.add_win_log(user.id, event_type=2, money=award)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)

    # Проверка на одинаковые крайние
    elif is_consolation:
        award = random.randrange(1, 5)
        if (await db.update_user(user, {"money" : User.money + award})):
            answer = await bot.send_message(user.chat_id, dict.trash_loto_consolation_money_award(user.tg_name, user.tg_id, award),
                                parse_mode=ParseMode.HTML)
            await db.add_win_log(user.id, event_type=3, money=award)
        else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)

    # Проверка на любые две одинаковые подряд
    elif is_minor_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = 1
            if (await db.update_user(user, {"length": User.length + length, "money" : user.money})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_minor_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
                await db.add_win_log(user.id, event_type=1, length=length)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(5, 10)
            if (await db.update_user(user, {"money" : User.money + award})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_minor_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
                await db.add_win_log(user.id, event_type=1, money=award)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
    else:
        answer = await bot.send_message(user.chat_id, dict.trash_loto_lose(user.tg_name, user.tg_id),
                            parse_mode=ParseMode.HTML)
        
    await db.update_user_status(user.id, 
        {UserStats.trash_loto_spins.name : UserStats.trash_loto_spins + 1, 
        UserStats.trash_loto_money_wins.name :  UserStats.trash_loto_money_wins + award,
        UserStats.trash_loto_length_wins.name :  UserStats.trash_loto_length_wins + length,
        UserStats.trash_loto_jackpots.name :  UserStats.trash_loto_jackpots + (1 if is_jackpot else 0),
        })
    
    if (have_delete_rights):
        await Utils.delete_old_message([] if (is_major_win or is_jackpot) 
                                       else [result, answer], 5)
        
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
    
    battle:BattleController = game_controller.get_battle(user)

    if (battle.phase == BattlePhases.PREPARE):
        game_controller.start_battle(user, callback.message)

    if (type(callback_data.gladiator_id) is int):
        battle.members[callback_data.gladiator_id].bet(callback_data.bet)
    
    status:Optional[Tuple[str, BattlePhases, BattleMember]] = await game_controller.get_battle_status(user)
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
    battle:BattleController = game_controller.get_battle(user)
    status:Optional[Tuple[str, BattlePhases, Optional[BattleMember]]] = await game_controller.get_battle_status(user)

    if (status):
        await SafeEditMessage.safe_edit(callback,status[0],
                                        reply_markup=combat_kb.battle_keyboard(user, battle) \
                                        if (not status[1] == BattlePhases.BATTLE_END) else None,
                                        parse_mode=ParseMode.HTML)