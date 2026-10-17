"""自动清理：未存档的图每次渲染时删掉 7 天前的，存档文件夹不动。

运行：python tests/test_自动清理.py（退出码 0 = 通过）
"""
import os, pathlib, sys, tempfile, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skill" / "scripts"))
import workdir  # noqa: E402

DAY = 86400


def touch(path, age_days):
    path.write_text("x", encoding="utf-8")
    t = time.time() - age_days * DAY
    os.utime(path, (t, t))
    return path


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "study-diagram"
        root.mkdir()
        old_png = touch(root / "01-旧图.png", 8)
        old_src = touch(root / "01-旧图.mmd", 8)
        new_png = touch(root / "02-新图.png", 1)
        sub = root / "存档"
        sub.mkdir()
        nested_old = touch(sub / "03-存档图.png", 30)

        removed = workdir.prune(root)
        assert set(removed) == {old_png, old_src}, removed
        assert not old_png.exists() and not old_src.exists()
        assert new_png.exists(), "7 天内的图不能删"
        assert nested_old.exists(), "子文件夹不能动"
        assert workdir.prune(root) == [], "重跑不再删东西"

        archive = pathlib.Path(tmp) / "用户存档"
        archive.mkdir()
        kept = touch(archive / "04-存档.png", 30)
        workdir.ROOT = root
        assert workdir.out_dir(str(archive)) == archive.resolve()
        assert kept.exists(), "给了 --out 的存档文件夹不能清理"
        assert workdir.out_dir(None) == root
    print("ok   自动清理 5 项通过")


if __name__ == "__main__":
    main()
