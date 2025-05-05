# convert_csv_to_jsonl.py

import csv
import json
import os

# Define the input and output file paths
input_csv_file = '/Users/bradyespey/Projects/Files/Reminders/exported_tagged_reminders.csv'
output_jsonl_file = '/Users/bradyespey/Projects/Files/Reminders/fine_tune_dataset.jsonl'

try:
    # Open the CSV file for reading
    with open(input_csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Open the JSONL file for writing (overwrite if it exists)
        with open(output_jsonl_file, 'w', encoding='utf-8') as jsonlfile:
            for row in reader:
                # Extract the Title and Tags fields
                title = row.get('Title', '').strip()
                tags = row.get('Tags', '').strip()
                
                # Skip if Title or Tags are missing
                if not title or not tags:
                    continue
                
                # Add colon at the end of the title if not already present
                if not title.endswith(':'):
                    title += ':'
                
                # Ensure the tag starts with '#'
                if not tags.startswith('#'):
                    tags = '#' + tags
                
                # Create the message structure
                messages = [
                    {"role": "user", "content": title},
                    {"role": "assistant", "content": tags}
                ]
                
                # Write as a JSON line
                json_line = json.dumps({"messages": messages}, ensure_ascii=False)
                jsonlfile.write(json_line + '\n')

    print(f"Exported reminders have been written to {output_jsonl_file}")

except FileNotFoundError:
    print(f"File not found: {input_csv_file}")
except Exception as e:
    print(f"An error occurred: {e}")
