"""手元に取り出した昔の記事（Markdown）と画像を、この Astro サイトへ取り込む。

    python -I scripts/import.py <記事のフォルダ> <画像のフォルダ>

取り込み元はこのリポジトリの外にあり、場所はここに書かない（公開リポジトリのため）。

- 記事は src/content/posts/<元のパス>.md（元の URL と同じ道のりで出すため）
- 画像は src/content/<元のパス>（記事が指しているものだけ）
- 画像と元のサイト内へのリンク（http://oshabe.com/...）は、記事のページから見た相対パスにする。
  記事は /<base>/<元のパス>/ に出るので、サイトの根元まではパスの段数ぶん ../ を重ねる。
  相対にしておけば、site や base を変えても同じ記事で動く
- 前回書いた記事（scripts/imported.txt）だけを消してから書く。手で書き足した記事は消さない
- 固定ページ（サイトマップ・プライバシーポリシー・お問い合わせ）は取り込まない。サイトマップはトップが代わりになる
- 芸能の記事は外す（2026-10-24 本人判断。他人が撮った芸能人の写真と噂話が多いため）。
  外した記事は scripts/excluded.tsv に並べる。戻すときは INCLUDE_GOSSIP を True にして取り込み直すだけ
- 漫画・家電・雑学のカテゴリの記事も外す（2026-10-24 本人指示）。戻すときは INCLUDE_HIDDEN を True にする
"""
import collections, json, os, re, shutil, sys

# 芸能の記事も出すなら True にする
INCLUDE_GOSSIP = False
# これらのカテゴリを1つでも持つ記事、またはカテゴリが「未分類」だけ・空の記事を芸能の記事とみなす
GOSSIP_CATS = {'女優', '俳優', 'お笑い', '10月ドラマ', 'アーティスト', 'グラビアアイドル', 'モデル', 'アイドル', 'ニュース'}
# 未分類・カテゴリ無しでも芸能ではない記事
NOT_GOSSIP = {'halloween2016', 'usj_amex2'}

