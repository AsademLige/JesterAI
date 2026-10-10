from features.battles.data.repository.gino_battle_repository import GinoBattleRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.battle_keyboard import BattleKeyboard
from apps.tg_bot.keyboards.hub_keyboard import hunt_button
from features.items.items_manager import ItemsManager
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from redis.asyncio import Redis
from aiogram import Router, F
from typing import Optional
from aiogram import Bot
import json

prefs = Prefs()
dictionary = Dictionary()
bot = Bot(token=prefs.bot_token)
combat_kb = BattleKeyboard()
user_repo:GinoUserRepository = GinoUserRepository()
battle_repo:GinoBattleRepository = GinoBattleRepository()
items_mg:ItemsManager = ItemsManager(user_repo)
links_cache = {}
rt = Router()

_redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    """Ленивая инициализация Redis клиента"""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(host='redis-broker', port=6379, decode_responses=True)
    return _redis_client

@rt.callback_query(StateFilter(None), F.data == "hub_hunt")
async def hunt_init(callback_query: CallbackQuery):
    message = callback_query.message
    user: User = await user_repo.get_user(callback_query.from_user.id, message.chat.id)

    if user.energy <= 0:
        answer = await bot.send_message(
            user.chat_id, 
            dictionary.energy_drain(user), 
            parse_mode=ParseMode.HTML
        )
        await Utils.delete_old_message([answer], 10)
        return

    await get_redis_client().publish("api_commands", json.dumps({
        "action": "create_battle_request",
        "user_tg_id": user.tg_id
    }, ensure_ascii=False))

    await message.delete()
    
    link_message = await bot.send_message(
        callback_query.message.chat.id, 
        "🏹 В воздухе витает чей-то запах...", 
        reply_markup=hunt_button(),
        parse_mode=ParseMode.HTML
    )
    
    await Utils.delete_old_message([link_message], 20)

###---------------------
###СТАРЫЙ БОЙ ЧЕРЕЗ БОТА
###---------------------

# ###Начало боя
# @rt.callback_query(BattleCF.filter(F.action.in_([a.value for a in UnitStrategy])))
# async def on_hunt_attack(callback: CallbackQuery, callback_data: BattleCF,
#                          state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()

#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]

#     if (user.tg_id != callback_data.user_id):
#         return
    
#     if (battle.phase == BattlePhases.PREPARE):
#         game_controller.start_battle(user, state_data["private_message"])

#     strategy = UnitStrategy(callback_data.action)
#     battle.active_member.choice_strategy(strategy)

#     if (strategy == UnitStrategy.DEFENSE):
#         battle.active_member.protect_all()

#     status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)

#     if (status):
#             await SafeEditMessage.safe_edit(callback, status[0],
#                                             reply_markup=combat_kb.battle_keyboard(user, battle) \
#                                             if (not status[1] == BattlePhases.BATTLE_END) else None,
#                                             parse_mode=ParseMode.HTML)
    
#             if (status[1] == BattlePhases.BATTLE_END and callback.message.chat.type == "private"):
#                 result = await bot.send_message(user.chat_id, status[0],
#                                     parse_mode=ParseMode.HTML)
#                 await Utils.delete_old_message([result], 360)

# ###Действие атаки
# @rt.callback_query(BattleCF.filter(F.action == "attack"))
# async def on_turn_attack(callback: CallbackQuery, callback_data: BattleCF,
#                           state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]

#     if (user.tg_id != callback_data.user_id):
#         return

#     battle.active_member.take_aim(list(BodyParts)[callback_data.part])
#     status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)

#     if (status):
#         await SafeEditMessage.safe_edit(callback, status[0],
#                                         reply_markup=combat_kb.battle_keyboard(user, battle) \
#                                         if (not status[1] == BattlePhases.BATTLE_END) else None,
#                                         parse_mode=ParseMode.HTML)

#         if (status[1] == BattlePhases.BATTLE_END and callback.message.chat.type == "private"):
#             result = await bot.send_message(user.chat_id, status[0],
#                                 parse_mode=ParseMode.HTML)
#             await Utils.delete_old_message([result], 360)

# ###Действие защиты
# @rt.callback_query(BattleCF.filter(F.action == "defense"))
# async def on_turn_defense(callback: CallbackQuery, callback_data: BattleCF, 
#                           state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]
#     items:List[InventoryItem] = []

#     if (user.tg_id != callback_data.user_id):
#         return

