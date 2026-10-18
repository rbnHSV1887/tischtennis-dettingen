#!/usr/bin/env python3
"""Baut site/index.html aus src/page.html. Mit --preview zusätzlich eine Fassung mit eingebetteter Schrift."""
import base64, sys
from pathlib import Path
R = Path(__file__).resolve().parent
src = (R / "src" / "page.html").read_text(encoding="utf-8")
head, sep, rest = src.partition('<header class="top">')
full = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head.replace('<style>', '<style>\n:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}\n'
                       'body{margin:0}\nimg{max-width:100%}\n[hidden]{display:none!important}', 1)
        + '</head>\n<body>\n' + sep + rest + '\n</body>\n</html>\n')
(R / "site" / "index.html").write_text(full, encoding="utf-8")
print("site/index.html gebaut")
if len(sys.argv) > 2 and sys.argv[1] == "--preview":
    font = base64.b64encode((R / "site/assets/fonts/archivo.woff2").read_bytes()).decode()
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(src.replace('url("assets/fonts/archivo.woff2")', f'url("data:font/woff2;base64,{font}")'), encoding="utf-8")
    print("Vorschau gebaut:", out / "index.html")