# 芸能とは別に、今は出さないカテゴリ（2026-10-24 本人指示「漫画もいつでも復活できるように非表示に」、同日に家電・雑学も）。
# 戻すときは集合から外すか INCLUDE_HIDDEN を True にして取り込み直す
INCLUDE_HIDDEN = False
HIDDEN_CATS = {'漫画', '家電', '雑学'}
# 記事は出すが、カテゴリとしては付けないもの（2026-11-05 本人「おでかけをやめたい」。付け方がばらばらだったため）
DROP_CATS = {'おでかけ'}
# 記事ごとに外すもの（2026-11-03 本人「AMEX の記事、中身の薄い記事、重複の1本を外して」）。戻すときは集合から消すか INCLUDE_HIDDEN を True に。
# 外した URL は astro.config.mjs の redirects でカテゴリの一覧などへ送る
HIDDEN_POSTS = {
    '2018/08/30/usj_amex', 'usj_amex2',   # AMEX カードの宣伝（元アフィリエイト、特典は 2018 年のまま）
    '2017/02/07/149', '2016/09/07/48', '2017/03/26/192', '2016/09/23/65',   # 中身の薄い記事
    '2016/11/11/113', '2016/11/11/114', '2016/11/18/121', '2017/03/03/177', '2017/03/03/178', '2017/04/04/208',   # 題に「画像」とあるのに画像が残っていない
    '2016/11/18/120/310',   # 2016/11/18/120 と同じ記事（WordPress の別 URL）
    # 2026-11-04 アドセンスの審査が「有用性の低いコンテンツ」だったため（本人「先に進めてOK」）。関連記事のカードを除いた本文が 500 字未満の記事
    '2016/11/22/126', '2017/01/24/137', '2017/02/04/143', '2017/02/18/158', '2017/02/27/168', '2017/02/28/169', '2017/03/02/176',
    '2017/04/04/206', '2017/04/04/207', '2017/05/08/240', '2017/05/20/254', '2017/05/20/255', '2017/06/03/267', '2017/06/20/293',
    '2017/11/17/382', '2017/11/17/383', '2017/12/06/390', '2017/12/11/391', '2018/01/11/397', '2018/02/08/413', '2018/02/08/414',
    '2018/02/08/415', '2018/02/09/417', '2018/02/21/422', '2018/03/13/432', '2018/03/22/427', '2018/09/11/490', '2018/09/11/492',
    '2019/06/13/496', 'halloween2016',
    # 同じ日。他人の Instagram 投稿へのリンクが中心のインスタ映えスポットの8本（表紙の写真がちーの撮影か未確認）
    '2017/05/02/234', '2017/05/02/236', '2017/05/04/237', '2017/05/10/241', '2017/07/08/309', '2017/07/12/310', '2017/07/28/319',
    '2017/08/28/332',
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'oshabe.com'
if len(sys.argv) != 3:
    sys.exit('使い方: python -I scripts/import.py <記事のフォルダ> <画像のフォルダ>')
SRC, BIN = sys.argv[1], sys.argv[2]
POSTS = os.path.join(ROOT, 'src', 'content', 'posts')
SKIP_PAGES = {'sitemap', 'privacy', 'contact_form'}

# 昔のタイトルの直し（scripts/titles.tsv。2026-11-03、書いた本人の確認済み）
TITLE_FIX = dict(l.split('\t', 1) for l in open(os.path.join(ROOT, 'scripts', 'titles.tsv'), encoding='utf-8').read().splitlines()
                 if l and not l.startswith('#'))


def read(name):
    text = open(os.path.join(SRC, name), encoding='utf-8').read()
    head, _, body = text.partition('\n---\n')
    meta = dict(re.findall(r'^- ([^:]+): (.*)$', head, re.M))
    title = re.search(r'^# (.*)$', head, re.M).group(1).strip()
    path = re.sub(r'^https?://[^/]+/', '', meta['元の URL']).strip('/')
    title = TITLE_FIX.get(path, title)
    cats =[c.strip() for c in meta.get('カテゴリ', '').split(',') if c.strip()]
    return meta, title, path, cats, body


def true_case(rel):
    """ディスク上の大文字・小文字に合わせる。元のサーバー（Linux）には FEWFEWF.jpg と fewfewf.jpg が別にあったが、
    Windows に落とすと1つに重なる。記事が小文字で指していても、GitHub の Linux でビルドが通るよう実在する名前にする
    （重なった片方は別の画像だった可能性がある）"""
    d, name = os.path.split(os.path.join(BIN, *rel.split('/')))
    for real in os.listdir(d):
        if real.lower() == name.lower():
            return rel[:len(rel) - len(name)] + real
    return rel


def is_gossip(path, cats):
    if path in NOT_GOSSIP:
        return False
    return bool(GOSSIP_CATS & set(cats)) or not (set(cats) - {'未分類'})


# 先に外す記事を決める（残す記事から外した記事へのリンクは、リンクを外して文字だけ残すため）
excluded = {}
for name in sorted(os.listdir(SRC)):
    meta, title, path, cats, _ = read(name)
    if path in SKIP_PAGES or not meta.get('公開'):
        continue
    if (not INCLUDE_GOSSIP and is_gossip(path, cats)) or (not INCLUDE_HIDDEN and (HIDDEN_CATS & set(cats) or path in HIDDEN_POSTS)):
        excluded[path] = (meta['公開'][:10], title, ','.join(cats))

# 前回この道具が書いた記事だけを消す。手で書き足した記事は消さない
IMPORTED = os.path.join(ROOT, 'scripts', 'imported.txt')
if os.path.exists(IMPORTED):
    for rel in open(IMPORTED, encoding='utf-8').read().split():
        p = os.path.join(POSTS, *rel.split('/'))
        if os.path.exists(p):
            os.remove(p)
os.makedirs(POSTS, exist_ok=True)
written = []
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
        rel = true_case(rel)
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
        'categories': [c for c in cats if c not in DROP_CATS],
        'original': meta['元の URL'],
    }
    if meta.get('更新'):
        fm['updatedDate'] = meta['更新']
    # 一覧のカードに出す画像は、本文の最初の画像（記事の .md から見た相対パス。Astro が縮小して出す）。
    # 別の記事へのカード（[![](画像) 題](リンク)）の画像は、その記事の画像なので飛ばす（2026-11-06）
    first = re.search(r'(?<!\[)!\[[^\]]*\]\((\.\./[^)]+)\)', body)
    if first:
        fm['cover'] = first.group(1)
    lines = ['---'] + [f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in fm.items()] + ['---', '']
    dst = os.path.join(POSTS, *path.split('/')) + '.md'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        sys.exit(f'{dst} は手で書いた記事と重なっている。どちらかの場所を変える')
    open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + body.strip() + '\n')
    written.append(path + '.md')
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
# アフィリエイト（楽天・A8・バリューコマース）の広告とリンクを外す（2026-10-25 本人指示「いつでも復活できるようにメモして外して」）。
# 外したものは scripts/affiliates.tsv に記事ごとに書き出す（リポジトリには入れない）。戻すときは INCLUDE_AFFILIATE を True に
INCLUDE_AFFILIATE = False
# ポイントサイト PONEY の招待リンク（紹介料が入る）も同じ扱い（同日、本人指示）
AFF = r'https?://(?:hbb?\.afl\.rakuten\.co\.jp|px\.a8\.net|ck\.jp\.ap\.valuecommerce\.com|(?:www|cdn)\.poney\.jp)/[^)\s]*'
aff_rows = []
if not INCLUDE_AFFILIATE:
    for rel in written:
        f = os.path.join(POSTS, *rel.split('/'))
        s = open(f, encoding='utf-8').read()
        found = re.findall(AFF, s)
        if not found:
            continue
        aff_rows += [(rel, u) for u in dict.fromkeys(found)]
        s = re.sub(r'!\[(?:[^\[\]]|\[[^\]]*\])*\]\(' + AFF + r'\)', '', s)       # 広告の画像
        s = re.sub(r'\[[^\]\n]*\]\(' + AFF + r'\)', '', s)                        # 商品名のリンク
        s = re.sub(r'^\s*\]?\(?' + AFF + r'\)?\s*$', '', s, flags=re.M)           # 改行で割れたリンクの残り
        s = re.sub(r'^[ \t]*\]\(' + AFF + r'\)[ \t]*$', '', s, flags=re.M)
        s = re.sub(r'^\s*\[\s*$', '', s, flags=re.M)                                # 取り残しの [
        s = re.sub(r'^\s*価格：[^\n]*時点\)\s*$', '', s, flags=re.M)                 # 当時の価格の行
        s = re.sub(r'\n{3,}', '\n\n', s)
        open(f, 'w', encoding='utf-8', newline='\n').write(s)
    with open(os.path.join(ROOT, 'scripts', 'affiliates.tsv'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('記事\tURL\n' + ''.join(f'{r}\t{u}\n' for r, u in aff_rows))
    print('affiliate removed', len(aff_rows), file=sys.stderr)

# はてなブックマークの件数（「1 user」）は当時の飾りなので外す（2026-10-25 本人指示「裏にメモ残して外して」）。
# 外したものは scripts/hatena.tsv（リポジトリには入れない）。戻すときは INCLUDE_HATENA を True に
INCLUDE_HATENA = False
HATENA = r'\[([^\]]*)\]\((https?://b\.hatena\.ne\.jp/[^)]*)\)'
# Instagram の埋め込みは、取り出すと「〜さん(@id)がシェアした投稿 – 日時」の文字だけになるので、1行のリンクに直す
INSTA = r'\[([^\]\n]*)\]\((https://www\.instagram\.com/p/[^)]+)\)(?:[ \t]*–[^\n]*)?'
insta = 0
hatena_rows = []
# 記事のパス → タイトル（ブログカードの直しに使う）
titles = {}
for rel in written:
    m = re.search(r'^title: (.*)$', open(os.path.join(POSTS, *rel.split('/')), encoding='utf-8').read(), re.M)
    titles[rel[:-3]] = json.loads(m.group(1))
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    s = open(f, encoding='utf-8').read()
    s2 = s
    if not INCLUDE_HATENA:
        hatena_rows += [(rel, m.group(1), m.group(2)) for m in re.finditer(HATENA, s2)]
        s2 = re.sub(r'[ \t]*' + HATENA, '', s2)
    def insta_link(m):
        if m.group(1).startswith('Instagram で見る'):
            return m.group(0)
        who = re.search(r'@([\w.]+)', m.group(1))
        return f"📷 [Instagram で見る{f'（@{who.group(1)}）' if who else ''}]({m.group(2)})"
    s2, k = re.subn(INSTA, insta_link, s2)
    # 記事の中の「ブログカード」は、取り出すと URL の行と「oshabe.com（このサイト内）」の行に崩れるので、
    # URL をその記事のタイトルに直し、「このサイト内」の行は外す
    s2 = re.sub(r'^\[ ?oshabe\.com（このサイト内）\]\([^)]*\)[ \t]*\n?', '', s2, flags=re.M)
    def card_url(m):
        # 直前にカード（画像とタイトルのリンク）があれば URL の行ごと外し、無ければタイトルのリンクにする
        if m.group(2) in s2[max(0, m.start() - 600):m.start()]:
            return ''
        return f"[{titles.get(m.group(1).strip('/'), 'この記事')}]({m.group(2)})"
    s2 = re.sub(r'^\[https?://oshabe\.com/([^\]]*?)/?\]\(([^)]*)\)[ \t]*$', card_url, s2, flags=re.M)
    s2 = re.sub(r'\n{3,}', '\n\n', s2)
    insta += k
    if s2 != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
with open(os.path.join(ROOT, 'scripts', 'hatena.tsv'), 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('記事\t文字\tURL\n' + ''.join(f'{r}\t{x}\t{u}\n' for r, x, u in hatena_rows))
print('hatena removed', len(hatena_rows), 'instagram', insta, file=sys.stderr)

# http の画像は https のページから読み込まれず崩れて見えるので外す（2026-10-25 本人指示）
http_dropped = 0
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    s = open(f, encoding='utf-8').read()
    s2, k = re.subn(r'!\[(?:[^\[\]]|\[[^\]]*\])*\]\(http://[^)]*\)', '', s)
    if k:
        http_dropped += k
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
print('http images dropped', http_dropped, file=sys.stderr)

# 取り出したときの崩れの残りを片付ける（2026-11-03 本人「取り込みなおして」）
# - 空の見出し（「#### 」だけの行）と、「|」だけの段落（表の枠の残り）は、画面に空の帯や縦線として出ていたので外す
# - 「2019年版はこちら↓↓↓ https://oshabe.com/… 抜粋...」のように、行の途中に崩れたブログカードの URL が残ったものは、
#   URL をその記事のタイトルのリンクにし、後ろの抜粋（別の記事の書き出し）は外す
cleaned = collections.Counter()
SELF_URL = r'(?<![(\[<])https?://(?:www\.)?' + re.escape(DOMAIN) + r'/((?:\d{4}/\d{2}/\d{2}/)?[^\s/)\]]+(?:/[^\s/)\]]+)*)/?'
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    s = open(f, encoding='utf-8').read()
    head, sep, body = s.partition('\n---\n')
    body, k = re.subn(r'^#{1,6}[ \t　|｜]*$', '', body, flags=re.M)
    cleaned['空の見出し'] += k
    body, k = re.subn(r'^[ \t　]*[|｜]+[ \t　]*$', '', body, flags=re.M)
    cleaned['「|」の段落'] += k
    # 関連記事のカードの後ろの抜粋（他の記事の書き出し。末尾が ...）は外し、カードはリンクだけにする（2026-11-04。本文の文字の 46% がこの抜粋とカードだった）
    body, k = re.subn(r'^[^\n]*\.\.\.[ \t　]*$', '', body, flags=re.M)
    cleaned['カードの抜粋'] += k
    up = '../' * len(rel[:-3].split('/'))
    # 見出しの段を詰める（## の次が #### の記事が多く、読み上げや検索では段が飛んで見えた）。使っている段を ## から順に振り直す
    used_lv = sorted({len(h) for h in re.findall(r'^(#{2,6}) ', body, flags=re.M)})
    remap = {lv: 2 + i for i, lv in enumerate(used_lv)}
    if any(k != v for k, v in remap.items()):
        body = re.sub(r'^(#{2,6}) ', lambda m: '#' * remap[len(m.group(1))] + ' ', body, flags=re.M)
        cleaned['見出しの段を詰めた記事'] += 1
    # それでも1つ上の見出しより2段以上深いもの（## の直後の #### など）は、1段深いところまで上げる
    prev = [1]

    def clamp(m):
        lv = min(len(m.group(1)), prev[0] + 1)
        prev[0] = lv
        return '#' * lv + ' '
    body = re.sub(r'^(#{2,6}) ', clamp, body, flags=re.M)
    # 外した記事を指す崩れたブログカード（URL の行・抜粋・「このサイト内」の行と、直前の【見出し】）は丸ごと外す
    body, k = re.subn(r'(?:^【[^】\n]*】[ \t]*\n+)?^[ \t]*https?://(?:www\.)?' + re.escape(DOMAIN) + '/(?:' + '|'.join(map(re.escape, excluded)) +
                      r')/?[ \t]*\n+(?:^[^\n]*(?:\.\.\.|…)[ \t]*\n+)?(?:^[ \t]*' + re.escape(DOMAIN) + r'（このサイト内）[ \t]*$)?', '', body, flags=re.M)
    cleaned['外した記事へのカード'] += k
    # AMEX の記事を外したので、USJ の記事に入っていた宣伝の見出し・カードと抜粋・バナーも外す
    if not INCLUDE_HIDDEN:
        n0 = len(body)
        body = re.sub(r'^【[^】\n]*AMEX[^】\n]*】[ \t]*$', '', body, flags=re.M)
        body = re.sub(r'^\[!\[[^\]]*\]\([^)]*\)[^\n]*\]\([^)]*usj_amex2?/\)[ \t]*\n+[^\n]*(?:\.\.\.|…)[ \t]*$', '', body, flags=re.M)
        body = re.sub(r'^\[\s*\n\s*!\[[^\]]*\]\([^)]*\)\s*\n\s*\]\([^)]*usj_amex2?/\)[ \t]*$', '', body, flags=re.M)
        if len(body) != n0:
            cleaned['AMEX の宣伝を外した記事'] += 1

    def self_url(m):
        path = m.group(1).strip('/')
        if path not in titles:
            return m.group(0)
        cleaned['行の途中の URL'] += 1
        return f'\n\n[{titles[path]}]({up}{path}/)\n\n'
    lines = []
    for ln in body.split('\n'):
        if re.search(SELF_URL, ln) and not re.search(r'\]\(' + SELF_URL, ln):
            ln = re.sub(r'[ \t　]*' + SELF_URL + r'[ \t　]*(?:[^\n]*?(?:\.\.\.|…))?[ \t　]*$', self_url, ln)
        lines.append(ln.rstrip(' \t'))
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))
    s2 = head + sep + body
    if s2 != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
print('cleaned', dict(cleaned), file=sys.stderr)

# 画像の説明（alt）を、すぐ前にある商品名の行から付ける（2026-11-03 本人「改修お願い」）。
# 当時の説明は、ファイル名のような英数字（fa343431 など）か、記事をまたいで同じ文（「ダイソー　ハロウィン　2016」が136枚など）が多かった。
# 説明が空・英数字だけ・サイト全体で10回以上使われている画像に限り、4行以内の前にある短い文の行（商品名・小見出し）を使う。
# 同じ行の下に写真が何枚も続くときは「（2）」から番号を付ける。前に使える行が無い画像は、このあと fill_alt.py がタイトルで埋める
IMG_LINE = re.compile(r'^!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)\)[ \t]*$')
alt_count = collections.Counter()
for rel in written:
    for m in re.finditer(r'^!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(', open(os.path.join(POSTS, *rel.split('/')), encoding='utf-8').read(), re.M):
        alt_count[m.group(1)] += 1
alt_set = 0
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    s = open(f, encoding='utf-8').read()
    head, sep, body = s.partition('\n---\n')
    lines = body.split('\n')
    cand, since, used_alt = None, 0, collections.Counter()
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t:
            continue
        m = IMG_LINE.match(t)
        if m:
            alt = m.group(1)
            weak = not alt.strip() or not re.search(r'[ぁ-んァ-ヶ一-龠]', alt) or alt_count[alt] >= 10
            if weak and cand and since <= 4:
                used_alt[cand] += 1
                new = cand + (f'（{used_alt[cand]}）' if used_alt[cand] > 1 else '')
                lines[i] = ln.replace(f'![{alt}](', f'![{new}](', 1)
                alt_set += 1
            continue
        since += 1
        text = re.sub(r'^#+\s*', '', t)
        text = re.sub(r'[*_`]|\[([^\]]*)\]\([^)]*\)', lambda x: x.group(1) or '', text).strip()
        # 短い文の行だけを候補にする（値段だけの行・抜粋「...」・リンクだけの行・箇条書きの記号は使わない）
        if (2 <= len(text) <= 60 and not t.startswith(('[', '!', '|', '>', '-', '*', '▼', '↓', '※'))
                and not re.search(r'(?:\.\.\.|…)$', text) and not re.fullmatch(r'[^\n]{0,12}\d[\d,]*円[^\n]{0,12}', text)):
            text = text.replace('[', '［').replace(']', '］')
            if text != cand:
                cand, since = text, 0
    s2 = head + sep + '\n'.join(lines)
    if s2 != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
print('alt from product lines', alt_set, file=sys.stderr)

# 閉店・移転した店や、無くなったページへのリンクには、後ろに注記を書き添える（2026-10-25 本人指示。表は scripts/link_notes.tsv）
notes = dict(l.split('\t', 1) for l in open(os.path.join(ROOT, 'scripts', 'link_notes.tsv'), encoding='utf-8').read().splitlines()
             if l and not l.startswith('#'))
noted = 0
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    s = open(f, encoding='utf-8').read()

    def note(m):
        global noted
        n = notes.get(m.group(2))
        if not n or s[m.end():m.end() + len(n)] == n:
            return m.group(0)
        noted += 1
        return m.group(0) + n
    s2 = re.sub(r'(?<!!)\[([^\]\n]*)\]\(([^)\s]+)\)', note, s)
    if s2 != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
print('link notes', noted, file=sys.stderr)

# 書いた記事の中の、サイト内に無いページへのリンク（昔の WordPress のカテゴリ・タグの一覧や、2ページ目など）は
# 開くと「見つかりません」になるので、リンクを外して文字だけ残す。画像と、実在する記事・手で足した記事へのリンクは残す
pages = {os.path.relpath(os.path.join(dp, f), POSTS).replace(os.sep, '/')[:-3]
         for dp, _, fs in os.walk(POSTS) for f in fs if f.endswith('.md')}
unlinked = 0
for rel in written:
    f = os.path.join(POSTS, *rel.split('/'))
    here = rel[:-3]   # 記事は /<パス>/ に出るので、リンクはそのフォルダから見た相対
    s = open(f, encoding='utf-8').read()

    def fix(m):
        global unlinked
        text, url = m.group(1), m.group(2)
        target = os.path.normpath(os.path.join(here, url.split('#')[0])).replace(os.sep, '/').strip('/')
        if url.startswith('http') or target.startswith('wp-content') or target in pages or target == '.':
            return m.group(0)
        unlinked += 1
        return text
    s2 = re.sub(r'(?<!!)\[((?:[^\[\]]|!\[[^\]]*\]\([^)]*\))*)\]\((\.\./[^)\s]*)\)', fix, s)
    if s2 != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(s2)
print('unlinked', unlinked, file=sys.stderr)
open(IMPORTED, 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(written)) + '\n')

# 片付けの手順で外したカードや宣伝が指していた画像は、最初に写した時点では使われていたので残っている。
# 書き終えた記事がどれも指していない画像は消す（公開リポジトリに第三者の画像を残さないため。2026-11-03）
refs = set()
for dp, _, fs in os.walk(POSTS):
    for fn in fs:
        if fn.endswith('.md'):
            t = open(os.path.join(dp, fn), encoding='utf-8').read()
            for src in re.findall(r'\]\(([^)\s]*wp-content/[^)\s]+)\)', t) + re.findall(r'^cover: "([^"]*wp-content/[^"]+)"', t, re.M):
                refs.add(src[src.index('wp-content/'):])
gone = sorted(u for u in used if u not in refs)
for rel in gone:
    os.remove(os.path.join(IMAGES, *rel.split('/')))
open(os.path.join(ROOT, 'scripts', 'images.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(used - set(gone))) + '\n')
print('unused images removed', len(gone), file=sys.stderr)

# 画像の説明（alt）を付ける。新しい記事は公開のたびに同じ道具が付ける
import subprocess
subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'scripts', 'fill_alt.py')], check=True)
print('posts', n, 'excluded', len(excluded), 'images', len(used), 'dropped', dropped, file=sys.stderr)
