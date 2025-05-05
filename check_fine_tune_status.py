# check_fine_tune_status.py

import openai
import json
import os

try:
    with open('/Users/bradyespey/Projects/Files/Reminders/openai_api_key.json') as f:
        data = json.load(f)
        openai.api_key = data['api_key']

    with open('/Users/bradyespey/Projects/Files/Reminders/openai_job_id.json') as f:
        job_data = json.load(f)
        job_id = job_data['job_id']
except FileNotFoundError as e:
    print(f"File not found: {e}")
    exit(1)
except KeyError as e:
    print(f"Missing key in JSON file: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)

# Retrieve the fine-tune job status
try:
    response = openai.fine_tuning.jobs.retrieve(job_id)

    # Output relevant information
    print(f"Status: {response.status}")
    if response.status == 'failed':
        print(f"Error: {response.error.message}")
    else:
        print(f"Model: {response.model}")
        if response.fine_tuned_model:
            print(f"Fine-tuned model: {response.fine_tuned_model}")
        else:
            print("Fine-tuning is still in progress...")
except Exception as e:
    print(f"Error retrieving status: {str(e)}")
