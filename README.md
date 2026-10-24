# oshabe-site

2016〜2019年に `oshabe.com` で書いていたブログ「オシャベ」（100均・USJ・季節のイベント）を、
Wayback Machine に残っていた記録から復元した静的サイト。Astro で作り、GitHub Pages に出す。
`hazieta-site` と同じ作り。

- 公開先: https://at-addition.github.io/oshabe-site/
- 記事の URL は元のサイトと同じ道のり（`/2017/05/25/257/` など）
- 書いた本人の了承を得て公開（2026-10-24）

## 中身

| 場所 | 中身 |
| :--- | :--- |
| `src/content/posts/` | 記事 333 本の Markdown。`scripts/import.py` が書き出すので手で直さない |
| `src/content/wp-content/` | 記事に載っている画像 9,165 枚。Astro が縮小・変換して出す |
| `src/pages/` | 一覧（`index.astro`）・記事（`[...slug].astro`）・404 |
| `scripts/import.py` | 取り出した記事と画像を、このサイトの形に書き直して取り込む |
| `scripts/excluded.tsv` | 外した芸能の記事 113 本の一覧（公開日・パス・カテゴリ・タイトル）。`import.py` が毎回書き出す。タイトルも噂話なので**リポジトリには入れない**（`.gitignore`） |
| `.github/workflows/deploy.yml` | `main` に入ったらビルドして Pages へ出す |

## 記事を取り込み直す

記事の元は、Wayback Machine から取り出して手元に置いたもの（このリポジトリの外）。

```powershell
python -I scripts/import.py
npm run build
```

`import.py` がやること:

- 固定ページ（サイトマップ・プライバシーポリシー・お問い合わせ）は取り込まない
- **芸能の記事は外す。** 芸能人の写真（他人が撮ったもの）と噂話が多いため。
  芸能のカテゴリ（女優・俳優・お笑い・10月ドラマ・アーティストなど）を持つ記事と、カテゴリが「未分類」だけの記事
  （2016年の記事はほぼ芸能）を外す。残す記事から外した記事へのリンクは、文字だけ残す
- 画像とサイト内リンクは**記事のページから見た相対パス**にする。GitHub Pages の `/oshabe-site/` でも独自ドメインの `/` でも同じ記事で動く
- 縮小版の画像（`-300x200.jpg`）を指していても、元の大きさの画像が残っていればそちらを使う
- Wayback に残っていなかった画像は落とす
- 関連記事のカード（改行入りのリンク）を1行に詰める

### 芸能の記事を戻す

`scripts/import.py` の `INCLUDE_GOSSIP` を `True` にして取り込み直し、PR で `main` に入れる。
戻した記事の画像は公開前に開いて見ること。

## 新しい記事を書き足す

`src/content/posts/` の下に Markdown を1本置き、PR で `main` に入れると公開される。
**置いた場所のパスがそのまま URL になる**（`src/content/posts/2026/10/24/halloween.md` → `/2026/10/24/halloween/`）。

```markdown
---
title: "記事のタイトル"
pubDate: "2026-10-24"
categories: ["カテゴリ"]
---

本文。画像は記事の .md から見た相対パスで書く（`src/content/` の下に置けば縮小・変換される）。
```

- `original` は昔の記事の元の URL なので、新しい記事には書かない
- `scripts/import.py` を動かし直しても、手で足した記事は消えない。消すのは前回この道具が書いた記事
  （`scripts/imported.txt` に並んでいるもの）だけ。昔の記事と同じパスに置くと `import.py` が止まって知らせる

## 独自ドメインにするとき

`oshabe.com` のドメインは今も契約が続いている（エックスサーバー、期限 2027-08-04）。

1. `astro.config.mjs` の `site` を `https://oshabe.com`、`base` を `/` にする
2. `public/CNAME` に `oshabe.com` と1行書く
3. リポジトリの Settings → Pages の Custom domain に入れ、エックスサーバーの DNS を GitHub Pages に向ける

## ブランチ運用

**`main` と `task` の2種類だけを使う。** 作業は `task/<内容>` で行い、`main` へは GitHub 上の PR でだけ入れる。
`main` に入るとそのまま公開される。

## 公開の前に見たこと（2026-10-24）

- 画像は無作為に選んだ 150 枚をコンタクトシートで見た。どれもお店の売り場と商品の写真で、
  「OSHABE」の透かしが入った本人の撮影。人の顔は商品のパッケージに印刷されたものだけだった。
  9,165 枚すべては見ていない（どれも元のブログで公開していた写真）
- 本文にメールアドレスや本名は無い。プライバシーポリシーは取り込んでいない
