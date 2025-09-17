from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    bot_token: SecretStr

class Prefs():
    def __init__(self):
        pass

    __config = Settings()

    @property 
    def bot_token(self) -> str:
        return self.__config.bot_token.get_secret_value()