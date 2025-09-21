from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    pg_password: SecretStr
    bot_token: SecretStr
    database: SecretStr
    pg_user: SecretStr
    port: SecretStr
    ip: SecretStr

class Prefs():
    def __init__(self):
        pass

    __config = Settings()

    @property 
    def bot_token(self) -> str:
        return self.__config.bot_token.get_secret_value()
    
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