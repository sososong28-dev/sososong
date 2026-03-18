#!/bin/bash
# 创建新备忘录
# 用法：./create-note.sh "备忘录名称" "备忘录内容"

NAME="$1"
CONTENT="$2"

osascript <<EOF
tell application "Notes"
    activate
    set newNote to make new note at folder "Notes" with properties {name:"$NAME", body:"$CONTENT"}
    return "创建成功：$NAME"
end tell
EOF
