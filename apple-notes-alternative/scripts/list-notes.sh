#!/bin/bash
# 列出所有备忘录

osascript <<EOF
tell application "Notes"
    activate
    set output to ""
    repeat with aFolder in folders
        repeat with aNote in notes of aFolder
            set output to output & name of aFolder & " / " & name of aNote & linefeed
        end repeat
    end repeat
    return output
end tell
EOF
