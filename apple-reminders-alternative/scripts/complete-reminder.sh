#!/bin/bash
# 完成提醒事项
# 用法：./complete-reminder.sh "提醒名称"

NAME="$1"

osascript <<EOF
tell application "Reminders"
    activate
    repeat with aReminder in reminders
        if name of aReminder contains "$NAME" then
            set completed of aReminder to true
            return "已完成：$NAME"
        end if
    end repeat
    return "未找到：$NAME"
end tell
EOF
