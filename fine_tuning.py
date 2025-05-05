# fine_tuning.py

import openai
import requests
import os
import json
import time

# Load API key from a JSON file
try:
    with open('/Users/bradyespey/Projects/Files/Reminders/openai_api_key.json') as f:
        data = json.load(f)
        openai.api_key = data['api_key']
except FileNotFoundError:
    print("API key file not found. Make sure the file exists at the specified path.")
    exit(1)
except KeyError:
    print("API key not found in the file. Check the file structure.")
    exit(1)
except Exception as e:
    print(f"An error occurred while loading the API key: {e}")
    exit(1)

# Upload the file using requests
def upload_file(file_path):
    try:
        headers = {
            "Authorization": f"Bearer {openai.api_key}"
        }

        files = {
            'file': open(file_path, 'rb')
        }

        data = {
            'purpose': 'fine-tune'
        }

        response = requests.post('https://api.openai.com/v1/files', headers=headers, files=files, data=data)
        response.raise_for_status()  # Raise an error if the request failed

        return response.json()

    except FileNotFoundError:
        print(f"File not found: {file_path}. Please make sure the file exists.")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the file upload: {e}")
        exit(1)

# Fine-tune the model
def fine_tune_model(file_id):
    try:
        url = "https://api.openai.com/v1/fine_tuning/jobs"
        data = {
            "training_file": file_id,
            "model": "gpt-3.5-turbo"
        }

        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an error if the request failed

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fine-tuning the model: {e}")
        exit(1)

# Check fine-tuning status
def check_fine_tune_status(job_id):
    try:
        response = openai.fine_tuning.jobs.retrieve(job_id)
        return response
    except Exception as e:
        print(f"An error occurred while checking fine-tuning status: {e}")
        exit(1)

# Main script execution
file_path = "/Users/bradyespey/Projects/Files/Reminders/fine_tune_dataset.jsonl"
upload_response = upload_file(file_path)
print("File uploaded:", upload_response)

# Get the file ID from the upload response
file_id = upload_response.get('id')

# Start fine-tuning
if file_id:
    fine_tune_response = fine_tune_model(file_id)
    print("Fine-tuning started:", fine_tune_response)

    # Get the job ID from fine-tuning response
    job_id = fine_tune_response.get('id')

    # Wait before checking the status (adjust as needed)
    time.sleep(60)

    # Check status
    if job_id:
        status_response = check_fine_tune_status(job_id)
        print("Fine-tuning status:", status_response)
else:
    print("File upload failed. Fine-tuning was not started.")
