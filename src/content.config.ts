import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// 昔の記事は scripts/import.py が手元の取り出し結果から書き出す。新しい記事は同じフォルダに手で足す。
// id はフォルダからのパスで、そのまま URL になる
const posts = defineCollection({
  loader: glob({
    base: './src/content/posts',
    pattern: '**/*.md',
    generateId: ({ entry }) => entry.replace(/\.md$/, ''),
  }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      categories: z.array(z.string()).default([]),
      // 一覧のカードに出す画像。記事の .md から見た相対パス（無ければテーマの色の帯になる）
      cover: image().optional(),
      original: z.string().optional(),
      // 検索結果・共有・RSS に出す説明文。無ければ本文の書き出しから作る（2026-11-06）
      description: z.string().optional(),
    }),
});

export const collections = { posts };
