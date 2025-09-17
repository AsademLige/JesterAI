from src.config_reader import Prefs

prefs = Prefs()

POSTGRES_URI = f'postgresql://{prefs.pg_user}:{prefs.pg_password}@{prefs.ip}:{prefs.port}/{prefs.database}'