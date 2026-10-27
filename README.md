# oshabe-site

ブログ「オシャベ」（100均・USJ・季節のイベント）のサイト。**https://oshabe.com/** で公開している。
Astro で作り、GitHub Pages に出す。`hazieta-site` と同じ作り。

- 2016〜2019年に書いた記事は、元のサーバーのデータが残っていなかったので Wayback Machine から取り出して復元した（2026-10-24）。
  記事の URL は元のサイトと同じ（`/2017/05/25/257/` など）
- 2026-10-24 からは、ここに新しい記事を書き足していく
- 書いた本人の了承を得て公開している

## 中身

| 場所 | 中身 |
| :--- | :--- |
| `src/content/posts/` | 記事の Markdown。昔の記事 329 本は `scripts/import.py` が書き出す（手で直さない）。新しい記事は手で置く |
| `src/content/wp-content/` | 昔の記事の画像 9,155 枚。`import.py` が毎回作り直す |
| `src/content/images/` | 新しい記事の画像を置くところ |
| `src/pages/` | 一覧（`index.astro`）・記事（`[...slug].astro`）・404・プライバシーポリシー（`privacy.astro`）・お問い合わせ（`contact.astro`） |
| `src/components/PostCard.astro` | 一覧のカード（画像・テーマのバッジ・日付・タイトル・抜き出し） |
| `src/lib/themes.ts` | カテゴリから決める「テーマ」（USJ・ディズニー・ハロウィン・100均など）と色。カードの抜き出しもここ |
| `src/assets/beyan.svg` | トップのマスコットの鳥（なぞった SVG） |
| `src/layouts/Base.astro` | 全ページ共通の枠（サイト名・説明文・フッター・色・アドセンスのコード） |
| `public/CNAME` | 独自ドメイン `oshabe.com` |
| `src/assets/oshabe-logo.svg` | ヘッダーの当時のロゴ（OSHABE.com）。元の PNG を色ごとになぞった SVG。黒は文字色、白は背景の色に合わせる |
| `public/favicon.svg` / `favicon.ico` / `apple-touch-icon.png` / `icon-192.png` / `icon-512.png` / `site.webmanifest` | 当時のマスコット（鳥）のアイコン。タブは SVG、スマホは白地の正方形 |
| `design/original/` | 当時の画像（Wayback から）。ロゴ `logo_338x109.png`（`wp-content/uploads/tcd-w/logo.png`）とマスコット `beyan_177x156.png`（SNS で共有したときの画像） |
| `design/beyan-square_1214.png` | マスコットの正方形アイコンの元 |
| `scripts/trace-logo-color.py` | 数色のロゴを色ごとになぞって SVG にする道具（vtracer・Pillow・numpy） |
| `public/ads.txt` | アドセンスのパブリッシャー ID（`Base.astro` の `ADSENSE_CLIENT` と揃える） |
| `scripts/import.py` | 取り出した昔の記事と画像を、このサイトの形に書き直して取り込む |
| `scripts/imported.txt` | `import.py` が前回書いた記事の一覧。取り込み直すとき、ここに載った記事だけを消す |
| `scripts/images.txt` | 昔の記事が使っている画像の一覧 |
| `.github/workflows/deploy.yml` | `main` に入ったらビルドして Pages へ出す |

## 新しい記事を書き足す

`src/content/posts/` の下に Markdown を1本置き、PR で `main` に入れると公開される。
**置いた場所のパスがそのまま URL になる**（`src/content/posts/2026/10/24/halloween.md` → `https://oshabe.com/2026/10/24/halloween/`）。

```markdown
---
title: "記事のタイトル"
pubDate: "2026-10-24"
categories: ["100均", "ハロウィン"]
cover: "../../../../images/2026-10-24-top.jpg"   # 一覧のカードに出す画像（省いてよい）
---

本文。画像は src/content/images/ に置き、記事の .md から見た相対パスで書く（縮小・変換される）。
```

- `original` は昔の記事の元の URL なので、新しい記事には書かない
- **新しい画像を `src/content/wp-content/` に置かない。** そこは `import.py` が毎回消して作り直す
- 昔の記事と同じパスに置くと、次に `import.py` を動かしたときに止まって知らせる

## 昔の記事を取り込み直す

記事の元は、Wayback Machine から取り出して手元に置いたもの（このリポジトリの外）。

```powershell
python -I scripts/import.py
npm run build
```

`import.py` がやること:

