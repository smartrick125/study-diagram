# 让本机所有 AI 装的 study-diagram 都是指向正本 skill/ 的链接：改正本 = 所有 AI 立刻生效。
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File scripts\同步入口.ps1 [-Schedule]
#   不带参数：修一遍。副本、指向别处的链接 → 先移到备份目录，再换成链接；重复运行结果不变。
#   -Schedule：注册 Windows 定时任务「study-diagram 入口同步」，开机登录和每天 9:00 各跑一次。
# 注意：本文件必须保存为 UTF-8 带 BOM，否则 Windows PowerShell 5.1 读错中文。
param([string]$UserHome = $HOME, [string]$BackupRoot, [int]$KeepDays = 7, [switch]$Schedule)
$ErrorActionPreference = 'Stop'
$skill = (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot) 'skill')).Path
if (-not $BackupRoot) { $BackupRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $PSScriptRoot) '..\G_project_009_学习图Skill_维护\入口备份')) }

if ($Schedule) {
  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`""
  $triggers = @((New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME), (New-ScheduledTaskTrigger -Daily -At 9am))
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskName 'study-diagram 入口同步' -Action $action -Trigger $triggers -Settings $settings -Force | Out-Null
  Write-Output '已注册定时任务「study-diagram 入口同步」：登录时和每天 9:00 运行'
  exit 0
}

# 各 AI 读个人 skill 的目录（唯一清单，新 AI 加在这里）。
# 必装：AI 装了（它的主目录存在）就保证有入口。可选：只把已经装了的副本换成链接。
$required = '.claude\skills', '.codex\skills', '.gemini\antigravity\skills'
$optional = '.agents\skills', '.gemini\skills', '.cursor\skills', '.grok\skills', '.copilot\skills', '.config\opencode\skills'

function Get-LinkTarget($dir) {
  $i = Get-Item -LiteralPath $dir -Force
  if (-not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return $null }
  return [string]($i.Target | Select-Object -First 1)
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
  $aiHome = Join-Path $UserHome ($rel -split '\\')[0]
  if (-not (Test-Path -LiteralPath $root)) {
    if ($required -notcontains $rel -or -not (Test-Path -LiteralPath $aiHome)) { continue }
    New-Item -ItemType Directory -Path $root | Out-Null
  }
  $installs = @(Get-ChildItem -LiteralPath $root -Directory -Force | Where-Object { Test-IsStudyDiagram $_.FullName })
  if ($installs.Count -eq 0 -and $required -contains $rel) {
    $installs = @([pscustomobject]@{ FullName = Join-Path $root 'study-diagram'; Missing = $true })
  }
  foreach ($d in $installs) {
    $p = $d.FullName
    if (-not $d.Missing) {
      $target = Get-LinkTarget $p
      if ($target -and ((Resolve-Path -LiteralPath $target -ErrorAction SilentlyContinue).Path -eq $skill)) { Write-Output "OK    $p"; continue }
      if ($target) {
        [IO.Directory]::Delete($p, $false)   # 只删链接本身，不碰它指向的文件夹
        $what = "链接原指向 $target"
      } else {
        $dest = Join-Path $BackupRoot "$stamp\$(($rel -replace '\\', '_'))_$(Split-Path $p -Leaf)"
        New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
        Move-Item -LiteralPath $p -Destination $dest
        $what = "副本已移到 $dest"
      }
    } else { $what = '原来没有入口' }
    New-Item -ItemType Junction -Path $p -Target $skill | Out-Null
    $changes += "FIXED $p → 正本（$what）"
  }
}
$changes | ForEach-Object { Write-Output $_ }

# 备份只留 $KeepDays 天；含链接的备份不自动删，防止删到链接指向的东西
if (Test-Path -LiteralPath $BackupRoot) {
  foreach ($b in Get-ChildItem -LiteralPath $BackupRoot -Directory | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays) }) {
    $links = @(Get-ChildItem -LiteralPath $b.FullName -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue)
    if ($links.Count -eq 0) { Remove-Item -LiteralPath $b.FullName -Recurse -Force; Write-Output "清理过期备份 $($b.Name)" }
  }
}
