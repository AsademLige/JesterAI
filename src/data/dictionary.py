from aiogram.utils.markdown import hbold, hcode, hblockquote, hitalic
from src.domain.utils.text_processing import TextProcessing as tp
from src.models.user_model import UserModel
from typing import Optional, List, Dict
import random

class Dictionary():
    def __init__(self):
        pass

    ###------------------------------------------------------------
    ###Описание команд бота
    ###------------------------------------------------------------

    help:str = "Что умеет бот"

    me:str = "Информация обо мне"

    pencil:str = "Недоволен своим размером? ЖМИ СЮДА"

    edit_sticker_set:str = "Изменить набор стикеров"

    create_sticker_set:str = "Создать набор стикеров"

    ###------------------------------------------------------------
    ###Общее
    ###------------------------------------------------------------

    error:str = "Что-то мне сегодня плохо, приходи попозже..."

    exit:str = "❌ Выход"

    back:str = "↩ Назад"

    skip:str = "⏩ Пропустить"

    trigger:str = "🚀 Запустить"

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
    '💰 Монет на руках: {{money}}'

    private_messages_restriction: str = "🚧 Здесь тебе(🤡) делать нечего 🚧"

    __user_link_m2 : str = '[{{full_name}}](tg://user?id={{tg_id}})'

    __user_link_html : str = '<a href="tg://user?id={{tg_id}}">{{full_name}}</a>'

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
    
    choice_sticker_set:str = "Выбери набор стикеров, который хочешь изменить"

    sticker_set_list_is_empty:str = "Нет наборов стикеров!"

    sticker_edit_variants:str = "Вот что мы можем с ним сделать:"

    delete_sticker_set_success:str = "🟢 Удалили удачно!"

    delete_sticker_set:str = "🚫 Удалить набор"

    add_sticker_to_set:str = "📥 Добавить стикер"

    delete_sticker_from_set:str = "🗑️ Удалить стикер"

    ###------------------------------------------------------------
    ###Описания розыгрышей
    ###------------------------------------------------------------

    __draw_list:List[str] = [
        '🎁 Запускаем розыгрыш мази для увеличения {{pencil_gen}}! '\
        'И сегодняшним победителем становится... 🎉{{user_link}}🎊, поздравляем победителя!\n'\
        'Его выигрыш составил: {{length}}'
    ]

    ###------------------------------------------------------------
    ###Описания подведения итогов
    ###------------------------------------------------------------

    __weekly_winners:List[str] = [
        "<blockquote>🏆 Начинаем подведение итогов в номинации «Самый длинный {{pencil}} недели»!</blockquote>\n{{winners}}"
    ]

    ###------------------------------------------------------------
    ###интерактивные действия изменения размера
    ###------------------------------------------------------------
    __positive_length_change:List[str] = [
    'Шут капает на член пользователя {{tg_name}} капельку странной жижи. '\
    'Тот в восторге! {{pencil}} увеличен на {{length}}',

    'Шут раздает получку, {{tg_name}} получает неожиданную прибавку на {{length}}, наливай!',

    'Шуту лень что-то придумывать, {{tg_name}} получает прибавку {{length}}',

    '{{tg_name}} сунул {{pencil}} в трубу пылесоса... {{length}}',
    
    'Волшебная палочка Шута срабатывает как надо! {{tg_name}} увеличивает {{pencil_accu}} на {{length}}',

    '🐁 {{tg_name}} крадет у шута {{length}}',

    'Шут проводит конкурс на самый длинный {{pencil}}... {{tg_name}} получает поощрительный приз размером {{length}}',

    'Рандом сегодня на стороне черта по имени {{tg_name}}! Он получает прибавку {{length}}',

    'Вы помогли бабушке перейти дорогу. Ваш внутренний стержень выпрямился на {{length}}!',

    'Пользователю {{tg_name}} впору теперь чесать свой {{pencil}} где-то в районе колена! Он увеличился на {{length}}',

    'Не в ширь, а ввысь!!! {{tg_name}} увеличивает свой дубильный шест на {{length}}',
    ]

    __negative_length_change:List[str] = [
    'Шут пританцовывает вокруг бедолаги с острым ножичком в руках! '\
    '{{tg_name}} нервничает. Ой... {{pencil}} уменьшен на {{length}}',

    'Джонклер достал острые ножницы! {{tg_name}} в ужасе! Но ничего не произошло...'\
    'От страха {{pencil}} уменьшился на {{length}}',   

    'Шут заявляет: <blockquote>Краткость сестра таланта!</blockquote>'\
    'С этими словами он уменьшает {{pencil_accu}} на {{length}} '\
    'совершенно нечестным способом! {{tg_name}} в слезах!',

    'Шут негодует: <blockquote>"Работал бы лучше, чем тут ерундой заниматься!\n'\
    'Выписываю тебе штраф в размере... {{length}}, давай оттяпывай</blockquote>',

    'Шут раздает получку, {{tg_name}} депремирован на {{length}}!',

    'Увеличение члена в домашних условиях! Нужно всего лишь каждый день... '\
    '{{tg_name}} пользовался советом три дня, но {{pencil}} сморщился на {{length}}',

    'Волшебная палочка Шута дает осечку! {{tg_name}} уменьшает {{pencil_accu}} на {{length}}',

    '{{tg_name}} смотрит на свои активы... {{pencil}} подвергается инфляции!\n'\
    'Ценные активы уменьшаются на {{length}}',

    'У Джонклера сегодня плохое настроение. Под руку попадается {{tg_name}}... {{length}}',

    'Шут решил, что ты и так слишком выделяешься!\n'\
    '<blockquote>Теперь твой {{pencil}} как WiFi в деревне: есть, но слабый! Получай {{length}}</blockquote>',
    ]

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

    __member_change_not_reset:str = "С тебя уже хватит, приходи позже...\n"\
    "<blockquote>⏰ Осталось потерпеть часов: {{hours}}</blockquote>"
    
    ###------------------------------------------------------------
    ###Методы
    ###------------------------------------------------------------

    def get_user_link(self, full_name: str, tg_id:int) -> str:
        return tp.text_replacement(self.__user_link_html, {
            "tg_id" : tg_id,
            "full_name" : full_name,
        })

    
    def first_meet(self, full_name:str, tg_id:int, length:int,  custom_title: Optional[str]) -> str:  
        return tp.text_replacement(self.__first_meet, {
            "user_link" : self.get_user_link(full_name, tg_id),
            "length" : self.length_wrapper(length, False), 
            "custom_title": f'А погоняло твое... Ага! {custom_title}' if type(custom_title) is str else '',
            **self.random_member(),
        }) 

    def user_information(self, user:UserModel, place_in_top:int) -> str:
        return tp.text_replacement(self.__user_information,
                                   {**self.random_member(),
                                    "user_link" : self.get_user_link(user.tg_name, user.tg_id),
                                    "money": user.money,
                                    "medal": self.get_medal_emoji(place_in_top),
                                    "place_in_top": place_in_top,
                                    "custom_title" : hcode(f'[{user.custom_title}]') if user.custom_title is not None else '',
                                    "length":self.length_wrapper(user.length, False)})
    
    def draw(self, user:UserModel, length_change:int) -> str:
        return tp.text_replacement(self.__draw_list[random.randint(0, len(self.__draw_list) - 1)], {
            "user_link" : self.get_user_link(user.tg_name, user.tg_id),
            **self.random_member(), 
            "length":self.length_wrapper(length_change), 
        })
    
    def weekly_winners(self, users:List[UserModel], rewards:List[int]) -> str:
        return tp.text_replacement(self.__weekly_winners[random.randint(0, len(self.__weekly_winners) - 1)],{
            "winners" : self.__generate_weekly_winners(users, rewards),
            **self.random_member(),
        })
    
    def __generate_weekly_winners(self, users:List[UserModel], rewards:List[int]) -> str:
        winners:str = ""
        for index, user in enumerate(users):
            winners += f"{self.get_medal_emoji(index+1, True)}"\
            f" {self.length_wrapper(user.length, False)} - "\
            f" {self.get_user_link(user.tg_name, user.tg_id)}"\
            f"{f' [{user.custom_title}] ' if type(user.custom_title) is str else ''}"\
            f" { f'{self.money_wrapper(rewards[index])}' if (len(rewards) > index) else ''}\n"
        return winners
    
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
    
    def member_change_not_reset(self, hours_left:int) -> str:
        return tp.text_replacement(self.__member_change_not_reset, {"hours" : hours_left})
    
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
