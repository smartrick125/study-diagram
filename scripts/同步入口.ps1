# 让本机所有 AI 装的 study-diagram 都是指向正本 skill/ 的链接：改正本 = 所有 AI 立刻生效。
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File scripts\同步入口.ps1 [-BackupRoot 目录] [-Schedule]
#   不带参数：修一遍。每个 skill 目录里只留一个 study-diagram 链接；副本先移到备份目录，
#   改过名的副本、链接只备份 / 拆掉不重建；重复运行结果不变。备份默认在 %TEMP%\study-diagram-入口备份，留 7 天。
#   -Schedule：注册 Windows 定时任务「study-diagram 入口同步」，开机登录和每天 9:00 各跑一次。
# 注意：本文件必须保存为 UTF-8 带 BOM，否则 Windows PowerShell 5.1 读错中文。
param([string]$UserHome = $HOME, [string]$BackupRoot, [int]$KeepDays = 7, [switch]$Schedule)
$ErrorActionPreference = 'Stop'
$skill = (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot) 'skill')).Path
if (-not $BackupRoot) { $BackupRoot = Join-Path ([IO.Path]::GetTempPath()) 'study-diagram-入口备份' }

if ($Schedule) {
  $arg = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`""
  if ($PSBoundParameters.ContainsKey('BackupRoot')) { $arg += " -BackupRoot `"$BackupRoot`"" }
  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg
  $triggers = @((New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME), (New-ScheduledTaskTrigger -Daily -At 9am))
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskName 'study-diagram 入口同步' -Action $action -Trigger $triggers -Settings $settings -Force | Out-Null
  Write-Output '已注册定时任务「study-diagram 入口同步」：登录时和每天 9:00 运行'
  exit 0
}

# 各 AI 读个人 skill 的目录（唯一清单，新 AI 加在这里；出处见 docs/借鉴记录.md B-017）。
# 必装：AI 装了（skills 的上一级目录存在）就保证有入口。可选：只修已经装了的。
$required = @(
  '.claude\skills'               # Claude Code
  '.codex\skills'                # Codex 旧路径，官方现在是 ~/.agents/skills，仍兼容（openai/codex#10437）
  '.gemini\antigravity\skills'   # Antigravity 旧路径，官方现在是 ~/.gemini/config/skills，仍兼容（antigravity.google/docs/skills）
)
$optional = '.agents\skills', '.gemini\skills', '.cursor\skills', '.grok\skills', '.copilot\skills', '.config\opencode\skills'

function Get-LinkTarget($dir) {
  $i = Get-Item -LiteralPath $dir -Force -ErrorAction SilentlyContinue
  if (-not $i -or -not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return $null }
  return [string]($i.Target | Select-Object -First 1)
}
function Test-PointsToSkill($dir) {
  $t = Get-LinkTarget $dir
  return $t -and ((Resolve-Path -LiteralPath $t -ErrorAction SilentlyContinue).Path -eq $skill)
}
function Test-IsStudyDiagram($dir) {
  if ((Split-Path $dir -Leaf) -eq 'study-diagram') { return $true }
  $f = Join-Path $dir 'SKILL.md'
  return (Test-Path -LiteralPath $f) -and (Select-String -LiteralPath $f -Pattern '^name:\s*study-diagram\s*$' -Quiet)
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$changes = @()
foreach ($rel in $required + $optional) {
  $root = Join-Path $UserHome $rel
  $isRequired = $required -contains $rel
  if (-not (Test-Path -LiteralPath $root)) {
    if (-not $isRequired -or -not (Test-Path -LiteralPath (Split-Path $root))) { continue }
    New-Item -ItemType Directory -Path $root | Out-Null
  }
  $installs = @(Get-ChildItem -LiteralPath $root -Directory -Force | Where-Object { Test-IsStudyDiagram $_.FullName })
  if ($installs.Count -eq 0 -and -not $isRequired) { continue }
  $entry = Join-Path $root 'study-diagram'
  foreach ($d in $installs) {
    $p = $d.FullName
    if ($p -eq $entry -and (Test-PointsToSkill $p)) { continue }
    $target = Get-LinkTarget $p
    if ($target) {
      [IO.Directory]::Delete($p, $false)   # 只删链接本身，不碰它指向的文件夹
      $changes += "拆掉 $p（链接原指向 $target）"
    } else {
      $dest = Join-Path $BackupRoot "$stamp\$(($rel -replace '\\', '_'))_$(Split-Path $p -Leaf)"
      New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
      Move-Item -LiteralPath $p -Destination $dest
      $changes += "备份 $p → $dest"
    }
  }
  if (Test-PointsToSkill $entry) { Write-Output "OK    $entry"; continue }
  New-Item -ItemType Junction -Path $entry -Target $skill | Out-Null
  $changes += "FIXED $entry → 正本"
}
$changes | ForEach-Object { Write-Output $_ }

# 备份只留 $KeepDays 天；含链接的备份不自动删，防止删到链接指向的东西
if (Test-Path -LiteralPath $BackupRoot) {
  foreach ($b in Get-ChildItem -LiteralPath $BackupRoot -Directory | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays) }) {
    $links = @(Get-ChildItem -LiteralPath $b.FullName -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue)
    if ($links.Count -eq 0) { Remove-Item -LiteralPath $b.FullName -Recurse -Force; Write-Output "清理过期备份 $($b.Name)" }
  }
}
