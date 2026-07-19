from logging.handlers import RotatingFileHandler
from logging import Logger, StreamHandler
from datetime import datetime, timedelta
from core.consts.consts import Consts
from typing import Dict
import logging
import glob
import sys
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
    __logger_show_time_states: Dict[str, bool] = {}

    def send_log(self, module: str, level=logging.DEBUG, message: str = "", show_time: bool = True):
        """
        Отправляет лог. Флаг show_time определяет, будет ли выведено время.
        Если состояние флага изменилось, логгер автоматически переинициализируется.
        """
        # Если логгер еще не создан ИЛИ изменилось требование к показу времени
        if module not in self.__loggers or self.__logger_show_time_states.get(module) != show_time:
            self.logs_init(module, show_time=show_time)

        logger = self.__loggers[module]
        logger.log(level, message, exc_info=bool(sys.exc_info()[0]))

    def logs_init(self, module: str, 
                  maxBytes: int = 1024 * 1024,
                  backupCount: int = 5,
                  level=logging.DEBUG,
                  log_format='%(asctime)s - %(levelname)s - %(message)s',
                  show_time: bool = True):
        
        self.__check_logs_folder(f'{self.__logs_folder}/{module}/')
        
        if not show_time:
            if log_format == '%(asctime)s - %(levelname)s - %(message)s':
                log_format = '%(levelname)s - %(message)s'
            else:
                log_format = log_format.replace('%(asctime)s', '').lstrip(' -:').strip()

        self.__logger_show_time_states[module] = show_time

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
        Поскольку флаг теперь динамический, метод проверяет последнее состояние модуля.
        """
        folder_path = f'{self.__logs_folder}/{module}'
        if not os.path.isdir(folder_path):
            return [f"Логи для модуля '{module}' не найдены."]

        show_time = self.__logger_show_time_states.get(module, True)

        if not show_time:
            return self._get_all_logs_without_time(folder_path, module)

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

    def _get_all_logs_without_time(self, folder_path: str, module: str) -> list[str]:
        """Вспомогательный метод для чтения логов, если в них нет меток времени."""
        all_logs = []
        log_files = glob.glob(os.path.join(folder_path, f"{module}.log*"))
        log_files.sort(key=os.path.getmtime)

        log_start_pattern = re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)')

        for file_path in log_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    current_log_entry = ""
                    for line in f:
                        if log_start_pattern.match(line):
                            if current_log_entry:
                                all_logs.append(current_log_entry.rstrip())
                            current_log_entry = line
                        else:
                            if current_log_entry:
                                current_log_entry += line
                            else:
                                current_log_entry = line
                    if current_log_entry:
                        all_logs.append(current_log_entry.rstrip())
            except Exception as e:
                all_logs.append(f"[Ошибка чтения файла {os.path.basename(file_path)}: {e}]")
        return all_logs
