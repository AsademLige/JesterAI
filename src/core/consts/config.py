from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    debug: SecretStr = Field(default=SecretStr("0"))
    media_folder: SecretStr
    super_users: SecretStr
    pg_password: SecretStr
    bot_token: SecretStr
    database: SecretStr
    pg_user: SecretStr
    port: SecretStr
    ip: SecretStr

class Prefs():
    _instance = None
    __config:Settings = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__config = Settings()
        return cls._instance

    @property 
    def bot_token(self) -> str:
        return self.__config.bot_token.get_secret_value()
    
    @property 
    def media_folder(self) -> str:
        return self.__config.media_folder.get_secret_value()
    
    @property 
    def debug(self) -> str:
        return self.__config.debug.get_secret_value()
    
    @property 
    def pg_password(self) -> str:
        return self.__config.pg_password.get_secret_value()
    
    @property 
    def database(self) -> str:
        return self.__config.database.get_secret_value()
    
    @property 
    def pg_user(self) -> str:
        return self.__config.pg_user.get_secret_value()
    
    @property 
    def port(self) -> str:
        return self.__config.port.get_secret_value()
    
    @property 
    def ip(self) -> str:
        return self.__config.ip.get_secret_value()
    
    @property 
    def super_users(self) -> List:
        return self.__config.super_users.get_secret_value().split()

    @property 
    def debug(self) -> bool:
        return self.__config.debug.get_secret_value() == "1"