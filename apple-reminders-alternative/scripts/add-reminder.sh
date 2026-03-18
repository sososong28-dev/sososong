#!/bin/bash
# 添加提醒事项
# 用法：./add-reminder.sh "提醒内容" [列表名] [日期]

NAME="$1"
LIST="$2"
DUE="$3"

if [ -z "$NAME" ]; then
    echo "用法：./add-reminder.sh \"提醒内容\" [列表名] [日期]"
    exit 1
fi

if [ -z "$LIST" ]; then
    # 默认添加到「提醒事项」列表
    RESULT=$(osascript -e "tell application \"Reminders\" to make new reminder with properties {name:\"$NAME\"}")
else
    if [ -z "$DUE" ]; then
        RESULT=$(osascript -e "tell application \"Reminders\" to make new reminder at end of reminders of list \"$LIST\" with properties {name:\"$NAME\"}")
    else
        RESULT=$(osascript -e "tell application \"Reminders\" to set newReminder to make new reminder at end of reminders of list \"$LIST\" with properties {name:\"$NAME\", due date:date \"$DUE\"}")
    fi
fi

echo "✅ 已添加：$NAME"
echo "ID: $RESULT"
