# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Documentation Rules (Non-Obvious Only)
- Development requires .env file with bot_token, database credentials, etc.
- Configuration loaded from .env file using pydantic-settings
- Media files stored in folder specified by media_folder config from .env
- Super users defined in super_users config (comma-separated IDs) from .env