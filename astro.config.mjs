// @ts-check
import { defineConfig } from 'astro/config';
import { readFileSync } from 'node:fs';
import imgSizes from './scripts/img-sizes.mjs';

// 2026-11-04 に外した記事（本文の薄い30本とインスタ映えの8本。scripts/import.py の HIDDEN_POSTS）の転送先。記事のテーマのカテゴリの一覧へ
const hidden = JSON.parse(readFileSync(new URL('./scripts/redirects.json', import.meta.url), 'utf-8'));

// 独自ドメイン oshabe.com の直下に出す（public/CNAME と GitHub の Pages 設定も oshabe.com）。
// 記事の本文の画像とリンクは相対パスで書いてある（scripts/import.py）ので、site や base を変えても記事は直さなくてよい
export default defineConfig({
  site: 'https://oshabe.com',
  base: '/',
  trailingSlash: 'always',
  // 本文の写真に大きさ違いの候補（srcset）を付ける。sizes は scripts/img-sizes.mjs がビルドの最後に表示の幅へ直す（2026-11-06）。
  // 見た目は今の CSS（[...slug].astro の .body img）のままにするので、Astro の付ける CSS は使わない。一覧のカードの画像は PostCard.astro で layout="none"
  image: { layout: 'constrained', responsiveStyles: false },
  integrations: [imgSizes()],
  // フォントのファイルは CSS に埋め込まない（4KB 未満が埋め込まれ、ページに無い文字の分まで毎回読ませていた。2026-11-06）
  vite: { build: { assetsInlineLimit: (file) => (/\.(woff2?|ttf)$/.test(file) ? false : undefined) } },
  // 昔の WordPress の URL（RSS とサイトマップのページ）を今のページへ送る
  // 今は出していないカテゴリ（芸能・漫画・家電・雑学）の一覧はトップへ
  redirects: {
    // 転送先はサイトの外の形（絶対 URL）で書く。'/rss.xml' だと trailingSlash で無いページ /rss.xml/ へ送ってしまう（2026-11-06）
    '/feed': 'https://oshabe.com/rss.xml', '/sitemap': '/',
    '/category/news': '/', '/category/未分類': '/', '/category/漫画': '/', '/category/家電': '/', '/category/雑学': '/',
    // おでかけのカテゴリはやめた（2026-11-05 本人の指示）
    '/category/おでかけ': '/',
    // 公開した日の URL で出してしまった記事を、写真を撮った日へ移した（2026-11-03）
    '/2026/11/03/koalas-march-fantasy-soda': '/2026/07/15/koalas-march-fantasy-soda/',
    '/2026/11/04/usj-mario-goods': '/2026/09/21/usj-mario-goods/',
    // 同じく写真を撮った日へ移した（2026-11-05 本人の指示。麦わらストアは10月の日付で、という指示なので 10/18 にした）
    '/2026/11/05/mugiwara-store-goods': '/2026/10/18/mugiwara-store-goods/',
    '/2026/11/05/capcorom': '/2026/11/02/capcorom/',
    '/2026/11/05/pokemon-center-stickers': '/2026/11/01/pokemon-center-stickers/',
    // 外した記事（2026-11-03 本人「AMEX の記事、中身の薄い記事、重複の1本を外して」。scripts/import.py の HIDDEN_POSTS）は近いカテゴリの一覧へ
    '/2018/08/30/usj_amex': '/category/usj/', '/usj_amex2': '/category/usj/', '/2016/09/23/65': '/category/usj/',
    '/2017/02/07/149': '/category/バレンタイン/', '/2016/09/07/48': '/category/ハロウィン/', '/2017/03/26/192': '/category/puchipura/',
    '/2016/11/11/113': '/category/xmas/', '/2016/11/11/114': '/category/xmas/', '/2016/11/18/121': '/category/100均/',
    '/2017/03/03/177': '/category/event/', '/2017/03/03/178': '/category/event/', '/2017/04/04/208': '/category/100均/',
    '/2016/11/18/120/310': '/2016/11/18/120/',
    ...hidden,
  },
});
