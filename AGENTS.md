# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Stack
- Python 3.9
- aiogram 3 (version <4.0)
- PostgreSQL database via psycopg2-binary and gino
- pydantic-settings for configuration management
- APScheduler for task scheduling

## Key Commands
- `python bot.py` - Start the Telegram bot
- `pip install -r requirements.txt` - Install dependencies

## Architecture Patterns
- Middleware pattern used for registration and captcha validation
- Handler-based routing system (src/handlers/)
- Service layer pattern (src/services/)
- Model-view-controller structure in domain components

## Project-Specific Conventions
- Configuration loaded from .env file using pydantic-settings
- Database connection managed through src/models/db_model.py and src/services/data_base/db.py
- All handlers are imported as modules in bot.py
- Scheduler jobs defined in src/services/scheduler/
- Media files stored in folder specified by media_folder config
- Super users defined in super_users config (comma-separated IDs)

## Code Style Guidelines
- Use snake_case for all Python identifiers
- All handler functions must be imported as modules in bot.py
- Database models should inherit from the base model in src/models/db_model.py
- Middleware classes must implement the required middleware interface

## Testing & Development
- No specific test configuration found in project structure
- Development requires .env file with bot_token, database credentials, etc.