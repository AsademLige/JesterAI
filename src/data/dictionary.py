from aiogram.utils.markdown import hbold, hcode, hblockquote, hitalic
from src.domain.utils.text_processing import TextProcessing as tp
from src.services.data_base.db import DataBase
from src.models.winners_log import WinnersLog
from src.models.user_model import UserModel
from src.domain.utils.utils import Utils
from typing import Optional, List, Dict
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
                        "У нас тут что-то вроде интерактивной игры, команда /me покажет небольшую сводку с твоими успехами\n\n"\
                        "Меряйся хозяйством с другими участниками! Команда /pencil поможет тебе получить БОЛЬШОЕ признание <i>(но есть шанс, что уменьшит его)</i>"\
                        "Бот все же заскамил тебя? Подожди 24 часа и пробуй еще раз!\n\n"\
                        "Каждый день проводим розыгрыш среди участников чата, а каждую пятницу подведем итоги и наградим самых крутых участников!\n\n"\
                        "<i>Все вопросы и предложения отправлять на почтовый ящик:</i> <code>2202202000651657</code>"
    
    __answer_restricted:str = "⛔️ Команду вызвал {{user_link}}, так что руки прочь!"

    ###------------------------------------------------------------
    ###Взаимодействие с пользователем
    ###------------------------------------------------------------
    
    __first_meet : str = 'А тебя я раньше здесь не видел... Ты, значится, {{user_link}}! '\
    'А я Шут. Ромашковый.🤡 Я работаю на мобильных разработчиков в их мобильном подвале. '\
    'Дай-ка я на тебя взгляну...\nИзмерим твой {{pencil}}...'\
    '\nОго! Вот это питон! {{length}}\n'\
    '{{custom_title}}'
    
    __user_information : str = f'{hblockquote("🔍 {{user_link}} {{custom_title}} Имеет {{pencil_accu}} длинной {{length}}!")}\n'\
    '{{medal}} Место в топе: {{place_in_top}}\n'\
    '💰 Монет на руках: {{money}}\n'\
    '⏰ Время до pencil: {{time_to_pencil}}\n'\
    '⏰ Время до dice_game: {{time_to_dice}}'

    private_messages_restriction: str = "🚧 Здесь тебе(🤡) делать нечего 🚧"

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
    ###изменение набора стикеров
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
    ###Описания треш лото
    ###------------------------------------------------------------

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
    ###Переменные игры с дайсами
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
        ["Нефритовый стержень", "Нефритового стержня", "Нефритовому стержню","Нефритовый стержень","Нефритовым стержнем",""],
        ["питон", "питона", "питону","питон","питоном",""],
        ["чучундрик", "чучундрика", "чучундрику","чучундрик","чучундриком",""],
        ["пистон", "пистона", "пистону","пистон","пистоном",""]
    ]

    __timer_message:str = "{{user_link}}, с тебя уже хватит, приходи позже...\n"\
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
    
    def not_enough_money(self, user:UserModel) -> str:
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

    
    def dice_lose(self, user:UserModel, combination:List[int], ) -> str:
        return tp.text_replacement(self.__dice_lose, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "combination" : self.dice_combination_name(combination)
        })
    
    def dice_minor_win(self, user:UserModel, combination:List[int], money:int) -> str:
        return tp.text_replacement(self.__dice_minor_win, {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "combination" : self.dice_combination_name(combination),
            "money" : self.money_wrapper(money), 
        })
    
    def dice_major_win(self, user:UserModel, combination:List[int], money:int) -> str:
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

    def user_information(self, user:UserModel, place_in_top:int, time_to_pencil:str = "Готов", time_to_dice:str = "Готов") -> str:
        return tp.text_replacement(self.__user_information,
                                   {**self.random_member(),
                                    "user_link" : self.get_user_link(user.tg_name, user.tg_id),
                                    "money": user.money,
                                    "medal": self.get_medal_emoji(place_in_top),
                                    "place_in_top": place_in_top,
                                    "custom_title" : hcode(f'[{user.custom_title}]') if user.custom_title is not None else '',
                                    "length":self.length_wrapper(user.length, False),
                                    "time_to_pencil" : time_to_pencil,
                                    "time_to_dice" : time_to_dice})
    
    def day_salary(self, money:int) -> str:
        return tp.text_replacement(self.__day_salary, {"money" : self.money_wrapper(money)})
    
    def tech_work_compensation(self, money:int) -> str:
        return tp.text_replacement(self.__tech_work_compensation, {"money" : self.money_wrapper(money)})
    
    def draw(self, user:UserModel, length_change:int) -> str:
        return tp.text_replacement(self.__draw_list[random.randint(0, len(self.__draw_list) - 1)], {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(), 
            "length":self.length_wrapper(length_change), 
        })
    
    def weekly_winners(self, users:List[UserModel], rewards:List[int]) -> str:
        return tp.text_replacement(self.__weekly_winners[random.randint(0, len(self.__weekly_winners) - 1)],{
            "winners" : self.__generate_leaderboard(users, rewards),
            **self.random_member(),
        })
    
    def __generate_leaderboard(self, users:List[UserModel], rewards:List[int] = []) -> str:
        winners:str = ""
        for index, user in enumerate(users):
            winners += f"{self.get_medal_emoji(index+1, True)}"\
            f" {self.length_wrapper(user.length, False)} - "\
            f" {self.get_user_link(user.tg_name, user.tg_id)}"\
            f"{f' [{user.custom_title}] ' if type(user.custom_title) is str else ''}"\
            f" ({self.money_wrapper(user.money, False)})"\
            f" { f'{self.money_wrapper(rewards[index])}' if (len(rewards) > index) else ''}\n"
        return winners
    
    def leaderboard(self, users:List[UserModel]) -> str:
        return tp.text_replacement(self.__leaderboard,{
            "leaderboard" : self.__generate_leaderboard(users),
            **self.random_member(),
        })
    
    def __generate_winners_logs(self, logs:List[WinnersLog], users:List[UserModel]) -> str:
        winners:str = ""
        for index, log in enumerate(logs):
            user:List[UserModel] = [user for user in users if user.id == log.user_id]

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
    
    def winners_logs(self, logs:List[WinnersLog], users:List[UserModel]) -> str:
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
        
    def media_caption(self, user:UserModel) -> str:
        return tp.text_replacement("Отправил: {{user_link}} {{custom_title}} - {{length}}", {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            "custom_title" : hcode(f'[{user.custom_title}]') if user.custom_title is not None else '',
            "length":self.length_wrapper(user.length, False)
        })
    
    def random_member(self) -> Dict[str, str]:
        index:int = random.randint(0, len(self.member_names) - 1)
        return {
            "pencil":self.member_names[index][0],
            "pencil_gen":self.member_names[index][1],
            "pencil_dat":self.member_names[index][2],
            "pencil_accu":self.member_names[index][3],
            "pencil_inst":self.member_names[index][4],
            "pencil_prep":self.member_names[index][5]
        }
    
    def timer_message(self, user:UserModel, time_left:str) -> str:
        return tp.text_replacement(self.__timer_message, {
            "time_left" : time_left,
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            })
    
    def length_wrapper(self, length:int, plus_visible:bool = True) -> str:
        return hcode(f'{"+" if (length > 0 and plus_visible) else ""}{length}см')
    
    def money_wrapper(self, money:int, plus_visible:bool = True) -> str:
        return hbold(f'{"+" if (money > 0 and plus_visible) else ""}{money}💰')
    
    def get_medal_emoji(self, place_in_top:int, only_tops:bool = False):
        if (place_in_top == 1):
            return "🥇"
        elif (place_in_top == 2):
            return "🥈"
        elif (place_in_top == 3):
            return "🥉"
        else:
            return "" if only_tops else "🏅"
