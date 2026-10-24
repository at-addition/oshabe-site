import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// 昔の記事は scripts/import.py が google-context から書き出す。新しい記事は同じフォルダに手で足す。
// id はフォルダからのパスで、そのまま URL になる
const posts = defineCollection({
  loader: glob({
    base: './src/content/posts',
    pattern: '**/*.md',
    generateId: ({ entry }) => entry.replace(/\.md$/, ''),
  }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    categories: z.array(z.string()).default([]),
    original: z.string().optional(),
  }),
});

export const collections = { posts };
