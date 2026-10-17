# 学习图 Skill 结构检查：任何 AI 改完 skill/ 后运行，全部 OK 才能提交。
# 用法：powershell -NoProfile -File scripts\检查.ps1
# 注意：本文件必须保存为 UTF-8 带 BOM，否则 Windows PowerShell 5.1 读错中文。

$root = Split-Path -Parent $PSScriptRoot
$skill = Join-Path $root 'skill'
$fail = 0
function Check($ok, $msg) { if ($ok) { Write-Output "OK    $msg" } else { Write-Output "FAIL  $msg"; $script:fail++ } }

# 1. 行数上限
$skillMd = Join-Path $skill 'SKILL.md'
$n = (Get-Content -LiteralPath $skillMd -Encoding UTF8).Count
Check ($n -le 120) "SKILL.md $n 行（上限 120）"
$modules = Get-ChildItem -LiteralPath (Join-Path $skill 'modules') -Filter *.md
foreach ($m in $modules) {
  $c = (Get-Content -LiteralPath $m.FullName -Encoding UTF8).Count
  Check ($c -le 100) "modules/$($m.Name) $c 行（上限 100）"
}

# 2. SKILL.md 引用的模块文件都存在；每个模块文件都被 SKILL.md 引用
$text = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
$refs = [regex]::Matches($text, 'modules/([^`\s]+\.md)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
foreach ($r in $refs) { Check (Test-Path -LiteralPath (Join-Path $skill "modules\$r")) "SKILL.md 引用的 modules/$r 存在" }
foreach ($m in $modules) { Check ($refs -contains $m.Name) "modules/$($m.Name) 已写进 SKILL.md" }

# 3. 模块文件格式（以「# 模块：」开头的文件）
$fields = '解决的问题', '触发词', '输入', '输出', '借鉴来源'
foreach ($m in $modules) {
  $t = Get-Content -LiteralPath $m.FullName -Raw -Encoding UTF8
  if ($t -notmatch '^# 模块：') { continue }
  $missing = @($fields | Where-Object { $t -notmatch "\*\*$_\*\*" })
  foreach ($s in '## 步骤', '## 验收') { if ($t -notmatch [regex]::Escape($s)) { $missing += $s } }
  Check ($missing.Count -eq 0) "modules/$($m.Name) 格式完整$(if ($missing) { '，缺：' + ($missing -join '、') })"
}

# 4. 各 AI 的全局入口都指向本项目的正本
$hash = (Get-FileHash -LiteralPath $skillMd).Hash
foreach ($e in "$HOME\.claude\skills\study-diagram", "$HOME\.codex\skills\study-diagram", "$HOME\.gemini\antigravity\skills\study-diagram") {
  $f = Join-Path $e 'SKILL.md'
  Check ((Test-Path -LiteralPath $f) -and ((Get-FileHash -LiteralPath $f).Hash -eq $hash)) "入口 $e 指向正本"
}

# 5. 每个测试样例都有期望要点
foreach ($s in Get-ChildItem -LiteralPath (Join-Path $root 'tests') -Filter *.mmd) {
  Check (Test-Path -LiteralPath ($s.FullName -replace '\.mmd$', '.期望.md')) "tests/$($s.Name) 有期望要点"
}

# 6. 脚本测试：tests/test_*.py 逐个跑，退出码不是 0 就 FAIL（新测试放进去自动生效）
$env:PYTHONIOENCODING = 'utf-8'
foreach ($t in Get-ChildItem -LiteralPath (Join-Path $root 'tests') -Filter 'test_*.py') {
  $out = & python $t.FullName 2>&1
  $ok = $LASTEXITCODE -eq 0
  Check $ok "tests/$($t.Name) $(if ($ok) { '通过' } else { '没通过：' + (($out | Select-Object -Last 3) -join ' / ') })"
}

if ($fail) { Write-Output "`n$fail 项未通过"; exit 1 } else { Write-Output "`n全部通过" }