#     status:Optional[Tuple[str, BattlePhases, BattleUnit]] = await game_controller.get_battle_status(user)

#     if (status):
#         await SafeEditMessage.safe_edit(callback, status[0],
#                                         reply_markup=combat_kb.battle_keyboard(user, battle) \
#                                         if (not status[1] == BattlePhases.BATTLE_END) else None,
#                                         parse_mode=ParseMode.HTML)
        
#         if (status[1] == BattlePhases.BATTLE_END and callback.message.chat.type == "private"):
#             result = await bot.send_message(user.chat_id, status[0],
#                                 parse_mode=ParseMode.HTML)
#             await Utils.delete_old_message([result], 360)

# ##Способности
# @rt.callback_query(BattleCF.filter(F.action == "spells"))
# async def on_hunter_backpack_open(callback: CallbackQuery, callback_data: BattleCF,
#                           state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]

#     if (user.tg_id != callback_data.user_id):
#         return

# ##Сумка охотника
# @rt.callback_query(BattleCF.filter(F.action == "items"))
# async def on_hunter_backpack_open(callback: CallbackQuery, callback_data: BattleCF,
#                           state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]

#     if (user.tg_id != callback_data.user_id):
#         return

#     items = await user_repo.get_user_heal_items(battle.active_member.entity)
#     await state.update_data(items=items)
#     status:str = "\n\n<blockquote>🎒 В сумке охотника:</blockquote>\n"

#     if (items):
#         for item in items:
#             status += items_mg.effects_description(item) + "\n"
#     else:
#         status += "<b>Пусто!</b>"

#     await SafeEditMessage.safe_edit(callback, status,
#         reply_markup=combat_kb.hunt_items(user, items) \
#         if (not status[1] == BattlePhases.BATTLE_END) else None,
#         parse_mode=ParseMode.HTML)

# ##Закрытие сумки охотника
# @rt.callback_query(BattleCF.filter(F.action == "items_select_cancel"))
# async def on_hunter_backpack_open(callback: CallbackQuery, callback_data: BattleCF,
#                           state: FSMContext, game_controller:GameController):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]

#     if (user.tg_id != callback_data.user_id):
#         return

#     await SafeEditMessage.safe_edit(callback, battle.last_status,
#                                     reply_markup=combat_kb.battle_keyboard(user, battle),
#                                     parse_mode=ParseMode.HTML)


        
# ###Применение предмета лечения
# @rt.callback_query(BattleCF.filter(F.action == "heal"))
# async def on_hunter_heal(callback: CallbackQuery, callback_data: BattleCF, state: FSMContext):
#     if (await SafeEditMessage.is_locked(callback)): return
#     state_data = await state.get_data()
#     if (not 'user' in state_data and not 'battle' in state_data): return
#     user: User = state_data["user"]
#     battle: BattleManager = state_data["battle"]
#     items:List[Tuple[UserInventoryLinkORM, ItemORM]] = state_data["items"]

#     if (user.tg_id != callback_data.user_id):
#         return
    
#     old_hp:int = battle.active_member.hp
#     heal_status:Optional[Tuple[str, int]] = await items_mg.use_heal_item(user, items[callback_data.item_index], battle.active_member)
#     items = await user_repo.get_user_heal_items(battle.active_member.entity)
#     message:str = ""

#     if (heal_status):
#         message += heal_status[0] + f"\nHP: {Utils.progress_bar(old_hp, battle.active_member.max_hp, recover=heal_status[1])}"
    
#     if (heal_status):
#         await callback.answer()
#         await bot.send_message(user.tg_id, message,
#                         reply_markup=combat_kb.battle_keyboard(user, battle),
#                         parse_mode=ParseMode.HTML)

# ###Побег от монстра
# @rt.callback_query(BattleCF.filter(F.action == "escape"))
# async def on_hunt_escape(callback: CallbackQuery, callback_data: BattleCF,
#                           state: FSMContext, game_controller:GameController):
#     state_data = await state.get_data()
#     if (not 'user' in state_data): return
#     user: User = state_data["user"]

#     if (user.tg_id != callback_data.user_id):
#         return

#     status:str = await game_controller.escape_battle(user)
#     if (status):
#         await callback.answer()
#         await bot.send_message(user.tg_id, status,
#                                 parse_mode=ParseMode.HTML)
#     else:
#         await callback.message.edit_text("⛔️ Неожиданная ошибка...",
#                                         parse_mode=ParseMode.HTML)
    
