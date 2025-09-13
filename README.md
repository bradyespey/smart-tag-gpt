# SmartTagGPT

**Scope**: This README replaces prior selected overview docs

<p align="center">
  <img src="images/overview_image.webp" alt="SmartTagGPT Overview" width="300"/>
</p>

## Overview

An automated system that intelligently tags Apple Reminders using OpenAI's GPT models with optional fine-tuning for personalized accuracy. The project exports existing tagged reminders, converts them to training data, fine-tunes a custom GPT model, and automatically applies tags to new untagged reminders via Apple Shortcuts automation running hourly.

## Live and Admin

- **Apple Shortcuts**: Automated workflows in iOS Shortcuts app
- **OpenAI Dashboard**: https://platform.openai.com/fine-tuning for model management
- **Cron Logs**: `/Users/brady/Projects/SmartTagGPT/logs/reminders_cron.log`
- **API Usage**: Monitor at https://platform.openai.com/usage

## Tech Stack

- **Automation**: Apple Shortcuts for iOS integration
- **AI Model**: OpenAI GPT-3.5-turbo with fine-tuning capability
- **Data Processing**: Python scripts for CSV/JSONL conversion
- **Scheduling**: macOS crontab for hourly automation
- **Storage**: Local JSON files for secure API key management

## Quick Start

```bash
git clone https://github.com/bradyespey/SmartTagGPT
cd SmartTagGPT
# Set up API key in /Users/bradyespey/Projects/Files/Reminders/openai_api_key.json
python convert_csv_to_jsonl.py
python fine_tuning.py
```

## Environment

Required files for API access:

```bash
# API Key
/Users/bradyespey/Projects/Files/Reminders/openai_api_key.json
# Model ID (after fine-tuning)
/Users/bradyespey/Projects/Files/Reminders/openai_model_id.json
# Job ID (for status checking)
/Users/bradyespey/Projects/Files/Reminders/openai_job_id.json
```

Example `.env.example`:
```json
{
  "api_key": "YOUR_OPENAI_API_KEY",
  "model_id": "ft:gpt-3.5-turbo-0125:YOUR_ORG::YOUR_MODEL_ID",
  "job_id": "ftjob-YOUR_JOB_ID"
}
```

## Run Modes

- **Development**: Test individual Python scripts manually for debugging
- **Production**: Automated hourly execution via crontab scheduling
- **Fine-tuning**: Optional model training mode using personal reminder data

## Scripts and Ops

- **Data Export**: Apple Shortcuts → "Export Tagged Reminders" → CSV output
- **Data Conversion**: `python convert_csv_to_jsonl.py` — CSV to JSONL format
- **Model Training**: `python fine_tuning.py` — Upload dataset and start fine-tuning
- **Status Check**: `python check_fine_tune_status.py` — Monitor training progress
- **Auto-Tagging**: Apple Shortcuts → "Add Tags to Reminders" (hourly via cron)

### Cron Automation
```bash
# Edit crontab
crontab -e

# Add hourly automation
0 * * * * /usr/bin/shortcuts run "Add Tags to Reminders" >> /Users/brady/Projects/SmartTagGPT/logs/reminders_cron.log 2>&1
59 23 * * 1 echo "" > /Users/brady/Projects/SmartTagGPT/logs/reminders_cron.log
```

## Deploy

- **Local Execution**: Python scripts run locally with API calls to OpenAI
- **Apple Shortcuts**: Deployed directly to iOS Shortcuts app
- **Automation**: Crontab scheduling for hands-free operation
- **No hosting required** — fully local automation system

## App Pages / Routes

### Apple Shortcuts Workflows
- **Export Tagged Reminders** — Finds tagged reminders, exports to CSV format
- **Add Tags to Reminders** — Processes untagged reminders via GPT API, applies suggested tags

### Python Scripts
- **convert_csv_to_jsonl.py** — Data preprocessing for fine-tuning
- **fine_tuning.py** — Model training orchestration
- **check_fine_tune_status.py** — Training progress monitoring
- **fine_tuning_request_test.py** — API testing and validation

## Directory Map

```
SmartTagGPT/
├── images/                     # Workflow screenshots and documentation
│   ├── overview_image.webp     # Project overview visual
│   ├── find_tagged_reminders.png
│   ├── export_tagged_reminders.png
│   └── tag_untagged_reminders.png
├── logs/
│   └── reminders_cron.log      # Automation execution logs
├── other/                      # Temporary files and exports
├── convert_csv_to_jsonl.py     # Data format conversion
├── fine_tuning.py              # Model training script
├── check_fine_tune_status.py   # Training progress monitoring
├── fine_tuning_request_test.py # API testing utilities
└── LICENSE                     # Project license
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Verify JSON files exist in `/Users/bradyespey/Projects/Files/Reminders/`
   - Check file permissions and JSON syntax
   - Ensure API key is valid and has sufficient credits

2. **Shortcuts Not Running**
   - Check iOS Shortcuts app permissions for Reminders access
   - Verify crontab syntax and shortcuts command path
   - Test shortcuts manually before automation

3. **Fine-Tuning Failures**
   - Ensure JSONL format is correct with proper message structure
   - Check dataset size meets OpenAI minimum requirements
   - Monitor API usage limits and billing status

4. **Cron Jobs Not Executing**
   - Verify crontab is properly configured with `crontab -l`
   - Check system permissions for shortcuts command
   - Review log files for error messages

## AI Handoff

This is a Python + Apple Shortcuts automation system for AI-powered reminder tagging. Focus on the data pipeline (CSV → JSONL → fine-tuning) and the Shortcuts integration for iOS Reminders. The system uses OpenAI's fine-tuning API with secure local JSON file storage for credentials.