- 固定ページ（サイトマップ・プライバシーポリシー・お問い合わせ）は取り込まない。サイトマップはトップが代わりになる
- **外すと決めた記事は取り込まない**（下の「出していない記事」）。残す記事から外した記事へのリンクは、文字だけ残す
- 画像とサイト内リンクは**記事のページから見た相対パス**にする。ドメインや `base` を変えても記事は直さなくてよい
- 縮小版の画像（`-300x200.jpg`）を指していても、元の大きさの画像が残っていればそちらを使う
- 画像の名前の大文字・小文字をディスク上の名前に合わせる（下の「踏んだこと」）
- Wayback に残っていなかった画像は落とす
- 関連記事のカード（改行入りのリンク）を1行に詰める
- 本文の最初の画像を `cover` にする（一覧のカードに出る。画像の無い記事はテーマの色の帯になる）
- 手で書き足した記事は消さない。消すのは `scripts/imported.txt` に載った前回の記事だけ

## 出していない記事

どちらも消してはいない。`scripts/import.py` の切り替えで戻せる。戻した記事の画像は公開前に開いて見ること。

| 何を | 本数 | 理由 | 戻し方 |
| :--- | ---: | :--- | :--- |
| 芸能の記事 | 113 | 芸能人の写真（他人が撮ったもの）と噂話が多い | `INCLUDE_GOSSIP = True` |
| カテゴリ「漫画」「家電」「雑学」の記事 | 4（漫画 1・家電 2・雑学 1） | 本人の判断 | `INCLUDE_HIDDEN = True`（または `HIDDEN_CATS` から外す） |

- 芸能の記事は、芸能のカテゴリ（`GOSSIP_CATS`。女優・俳優・お笑い・10月ドラマ・アーティストなど）を持つ記事と、
  カテゴリが「未分類」だけの記事（2016年の記事はほぼ芸能）。未分類でも芸能でない記事は `NOT_GOSSIP` に並べて残す
- ほかのカテゴリを隠したいときは `HIDDEN_CATS` に名前を足す
- 外した記事の一覧は `import.py` が `scripts/excluded.tsv` に書き出す。タイトルも噂話なので**リポジトリには入れない**（`.gitignore`）
- 漫画・家電・雑学の記事は最初の公開に入っていたので、このリポジトリの履歴には残っている。芸能の記事は一度も入れていない

## ドメインと DNS

`oshabe.com` はネットオウル（スタードメイン）で契約している。期限は 2027-08-04 で、毎年6月に更新される。

| 項目 | 設定 |
| :--- | :--- |
| ネームサーバー | `ns1.star-domain.jp` / `ns2.star-domain.jp` / `ns3.star-domain.jp` |
| A（`oshabe.com`） | `185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153`（GitHub Pages） |
| CNAME（`www`） | `at-addition.github.io` |
| TXT（`_github-pages-challenge-at-addition`） | GitHub のアカウントでドメインを確認するための値。**消さない** |
| HTTPS | GitHub が証明書を発行・更新する（`oshabe.com` と `www.oshabe.com`）。強制オン |

- `www.oshabe.com` と旧 URL `https://at-addition.github.io/oshabe-site/` は `https://oshabe.com/` へ転送される
- 2026-02 から 2026-10-24 まで表示されていなかったのは、ネームサーバーが使っていないエックスサーバー（`ns1`〜`5.xserver.jp`）を向いたままだったため
- **証明書がなかなか出ないときは、カスタムドメインを外して付け直す**と出る（2026-10-24 は 30 秒で出た）

```powershell
gh api -X PUT repos/at-addition/oshabe-site/pages -f cname=
gh api -X PUT repos/at-addition/oshabe-site/pages -f cname=oshabe.com
```

## 広告とお問い合わせ

- **広告は Google アドセンス。** パブリッシャー ID は `pub-5250963766765858`（hqzietq のアカウント。
  2026-10-24 時点で「一定期間ご利用がないため無効」で、再有効化して `google@nakagawamail.com` を管理者に招待する予定）。
  全ページの `<head>` に `adsbygoogle.js` を入れ、`https://oshabe.com/ads.txt` に同じ ID を出している。
  ID を変えるときは `Base.astro` の `ADSENSE_CLIENT` と `public/ads.txt` の両方を直す
