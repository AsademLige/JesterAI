from logging.handlers import RotatingFileHandler
from core.consts.consts import Consts
from logging import Logger
from typing import Dict
import logging
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

    __logs_folder:str = Consts.LOGS_DIR

    __loggers:Dict[str, Logger] = {}

    def send_log(self, module:str, level = logging.DEBUG, message:str = ""):
        if (module not in self.__loggers):
            self.logs_init(module)

        logger = self.__loggers[module]

        if (level == logging.DEBUG):
            logger.debug(message)
        elif (level == logging.INFO):
            logger.info(message)
        elif (level == logging.WARNING):
            logger.warning(message)
        elif (level == logging.ERROR):
            logger.error(message)

    def logs_init(self, module:str, 
                  maxBytes:int = 1024 * 1024,
                  backupCount:int = 5,
                  level = logging.DEBUG,
                  format = '%(asctime)s - %(levelname)s - %(message)s'):
        self.__check_logs_folder(f'{self.__logs_folder}/{module}/')

        file_handler = RotatingFileHandler(
            f'{self.__logs_folder}/{module}/{module}.log',
            maxBytes=maxBytes,
            backupCount=backupCount
        )
        
        logging.basicConfig(level=level, format=format)
        logger = logging.getLogger(module)
        logger.addHandler(file_handler)

        self.__loggers[module] = logger
    
    def __check_logs_folder(self, path:str):
        if not os.path.isdir(path):
             os.makedirs(path, exist_ok=True)
        
        