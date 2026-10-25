import { getCollection } from 'astro:content';
import { getImage } from 'astro:assets';
import type { APIRoute } from 'astro';
import { themeOf, excerpt } from '../lib/themes';

// 全記事のカードの中身。トップとカテゴリの一覧は最初の24本だけを HTML に入れ、「もっと見る」・絞り込み・検索のときにここから足す（lib/cardlist.ts）
export const GET: APIRoute = async () => {
  const base = import.meta.env.BASE_URL;
  const posts = (await getCollection('posts')).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  const rows = await Promise.all(posts.map(async (p) => {
    const t = themeOf(p.data.categories);
    const img = p.data.cover ? await getImage({ src: p.data.cover, width: 480 }) : undefined;
    return {
      u: `${base}${p.id}/`, t: p.data.title, c: p.data.categories.join('|'), h: t.hue, l: t.label,
      d: p.data.pubDate.toISOString(), e: excerpt(p.body, 60),
      ...(img ? { i: img.src, w: img.attributes.width, ht: img.attributes.height } : {}),
    };
  }));
  return new Response(JSON.stringify(rows), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
