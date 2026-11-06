// 記事の本文の写真に、画面の大きさに合った sizes を付ける（2026-11-06）。
// astro.config.mjs の image.layout: 'constrained' で写真に大きさ違いの候補（srcset）が付くが、
// Astro が付ける sizes は「元の幅いっぱい」（例: 1200px）なので、スマホでもいちばん大きい候補を読んでしまう。
// 本文の写真の表示は、本文の幅（最大 664px、スマホは画面の幅 − 約 70px）と高さ 560px までに収まる（[...slug].astro の .body img）。
// ビルドの最後に dist の HTML の写真の sizes を、その表示の幅に書き換える
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const COLUMN = 664; // 本文の幅の最大（.post 760px − 左右の余白 48px × 2）
const GUTTER = 70; // スマホで画面の幅から引く分（main の余白 16px × 2 と .body の余白 18px 前後 × 2）
const MAX_H = 560; // .body img の max-height

function walk(dir, out = []) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (f.endsWith('.html')) out.push(p);
  }
  return out;
}

export default function imgSizes() {
  return {
    name: 'img-sizes',
    hooks: {
      'astro:build:done': ({ dir, logger }) => {
        let n = 0;
        for (const file of walk(fileURLToPath(dir))) {
          const html = readFileSync(file, 'utf-8');
          const out = html.replace(/<img\b[^>]*data-astro-image="constrained"[^>]*>/g, (tag) => {
            if (/\sdata-astro-cid-/.test(tag)) return tag; // 部品（カードなど）の画像は除く。本文（Markdown）の写真だけ
            const w = Number(tag.match(/\swidth="(\d+)"/)?.[1]);
            const h = Number(tag.match(/\sheight="(\d+)"/)?.[1]);
            if (!w || !h || !/\ssrcset="[^"]*,/.test(tag)) return tag; // 候補が1つなら直さない
            const shown = Math.round(Math.min(COLUMN, w, (w * MAX_H) / h));
            n++;
            return tag.replace(/\ssizes="[^"]*"/, ` sizes="(max-width: ${shown + GUTTER}px) calc(100vw - ${GUTTER}px), ${shown}px"`);
          });
          if (out !== html) writeFileSync(file, out);
        }
        logger.info(`本文の写真の sizes を直した: ${n} 枚`);
      },
    },
  };
}
