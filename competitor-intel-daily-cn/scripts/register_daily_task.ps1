param(
    [string]$TaskName = "Competitor Intel Daily CN",
    [string]$OpenClawCommand = 'openclaw run --skill competitor-intel-daily-cn --input "生成今日避孕套行业竞品情报日报，并输出 PDF 与消息摘要。"',
    [string]$StartTime = "08:30",
    [switch]$RunNow
)

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command $OpenClawCommand"
$Trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null
Write-Host "Registered scheduled task: $TaskName at $StartTime"

if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Started task immediately: $TaskName"
}
