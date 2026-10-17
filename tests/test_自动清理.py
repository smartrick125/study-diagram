"""自动清理：未存档的图每次渲染时删掉 7 天前的，复制进来的旧文件和存档文件夹不动。

运行：python tests/test_自动清理.py（退出码 0 = 通过）
"""
import os, pathlib, sys, tempfile, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skill" / "scripts"))
import workdir  # noqa: E402

DAY = 86400


def touch(path, mtime_days_ago, now):
    """New file whose modify time is set back, like a copy of an old figure."""
    path.write_text("x", encoding="utf-8")
    t = now - mtime_days_ago * DAY
    os.utime(path, (t, t))
    return path


def main():
    now = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "study-diagram"
        root.mkdir()
        copied = touch(root / "backup_笔记_01-旧图.png", 30, now)
        fresh = touch(root / "02-新图.png", -2, now)
        sub = root / "存档"
        sub.mkdir()
        nested = touch(sub / "03-存档图.png", 30, now)

        # 1. 刚复制进来的旧图：修改时间是 30 天前，但复制才刚发生，不能删
        assert workdir.prune(root, now=now) == [], "刚复制进来的文件被删了"
        assert copied.exists()

        # 2. 8 天后再渲染：复制进来的图已满 7 天，删掉
        later = now + 8 * DAY
        removed = workdir.prune(root, now=later)
        assert removed == [copied], removed

        # 3. 6 天内改过的图不删；4. 子文件夹不动
        assert fresh.exists(), "7 天内的图不能删"
        assert nested.exists(), "子文件夹不能动"

        # 5. 重跑不再删东西
        assert workdir.prune(root, now=later) == [], "重跑不再删东西"

        # 6. 给了 --out 的存档目录不清理（根本不调用 prune）
        archive = pathlib.Path(tmp) / "用户存档"
        archive.mkdir()
        real_prune, workdir.prune = workdir.prune, None
        try:
            assert workdir.out_dir(str(archive)) == archive.resolve()
        finally:
            workdir.prune = real_prune
        workdir.ROOT = root
        assert workdir.out_dir(None) == root
    print("ok   自动清理 6 项通过")


if __name__ == "__main__":
    main()
