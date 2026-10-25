"""記事の Markdown の、説明（alt）が空の画像に「記事のタイトル（写真 n）」を付ける。

    python scripts/fill_alt.py

昔の記事は import.py の最後に、新しい記事は公開のたび（.github/workflows/deploy.yml のビルドの前）に動く。
すでに説明が書いてある画像はそのまま。何度動かしても結果は同じ。
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
    body2 = re.sub(r'!\[\]\(', rep, body)
    if n:
        open(path, 'w', encoding='utf-8', newline='\n').write(head + sep + body2)
    return n


if __name__ == '__main__':
    total = sum(fill(os.path.join(dp, f)) for dp, _, fs in os.walk(POSTS) for f in fs if f.endswith('.md'))
    print('alt filled', total, file=sys.stderr)
