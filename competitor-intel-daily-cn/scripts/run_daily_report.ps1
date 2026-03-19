param(
    [string]$Prompt = "生成今日避孕套行业竞品情报日报，并输出 PDF 与消息摘要。"
)

$ErrorActionPreference = 'Stop'
Write-Host "Running competitor-intel-daily-cn with prompt: $Prompt"
openclaw run --skill competitor-intel-daily-cn --input $Prompt
