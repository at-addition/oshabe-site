"""google-context に取り出した記事（Markdown）と画像を、この Astro サイトへ取り込む。

    python -I scripts/import.py

- 記事は src/content/posts/<元のパス>.md（元の URL と同じ道のりで出すため）
- 画像は src/content/<元のパス>（記事が指しているものだけ）
- 画像と元のサイト内へのリンク（http://hazieta.com/...）は、記事のページから見た相対パスにする。
  記事は /<base>/<元のパス>/ に出るので、サイトの根元まではパスの段数ぶん ../ を重ねる。
  相対にしておけば、GitHub Pages の /oshabe-site/ でも独自ドメインの / でも同じ記事で動く
- 固定ページ（サイトマップ・プライバシーポリシー・お問い合わせ）は取り込まない。サイトマップはトップが代わりになる
- 芸能の記事は外す（2026-10-24 本人判断。他人が撮った芸能人の写真と噂話が多いため）。
  外した記事は scripts/excluded.tsv に並べる。戻すときは INCLUDE_GOSSIP を True にして取り込み直すだけ
"""
import json, os, re, shutil, sys

# 芸能の記事も出すなら True にする
INCLUDE_GOSSIP = False
# これらのカテゴリを1つでも持つ記事、またはカテゴリが「未分類」だけ・空の記事を芸能の記事とみなす
GOSSIP_CATS = {'女優', '俳優', 'お笑い', '10月ドラマ', 'アーティスト', 'グラビアアイドル', 'モデル', 'アイドル', 'ニュース'}
# 未分類・カテゴリ無しでも芸能ではない記事
NOT_GOSSIP = {'halloween2016', 'usj_amex2'}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'oshabe.com'
SRC = rf'C:\@Addition\google-context\doc_txt\AdSenseブログ\{DOMAIN}\記事'
BIN = rf'C:\@Addition\google-context\doc_bin\AdSenseブログ\{DOMAIN}'
POSTS = os.path.join(ROOT, 'src', 'content', 'posts')
SKIP_PAGES = {'sitemap', 'privacy', 'contact_form'}

def read(name):
    text = open(os.path.join(SRC, name), encoding='utf-8').read()
    head, _, body = text.partition('\n---\n')
    meta = dict(re.findall(r'^- ([^:]+): (.*)$', head, re.M))
    title = re.search(r'^# (.*)$', head, re.M).group(1).strip()
    path = re.sub(r'^https?://[^/]+/', '', meta['元の URL']).strip('/')
    cats = [c.strip() for c in meta.get('カテゴリ', '').split(',') if c.strip()]
    return meta, title, path, cats, body


def is_gossip(path, cats):
    if path in NOT_GOSSIP:
        return False
    return bool(GOSSIP_CATS & set(cats)) or not (set(cats) - {'未分類'})


# 先に外す記事を決める（残す記事から外した記事へのリンクは、リンクを外して文字だけ残すため）
excluded = {}
for name in sorted(os.listdir(SRC)):
    meta, title, path, cats, _ = read(name)
    if path not in SKIP_PAGES and meta.get('公開') and not INCLUDE_GOSSIP and is_gossip(path, cats):
        excluded[path] = (meta['公開'][:10], title, ','.join(cats))

shutil.rmtree(POSTS, ignore_errors=True)
os.makedirs(POSTS)
used, n, dropped = set(), 0, 0
for name in sorted(os.listdir(SRC)):
    meta, title, path, cats, body = read(name)
    if path in SKIP_PAGES or not meta.get('公開') or path in excluded:
        continue

    up = '../' * len(path.split('/'))

    def local_img(m):
        rel = m.group(1)
        # 縮小版（-300x200.jpg）を指していても、元の大きさの画像が取れていればそちらを使う
        full = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', rel)
        if full != rel and os.path.exists(os.path.join(BIN, *full.split('/'))):
            rel = full
        used.add(rel)
        return f']({up}{rel})'
    body = re.sub(r'\]\((?:\.\./)+doc_bin/AdSenseブログ/' + re.escape(DOMAIN) + r'/([^)]+)\)', local_img, body)
    # Wayback に残っていなかった自サイトの画像は、もう表示できないので落とす
    body, gone = re.subn(r'!\[[^\]]*\]\(https?://(?:www\.)?' + re.escape(DOMAIN) + r'/[^)]*\)\s*', '', body)
    dropped += gone
    # 外した記事へのリンクは文字だけ残す（画像付きのカードは画像ごと落とす）
    def drop_link(m):
        return '' if m.group(1).lstrip().startswith('![') else m.group(1)
    for p in excluded:
        body = re.sub(r'\[((?:[^\[\]]|\[[^\]]*\])*)\]\(https?://(?:www\.)?' + re.escape(DOMAIN) + '/' + re.escape(p) + r'/?\)', drop_link, body)
    body = re.sub(r'\]\(https?://(?:www\.)?' + re.escape(DOMAIN) + r'/([^)]*)\)', lambda m: f']({up}{m.group(1)})', body)
    body = re.sub(r'\]\(//', '](https://', body)
    # 関連記事のカード（[ 改行 ![](画像) 改行 タイトル](URL)）は改行が入ると Markdown のリンクにならないので1行に詰める
    body = re.sub(r'\[\s*\n\s*((?:!\[[^\]]*\]\([^)]*\)\s*)?)([^\[\]\n]+?)\s*\]\(',
                  lambda m: '[' + m.group(1).strip() + (' ' if m.group(1).strip() else '') + m.group(2).strip() + '](', body)

    fm = {
        'title': title,
        'pubDate': meta['公開'],
        'categories': cats,
        'original': meta['元の URL'],
    }
    if meta.get('更新'):
        fm['updatedDate'] = meta['更新']
    lines = ['---'] + [f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in fm.items()] + ['---', '']
    dst = os.path.join(POSTS, *path.split('/')) + '.md'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + body.strip() + '\n')
    n += 1

# 画像は src/content/wp-content に置く。記事の .md から見た相対パスがそのままここを指し、
# Astro が画像として取り込んで（縮小・変換して）出力する
IMAGES = os.path.join(ROOT, 'src', 'content')
shutil.rmtree(os.path.join(IMAGES, 'wp-content'), ignore_errors=True)
for rel in sorted(used):
    s, d = os.path.join(BIN, *rel.split('/')), os.path.join(IMAGES, *rel.split('/'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(s, d)
open(os.path.join(ROOT, 'scripts', 'images.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(used)) + '\n')
with open(os.path.join(ROOT, 'scripts', 'excluded.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('公開日\tパス\tカテゴリ\tタイトル\n')
    for p, (d, t, c) in sorted(excluded.items(), key=lambda kv: kv[1][0]):
        f.write(f'{d}\t{p}\t{c}\t{t}\n')
print('posts', n, 'excluded', len(excluded), 'images', len(used), 'dropped', dropped, file=sys.stderr)
