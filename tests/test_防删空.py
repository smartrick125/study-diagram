"""防删空：skill/ 被删空时，scripts/同步入口.ps1 用 git 把被删的文件恢复回来；少量删改不动。

在临时 git 仓库和假主目录里跑，不碰真实的 skill/ 和各 AI 入口。
运行：python tests/test_防删空.py（退出码 0 = 通过）
"""
import pathlib, shutil, subprocess, sys, tempfile

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "同步入口.ps1"
FILES = {"SKILL.md": "入口\n", "modules/路线.md": "a\n", "modules/时序.md": "b\n", "scripts/render.py": "c\n"}


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(tmp):
    repo = tmp / "repo"
    for rel, text in FILES.items():
        f = repo / "skill" / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    return repo


def run(tmp, repo):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
                        "-Repo", str(repo), "-UserHome", str(tmp / "home"), "-BackupRoot", str(tmp / "backup"),
                        "-LogPath", str(tmp / "恢复日志.txt")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def main():
    if sys.platform != "win32":
        print("skip 同步入口只在 Windows 上用")
        return
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        (tmp / "home").mkdir()
        repo = make_repo(tmp)
        skill = repo / "skill"

        # 1. 只删 1 个模块（正常删改，入口还在）：不恢复
        (skill / "modules" / "时序.md").unlink()
        out = run(tmp, repo)
        assert "RESTORED" not in out and not (skill / "modules" / "时序.md").exists(), out
        git(repo, "restore", "skill")

        # 2. 整个 skill/ 被删空：全部恢复，日志写明缺了哪些（含中文文件名）
        shutil.rmtree(skill)
        out = run(tmp, repo)
        assert all((skill / rel).exists() for rel in FILES), out
        log = (tmp / "恢复日志.txt").read_text(encoding="utf-8-sig")
        assert "4/4" in log and "modules/路线.md" in log, log

        # 3. git rm 暂存的删除也算
        git(repo, "rm", "-rq", "skill")
        run(tmp, repo)
        assert (skill / "SKILL.md").exists(), "暂存的删除没恢复"

        # 4. 只删了 SKILL.md：恢复它；同时手上改了一半的文件保持原样
        (skill / "modules" / "路线.md").write_text("改到一半\n", encoding="utf-8")
        (skill / "SKILL.md").unlink()
        run(tmp, repo)
        assert (skill / "SKILL.md").exists(), "SKILL.md 没恢复"
        assert (skill / "modules" / "路线.md").read_text(encoding="utf-8") == "改到一半\n", "没被删的改动被覆盖了"

        # 5. 没东西可恢复时重跑不再动
        assert "RESTORED" not in run(tmp, repo)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ok   防删空 5 项通过")


if __name__ == "__main__":
    main()
