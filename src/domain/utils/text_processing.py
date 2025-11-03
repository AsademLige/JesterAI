from typing import Dict, Optional, Any
from aiogram.enums import ParseMode
import uuid
import re

class TextProcessing():
    #TODO:Надо добавить возможность делать первую букву значения заглавной
    def text_replacement(text:str, args: Dict[str, Any], parse_mode:ParseMode = ParseMode.HTML) -> str:
        """
        Экранируем символы входящей строки,
        затем подменяем args значения по ключам.
        Шаблонная вставка имеет вид {{value}}
        """
        buf_list:Dict[str, str] = {}
        matches = re.findall(r"(\{\{.*?\}\})", text)
        for match in matches:
            key:str = match[2:len(match)-2]
            if (key in args):
                value:Optional[str] = args[key]
                id:str = uuid.uuid4().hex
                buf_list[id] = value
                text = text.replace(match, id)
            else:
                text = text.replace(match, "&missing_key&")
        
        if (parse_mode == ParseMode.MARKDOWN_V2):
            text = TextProcessing.escape_md2(text)
            

        for key, value in buf_list.items():
            text = text.replace(key, f"{value}")

        return text

    def escape_md2(text:str) -> str:
        """
        Экранируем все markdown спецсимволы
        """
        return re.sub(r'[_[\]()#\+\-=|{}.!]', lambda x: '\\' + x.group(), text)