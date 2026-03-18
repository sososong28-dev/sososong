#!/bin/bash
# 抓取并摘要网页内容
# 用法：./summarize-url.sh "URL" [short|medium|long]

URL="$1"
LENGTH="${2:-medium}"

echo "正在抓取：$URL"
CONTENT=$(node ../playwright-scraper/scripts/playwright-simple.js "$URL" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "抓取失败，尝试使用 stealth 模式..."
    CONTENT=$(node ../playwright-scraper/scripts/playwright-stealth.js "$URL" 2>/dev/null)
fi

echo ""
echo "=== 抓取完成 ==="
echo ""
echo "请将以下内容发送给 AI 进行摘要："
echo ""
echo "--- 开始 ---"
echo "$CONTENT"
echo "--- 结束 ---"
echo ""
echo "摘要要求：$LENGTH 篇幅，3-5 个要点"
