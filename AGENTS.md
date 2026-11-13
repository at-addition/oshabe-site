# このリポジトリの決まり（最初に読む）

このリポジトリは **公開（public）** で、`main` に入ったものはそのまま GitHub Pages に公開される。詳しくは README。

- **`main` へは PR でだけ入れる。** PR のたびに `.github/workflows/check.yml` がビルドとサイト内のリンク切れを調べる。通ってからマージする
- **公開リポジトリなので、サイトに要るもの以外を書かない。** 手元や Drive のパス・メールアドレス・アカウント名・本名・住んでいる地域・ほかのリポジトリの名前を、ファイル・注釈・コミット・PR のどこにも書かない
- `src/content/posts/` は、置いた場所のパスがそのまま URL になる
- 昔の記事（`scripts/imported.txt` に載っているもの）は `scripts/import.py` が書き出す。**手で直さない**（直すなら `import.py` を直して取り込み直す）
- 新しい記事の画像は `src/content/images/` に置く。`src/content/wp-content/` は `import.py` が毎回作り直す
- スマホの写真は `scripts/prep_photos.py` を通す（位置情報などの EXIF を落とし、透かしを入れる）。残っていると `scripts/check_exif.py` が PR と公開を止める
- 記事の画像の説明（alt）は空で書いてよい。公開のたびに `scripts/fill_alt.py` が付ける
- もう1つのサイトと共通のファイルは README の「もう1つのサイトと共通のファイル」。片方を直したらもう片方も直す

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
