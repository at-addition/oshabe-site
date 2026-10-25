// @ts-check
import { defineConfig } from 'astro/config';

// 独自ドメイン oshabe.com の直下に出す（public/CNAME と GitHub の Pages 設定も oshabe.com）。
// 記事の本文の画像とリンクは相対パスで書いてある（scripts/import.py）ので、site や base を変えても記事は直さなくてよい
export default defineConfig({
  site: 'https://oshabe.com',
  base: '/',
  trailingSlash: 'always',
  // 昔の WordPress の URL（RSS とサイトマップのページ）を今のページへ送る
  // 今は出していないカテゴリ（芸能・漫画・家電・雑学）の一覧はトップへ
  redirects: {
    '/feed': '/rss.xml', '/sitemap': '/',
    '/category/news': '/', '/category/未分類': '/', '/category/漫画': '/', '/category/家電': '/', '/category/雑学': '/',
  },
});
