// @ts-check
import { defineConfig } from 'astro/config';

// GitHub Pages のプロジェクトサイトは /<リポジトリ名>/ の下に出る。独自ドメインにしたら base を '/' にする。
// 記事の本文の画像とリンクは相対パスで書いてある（scripts/import.py）ので、base を変えても記事は直さなくてよい
export default defineConfig({
  site: 'https://oshabe.com',
  base: '/',
  trailingSlash: 'always',
});
