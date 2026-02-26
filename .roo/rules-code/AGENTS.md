# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Coding Rules (Non-Obvious Only)
- All handler functions must be imported as modules in bot.py
- Database models should inherit from the base model in src/models/db_model.py
- Middleware classes must implement the required middleware interface
- Configuration loaded from .env file using pydantic-settings
- Media files stored in folder specified by media_folder config from .env
- Super users defined in super_users config (comma-separated IDs) from .env

## Architecture Patterns
- Middleware pattern used for registration and captcha validation
- Handler-based routing system (src/handlers/)
- Service layer pattern (src/services/)
- Model-view-controller structure in domain components

## Development Guidelines
- Development requires .env file with bot_token, database credentials, etc.
- Scheduler jobs defined in src/services/scheduler/