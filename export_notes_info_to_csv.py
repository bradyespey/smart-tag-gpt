import subprocess
import csv
import os
import base64
from datetime import datetime

# Define the path where the CSV will be saved
csv_export_path = "/Users/bradyespey/Projects/Files/Evernote/Notes Metadata.csv"

# Dictionary to hold folder counts for comparison
notes_app_folder_counts = {}
csv_folder_counts = {}

def get_notes_data():
    script = '''
    tell application "Notes"
        set notesData to ""
        repeat with f in folders
            set folderName to name of f
            if folderName does not start with "Smart" then
                set noteCount to count of notes of f
                -- Add folder count for Notes app
                set notesData to notesData & "FOLDER_COUNT_START||" & folderName & "||" & noteCount & "FOLDER_COUNT_END;;;"
                repeat with n in notes of f
                    set noteTitle to name of n
                    set creationDate to creation date of n
                    set modificationDate to modification date of n
                    set hasAttachments to false

                    -- Check for attachments
                    if (count of attachments of n) > 0 then
                        set hasAttachments to true
                    end if

                    set noteInfo to noteTitle & "||" & folderName & "||" & creationDate & "||" & modificationDate & "||" & hasAttachments
                    set notesData to notesData & noteInfo & ";;;"
                end repeat
            end if
        end repeat
        set encodedData to do shell script "echo " & quoted form of notesData & " | base64"
        return encodedData
    end tell
    '''
    result = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
    decoded_data = base64.b64decode(result).decode("utf-8")
    notes_data = [item.split("||") for item in decoded_data.split(";;;") if item]
    
    # Track folder counts from Apple Notes (extracted from the special "FOLDER_COUNT_START" marker)
    for note in notes_data[:]:
        if "FOLDER_COUNT_START" in note[0]:
            folder_name = note[1]
            note_count = int(note[2].replace("FOLDER_COUNT_END", ""))  # Clean the string
            notes_app_folder_counts[folder_name] = note_count
            notes_data.remove(note)  # Remove this entry from normal note data
    return notes_data

def clean_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, '%A, %B %d, %Y at %I:%M:%S %p')
        return parsed_date.strftime('%m/%d/%y %I:%M:%S %p')
    except ValueError:
        return date_str.strip()

def export_to_csv(data):
    with open(csv_export_path, "w", newline="", encoding='utf-8') as csvfile:
        fieldnames = ["Note Title", "Folder", "Date Created", "Date Modified", "Attachments"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for note in data:
            if len(note) != 5:
                continue  # Skip any malformed data
            title, folder, creation_date, modification_date, has_attachments = note
            creation_date = clean_date(creation_date)
            modification_date = clean_date(modification_date)
            writer.writerow({
                "Note Title": title,
                "Folder": folder,
                "Date Created": creation_date,
                "Date Modified": modification_date,
                "Attachments": "Yes" if has_attachments == "true" else "No"
            })
            
            # Count notes in CSV for comparison
            csv_folder_counts[folder] = csv_folder_counts.get(folder, 0) + 1

    print(f"Notes exported to {csv_export_path}")

def compare_folder_counts():
    print("\n--- Folder Comparison ---")
    print("Notes in App vs. Notes Exported to CSV\n")
    print(f"{'Folder Name':<30}{'Notes in App':<15}{'Notes in CSV':<15}{'Difference'}")
    print("-" * 65)
    for folder, app_count in notes_app_folder_counts.items():
        csv_count = csv_folder_counts.get(folder, 0)
        difference = app_count - csv_count
        print(f"{folder:<30}{app_count:<15}{csv_count:<15}{difference}")

def main():
    notes_data = get_notes_data()
    export_to_csv(notes_data)
    compare_folder_counts()
    open_csv_in_excel()

def open_csv_in_excel():
    subprocess.call(['open', '-a', 'Microsoft Excel', csv_export_path])

if __name__ == "__main__":
    main()