- **お問い合わせは Google フォーム**「オシャベ お問い合わせ」（`google@nakagawamail.com` の持ち物。
  Drive では `@Addition\google-context\doc_nat\AdSenseブログ\oshabe.com\`）。
  ログインなしで誰でも送れる。新しい回答はメールで届く。フォームの URL は `contact.astro` の `FORM_URL`
- プライバシーポリシーは昔のものを取り込まず、2026-10-24 に書き直した（`privacy.astro`）

## ブランチ運用

**`main` と `task` の2種類だけを使う。** 作業は `task/<内容>` で行い、`main` へは GitHub 上の PR でだけ入れる。
`main` に入るとそのまま公開される。

## 踏んだこと

- **元のサーバーには、大文字・小文字だけ違う画像が別々にあった**（`FEWFEWF.jpg` と `fewfewf.jpg` など 11 組）。
  Windows に落とすと1つに重なり、GitHub Actions（Linux）では `ImageNotFound` でビルドが止まった。
  `import.py` が名前をディスクに合わせ、このリポジトリは `git config core.ignorecase false` にして改名を記録した。
  重なった片方は、本来は別の画像だった可能性がある
- **Astro 7 は `markdown.rehypePlugins` が既定で使えない**（Markdown の処理系が替わった）。画像とリンクを相対パスにして避けた
- **Markdown の中の相対パスの画像は `.md` から見たファイルとして取り込まれる。** 無いとビルドが止まる

## 公開の前に見たこと（2026-10-24）

- 画像は無作為に選んだ 150 枚をコンタクトシートで見た。どれもお店の売り場と商品の写真で、
  「OSHABE」の透かしが入った本人の撮影。人の顔は商品のパッケージに印刷されたものだけだった。
  9,155 枚すべては見ていない（どれも元のブログで公開していた写真）
- 本文にメールアドレスや本名は無い。プライバシーポリシーは取り込んでいない

## 自動で付くもの（2026-10-25）

- 画像の説明（alt）: 空なら「記事のタイトル（写真 n）」。`scripts/fill_alt.py` が取り込みの最後と公開のたび（deploy.yml）に付ける
- 構造化データ（JSON-LD）: 記事は BlogPosting、それ以外は WebSite（`src/layouts/Base.astro`）
- RSS: `/rss.xml`（新しい50本、`src/pages/rss.xml.ts`）
- http の画像は取り込みで外す（https のページでは出ないため）
- アフィリエイト（楽天・A8・バリューコマース）の広告とリンクは外している。外したものは取り込みのたびに `scripts/affiliates.tsv`（git に入れない）へ書き出す。戻すときは `scripts/import.py` の `INCLUDE_AFFILIATE` を True にして取り込み直す
- トップの一覧は24本ずつ。「もっと見る」で足す
- はてなブックマークの件数リンクは外している（`scripts/hatena.tsv` に記録、git に入れない）。戻すときは `INCLUDE_HATENA` を True に
- Instagram の埋め込みの残りは「📷 Instagram で見る（@id）」の1行に、崩れたブログカードは URL の行と「このサイト内」の行を外す
- トップの HTML は最初の24本だけ。25本目からは `/cards.json` を「もっと見る」・絞り込みのときに読む（本数は `src/lib/themes.ts` の FIRST）
- 記事の最後に「あわせて読みたい」（カテゴリの重なりが多い順に4本）
- カテゴリの一覧 `/category/<名前>/`（昔の WordPress と同じ URL。英字の名前は `src/lib/themes.ts` の SLUGS）。記事にはパンくず（構造化データにも）
- 昔の `/feed/`・`/sitemap/`・出していないカテゴリの一覧は `astro.config.mjs` の redirects で今のページへ
- 閉店・移転した店や無くなったページへのリンクには注記を書き添える（表は `scripts/link_notes.tsv`、取り込みで付く）。PONEY の招待リンクはアフィリエイトと同じ扱い
- トップにタイトルの検索窓（?q=）。画像の無い記事のカードはマスコットの板
- カテゴリの一覧も最初の24本だけ HTML に入れ、「もっと見る」で `/cards.json`（全記事）から足す（`src/lib/cardlist.ts`、トップと共通）
- 1年より前の記事には「この記事は〇年に書いたもの」の注記、記事の最後に X・LINE の共有ボタン（リンクだけ）
- 404 ページに検索窓と入口のリンク。ページのタイトル（検索結果・タブ）は40字を超えたら切る（`Base.astro` の shortTitle、見出しはそのまま）
- フォントは Google から読まずに @fontsource でサイトから出す
- 全ページの上に翻訳ボタン（English・繁體中文・한국어）。Google 翻訳へのリンクだけで、翻訳後のページは Google のアドレスで開く（`Base.astro` の translate）
