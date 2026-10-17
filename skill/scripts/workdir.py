"""Shared work folder for unsaved study diagrams, pruned on every render.

Unsaved figures (the default) go to <system temp>/study-diagram/. Every run of
render.py or plot.py first deletes plain files there that are older than
KEEP_DAYS, so the folder never piles up. Archives the user asked for live in a
folder passed with --out and are never touched.
"""
import pathlib, tempfile, time

KEEP_DAYS = 7
ROOT = pathlib.Path(tempfile.gettempdir()) / "study-diagram"


def last_touched(st):
    """Newest of modify / create / change time. A copy keeps the source's mtime,
    but its create time (Windows) or ctime (Linux, macOS) is when it was copied."""
    return max(st.st_mtime, st.st_ctime, getattr(st, "st_birthtime", 0))


def prune(root=None, days=KEEP_DAYS, now=None):
    """Delete plain files directly in root older than `days`; skip links and folders.
    A file that cannot be deleted (in use) is skipped: cleanup never blocks drawing."""
    root = ROOT if root is None else root
    if not root.is_dir():
        return []
    cutoff = (time.time() if now is None else now) - days * 86400
    removed = []
    for p in root.iterdir():
        try:
            if p.is_symlink() or not p.is_file() or last_touched(p.stat()) >= cutoff:
                continue
            p.unlink()
        except OSError:
            continue
        removed.append(p)
    return removed


def out_dir(arg):
    """--out if given (an archive, left alone), else the pruned shared work folder."""
    if arg:
        return pathlib.Path(arg).resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    removed = prune()
    if removed:
        print(f"cleaned {len(removed)} file(s) older than {KEEP_DAYS} days in {ROOT}")
    return ROOT
