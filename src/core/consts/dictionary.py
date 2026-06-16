from features.store.data.models.discounts_model import ProductDiscounts
from aiogram.utils.markdown import hbold, hcode, hblockquote, hitalic
from features.battles.battle_unit_entity import BattleUnit, BodyParts
from features.user.data.dtos.inventory_item_dto import InventoryItem
from features.battles.data.models.monster_orm import MonsterORM
from core.utils.text_processing import TextProcessing as tp
from features.store.data.models.warehouse import Warehouse
from core.data.models.winners_log_model import WinnersLog
from features.items.data.models.item_orm import ItemORM
from core.utils.enums import AttackStatus, BattleMode
from typing import Optional, List, Dict, Tuple, Union
from features.user.data.dtos.user_dto import User
from core.data.data_base import DataBase
from core.utils.utils import Utils
import random

class Dictionary():
    _instance = None
    db = DataBase()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def init(self):
        await self.load_strings()

    ###------------------------------------------------------------
    ###Описание команд бота
    ###------------------------------------------------------------

    help:str = "Что умеет бот"

    me:str = "Информация обо мне"

    pencil:str = "Недоволен своим размером? ЖМИ СЮДА"

    leaderboard_description:str = "ЧСВ жмет? Покажи им свое место! (и их заодно)"

    sticker_pack:str = "Аудио стикеры!"

    winners_log_description:str = "🗒 Список выигрышей игроков"

    edit_sticker_set:str = "Изменить набор стикеров"

    create_sticker_set:str = "Создать набор стикеров"

    trash_loto:str = "🎰 Деньги карман жгут? Попытай удачу за 5💰"

    dice_game:str = "🎲 Кидаешь кубик и выигрываешь!"

    gamba_house:str = "🎲 🎰 Оставь надежду, всяк сюда входящий!"

    hub:str = "🪧 Пора найти приключений себе на жепу"

    hunt:str = "⚔️ Бери наперевес свой pencil и вперед, геройствовать!"

    ###------------------------------------------------------------
    ###Общее
    ###------------------------------------------------------------

    error:str = "Что-то мне сегодня плохо, приходи попозже..."

    exit:str = "❌ Выход"

    back:str = "↩ Назад"

    skip:str = "⏩ Пропустить"

    trigger:str = "🚀 Запустить"

    rules:str = "❓ Правила"

    bot_description:str = "Команда /sticker_pack отправит ссылку на стикеры, которые МАГИЧЕСКИМ образом превращаются в видео!\n\n"\
                        "🎒У нас тут что-то вроде интерактивной игры, команда /me покажет небольшую сводку с твоими успехами\n\n"\
                        "🍆Меряйся хозяйством с другими участниками! Команда /pencil поможет тебе получить БОЛЬШОЕ признание <i>(но есть шанс, что уменьшит его)</i>"\
                        "Бот все же заскамил тебя? Подожди 24 часа и пробуй еще раз!\n\n"\
                        "🎲🎰 Заглядывай в наше домик развлечений /gamba_house! За твои деньги, мы знатно тебя <s>разведем</s>РАЗВЛЕЧЕМ\n\n"\
                        "⚔️Нечисть и уроды различной степени наводнили наши земли, охоться /hunt на них и получай награду! "\
                        "Обязательно прочитай про бои, там много полезной информации!\n\n"\
                        "<i>Все вопросы и предложения отправлять на почтовый ящик:</i> <code>2202202000651657</code>"
    
    __answer_restricted:str = "⛔️ Команду вызвал {{user_link}}, так что руки прочь!"

    ###------------------------------------------------------------
    ###Взаимодействие с пользователем
    ###------------------------------------------------------------
    
    __first_meet:str = 'А тебя я раньше здесь не видел... Ты, значится, {{user_link}}! '\
    'А я Шут. Ромашковый.🤡 Я работаю на мобильных разработчиков в их мобильном подвале. '\
    'Дай-ка я на тебя взгляну...\nИзмерим твой {{pencil}}...'\
    '\nОго! Вот это питон! {{length}}\n'\
    '{{custom_title}}'
    
    __user_information:str = f'{hblockquote("🔍 {{user_link}} {{custom_title}} Имеет {{pencil_accu}} длинной {{length}}!")}\n'\
    '{{medal}} Место в топе: {{place_in_top}}\n'\
    '💰 Монет на руках: {{money}}\n\n'\
    '{{user_stats}}\n\n'\
    '⏰ <i>До проверки {{pencil_gen}}: {{time_to_pencil}}</i>\n'\
    '⏰ <i>До игры в кости: {{time_to_dice}}</i>'

    __inventory_info:str = "<blockquote>🎒 Инвентарь {{user_link}}</blockquote>\n{{items}}"

    __inventory_item_info:str = "<blockquote>{{title}}</blockquote>\n<i>{{description}}</i>"

    select_target:str = "🎁 Кто получит твой подарок?"

    use_myself:str = "📤 Использовать на себя"
    select_target:str = "🎯 Выбрать цель"

    pencil_timer_decresc_target:str = "⏰ {{user_link1}} использовал {{item_title}} на {{user_link2}} и сбросил его таймер на проверку {{pencil_gen}}"
    pencil_timer_decresc:str = "⏰ {{user_link1}} использовал {{item_title}} на себя и сбросил таймер на проверку {{pencil_gen}}"

    dice_game_timer_decresc_target:str = "⏰ {{user_link1}} использовал {{item_title}} на {{user_link2}} и сбросил его таймер на игру в кости"
    dice_game_timer_decresc:str = "⏰ {{user_link1}} использовал {{item_title}} на себя и сбросил таймер на игру в кости"

    item_steal_usage:str = "🐀 {{user_link1}} использовал {{item_title}} на {{user_link2}} и украл {{steal_item_title}}"
    item_steal_money:str = "🐀 {{user_link1}} использовал {{item_title}} на {{user_link2}} и украл {{money}}"

    length_decresc_target:str = "🔪 {{user_link1}} взял <code>{{item_title}}</code> и отрезал у {{user_link2}} {{length}} {{pencil_gen}}!"
    length_decresc:str = "🔪 {{user_link1}} взял {{item_title}} и отрезал у себя {{length}} {{pencil_gen}}, ненормальный..."

    length_add_target:str = "💊 {{user_link1}} взял {{item_title}} и увеличил у {{user_link2}} {{pencil_accu}} на {{length}}!"
    length_add:str = "💊 {{user_link1}} взял {{item_title}} и увеличил {{pencil_accu}} на {{length}}!"

    private_messages_restriction:str = "🚧 такое тебе(🤡) тут делать ПОКА ЧТО запрещено 🚧"

    __user_link_m2 : str = '[{{full_name}}](tg://user?id={{tg_id}})'

    __user_link_html : str = '<a href="tg://user?id={{tg_id}}">{{full_name}}</a>'

    __not_enough_money:str = '🤡 {{user_link}}, у тебя карман дырявый, иди подкопи:D'

    ###------------------------------------------------------------
    ###Создание набора стикеров
    ###------------------------------------------------------------

    error_sticker_set_create:str = "Ошибка создания набора стикеров"

    use_this:str = "Использовать видео стикера"

    send_sticker_placeholder:str = "Отправь видео, которым будет заменяться стикер"

    __sticker_set_create_success: str = "🟢 Набор стикеров создан: https://t.me/addstickers/{{sticker_set_name}}"

    ###------------------------------------------------------------
    ###Изменение набора стикеров
    ###------------------------------------------------------------

    __sticker_add_to_set_success: str = "🟢 Стикер добавлен: https://t.me/addstickers/{{sticker_set_name}}"
    
    __sticker_set_link: str = "https://t.me/addstickers/{{sticker_set_name}}"
    
    choice_sticker_set:str = "Выбери набор стикеров, который хочешь изменить"

    sticker_set_list_is_empty:str = "Нет наборов стикеров!"

    sticker_edit_variants:str = "Вот что мы можем с ним сделать:"

    delete_sticker_set_success:str = "🟢 Удалили удачно!"

    delete_sticker_set:str = "🚫 Удалить набор"

    add_sticker_to_set:str = "📥 Добавить стикер"

    delete_sticker_from_set:str = "🗑️ Удалить стикер"

    ###------------------------------------------------------------
    ###Текстовые переменные треш лото
    ###------------------------------------------------------------

    __gamba_house_description:str = "<blockquote>🎰🎲 Шут и Госпожа Удача приветствуют тебя, {{user}}! Как пожелаешь заскамить тебя сегодня?</blockquote>\n\n<i>Скам-хаус заработал: {{total}}</i>"
    
    __trash_loto_consolation_money_award: str = "🌱 чут-чут повезло, держи копейку, {{user_link}}: {{money}}"
    
    __trash_loto_minor_length_award: str = "🍆 {{user_link}} выиграл мазь для увеличения {{pencil_gen}} на целых {{length}}!"

    __trash_loto_minor_money_award: str = "☘️ Сегодня твой день, {{user_link}}! Выигрыш составил: {{money}}"

    __trash_loto_major_length_award: str = "<blockquote>🍆 ВОТ ЭТО УДАЧА!</blockquote> {{user_link}}, весь персонал казино тянул за твой {{pencil_accu}}, и вытянул на целых {{length}}!"

    __trash_loto_major_money_award: str = "<blockquote>🍀 ВОТ ЭТО УДАЧА!</blockquote> {{user_link}}, на твоей совести наша бабка-бухгалтер! Выигрыш составил: {{money}}"

    __trash_loto_jackpot_money_award: str = "<blockquote>💎 ДЖЕКПОТ!!! 💎</blockquote>\n Однорукий бандит сегодня ты, {{user_link}}! Казино ОГРАБЛЕНО! Выигрыш составил: {{money}}"

    __trash_loto_lose:List[str] = [
        "🎰 Жена плачет, дочь рыдает, {{user_link}} снова доливает! Минус бабки...",
        "🧻 Додеп, додеп, еще додеп! Денег нет теперь на хлеб..."
    ]

    trash_loto_error:str = "Ошибочка вышла... Зато деньги твои целы!"

    ###------------------------------------------------------------
    ###Текстовые переменные игры с дайсами
    ###------------------------------------------------------------
    
    dice_game_start:str = "<blockquote>🎲 Кубики!</blockquote>\n Сделай свой прогноз:"

    dice_game_rules:str = "<b>🎲 Выше или ниже семи</b>\n"\
                          "Игрок перед броском делает «ставку»: будет ли сумма двух кубиков меньше 7, больше 7 или ровно 7\n"\
                          "<b>Выигрыш:</b> \n"\
                          "🍀 Угадал меньше или больше 7 - <b>5</b>💰\n" \
                          "💎 Угадал ровно 7 - <b>15</b>💰"
    
    __dice_lose:str = "🪗 <b>{{combination}}</b> Мимо! Повезет в следующий раз, {{user_link}}, но я не то чтобы гарантирую..."
    __dice_minor_win:str = "🎯 <b>{{combination}}</b> Угадал! Выигрыш твой, {{user_link}}! Ну чертяка! {{money}}"
    __dice_major_win:str = "<blockquote>💎 <b>{{combination}}</b> {{user_link}} супер угадал!</blockquote>\n"\
                           "Забирай свои грязные бумажки! {{money}}"

    __dice_combinations:Dict[List[int], List[str]] = {
        (1, 1) : ["Змеиные глазки", "Близнецы-подкидыши", "Копейки"],
        (1, 2) : ["Третий лишний", "Полторашка"],
        (1, 4) : ["Четыре шлюхи и сутенёр"],
        (2, 2) : ["Гуси лебеди"],
        (2, 3) : ["Пятый угол"],
        (3, 3) : ["Две косички", "Усы", "Барабаны"],
        (3, 4) : ["Топор"],
        (2, 5) : ["Топор", "Четвертак"],
        (1, 6) : ["Топор"],
        (4, 4) : ["Стулья", "Квадратная пара"],
        (5, 5) : ["Десятка червонная"],
        (4, 6) : ["Десятка червонная"],
        (6, 6) : ["Чертова дюжина", "Pay Day", "Вагоны"],
    }

    dice_smaller:str = "💵 <7 💵"
    dice_bigger:str = "💴 >7 💴"
    dice_equal:str = "💎 =7 💎"

    dice_error:str = "Ошибочка вышла..."

    ###------------------------------------------------------------
    ###Текстовые переменные битвы
    ###------------------------------------------------------------
    
    combat_interface:str = "{{fight_name}}\n\n"\
                             "{{player1_icon}} : {{player1}}\n"\
                             "HP: {{health1}}\n\n"\
                             "{{player2_icon}} : {{player2}}\n"\
                             "HP: {{health2}}\n"\
                             "━━━━━━━━━━━━━\n"\
                             "⏳ Таймер: {{timer}}\n"\
                             
    gladiators_interface:str = "{{player1_icon}} : {{player1}}\n"\
                               "HP: {{health1}}\n\n"\
                               "{{player2_icon}} : {{player2}}\n"\
                               "HP: {{health2}}\n"\
    
    __monster_meeting:List[str] = [
        "❗️ Из кустов выползает <code>{{monster_name}}</code>, а его {{pencil}} смотрит прямо на тебя! Что будешь делать?"
    ]

    __boss_meeting:List[str] = [
        "<blockquote>🚧 ОПАСНОСТЬ! Сильный противник <code>{{monster_name}}</code> встречается на твоем пути, а его {{pencil}} в другой весовой категории!🚧</blockquote>"
    ]

    __gladiators_introduce:List[str] = [
        "📣 Под общие овации на арену выбрасывают ({{gladiator1_icon}}) <code>{{gladiator1_name}}</code>! Его соперник ({{gladiator2_icon}}) <code>{{gladiator2_name}}</code> уже стоит в боевой стойке и ждет сигнала!",
        "📣 На арене появляются наши бедолаги! ({{gladiator1_icon}}) <code>{{gladiator1_name}}</code> под грибами и не понимает, где находится, а ({{gladiator2_icon}}) <code>{{gladiator2_name}}</code> еле стоит на ногах от страха!",
    ]

    __battle_escape:List[str] = [
        "💨 {{member}} бежит, роняя кал и спотыкаясь о {{pencil_accu}}...",
        "💨 Ну что, {{member}}, помог тебе {{pencil}} {{length}}?",
        "💨 Пора дать на пятку, пока при памяти!"
    ]

    battle_protect_description:List[str] = [
        "прячется за {{pencil_inst}}",
        "спасается бегством за ближайший камень",
        "игнорирует любые попытки атаки",
        "не чувствует урона",
        "взывает к здравому смыслу и не получает урон",
        "демонстративно закатывает глаза, игнорируя урон",
        "использует режим бога и игнорирует любой урон",
        "отпрыгивает в последний момент",
        "делает вид, что это не больно",
        "жалуется на качество удара",
        "выставляет вперед стажера из тестеров, заблокировав им урон",
        "отрицает существование оппонента",
        "откатывается к прошлому состоянию без урона"
    ]

    battle_attacked_description:List[str] = [
        "драматично берется за окровавленное место",
        "выдает синий экран смерти",
        "падает, прижимая руки к {{part_dat}}",
        "медленно оседает на пол",
        "хватается за {{pencil_accu}}, хотя били в {{part_accu}}",
        "закатывает глаза и падает плашмя",
        "готовиться к флешбекам перед паверапом",
        "смотрит на новую дырень в теле, но делает вид, что так и было",
        "выдает ошибку <b>404 (ebalo not found)</b>",
        "вытирает пот со лба и кровь с {{pencil_gen}}",
    ]

    battle_attack_description:List[str] = [
        "выходит на удушающий {{pencil_inst}}",
        "прописывает двоечку в {{part_accu}}",
        "проводит психологическую атаку",
        "распахивает плащ",
        "стреляет сомнительной жидкостью",
        "давит интеплектом",
        "пытается насадить на {{pencil_accu}}",
        "втыкает {{pencil_accu}} в {{part}} оппонента",
        "начинает газлайтинг",
        "ломает через колено {{pencil_accu}} оппонента",
        "спамит один удар",
        "натягивает {{pencil_accu}} оппонента на глобус"
    ]

    battle_none_status_description:List[str] = [
        "удивляется пассивностью противника",
        "видит, как противник застрял в текстурах и не может атаковать"
    ]

    battle_dead_description:List[str] = [
        "сдох, обоссавшись и обосравшись!",
        "прикрывает рукой  {{part_accu}}, затем падает без дыхания",
        "становиться отрицательно живым"
    ]

    gladiators_cheer_up:List[str] = [
        "⚔️ Снеси ему кабину!",
        "⚔️ Переломи его об хуй!",
        "⚔️ Харкни ему в очко!",
        "⚔️ Двоечку этой пенсии!",
        "⚔️ Трахай, родной!",
        "⚔️ В помоечку!",
        "⚔️ Туда эту шмару!",
        "⚔️ Дай ему на клык!",
        "⚔️ Я щас трусы сниму!",
        "⚔️ Добить выживших!",
        "⚔️ Глубже, глубже давай!",
        "⚔️ Кончай в него! То есть его!!",
        "⚔️ ЭТОТ ПРИЦЕЛ ПРОСТО ИМБА!",
    ]

    gladiators_sucks:List[str] = [
        "🌧 Ну ты и кляча!",
        "🌧 Вставай, помойка!",
        "🌧 Вытри сопли и дерись!",
        "🌧 Вытри сопли и дерись!",
        "🌧 ГГ, проебали...",
        "🌧 Ну и на кого я поставил!?",
        "🌧 Я сейчас выйду тебя добить!",
        "🌧 Какой же ты нищий!",
        "🌧 После боя еще и от меня получишь!",
        "🌧 За что мне этот инвалид!",
        "🌧 Хватит уже нализывать яйца!",
    ]

    __hunt_loot:List[str] = [
        "Пошарим в воровском кармане... Ага! <code>{{item_icon}} {{item_name}}</code>!"
    ]

    ###------------------------------------------------------------
    ###Текстовые переменные магазина
    ###------------------------------------------------------------

    __store_description:str = "<blockquote>🛒 Приветствуем в <b>DICKSI</b>, {{user_link}}!</blockquote>\n"\
                              "<i>Пакетик брать будете или Вы со своим?</i>\n\n{{products}}\n<i>Баланс: {{money}}</i>"
    
    __product_description:str = "<blockquote>{{title}}</blockquote>\n<i>{{description}}</i>\n\n<b>Стоимость</b>: {{price}}"
    
    __buttons_types:List[str] = ['🈶','🈚️','🈸','🈺', '🈷️']

    __store_exit:List[str] = [
        "🚪 {{user_link}}, не задерживайте очередь, там за вами бабушка с 30 мешками сахара в руках уже сознание теряет!",
        "🚪 Ты бы еще консервных банок насобирал! Как проветришься, заходи...",
        "🚪 {{user_link}} стоит, копейки свои дрочит! Пропусти людей, не задерживай очередь!",
        "🚪 Слил вcю котлету треш лото, чудик, теперь даже на пакет денег нет"
    ]

    __product_buying_thanks:List[str] = ["💳 Оплата прошла, спасибо за покупку, {{user_link}}!", 
                                         "💳 Не желаете гречку по акции, корм для голубей, передние стойки стабилизатора на гранту? Спасибо за покупку, {{user_link}}, приходите еще!",
                                         "💳 За покупку вам бонус в виде наклейки! Наклеите 999 штук на свой {{pencil}}, и он увеличится на <b>1cm</b>"]
    
    __warehouse_update:str = "<blockquote>🏪 Обновление остатков магазина, бегом за покупками!</blockquote>\n" \
                                                    "<i>Специальные предложения:\n</i>"\
                                                    "{{discounts_description}}"\
                                                    "<i>Поторопись опередить бабок в гонке за просрочкой!\n</i>"

    ###------------------------------------------------------------
    ###Описания розыгрышей
    ###------------------------------------------------------------

    __draw_list:List[str] = [
        '🎁 Запускаем розыгрыш мази для увеличения {{pencil_gen}} среди лоутабов! '\
        'И сегодняшним победителем становится... 🎉{{user_link}}🎊, поздравляем победителя!\n'\
        'Его выигрыш составил: {{length}}'
    ]

    __day_salary:str = "<blockquote>💵 <b>ПОЛУЧКА</b>!</blockquote>\nРаботяги получают свои честно заработанные {{money}}! "\
                        "\nНе забывайте проставить время в карточке!"
    
    __tech_work_compensation:str = "<blockquote>🚧 <b>ОБНОВЛЕНИЕ!</b>!</blockquote>\nА работяги в честь праздника получают премию: {{money}}!"

    ###------------------------------------------------------------
    ###Описания подведения итогов
    ###------------------------------------------------------------

    __weekly_winners:List[str] = [
        "<blockquote>🏆 Начинаем подведение итогов в номинации «Самый длинный {{pencil}} недели»!</blockquote>\n{{winners}}"
    ]

    __leaderboard:str = "<blockquote>🍆 Длинный {{pencil}} - это про них!</blockquote>\n{{leaderboard}}"

    __winners_log:str = "<blockquote>🗓 Таблица данных о выигрышах пользователей</blockquote>\n{{logs}}"

    ###------------------------------------------------------------
    ###интерактивные действия изменения размера
    ###------------------------------------------------------------
    
    __positive_length_change:List[str] = []

    __negative_length_change:List[str] = []

    ### 0 - Именительный падеж
    ### 1 - Родительный
    ### 2 - Дательный
    ### 3 - Винительный
    ### 4 - Творительный
    ### 5 - Предложный 
    member_names:List[List[str]] = [
        ["член", "члена", "члену","член","членом",""],
        ["нефритовый стержень", "нефритового стержня", "нефритовому стержню","нефритовый стержень","нефритовым стержнем",""],
        ["питон", "питона", "питону","питон","питоном",""],
        ["смычок", "смычка", "смычку","смычок","смычком",""],
        ["дрын", "дрына", "дрыну","дрын","дрыном",""],
        ["хер", "хера", "херу","хер","хером",""],
        ["елда", "елды", "елде","елду","елдой",""],
        ["болт", "болта", "болту","болт","болтом",""],
        ["прибор", "прибора", "прибору","прибор","прибором",""],
        ["чучундрик", "чучундрика", "чучундрику","чучундрик","чучундриком",""],
        ["пистон", "пистона", "пистону","пистон","пистоном",""]
    ]

    __timer_message:str = "{{user_link}}, с тебя уже хватит, приходи позже...\n"\
    "<blockquote>⏰ Осталось потерпеть: {{time_left}}</blockquote>"

    __hunt_timer_message:str = "{{user_link}}, отдохни, вылечи раны с последней охоты!\n"\
    "<blockquote>⏰ Осталось потерпеть: {{time_left}}</blockquote>"
    
    ###------------------------------------------------------------
    ###Методы
    ###------------------------------------------------------------
    
    async def load_strings(self) -> bool:
        try:
            self.__negative_length_change.extend(await self.db.get_negative_length_change_assets())
            self.__positive_length_change.extend(await self.db.get_positive_length_change_assets())
            return True
        except Exception as error:
            print(f"load assets error: {error}")
            return False
        
    def gamba_house_description(self, total_gamba_house_win, user:User) -> str:
        return tp.text_replacement(self.__gamba_house_description, {
            "total":self.money_wrapper(total_gamba_house_win, False),
            "user":self.get_user_link(user.tg_name, user.tg_id),
        })
    
    def hunt_monster_meeting(self, monster:MonsterORM, strategy:str, fighting_style_visual:str) -> str:
        return tp.text_replacement(random.choice(self.__monster_meeting if (monster.tag == "mob") else self.__boss_meeting) + \
                                   f"\n\n{strategy}" + \
                                   f"\n\n❤️ <b>Здоровье: {monster.health}</b>\n"\
                                   f"🔪 <b>Атака: {monster.min_damage}-{monster.max_damage}</b>\n"\
                                   f"🎯 <b>Крит. шанс: {monster.crit_chance}%</b>\n"\
                                   f"🥋 <b>Стиль боя</b>: {fighting_style_visual}\n"
                                   f"\n<b>Описание:</b> <i>{monster.description}</i>", {
            "monster_name": monster.name,
            **self.random_member(),
        })
    
    def gladiators_introduce(self, members:List[BattleUnit], ui_data:Dict[str, str]) -> str:
        return tp.text_replacement(random.choice(self.__gladiators_introduce) + 
                                   "\n\n{{gladiators_ui}}" + 
                                   "━━━━━━━━━━━━━\n"+ \
                                   "<i>Делайте ваши ставки, господа!</i>", {
            "gladiator1_name" :members[0].entity.name,
            "gladiator1_icon" :members[0].utf8_icon,
            "gladiator2_name" :members[1].entity.name,
            "gladiator2_icon" :members[1].utf8_icon,
            "gladiators_ui":tp.text_replacement(self.gladiators_interface, {**ui_data})
        })
    
    def battle_escape(self, member:Union[User, MonsterORM]) -> str:
        return tp.text_replacement(random.choice(self.__battle_escape), {
            "member" : self.get_user_link(member.tg_name, member.tg_id) if type(member) is User else f"<code>{member.name}</code>",
            "length": self.length_wrapper(member.length if type(member) is User else random.randint(1, 30)), 
            **self.random_member(),
        })
        
    def store_description(self, products:List[Tuple[Warehouse, ItemORM, ProductDiscounts]], user:User) -> str:
        return tp.text_replacement(self.__store_description, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "products": self.__generate_products_list(products),
            "money": self.money_wrapper(user.money, False),
            **self.random_member(),
        }, recursive_parse_args = True)
    
    def __generate_products_list(self, products:List[Tuple[Warehouse, ItemORM, ProductDiscounts]]) -> str:
        products_str:str = ""
        index:int = 1
        for warehouse_item, product, discount in products:
            price_formatted:str = f"{self.price_wrapper(product.price, False)}"
            if (discount):
                discount_price:int = round(product.price - (product.price * (discount.discount_percent / 100)))
                price_formatted = f"{self.price_wrapper(discount_price)} <s>{price_formatted}</s>💰"
            icon:str = f"<b>({index})</b> {random.choice(self.__buttons_types)}{product.utf8_icon}"
            body:str = icon + f"{hcode(product.title)}<b>({warehouse_item.quantity}/{warehouse_item.max_capacity})</b> - {price_formatted}"

            products_str += f"{body}\n"
            index+=1

        return products_str
    
    def product_description(self, product:Tuple[Warehouse, ItemORM, ProductDiscounts]) -> str:
        price_formatted:str = f"{self.price_wrapper(product[1].price, False)}"
        if (product[2]):
            discount_price:int = round(product[1].price - (product[1].price * (product[2].discount_percent / 100)))
            price_formatted = f"{self.price_wrapper(discount_price)} <s>{price_formatted}</s>💰"
        else:
            price_formatted = f"{price_formatted}💰"
        return tp.text_replacement(self.__product_description, {
            "title": product[1].title,
            "description": product[1].description,
            "price": f"{price_formatted}" if (product[0].quantity > 0) else "<b>Нет в наличии!</b>",
            **self.random_member(),
        }, recursive_parse_args = True)
    
    def store_exit(self, user:User) -> str:
        return tp.text_replacement(random.choice(self.__store_exit), {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(),
        })
    
    def product_buying_thanks(self, user:User) -> str:
        return tp.text_replacement(random.choice(self.__product_buying_thanks), {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(),
        })
    
    def warehouse_update(self, discounts:List[Tuple[ProductDiscounts, ItemORM]]) -> str:
        discounts_description:str = ""
        for i, discount in enumerate(discounts):
            discounts_description += f"<blockquote>{discount[1].utf8_icon} {discount[1].title} "\
                f"<b>-{discount[0].discount_percent}%</b>!</blockquote>\n"
            
        return tp.text_replacement(self.__warehouse_update, {
            "discounts_description": discounts_description,
            **self.random_member(),
        }, recursive_parse_args = True)
    
    def answer_restricted(self, full_name: str, tg_id:int) -> str:
        return tp.text_replacement(self.__answer_restricted, {
            "user_link" : self.get_user_link(full_name, tg_id),
        })
    
    def get_sticker_set_link(self, sticker_set_name:str) -> str:
        return tp.text_replacement(self.__sticker_set_link, {"sticker_set_name" : sticker_set_name})

    def get_user_link(self, full_name: str, tg_id:int) -> str:
        return tp.text_replacement(self.__user_link_html, {
            "tg_id" : tg_id,
            "full_name" : full_name,
        })
    
    def not_enough_money(self, user:User) -> str:
        return tp.text_replacement(self.__not_enough_money, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
        })
    
    def dice_combination_name(self, combination:List[int]) -> str:
        list:List[str] = []
        
        if (tuple(sorted(combination)) in self.__dice_combinations):
            list = self.__dice_combinations[tuple(sorted(combination))]
        
        if (tuple(sorted(combination, reverse=True)) in self.__dice_combinations):
            list = self.__dice_combinations[tuple(sorted(combination, reverse=True))]

        return f"{random.choice(list)}!" if list else ""

    
    def dice_lose(self, user:User, combination:List[int], ) -> str:
        return tp.text_replacement(self.__dice_lose, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "combination" : self.dice_combination_name(combination)
        })
    
    def dice_minor_win(self, user:User, combination:List[int], money:int) -> str:
        return tp.text_replacement(self.__dice_minor_win, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "combination" : self.dice_combination_name(combination),
            "money" : self.money_wrapper(money), 
        })
    
    def dice_major_win(self, user:User, combination:List[int], money:int) -> str:
        return tp.text_replacement(self.__dice_major_win, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "combination" : self.dice_combination_name(combination),
            "money" : self.money_wrapper(money), 
        })
    
    def trash_loto_minor_length_award(self, full_name:str, tg_id:int, length:int) -> str:
        return tp.text_replacement(self.__trash_loto_minor_length_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "length" : self.length_wrapper(length, False), 
            **self.random_member(),
        })
    
    def trash_loto_consolation_money_award(self, full_name:str, tg_id:int, money:int) -> str:
        return tp.text_replacement(self.__trash_loto_consolation_money_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "money" : self.money_wrapper(money, False), 
        })
    
    def trash_loto_minor_money_award(self, full_name:str, tg_id:int, money:int) -> str:
        return tp.text_replacement(self.__trash_loto_minor_money_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "money" : self.money_wrapper(money, False), 
        })
    
    def trash_loto_major_length_award(self, full_name:str, tg_id:int, length:int) -> str:
        return tp.text_replacement(self.__trash_loto_major_length_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "length" : self.length_wrapper(length, False), 
            **self.random_member(),
        })
    
    def trash_loto_major_money_award(self, full_name:str, tg_id:int, money:int) -> str:
        return tp.text_replacement(self.__trash_loto_major_money_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "money" : self.money_wrapper(money, False), 
        })
    
    def trash_loto_jackpot_money_award(self, full_name:str, tg_id:int, money:int) -> str:
        return tp.text_replacement(self.__trash_loto_jackpot_money_award, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "money" : self.money_wrapper(money, False), 
        })
    
    
    def trash_loto_lose(self, full_name:str, tg_id:int) -> str:
        return tp.text_replacement(self.__trash_loto_lose[random.randint(0, len(self.__trash_loto_lose) - 1)], {
            "user_link" : self.get_user_link(full_name, tg_id),
        })

    
    def first_meet(self, full_name:str, tg_id:int, length:int,  custom_title: Optional[str]) -> str:  
        return tp.text_replacement(self.__first_meet, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "length" : self.length_wrapper(length, False), 
            "custom_title": f'А погоняло твое... Ага! {custom_title}' if type(custom_title) is str else '',
            **self.random_member(),
        }) 

    def user_information(self, user:User, place_in_top:int, time_to_pencil:str = "Готов", time_to_dice:str = "Готов") -> str:
        return tp.text_replacement(self.__user_information,
                                   {**self.random_member(),
                                    "user_link" : self.get_user_link(user.tg_name, user.tg_id),
                                    "money": user.money,
                                    "medal": self.get_medal_emoji(place_in_top),
                                    "user_stats": self.generate_user_stats(user),
                                    "place_in_top": place_in_top,
                                    "custom_title" : hcode(f'[{user.custom_title}]') if user.custom_title is not None else '',
                                    "length":self.length_wrapper(user.length, False),
                                    "time_to_pencil" : time_to_pencil,
                                    "time_to_dice" : time_to_dice})
    
    def generate_user_stats(self, user:User) -> str:
        stats_str:str = ""

        stats_str += f"🎰 Всего спинов\джекпотов: <b>{user.trash_loto_spins} \ {user.trash_loto_jackpots}</b>\n"
        stats_str += f"🍀 Выигрыш в треш-лото: <b>{self.money_wrapper(user.trash_loto_money_wins)} \ {self.length_wrapper(user.trash_loto_length_wins)}</b>\n"
        stats_str += f"🎲 Статистика игры в кости: <b>{user.dice_games} \ 🎯{user.dice_minor_wins + user.dice_major_wins}</b>\n"
        stats_str += f"🏟 Всадил/выиграл на арене: <b>{user.gladiators_bet} \ {user.gladiators_bet_win}</b>\n"
        stats_str += f"🏹 Уничтожил чудовищ: <b>{user.good_hunting_count}</b>"

        return stats_str
    
    def user_inventory(self, user:User) -> str:
        return tp.text_replacement(self.__inventory_info, {
            "items" : self.__generate_inventory_items_list(user.inventory) if user.inventory else "<b>В рюкзаке пусто!</b>",
            "user_link": self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(), 
        }, recursive_parse_args = True)
    
    def __generate_inventory_items_list(self, items:List[InventoryItem]) -> str:
        items_str:str = ""
        index:int = 1
        for item in items:
            items_str += f"<b>({index})</b> {item.utf8_icon} {hcode(item.title)}<b> ({item.quantity}шт.)</b>\n"
            index+=1

        return items_str
    
    def inventory_item_info(self, item:InventoryItem) -> str:
        return tp.text_replacement(self.__inventory_item_info, {
            "title": item.title,
            "description": item.description,
            **self.random_member(),
        }, recursive_parse_args = True)
    
    def day_salary(self, money:int) -> str:
        return tp.text_replacement(self.__day_salary, {"money" : self.money_wrapper(money)})
    
    def tech_work_compensation(self, money:int) -> str:
        return tp.text_replacement(self.__tech_work_compensation, {"money" : self.money_wrapper(money)})
    
    def draw(self, user:User, length_change:int) -> str:
        return tp.text_replacement(self.__draw_list[random.randint(0, len(self.__draw_list) - 1)], {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(), 
            "length":self.length_wrapper(length_change), 
        })
    
    def weekly_winners(self, users:List[User], rewards:List[int]) -> str:
        return tp.text_replacement(self.__weekly_winners[random.randint(0, len(self.__weekly_winners) - 1)],{
            "winners" : self.__generate_leaderboard(users, rewards),
            **self.random_member(),
        })
    
    def __generate_leaderboard(self, users:List[User], rewards:List[int] = []) -> str:
        winners:str = ""
        for index, user in enumerate(users):
            winners += f"{self.get_medal_emoji(index+1, True)}"\
            f" {self.length_wrapper(user.length, False)} - "\
            f" {self.get_user_link(user.tg_name, user.tg_id)}"\
            f"{f' [{user.custom_title}] ' if type(user.custom_title) is str else ''}"\
            f" ({self.money_wrapper(user.money, False)})"\
            f" { f'{self.money_wrapper(rewards[index])}' if (len(rewards) > index) else ''}\n"
        return winners
    
    def leaderboard(self, users:List[User]) -> str:
        return tp.text_replacement(self.__leaderboard,{
            "leaderboard" : self.__generate_leaderboard(users),
            **self.random_member(),
        })
    
    def __generate_winners_logs(self, logs:List[WinnersLog], users:List[User]) -> str:
        winners:str = ""
        for index, log in enumerate(logs):
            user:List[User] = [user for user in users if user.id == log.user_id]

            winners += f"{hcode(Utils.format_datetime(log.win_date))}"\
            f" {self.__winner_log_event_by_index(log.event_type)} "\
            f" {self.get_user_link(user[0].tg_name, user[0].tg_id)} - "\
            f" {self.money_wrapper(log.money) if log.money > 0 else self.length_wrapper(log.length)}\n"\
           
        return winners
    
    def __winner_log_event_by_index(self, index:int) -> str:
        if (index == 0):
            return "🎰💎 Джекпот"
        elif (index == 1):
            return "🎰☘️ средняя"
        elif (index == 2):
            return "🎰🍀 большая"
        elif (index == 3):
            return "🎰🌱 мини"
        elif (index == 4):
            return "🎲🍀 мини"
        elif (index == 5):
            return "🎲💎 большая"
        else:
            return ""
    
    def winners_logs(self, logs:List[WinnersLog], users:List[User]) -> str:
        return tp.text_replacement(self.__winners_log,{
            "logs" : self.__generate_winners_logs(logs, users),
        })
    
    def sticker_set_create_success(self, sticker_set_name:str) -> str:
        return tp.text_replacement(self.__sticker_set_create_success, {
            "sticker_set_name":sticker_set_name
        })
    
    def sticker_add_to_set_success(self, sticker_set_name:str) -> str:
        return tp.text_replacement(self.__sticker_add_to_set_success, {
            "sticker_set_name":sticker_set_name
        })

    def length_change(self, tg_name:str, length_change:int) -> str:
        params: Dict = {**self.random_member(), 
                        "length":self.length_wrapper(length_change), 
                        "tg_name": hbold(tg_name)}
        
        if (length_change > 0):
            return tp.text_replacement(f"⚠️ {self.__positive_length_change[random.randint(0, len(self.__positive_length_change) - 1)]}",
                                       params)
        else:
            return tp.text_replacement(
                f"⚠️ {self.__negative_length_change[random.randint(0, len(self.__negative_length_change) - 1)]}",
                                       params)
        
    def user_wrapper(self, user:User, show_length:bool = True) -> str:
        return tp.text_replacement("{{user_link}} {{custom_title}}" + " - {{length}}" if (show_length) else "", {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "custom_title" : hcode(f'[{user.custom_title}]') if user.custom_title is not None else '',
            "length":self.length_wrapper(user.length, False)
        })
    
    def random_member(self) -> Dict[str, str]:
        member:List[str] = random.choice(self.member_names)
        return {
            "pencil":member[0],
            "pencil_gen":member[1],
            "pencil_dat":member[2],
            "pencil_accu":member[3],
            "pencil_inst":member[4],
            "pencil_prep":member[5]
        }
    
    def get_part_cases(self, parts:List[BodyParts], prefix:str = "") -> Dict[str, str]:
        parts_str:dict[BodyParts, dict[str, str]] = {
            BodyParts.HEAD: {
                f"{prefix}part": "кабина",
                f"{prefix}part_gen": "кабины",
                f"{prefix}part_dat": "кабине",
                f"{prefix}part_accu": "кабину",
                f"{prefix}part_inst": "кабиной",
                f"{prefix}part_prep": "о кабине",
                f"{prefix}part_prep_ob": "об кабину",
            },
            BodyParts.CHEST: {
                f"{prefix}part": "туз",
                f"{prefix}part_gen": "туза",
                f"{prefix}part_dat": "тузу",
                f"{prefix}part_accu": "туз",
                f"{prefix}part_inst": "тузом",
                f"{prefix}part_prep": "о тузе",
                f"{prefix}part_prep_ob": "о тузе",
            },
            BodyParts.KNEES: {
                f"{prefix}part": "костыли",
                f"{prefix}part_gen": "костылей",
                f"{prefix}part_dat": "костылям",
                f"{prefix}part_accu": "костыли",
                f"{prefix}part_inst": "костылями",
                f"{prefix}part_prep": "о костылях",
                f"{prefix}part_prep_ob": "о костылях",
            },
        }

        return parts_str[parts[0]] if (parts) else random.choice(list(parts_str.values()))
    
    def timer_message(self, user:User, time_left:str) -> str:
        return tp.text_replacement(self.__timer_message, {
            "time_left" : time_left,
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            })
    
    def hunt_timer_message(self, user:User, time_left:str) -> str:
        return tp.text_replacement(self.__hunt_timer_message, {
            "time_left" : time_left,
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            })
    
    def length_wrapper(self, length:int, plus_visible:bool = True) -> str:
        return hcode(f'{"+" if (length > 0 and plus_visible) else ""}{length}см')
    
    def money_wrapper(self, money:int, plus_visible:bool = True) -> str:
        return hbold(f'{"+" if (money > 0 and plus_visible) else ""}{money}💰')
    
    def price_wrapper(self, money:int, bold:bool = True) -> str:
        return hbold(f'{money - 1},99') if (bold) else f"{money - 1},99"
    
    def get_medal_emoji(self, place_in_top:int, only_tops:bool = False):
        if (place_in_top == 1):
            return "🥇"
        elif (place_in_top == 2):
            return "🥈"
        elif (place_in_top == 3):
            return "🥉"
        else:
            return "" if only_tops else "🏅"
        
    ###------------------------------------------------------------
    ###Методы битвы
    ###------------------------------------------------------------

    def battle_end_draft(self, deads:List[BattleUnit]) -> str:
        return "⚰️⚰️ Бой кровавый, и победителя в нем нет, лежат все без дыхания..."
    
    def battle_turn_log(self, active:BattleUnit, opponent:BattleUnit,
                        active_status:Optional[Tuple[AttackStatus, int, bool]], 
                        opponent_status:Optional[Tuple[AttackStatus, int, bool]],
                        mode:BattleMode = BattleMode.HUNT):
        full_log:str = ""
        status_icon:str = "⏳" if (active_status[0] == AttackStatus.NONE) else "🩸" if (active_status[0] == AttackStatus.DAMAGED) else "🛡"
        opponent_damage_str:str = f"Получено: <code>{(f'🎯{active_status[1]}!') if (active_status[2]) else (f'💥{active_status[1]}') }</code>" if active_status[1] else ""
        active_damage_str:str = f"Нанесено: <code>{(f'🎯{opponent_status[1]}!') if (opponent_status[1]) else (f'💥{opponent_status[1]}') }</code>" if opponent_status[1] else ""

        action_protect:str = tp.text_replacement(random.choice(self.battle_protect_description), 
                                                {**self.get_part_cases(active.protected_parts),
                                                 **self.random_member()}) 
            
        action_attack:str = tp.text_replacement(random.choice(self.battle_attack_description), {
                        **self.get_part_cases(active.attack_target),
                        **self.random_member()
                    })
        
        action_damaged:str = tp.text_replacement(random.choice(self.battle_attacked_description), {
                        **self.get_part_cases(opponent.attack_target),
                        **self.random_member()
                    })
        
        action_none_attacked:str = tp.text_replacement(random.choice(self.battle_none_status_description), {
            **self.random_member()
        })

        if (active_status[0] in [AttackStatus.NONE, AttackStatus.DEFENDED]):
            full_log += f"{active.short_battle_name} {action_none_attacked if (active_status[0] == AttackStatus.NONE) else action_protect}"    

        if (active_status[0] == AttackStatus.DAMAGED):
            full_log += f"{active.short_battle_name} {action_damaged}"    
        
        full_log += f'{active.short_battle_name if (not full_log) else ", затем"} {action_attack}'\
              if (opponent_status[0] == AttackStatus.DAMAGED) else ''

        if (mode == BattleMode.HUNT):
            full_log += f"\n[{active_damage_str}{' | ' if (active_damage_str and opponent_damage_str) else ''}{opponent_damage_str}]" \
                if (active_damage_str or opponent_damage_str) else ''

        return tp.text_replacement(status_icon + full_log, {**self.random_member()})
    
    def hunt_loot(self, inventory:Optional[Tuple[List[ItemORM], int]]) -> str:
        if (not inventory): return ""
        money:str = f" {'А так же монеты' if inventory[0] else 'Собрали с трупа горсть монет'} {self.money_wrapper(inventory[1])}" if (inventory[1]) else ""

        item:str = ""
        if (inventory[0]):
            item = tp.text_replacement(random.choice(self.__hunt_loot), {
            "item_name": inventory[0][0].title,
            "item_icon": inventory[0][0].utf8_icon,
            **self.random_member()
        }, recursive_parse_args = True)

        return item + money


    def battle_end(self, dead:BattleUnit, winner:BattleUnit, mode:BattleMode, damage:Tuple[int, bool]) -> str:
        icon_hunt:str = "☠️" if (mode == BattleMode.HUNT and type(dead.entity) is User) else "🎯"
        icon_gladiators:str = "💰" if (dead.bet_money == 0) else "🚽"

        icon:str = icon_hunt if (mode == BattleMode.HUNT) else icon_gladiators
        return tp.text_replacement(icon + " {{player1}} {{dead}}, получив {{opponent_hit}}, {{winner}} празднует победу!", {
            "player1": dead.short_battle_name,
            "winner" : winner.short_battle_name,
            "dead": tp.text_replacement(random.choice(self.battle_dead_description), {
                **self.random_member(),
                **self.get_part_cases(dead.protected_parts),
            }),
            "opponent_hit" : f"<code>[{(f'🎯{damage[0]}!') if (damage[1]) else (f'💥{damage[0]}') }]</code>",
        })
    