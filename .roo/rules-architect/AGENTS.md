# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Architecture Rules (Non-Obvious Only)
- Middleware pattern used for registration and captcha validation
- Handler-based routing system (src/handlers/)
- Service layer pattern (src/services/)
- Model-view-controller structure in domain components
- Database connection managed through src/models/db_model.py and src/services/data_base/db.py
- Scheduler jobs defined in src/services/scheduler/