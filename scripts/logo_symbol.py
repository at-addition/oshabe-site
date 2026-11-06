"""src/assets/oshabe-logo.svg から、ヘッダーが <use> で呼ぶ public/oshabe-logo.svg（symbol id="logo"）を作る。

    python scripts/logo_symbol.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src', 'assets', 'oshabe-logo.svg'), encoding='utf-8').read()
m = re.match(r'\s*<svg([^>]*)>(.*)</svg>\s*$', src, re.S)
vb = re.search(r'viewBox="([^"]+)"', m.group(1)).group(1)
open(os.path.join(ROOT, 'public', 'oshabe-logo.svg'), 'w', encoding='utf-8', newline='\n').write(
    f'<svg xmlns="http://www.w3.org/2000/svg"><symbol id="logo" viewBox="{vb}">{m.group(2)}</symbol></svg>\n')
w, h = vb.split()[2:]
print('viewBox', vb, f'— Base.astro の <svg viewBox> は "0 0 {w} {h}" にする')
