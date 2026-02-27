from src.domain.controllers.items_controller import ItemsController
from src.domain.controllers.rights_controller import RightsController
from src.domain.states.user_information_set import UserInformationSet
from src.models.user_inventory_item_model import UserInventoryItem
from src.keyboards.interactive_keyboard import InteractiveKeyboard
from src.keyboards.callback_fabrics import DiceGameCF, InventoryCF
from src.domain.states.dice_game_set import DiceGameSet
from src.models.user_stats_model import UserStats
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.store_item_model import StoreItem
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import List, Tuple
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
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    place_in_top:int = await db.get_place_in_top_by_member(user.tg_id, user.chat_id)

    await state.update_data(user=user)
    await state.set_state(UserInformationSet.detail)
    
    # Получаем оставшееся время до возможности использовать pencil
    delta_pencil:timedelta = Utils.get_last_member_check_delta(user.last_length_check)
    # Если оставшееся время отрицательное, значит можно использовать команду
    if math.floor(delta_pencil.total_seconds() / 3600) < 0:
        time_to_pencil = Utils.timedelta_to_hhmm(delta_pencil)
    else:
        time_to_pencil = "Готов"
    
    # Получаем оставшееся время до возможности использовать dice_game
    delta_dice:timedelta = Utils.get_last_member_check_delta(user.last_dice_play, 1)
    # Если оставшееся время отрицательное, значит можно использовать команду
    if math.floor(delta_dice.total_seconds() / 3600) < 0:
        time_to_dice = Utils.timedelta_to_hhmm(delta_dice)
    else:
        time_to_dice = "Готов"
    
    await message.delete()
    answer = await bot.send_message(user.chat_id, dict.user_information(user, place_in_top, time_to_pencil, time_to_dice),
                         reply_markup=interactive_kb.user_information_buttons(user),
                         parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 90)
    if (await state.get_state() == UserInformationSet.detail):
        await state.clear()

###Выбор действия
@rt.callback_query(UserInformationSet.detail, InventoryCF.filter())
async def user_information_detail(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    user: User = state_data["user"]
    
    if (user.tg_id != callback_data.user_id):
        return

    if (callback_data.action == "inventory"):
        inventory:List[Tuple[UserInventoryItem, StoreItem]] = await db.get_user_inventory(user)
        await state.update_data(inventory=inventory)
        await callback.message.edit_text(dict.user_inventory(user, inventory),
                                         reply_markup=interactive_kb.inventory_items(inventory, user),
                                         parse_mode=ParseMode.HTML)
    
    elif (callback_data.action == "inventory_choice"):
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        item:Tuple[UserInventoryItem, StoreItem] = next((p for p in inventory if p[1].id == callback_data.item_id), None)
        await state.update_data(item=item)
        await callback.message.edit_text(dict.inventory_item_info(item),
                                         reply_markup=interactive_kb.item_keyboard(user),
                                         parse_mode=ParseMode.HTML)
        
    elif (callback_data.action == "use_myself"):
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        item:Tuple[UserInventoryItem, StoreItem] = state_data["item"]

        use_status:str = await ItemsController.use_item(user, item)
        if (use_status):
            await callback.message.delete()
            await bot.send_message(user.chat_id, use_status, parse_mode=ParseMode.HTML)
        await state.clear()
        await Utils.delete_old_message([callback.message],5)
        return
    elif (callback_data.action == "use_target"):
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        users: List[User] = await db.get_all_users_by_chat(user.chat_id)
        await callback.message.edit_text(dict.select_target,
                                         reply_markup=interactive_kb.select_target(users, user),
                                         parse_mode=ParseMode.HTML)
    elif (callback_data.action == "target_selected"):
        target: User = await db.get_user_by_id(callback_data.item_id)
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        item:Tuple[UserInventoryItem, StoreItem] = state_data["item"]
        use_status:str = await ItemsController.use_item(user, item, target)
        if (use_status):
            await callback.message.delete()
            await bot.send_message(user.chat_id, use_status, parse_mode=ParseMode.HTML)
        await state.clear()
        await Utils.delete_old_message([callback.message],5)
        return
    elif (callback_data.action == "target_cancel"): 
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        user: User = state_data["user"]
        await callback.message.edit_text(dict.user_inventory(user, inventory),
                                         reply_markup=interactive_kb.inventory_items(inventory, user),
                                         parse_mode=ParseMode.HTML)
    elif (callback_data.action == "cancel"): 
        inventory: List[Tuple[UserInventoryItem, StoreItem]] = state_data["inventory"]
        user: User = state_data["user"]
        await callback.message.edit_text(dict.user_inventory(user, inventory),
                                         reply_markup=interactive_kb.inventory_items(inventory, user),
                                         parse_mode=ParseMode.HTML)
    elif (callback_data.action == "exit"): 
        await callback.message.delete()
        await state.clear()
        return

    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
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
    users: List[User] = await db.get_all_users_by_chat(message.chat.id)
    sorted_users: List[User] = sorted(users, 
                                            key=lambda u: u.length,
                                            reverse=True)
    await message.delete()
    answer = await bot.send_message(users[0].chat_id, dict.leaderboard(sorted_users),
                        parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 15)

###Команда отображения списка выигрышей
@rt.message(StateFilter(None), Command(cn.winners_log))
async def winners_log(message: Message, state: FSMContext):
    logs, total_pages, users = await db.get_winners_logs_page(message.chat.id, 1)
    chat_id:int = message.chat.id
    await message.delete()

    if not logs:
        await bot.send_message(chat_id, "📭 Записей пока нет")
        return
    
    await bot.send_message(chat_id, dict.winners_logs(logs, users), 
                         reply_markup=interactive_kb.get_pagination_keyboard(1, total_pages), 
                         parse_mode=ParseMode.HTML)
    
# Обработчик нажатий на кнопки пагинации
@rt.callback_query(lambda c: c.data.startswith('page_'))
async def process_pagination(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])

    logs, total_pages, users = await db.get_winners_logs_page(callback.message.chat.id, page)

    await callback.message.edit_text(dict.winners_logs(logs, users), 
                         reply_markup=interactive_kb.get_pagination_keyboard(page, total_pages), 
                         parse_mode=ParseMode.HTML)
    await callback.answer()

