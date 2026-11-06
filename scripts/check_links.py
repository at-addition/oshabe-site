"""ビルドした dist の HTML から、サイト内を指すリンク・画像・転送先が dist に実在するかを調べる。

    python3 -I scripts/check_links.py dist / oshabe.com      （ハジエッセイは dist /hazieta-site/ at-addition.github.io）

見るのは href・src・srcset と、転送のページ（meta refresh）の行き先。3つ目の引数のドメインへの絶対 URL もサイト内として見る。ほかのサイトは見ない。
見つかったら一覧を出して 1 で終わる（GitHub Actions を赤にする）。.github/workflows/check.yml が PR のたびに動かす。
"""
import collections, html as H, os, re, sys
from urllib.parse import unquote, urljoin, urlparse

dist, base = sys.argv[1], sys.argv[2]
host = sys.argv[3] if len(sys.argv) > 3 else ''
bad = collections.defaultdict(set)
pages = 0


def urls(doc):
    for u in re.findall(r'\s(?:href|src)="([^"]+)"', doc):
        yield u
    for s in re.findall(r'\ssrcset="([^"]+)"', doc):
        for part in s.split(','):
            if part.strip():
                yield part.strip().split()[0]
    for u in re.findall(r'http-equiv="refresh"\s+content="\d+;\s*url=([^"]+)"', doc, re.I):
        yield u


for dp, _, fs in os.walk(dist):
    for f in fs:
        if not f.endswith('.html'):
            continue
        pages += 1
        rel = os.path.relpath(os.path.join(dp, f), dist).replace(os.sep, '/')
        here = base + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
        doc = open(os.path.join(dp, f), encoding='utf-8').read()
        for url in urls(doc):
            url = H.unescape(url)
            if url.startswith(('mailto:', 'data:', '#', 'javascript:', 'tel:')):
                continue
            p = urlparse(urljoin('http://x' + here, url))
            if p.scheme in ('http', 'https') and p.netloc not in ('x', host, 'www.' + host):
                continue  # ほかのサイト
            path = unquote(p.path)
            target = os.path.join(dist, path[len(base):]) if path.startswith(base) else None
            if target and path.endswith('/'):
                target = os.path.join(target, 'index.html')
            if not target or not os.path.exists(target):
                bad[path].add(here)
print(f'{pages} ページ、サイト内のリンク切れ {len(bad)} 件', file=sys.stderr)
for path, srcs in sorted(bad.items()):
    print(f'  {path} ← {len(srcs)} ページ（例: {sorted(srcs)[0]}）', file=sys.stderr)
sys.exit(1 if bad else 0)
