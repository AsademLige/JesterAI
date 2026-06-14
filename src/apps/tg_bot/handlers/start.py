from apps.tg_bot.keyboards.system_keyboard import SystemKeyboard
from apps.tg_bot.keyboards.callback_fabrics import HelpCF
from aiogram.types import CallbackQuery, Message
from apps.tg_bot.commands import Commands as cn
from core.data.datasource import DataBase
from core.consts.dictionary import Dictionary
from core.utils.utils import Utils
from aiogram.filters import Command
from aiogram.enums import ParseMode
from core.consts.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
system_kb = SystemKeyboard()
dict = Dictionary()
db = DataBase()
rt = Router()

### Запустить бота
@rt.message(Command(cn.start))
async def start_handler(message: Message):
    await message.answer(dict.bot_description)

### Что умеет бот
@rt.message(Command(cn.help))
async def help_handler(message: Message):
    await Utils.delete_old_message([message], 5)
    await message.answer(dict.bot_description, 
                         reply_markup=system_kb.help_btns(),
                         parse_mode=ParseMode.HTML)
    
###Действие защиты
@rt.callback_query(HelpCF.filter(F.action == "hunt"))
async def on_hunt_help(callback: CallbackQuery):
    await callback.message.edit_text("<blockquote>Молись Госпожа Удаче и, возможно, она не повернется к тебе своей решкой</blockquote>\n\n"\
                                     
                                    "У тебя 2 действия за раунд:\n"\
                                    "→ куда бить (кабина/туз/колени)\n"\
                                    "→ что защищать (кабина/туз/колени)\n\n"\

                                    "Попал в незащищённую часть монстра - 💥 нанес урон\n"\
                                    "Попал в защищённую - 🩸 получил по кляче своей\n\n"\
                                    
                                    "Выбери стратегию перед началом раунда: \n"\
                                    "⚔️⚔️ Атака — два удара, защиты нет, урон по тебе повышен\n"\
                                    "🗡🛡 Контратака — удар + защита\n"\
                                    "🛡🛡 Защита — две защиты, урон снижен, после можно сбежать или полечиться\n\n"\

                                    "🍺Кстати, если ты нищук с пустыми карманом, одну баночку <code>охоты крепкой</code>"\
                                    " для поправки здоровья тебе всегда любезно выдадут перед боем!\n\n"\

                                    "👹 Тоже выбирают стратегию на основе своего стиля боя:\n"\
                                    "🗡🗡🗡🛡🛡🛡 → контратака (средний)\n"\
                                    "🛡🛡🛡🛡🛡🛡 → защита (туша, но бьёт больно)\n"\
                                    "🗡🗡🗡🗡🗡🗡 → атака (мелкий, частый урон)\n\n"\

                                    "🚧 У тебя один из самых длинных членов? Что ж... ОНИ придут за тобой, но не отчаивайся! "\
                                    "Если сможешь дать сильным мира сего достойный отпор, то еще поживешь спокойно! Какое-то время...\n\n"

                                    "<i>Совет: Тушу бей смело, пока она пассивна. Помни, что перед лечением нужно пережить раунд в защите!</i>",
                                     reply_markup=system_kb.help_hunt_btns(),
                                     parse_mode=ParseMode.HTML)
    
###Действие защиты
@rt.callback_query(HelpCF.filter(F.action == "exit"))
async def on_help_close(callback: CallbackQuery):
    await callback.message.delete()
    