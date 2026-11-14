from core.consts.config import Prefs
from core.utils.app_herald import AppHerald
from typing import List, Optional
import logging
import random
import html
import re

# Локальные курируемые списки — используются всегда как фолбэк,
# а для анекдота как основной источник, если API не настроен или недоступен.

ANECDOTES: List[str] = [
    "— Доктор, меня все игнорируют.\n— Следующий!",
    "Рыбак час сидел без клёва. Потом без клёва сидел уже весь берег.",
    "— Сколько раз тебе говорить, что счастье не в деньгах?\n— Да пока не скажешь — не поверю.",
    "Оптимист изобрёл самолёт, пессимист — парашют, а реалист до сих пор ждёт свой рейс.",
    "В казино уверены: деньги любят тишину. Особенно когда уходят.",
    "— Папа, а правда, что в некоторых странах мужчина может иметь трёх жён?\n— Правда, сынок. Но не в этой квартире.",
    "Программист ставит на стол два стакана: один с водой — если захочет пить, второй пустой — если не захочет.",
    "Крупная рыба потому и крупная, что мелкую не слушает.",
]

HOROSCOPES: List[str] = [
    "Овнам на этой неделе противопоказано спорить с рыбой крупнее их самих.",
    "Тельцов ждёт неожиданная прибыль. Настолько неожиданная, что они её не заметят.",
    "Близнецам звёзды рекомендуют определиться, чего они всё-таки хотят, хотя бы к пятнице.",
    "Ракам совет: не пятитесь назад хотя бы в сторону гамба-хауса.",
    "Львам на этой неделе лучше делить улов, а не царский трон.",
    "Девам звёзды обещают идеальный порядок. Держитесь, это ненадолго.",
    "Весам предстоит сложный выбор: леска потолще или спиннинг полегче.",
    "Скорпионам не стоит жалить руку, которая вас кормит. Особенно если в руке удочка.",
    "Стрельцам повезёт ровно один раз. Не промахнитесь.",
    "Козерогам звёзды советуют иногда спускаться с вершины к воде.",
    "Водолеям на этой неделе лучше лить воду, а не слёзы над проигрышем.",
    "Рыбам — лучший клёв недели. Но осторожно: могут поймать и их самих.",
]

FAKE_HEADLINES: List[str] = [
    "Учёные доказали: рыба клюёт лучше, когда никто не видит.",
    "Местный житель выловил рыбу мечты. Рыба подала встречный иск.",
    "В гамба-хаусе обнаружен аномально щедрый игрок. Ведётся проверка на святость.",
    "Экономика чата показала рекордный рост. Эксперты в шоке, эксперты — это мы.",
    "Спиннинг недели признан виновным в чрезмерном улове.",
    "Британские учёные выяснили, почему не клюёт. Ответ засекречен до лучших времён.",
    "В водоёме замечена легендарная рыба. Рыболовы объявили трёхдневный пост.",
]

FISH_FACTS: List[str] = [
    "Факт дня: рыба не тонет, потому что считает это ниже своего достоинства.",
    "Факт дня: чешуя — это броня, которую рыба забыла снять перед сном.",
    "Факт дня: рыбы спят с открытыми глазами, чтобы следить за вашими снастями.",
    "Факт дня: самая крупная рыба всегда находится на один заброс дальше вашего.",
    "Факт дня: рыба помнит каждого, кто её упустил. И рассказывает подругам.",
    "Факт дня: у рыб нет век, зато есть огромное самомнение.",
]

FISHING_FORECASTS: List[str] = [
    "Прогноз клёва: 9/10. Ветер в сторону казино, но вы держитесь.",
    "Прогноз клёва: 3/10. Рыба ушла в отпуск, берите выходной и вы.",
    "Прогноз клёва: 7/10. Идеально, чтобы хвастаться и не очень — чтобы ловить.",
    "Прогноз клёва: 11/10. Берите подсак побольше и соседа для свидетелей.",
    "Прогноз клёва: 5/10. Клевало бы лучше, если бы вы не шумели.",
    "Прогноз клёва: 1/10. Даже червяк попросил отпуск за свой счёт.",
]

