"""同步入口：本机各 AI 装的 study-diagram 都变成指向正本的链接，改正本所有 AI 立刻生效。

在临时假主目录里跑 scripts/同步入口.ps1，不碰真实的 ~/.claude 等目录。
运行：python tests/test_同步入口.py（退出码 0 = 通过）
"""
import os, pathlib, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = (REPO / "skill").resolve()
SCRIPT = REPO / "scripts" / "同步入口.ps1"


def run(home, backup):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
                        "-UserHome", str(home), "-BackupRoot", str(backup)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def copy_of_skill(path, extra="Codex 改过的副本"):
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: study-diagram\n---\n旧版\n", encoding="utf-8")
    (path / "独有.txt").write_text(extra, encoding="utf-8")


def points_to_skill(path):
    return path.is_junction() and pathlib.Path(os.path.realpath(path)) == SKILL


def main():
    if sys.platform != "win32":
        print("skip 同步入口只在 Windows 上用")
        return
    tmp = pathlib.Path(tempfile.mkdtemp())
    home, backup = tmp / "home", tmp / "backup"
    links = []
    try:
        claude = home / ".claude" / "skills" / "study-diagram"
        copy_of_skill(claude)                                    # 1. 必装入口被换成副本
        cursor = home / ".cursor" / "skills" / "学习图"
        copy_of_skill(cursor)                                    # 2. 别的 AI 装了改名的副本
        other = home / ".cursor" / "skills" / "别的skill"
        other.mkdir()
        (other / "SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")
        (home / ".codex").mkdir()                                # 3. Codex 装了但没有入口
        codex = home / ".codex" / "skills" / "study-diagram"
        links = [claude, cursor, codex]

        out = run(home, backup)
        for p in links:
            assert points_to_skill(p), f"{p} 没变成指向正本的链接\n{out}"
        saved = list(backup.rglob("独有.txt"))
        assert len(saved) == 2, f"副本没有备份：{saved}"                      # 4. 副本先备份再换
        assert (other / "SKILL.md").exists() and not other.is_junction()    # 5. 别的 skill 不动
        assert not (home / ".grok").exists(), "没装的 AI 不该建目录"          # 6. 没装的 AI 不碰
        again = run(home, backup)
        assert "FIXED" not in again, f"重跑又改了东西：{again}"               # 7. 重跑结果不变
        assert (SKILL / "SKILL.md").exists(), "正本不能被动到"
    finally:
        for p in links:                                          # 先拆链接，防止删临时目录时删到正本
            if p.is_junction():
                os.rmdir(p)
        assert (SKILL / "SKILL.md").exists()
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    print("ok   同步入口 7 项通过")


if __name__ == "__main__":
    main()