@rt.callback_query(lambda c: c.data.startswith('close_pagination'))
async def delete_winners_log_table(callback: CallbackQuery):
    await callback.message.delete()

###Полезный заработок денег
@rt.message(StateFilter(None), Command(cn.dice_game))
async def dice_game_menu(message: Message, state: FSMContext):
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()

    delta:timedelta = Utils.get_last_member_check_delta(user.last_dice_play, 1)
    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    answer = await bot.send_message(user.chat_id, dict.dice_game_start, 
                     reply_markup = interactive_kb.dice_choice(),
                     parse_mode=ParseMode.HTML)
    await state.update_data(user = user)
    await state.set_state(DiceGameSet.dice_menu_choice)

    await Utils.delete_old_message([answer], 15)
    if (await state.get_state() == DiceGameSet.dice_menu_choice):
        await state.clear()

### Выбор действия
@rt.callback_query(DiceGameSet.dice_menu_choice, DiceGameCF.filter())
async def dice_game_start(callback: CallbackQuery, callback_data: DiceGameCF, state: FSMContext):
    state_data = await state.get_data()
    user: User = state_data["user"]

    await callback.message.delete()
    await state.clear()

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
        
    await db.update_user_stats(user.id, 
        {UserStats.dice_games.name : UserStats.dice_games + 1, 
          UserStats.dice_minor_wins.name :  UserStats.dice_minor_wins + (1 if is_minor_win else 0),
          UserStats.dice_major_wins.name :  UserStats.dice_major_wins + (1 if is_major_win else 0),
        })
    
    await Utils.delete_old_message([dice1, dice2, message], 10)
        
###Бесполезная трата денег
@rt.message(StateFilter(None), Command(cn.trash_loto))
async def trash_loto(message: Message, state: FSMContext):
    await message.delete()
    have_delete_rights = (await RightsController.check_is_admin(message.chat.id) and
        await RightsController.check_delete_messages_rights(message.chat.id))
    
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    
    loto_cost:int = 5

    if (user.money < loto_cost):
        answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                            parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([message, answer])
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
        
    await db.update_user_stats(user.id, 
        {UserStats.trash_loto_spins.name : UserStats.trash_loto_spins + 1, 
        UserStats.trash_loto_money_wins.name :  UserStats.trash_loto_money_wins + award,
        UserStats.trash_loto_length_wins.name :  UserStats.trash_loto_length_wins + length,
        UserStats.trash_loto_jackpots.name :  UserStats.trash_loto_jackpots + (1 if is_jackpot else 0),
        })
    
    if (have_delete_rights):
        await Utils.delete_old_message([] if (is_major_win or is_jackpot) 
                                       else [result, answer], 5)
    


