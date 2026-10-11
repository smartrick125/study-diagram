"""Render mermaid .mmd files to PNG with headless Chrome/Edge.

Usage:
    python render.py <file.mmd> [<file2.mmd> ...] [--out DIR] [--scale 2]

Each <name>.mmd becomes <name>.png (in --out, default: next to the .mmd).
Mermaid is loaded from cdn.jsdelivr.net, so the first run needs network.
"""
import argparse, json, os, pathlib, re, subprocess, sys

FONT = '"Microsoft YaHei", "PingFang SC", sans-serif'
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium",
]

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff}</style></head><body><div id="out"></div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({startOnLoad:false, theme:'default', securityLevel:'loose',
  fontFamily:%s, flowchart:{wrappingWidth:420, htmlLabels:true, padding:14},
  sequence:{wrap:false, noteMargin:12, messageMargin:40}});
mermaid.render('g', %s).then(r => { document.getElementById('out').innerHTML = r.svg; })
  .catch(e => { document.getElementById('out').textContent = 'MERMAID_ERROR ' + e; });
</script></body></html>"""

STATIC = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#fff} #w{padding:20px;display:inline-block}</style></head>
<body><div id="w">%s</div></body></html>"""


def find_browser():
    env = os.environ.get("CHROME_PATH")
    for p in ([env] if env else []) + CANDIDATES:
        if p and os.path.exists(p):
            return p
    sys.exit("No Chrome/Edge found. Set CHROME_PATH to a Chromium-based browser.")


def run(browser, *args):
    return subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-sandbox", *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=180)


def render(browser, mmd, out_dir, scale):
    src = mmd.read_text(encoding="utf-8")
    work = out_dir / f".{mmd.stem}_live.html"
    work.write_text(PAGE % (json.dumps(FONT), json.dumps(src)), encoding="utf-8")
    svg, last = None, ""
    for _ in range(3):  # first CDN fetch sometimes times out
        last = run(browser, "--virtual-time-budget=20000", "--dump-dom", work.as_uri()).stdout
        m = re.search(r"<svg.*</svg>", last, re.S)
        if m:
            svg = m.group(0)
            break
        if "MERMAID_ERROR" in last:
            break
    work.unlink(missing_ok=True)
    if not svg:
        err = re.search(r"MERMAID_ERROR[^<]*", last)
        print(f"FAIL {mmd.name}: {err.group(0) if err else 'no svg rendered'}")
        return False
    vb = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', svg)
    w, h = float(vb.group(3)), float(vb.group(4))
    svg = svg.replace('width="100%"', f'width="{w}"', 1)
    svg = re.sub(r'style="max-width:[^"]*"', f'style="max-width:none" height="{h}"', svg, count=1)
    static = out_dir / f".{mmd.stem}_static.html"
    static.write_text(STATIC % svg, encoding="utf-8")
    png = out_dir / f"{mmd.stem}.png"
    run(browser, f"--screenshot={png}", f"--window-size={int(w) + 40},{int(h) + 40}",
        f"--force-device-scale-factor={scale}", "--hide-scrollbars", static.as_uri())
    static.unlink(missing_ok=True)
    print(f"ok   {png}  ({int(w) + 40}x{int(h) + 40} @{scale}x)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=2)
    a = ap.parse_args()
    browser = find_browser()
    ok = True
    for f in a.files:
        mmd = pathlib.Path(f).resolve()
        out = pathlib.Path(a.out).resolve() if a.out else mmd.parent
        out.mkdir(parents=True, exist_ok=True)
        ok &= render(browser, mmd, out, a.scale)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
