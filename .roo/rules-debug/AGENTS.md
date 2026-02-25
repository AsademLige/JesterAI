# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Debug Rules (Non-Obvious Only)
- Database connection managed through src/models/db_model.py and src/services/data_base/db.py
- Scheduler jobs defined in src/services/scheduler/
- Development requires .env file with bot_token, database credentials, etc.