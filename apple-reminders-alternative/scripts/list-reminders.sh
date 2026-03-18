#!/bin/bash
# 列出提醒事项

osascript -e '
tell application "Reminders"
    set output to "📋 提醒事项列表：" & linefeed & linefeed
    repeat with aList in lists
        set listName to name of aList
        set reminderCount to count of reminders of aList
        if reminderCount > 0 then
            set output to output & "【" & listName & "】(" & reminderCount & "个)" & linefeed
            repeat with aReminder in reminders of aList
                set rName to name of aReminder
                set rCompleted to completed of aReminder
                if rCompleted then
                    set output to output & "  ✅ " & rName & linefeed
                else
                    set output to output & "  ⏳ " & rName & linefeed
                end if
            end repeat
            set output to output & linefeed
        end if
    end repeat
    return output
end tell
'
