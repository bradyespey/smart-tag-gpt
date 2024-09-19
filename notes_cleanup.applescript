-- Define the path for the CSV file
set outputPath to "/Users/bradyespey/Projects/Evernote/Problematic Notes.csv"

-- Start the CSV content
set csvOutput to "Folder,Note Name,Issue\n"

tell application "Notes"
    set allFolders to every folder
    repeat with aFolder in allFolders
        set folderName to name of aFolder
        set notesList to every note of aFolder
        set noteNames to {}

        repeat with aNote in notesList
            set noteName to name of aNote
            set issueList to {}

            -- Check for duplicate note names within the same folder
            if noteName is in noteNames then
                set end of issueList to "Duplicate Note Name"
            else
                set end of noteNames to noteName
            end if

            -- Check for colons, periods, quotes, and apostrophes in the note title
            if noteName contains ":" then
                set end of issueList to "Contains Colon"
            end if

            if noteName contains "." then
                set end of issueList to "Contains Period"
            end if

            if noteName contains "\"" then
                set end of issueList to "Contains Quote"
            end if

            if noteName contains "'" then
                set end of issueList to "Contains Apostrophe"
            end if

            -- If any issues were found, add the note to the CSV output
            if (count of issueList) > 0 then
                set csvOutput to csvOutput & folderName & "," & noteName & "," & (issueList as string) & "\n"
            end if
        end repeat
    end repeat
end tell

-- Write CSV to file
do shell script "echo " & quoted form of csvOutput & " > " & quoted form of outputPath

-- Open CSV in Excel
tell application "Microsoft Excel"
    open outputPath
end tell

return "CSV written to: " & outputPath
