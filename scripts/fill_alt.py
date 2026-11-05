"""記事の Markdown の、説明（alt）が空の画像に説明を付ける。

まず、画像のすぐ上（4行以内）にある短い行（商品名・小見出し）を使う（2026-11-06。新しい記事は「商品名 → 写真 → 値段」の形で書く）。
同じ商品名の下に写真が続くときは「（2）」から番号を付ける。使える行が無い画像には「記事のタイトル（写真 n）」を付ける。

    python scripts/fill_alt.py

昔の記事は import.py の最後に、新しい記事は公開のたび（.github/workflows/deploy.yml のビルドの前）に動く。
すでに説明が書いてある画像はそのまま。何度動かしても結果は同じ。
別の記事へのカード（[![](画像) 題](リンク)）の画像は、リンクの題が読まれるので説明を空のまま（飾り）にし、番号にも数えない（2026-11-06）。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, 'src', 'content', 'posts')


def fill(path):
    s = open(path, encoding='utf-8').read()
    m = re.search(r'^title:\s*(.+)$', s, re.M)
    if not m:
        return 0
    raw = m.group(1).strip()
    try:
        title = json.loads(raw)
    except ValueError:
        title = raw.strip('"\'')
    title = title.replace('[', '［').replace(']', '］')
    n = 0

    def rep(mm):
        nonlocal n
        n += 1
        return f'![{title}（写真 {n}）]('
    head, sep, body = s.partition('\n---\n') if s.startswith('---') else ('', '', s)
    body = product_alts(body)
    body2 = re.sub(r'(?<!\[)!\[\]\(', rep, body)
    if head + sep + body2 != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(head + sep + body2)
    return n


IMG_LINE = re.compile(r'^!\[\]\(([^)\s]+)\)[ \t]*$')
# 説明に使わない行: 文（全角の。！？♪☆♡ で終わる。商品名の英字の ! は使う）・値段の入った行・抜粋（...）・リンクや記号で始まる行・中身の無い見出し
SKIP_HEADS = ('[', '!', '|', '>', '-', '*', '▼', '↓', '※')
SKIP_WORDS = {'値段', 'まとめ', '画像一覧'}


def product_alts(body):
    lines = body.split('\n')
    cand, since, used = None, 0, {}
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t:
            continue
        if IMG_LINE.match(t):
            if cand and since <= 4:
                used[cand] = used.get(cand, 0) + 1
                alt = cand + (f'（{used[cand]}）' if used[cand] > 1 else '')
                lines[i] = ln.replace('![](', f'![{alt}](', 1)
            continue
        since += 1
        text = re.sub(r'^#+\s*', '', t)
        text = re.sub(r'[*_`]|\[([^\]]*)\]\([^)]*\)', lambda x: x.group(1) or '', text).strip()
        if (2 <= len(text) <= 60 and not t.startswith(SKIP_HEADS) and text not in SKIP_WORDS
                and not re.search(r'(?:\.\.\.|…|[。！？♪☆♡])$', text) and '円' not in text):
            text = text.replace('[', '［').replace(']', '］')
            cand, since = text, 0
    return '\n'.join(lines)


if __name__ == '__main__':
    total = sum(fill(os.path.join(dp, f)) for dp, _, fs in os.walk(POSTS) for f in fs if f.endswith('.md'))
    print('alt filled', total, file=sys.stderr)
