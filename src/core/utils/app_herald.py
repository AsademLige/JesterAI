from logging.handlers import RotatingFileHandler
from logging import Logger, StreamHandler
from core.consts.consts import Consts
from datetime import datetime, timedelta
from typing import Dict
import logging
import glob
import re
import os

class AppHerald():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    __logs_folder: str = Consts.LOGS_DIR
    __loggers: Dict[str, Logger] = {}

    def send_log(self, module: str, level=logging.DEBUG, message: str = ""):
        if module not in self.__loggers:
            self.logs_init(module)

        logger = self.__loggers[module]
        logger.log(level, message)

    def logs_init(self, module: str, 
                  maxBytes: int = 1024 * 1024,
                  backupCount: int = 5,
                  level=logging.DEBUG,
                  log_format='%(asctime)s - %(levelname)s - %(message)s'):
        
        self.__check_logs_folder(f'{self.__logs_folder}/{module}/')
        formatter = logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = RotatingFileHandler(
            f'{self.__logs_folder}/{module}/{module}.log',
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)

        logger = logging.getLogger(module)
        logger.setLevel(level)
        
        logger.handlers.clear()
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        self.__loggers[module] = logger
    
    def __check_logs_folder(self, path: str):
        if not os.path.isdir(path):
             os.makedirs(path, exist_ok=True)

    def get_logs(self, module: str, period: timedelta) -> list[str]:
        """
        Возвращает список строк логов для указанного модуля за заданный период.
        Пример использования period: timedelta(hours=2) или timedelta(days=1)
        """
        folder_path = f'{self.__logs_folder}/{module}'
        if not os.path.isdir(folder_path):
            return [f"Логи для модуля '{module}' не найдены."]

        now = datetime.now()
        start_time = now - period

        date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')

        matching_logs = []

        log_files = glob.glob(os.path.join(folder_path, f"{module}.log*"))
        log_files.sort(key=os.path.getmtime)

        for file_path in log_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    current_log_entry = ""
                    
                    for line in f:
                        match = date_pattern.match(line)
                        
                        if match:
                            if current_log_entry:
                                self._process_log_entry(current_log_entry, date_pattern, start_time, matching_logs)
                            current_log_entry = line
                        else:
                            if current_log_entry:
                                current_log_entry += line
                                
                    if current_log_entry:
                        self._process_log_entry(current_log_entry, date_pattern, start_time, matching_logs)
                        
            except Exception as e:
                matching_logs.append(f"[Ошибка чтения файла {os.path.basename(file_path)}: {e}]")

        return matching_logs

    def _process_log_entry(self, entry: str, pattern: re.Pattern, start_time: datetime, result_list: list):
        """Вспомогательный метод для парсинга даты и фильтрации записи лога."""
        match = pattern.match(entry)
        if match:
            date_str = match.group(1)
            try:
                log_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if log_time >= start_time:
                    result_list.append(entry.rstrip())
            except ValueError:
                pass

