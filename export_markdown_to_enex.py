import os
import subprocess
from pathlib import Path
import csv

# Paths
base_directory = Path("/Users/bradyespey/Projects/Files/Evernote/iCloud")
output_directory = Path("/Users/bradyespey/Projects/Files/Evernote/Converted")
problematic_files_csv = Path("/Users/bradyespey/Projects/Files/Evernote/enex_file_issues.csv")  # Single CSV for all issues

# Create output directories if they don't exist
output_directory.mkdir(parents=True, exist_ok=True)

# Initialize counters and lists
total_md_files = 0
total_notes_in_enex = 0
converted_folders = 0
folders_with_md_files = 0

folder_details = []
converted_files = []

# Prepare the problematic files CSV (overwrite if exists)
with problematic_files_csv.open('w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Add additional columns as needed for more granular data
    csv_writer.writerow(["Folder", "Markdown File", "Error", "Error Details", "File Size (KB)", "Note Count in ENEX"])

    # Iterate over each direct subfolder in the iCloud directory
    for folder in base_directory.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            folder_md_count = 0
            folder_enex_count = 0

            # Clear the terminal for each folder
            os.system('clear')
            print(f"Processing folder: {folder_name}")

            # Prepare the ENEX output path
            enex_file = output_directory / f"{folder_name}.enex"

            # Count markdown files in the current folder
            markdown_notes = list(folder.glob('*.md'))
            md_file_count = len(markdown_notes)
            total_md_files += md_file_count
            folder_md_count = md_file_count

            if md_file_count > 0:
                folders_with_md_files += 1
                folder_details.append(f"{folder_name} - {md_file_count} notes")

                # Command for conversion
                command = [
                    "/usr/bin/python3",
                    "/Users/bradyespey/Projects/Evernote/md2enex.py",
                    str(folder),
                    "-o",
                    str(enex_file)
                ]

                # Run the conversion command
                result = subprocess.run(command, capture_output=True, text=True)

                # Capture standard output and errors
                output = result.stdout
                errors = result.stderr

                # Count how many notes were successfully converted
                notes_converted = output.count("Successfully wrote")
                total_notes_in_enex += notes_converted
                folder_enex_count = notes_converted

                if notes_converted > 0:
                    converted_folders += 1
                    converted_files.append(f"{enex_file.name} - {notes_converted} notes")
                    print(f"Successfully converted {notes_converted} notes to {enex_file.name}")
                else:
                    # Log any errors to the single CSV for all folders
                    for markdown_file in markdown_notes:
                        if str(markdown_file) in errors:
                            # Gather additional details like file size (in KB)
                            file_size_kb = os.path.getsize(markdown_file) / 1024
                            csv_writer.writerow([
                                folder_name, 
                                markdown_file.name, 
                                "Conversion failed.", 
                                errors.strip(), 
                                f"{file_size_kb:.2f}",  # File size in KB
                                notes_converted
                            ])
                    print(f"Errors found in {folder_name}. Check the CSV for details.")
            else:
                print(f"No markdown notes found in {folder_name}")

# Output final stats
print(f"\n--- Conversion Summary ---")
print(f"Folders with markdown files: {folders_with_md_files}")
print(f"Folders converted to enex files: {converted_folders}\n")

print("Folders in iCloud:")
for detail in folder_details:
    print(detail)

print("\nList of files converted to enex:")
for converted in converted_files:
    print(converted)

print(f"\nTotal markdown notes: {total_md_files}")
print(f"Total enex notes: {total_notes_in_enex}")

print(f"\nProblematic files (if any) have been logged to: {problematic_files_csv}")
