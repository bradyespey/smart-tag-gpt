# Project Context

Read README.md for full project context before making changes.

## Overview
Automation pipeline that tags Apple Reminders with OpenAI models, with optional fine-tuning and hourly shortcut-based execution.

## Stack
Python scripts, Apple Shortcuts, OpenAI fine-tuning API, macOS cron.

## Key Files
- convert_csv_to_jsonl.py
- fine_tuning.py
- check_fine_tune_status.py
- fine_tuning_request_test.py
- logs/reminders_cron.log

## Dev Commands
- Start: python convert_csv_to_jsonl.py
- Build: N/A (script-based project)
- Deploy: N/A (local automation + shortcuts)

## Rules
- Do not introduce new frameworks
- Follow existing structure and naming
- Keep solutions simple and fast

## Notes
- Secrets/model metadata are read from JSON files in `/Users/bradyespey/Projects/Files/Reminders/`.
- Hourly automation runs via `shortcuts` + `crontab`.
