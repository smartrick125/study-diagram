"""Run a matplotlib figure script with Chinese fonts and study-note helpers preloaded.

Usage:
    python plot.py <figure.py> [...] [--out DIR] [--dpi 200]

A figure script is plain Python. These names are already defined for it:
    plt, np        matplotlib.pyplot and numpy
    mark(ax, x, y, text, color, dx=40, dy=-50, guide=True)
                   dot + arrow annotation (+ dashed guide line down to y=0)
    save(fig)      writes <OUT>/<script stem>.png
<OUT> is --out (an archive folder) or by default the shared work folder
<system temp>/study-diagram/, which drops files older than 7 days.
When archiving, keep the script in 源码/ next to the PNG so it can be edited later.
"""
import argparse, pathlib, runpy, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import workdir

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "Noto Sans SC", "SimHei", "PingFang SC", "DejaVu Sans"],
    "axes.unicode_minus": False,   # keep "-" readable with CJK fonts
    "mathtext.fontset": "stix",    # $...$ formulas look like LaTeX
    "figure.dpi": 100,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 12,
})


def mark(ax, x, y, text, color, dx=40, dy=-50, guide=True):
    """Dot on (x, y), arrow from the label to it, optional dashed line down to y=0."""
    if guide:
        ax.plot([x, x], [0, y], ls="--", lw=1.3, color=color)
    ax.plot([x], [y], "o", ms=7, color=color, zorder=5)
    if text:
        ax.annotate(text, xy=(x, y), xytext=(dx, -dy), textcoords="offset points",
                    color=color, fontsize=12,
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--dpi", type=int, default=200)
    a = ap.parse_args()
    out = workdir.out_dir(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in a.files:
        script = pathlib.Path(f).resolve()
        png = out / f"{script.stem}.png"

        def save(fig, _png=png):
            fig.savefig(_png, dpi=a.dpi, bbox_inches="tight", facecolor="white")
            print(f"ok   {_png}")

        runpy.run_path(str(script), init_globals={"plt": plt, "np": np, "mark": mark, "save": save})
        plt.close("all")


if __name__ == "__main__":
    sys.exit(main())
