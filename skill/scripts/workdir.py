"""Shared work folder for unsaved study diagrams, pruned on every render.

Unsaved figures (the default) go to <system temp>/study-diagram/. Every run of
render.py or plot.py first deletes plain files there whose mtime is older than
KEEP_DAYS, so the folder never piles up. Archives the user asked for live in a
folder passed with --out and are never touched.
"""
import pathlib, tempfile, time

KEEP_DAYS = 7
ROOT = pathlib.Path(tempfile.gettempdir()) / "study-diagram"


def prune(root=None, days=KEEP_DAYS, now=None):
    """Delete plain files directly in root older than `days`; skip links and folders."""
    root = ROOT if root is None else root
    if not root.is_dir():
        return []
    cutoff = (time.time() if now is None else now) - days * 86400
    removed = []
    for p in root.iterdir():
        if p.is_symlink() or not p.is_file():
            continue
        if p.stat().st_mtime < cutoff:
            p.unlink(missing_ok=True)
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
