from src.data.config import Prefs

prefs = Prefs()

POSTGRES_URI = f'postgresql://{prefs.pg_user}:{prefs.pg_password}@{prefs.ip}:{prefs.port}/{prefs.database}'