# Ограничение на длину анекдота: газета уходит подписью к фото,
# а у caption в Telegram лимит 1024 символа на весь выпуск.
MAX_ANECDOTE_LENGTH = 300

# Соответствие категории и заголовка блока в газете
CATEGORIES = {
    "anecdote": ("🎭 Анекдот недели", ANECDOTES),
    "horoscope": ("🔮 Гороскоп недели", HOROSCOPES),
    "headline": ("📢 Заголовок недели", FAKE_HEADLINES),
    "fish_fact": ("🐟 Факт о рыбе", FISH_FACTS),
    "forecast": ("🎣 Прогноз клёва", FISHING_FORECASTS),
}


class HumorProvider:
    """Генератор случайного юмористического наполнения для еженедельной газеты.
    Пытается получить анекдот из внешнего API (если настроен), иначе — из локального списка."""

    def __init__(self):
        self.prefs = Prefs()
        self.logger = AppHerald()

    async def get_blocks(self, count: int = 2) -> List[dict]:
        """Анекдот входит в каждый выпуск; остальные (count - 1) блоков выбираются
        случайно из прочих категорий. Возвращает список {'title', 'text'}."""
        # Анекдот стараемся взять из API, если он настроен и доступен
        api_anecdote: Optional[str] = await self.__fetch_api_anecdote()
        anecdote_title, anecdote_source = CATEGORIES["anecdote"]
        # Длинные анекдоты отсеиваем — иначе выпуск не влезет в лимит подписи
        short_anecdotes = [a for a in anecdote_source if len(a) <= MAX_ANECDOTE_LENGTH] or list(anecdote_source)
        blocks: List[dict] = [{
            "title": anecdote_title,
            "text": api_anecdote or random.choice(short_anecdotes),
        }]

        other_keys = [key for key in CATEGORIES if key != "anecdote"]
        random.shuffle(other_keys)
        for key in other_keys[:max(0, count - 1)]:
            title, source = CATEGORIES[key]
            blocks.append({"title": title, "text": random.choice(source)})

        return blocks

    async def __fetch_api_anecdote(self) -> Optional[str]:
        """Попытка получить случайный анекдот из внешнего источника (HTML-страница,
        например https://baneks.ru/random). Любой сбой тихо игнорируется — сработает локальный фолбэк."""
        url = (self.prefs.anecdote_api_url or "").strip()
        if not url:
            return None

        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=8)
            headers = {"User-Agent": "Mozilla/5.0 (compatible; JesterAI-newspaper/1.0)"}
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                # baneks.ru/random отвечает 302 на страницу конкретного анекдота — aiohttp идёт по редиректу
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    page = await response.text()

            return self.__parse_anecdote(page)
        except Exception as error:
            self.logger.send_log("newspaper", logging.WARNING, f"anecdote api error: {error}")
            return None

    def __parse_anecdote(self, page: str) -> Optional[str]:
        """Достаёт текст анекдота из HTML, приводит переносы строк и экранирует под Telegram HTML."""
        if not page:
            return None

        # Основной контейнер: <section class="anek-view"> ... <article> ... <p>...</p> ... </article>
        article = re.search(r"<article[^>]*>(.*?)</article>", page, re.DOTALL | re.IGNORECASE)
        chunk = article.group(1) if article else page

        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.DOTALL | re.IGNORECASE)
        if not paragraphs:
            # Фолбэк: мета-тег description содержит полный текст анекдота
            meta = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
                page, re.DOTALL | re.IGNORECASE)
            if not meta:
                return None
            paragraphs = [meta.group(1)]

        raw = "\n".join(paragraphs)
        raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
        raw = re.sub(r"<[^>]+>", "", raw)

        text = html.unescape(raw).strip()
        # Отсеиваем слишком длинные анекдоты: выпуск должен влезть в лимит подписи (1024)
        if not text or len(text) > MAX_ANECDOTE_LENGTH:
            return None

        # Экранируем служебные символы, т.к. газета отправляется с parse_mode=HTML
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

