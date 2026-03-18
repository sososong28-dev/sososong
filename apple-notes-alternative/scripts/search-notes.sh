#!/bin/bash
# 搜索备忘录
# 用法：./search-notes.sh "搜索关键词"

QUERY="$1"

osascript <<EOF
tell application "Notes"
    activate
    set output to ""
    repeat with aNote in notes
        if body of aNote contains "$QUERY" then
            set output to output & name of aNote & linefeed
        end if
    end repeat
    return output
end tell
EOF
