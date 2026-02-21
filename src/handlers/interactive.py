from src.domain.controllers.rights_controller import RightsController
from src.keyboards.interactive_keyboard import InteractiveKeyboard
from src.domain.states.dice_game_set import DiceGameSet
from src.keyboards.callback_fabrics import DiceGameCF
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.user_model import UserModel
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import List
import asyncio
import random
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
db = DataBase()
rt = Router()

member_change_reset_time:int = 24

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.me))
async def user_information(message: Message, state: FSMContext):
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    place_in_top:int = await db.get_place_in_top_by_member(user.tg_id, user.chat_id)
    await message.delete()
    answer = await bot.send_message(user.chat_id, dict.user_information(user, place_in_top),
                         parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 15)
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()
    delta:timedelta = Utils.get_last_member_check_delta(user.last_length_check)

    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    action = random.choices([1, 2])
    length_change:int = (random.randrange(2, 5) * -1) if (action[0] == 1) else random.randrange(1, 7)

    if (await db.update_user(user, {
        "length": user.length + length_change,
        "last_length_check" : datetime.now()
    })):
        answer = await bot.send_message(user.chat_id, dict.length_change(user.tg_name, length_change),
                            parse_mode=ParseMode.HTML)

###Команда отображения таблицы лидеров
@rt.message(StateFilter(None), Command(cn.leaderboard))
async def leaderboard(message: Message, state: FSMContext):
    users: List[UserModel] = await db.get_all_users_by_chat(message.chat.id)
    sorted_users: List[UserModel] = sorted(users, 
                                            key=lambda u: u.length,
                                            reverse=True)
    await message.delete()
    answer = await bot.send_message(users[0].chat_id, dict.leaderboard(sorted_users),
                        parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 15)

###Полезный заработок денег
@rt.message(StateFilter(None), Command(cn.dice_game))
async def dice_game_menu(message: Message, state: FSMContext):
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()

    answer = await bot.send_message(user.chat_id, dict.dice_game_start, 
                     reply_markup = interactive_kb.dice_choice(),
                     parse_mode=ParseMode.HTML)
    await state.update_data(user = user)
    await state.set_state(DiceGameSet.dice_menu_choice)
    await Utils.delete_old_message([answer], 15)

### Выбор действия
@rt.callback_query(DiceGameSet.dice_menu_choice, DiceGameCF.filter())
async def dice_game_start(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    user: UserModel = state_data["user"]
    await callback.message.delete()
    await state.clear()

    if (callback_data.action == "exit"): return

    if (callback_data.action == "rules"):
        message = await bot.send_message(user.chat_id, dict.dice_game_rules, 
                                                    parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([message], 60)
        return

    delta:timedelta = Utils.get_last_member_check_delta(user.last_dice_play, 1)
    
    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    if (not await db.update_user(user, 
            {"last_dice_play": datetime.now() })):
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
        
    if (not await db.update_user(user, 
            {"money" : UserModel.money + (minor_win_award if is_minor_win else major_win_award),
             })):
        await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
    
    await Utils.delete_old_message([dice1, dice2, message], 10)
        
###Бесполезная трата денег
@rt.message(StateFilter(None), Command(cn.trash_loto))
async def trash_loto(message: Message, state: FSMContext):
    await message.delete()
    have_delete_rights = (await RightsController.check_is_admin(message.chat.id) and
        await RightsController.check_delete_messages_rights(message.chat.id))
    
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    
    loto_cost:int = 5

    if (user.money < loto_cost):
        answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                            parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([message, answer])
        return
    
    if (not await db.update_user(user, {"money" : UserModel.money - loto_cost})):
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

    # 777
    if is_jackpot:
        award =  random.randrange(20, 30)
        if (await db.update_user(user, {"money" : UserModel.money + award})):
            answer = await bot.send_message(user.chat_id, dict.trash_loto_jackpot_money_award(user.tg_name, user.tg_id, award),
                                parse_mode=ParseMode.HTML)
        else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
    #тройная комбинаций
    elif is_major_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = random.randrange(2, 4)
            if (await db.update_user(user, {"length": UserModel.length + length, "money" : user.money})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_major_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(10, 15)
            if (await db.update_user(user, {"money" : UserModel.money + award})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_major_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)

    # Проверка на одинаковые крайние
    elif is_consolation:
        award = random.randrange(1, 5)
        if (await db.update_user(user, {"money" : UserModel.money + award})):
            answer = await bot.send_message(user.chat_id, dict.trash_loto_consolation_money_award(user.tg_name, user.tg_id, award),
                                parse_mode=ParseMode.HTML)
        else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)

    # Проверка на любые две одинаковые подряд
    elif is_minor_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = random.randrange(1, 3)
            if (await db.update_user(user, {"length": UserModel.length + length, "money" : user.money})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_minor_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(5, 10)
            if (await db.update_user(user, {"money" : UserModel.money + award})):
                answer = await bot.send_message(user.chat_id, dict.trash_loto_minor_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
            else: answer = await bot.send_message(user.chat_id, dict.trash_loto_error, parse_mode=ParseMode.HTML)
    else:
        answer = await bot.send_message(user.chat_id, dict.trash_loto_lose(user.tg_name, user.tg_id),
                            parse_mode=ParseMode.HTML)
    
    if (have_delete_rights):
        await Utils.delete_old_message([result, answer] if (is_lose) else [] 
                                 if (is_major_win or is_jackpot) else [result], 5)
    


