import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { excerpt } from '../lib/themes';

// フィードリーダー向けの RSS。新しい記事から50本。記事を足せば自動で載る
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export const GET: APIRoute = async ({ site }) => {
  const base = import.meta.env.BASE_URL;
  const url = (path: string) => new URL(`${base}${path}`, site).href;
  const posts = (await getCollection('posts')).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()).slice(0, 50);
  const items = posts.map((p) => `<item><title>${esc(p.data.title)}</title><link>${url(p.id + '/')}</link><guid>${url(p.id + '/')}</guid><pubDate>${p.data.pubDate.toUTCString()}</pubDate><description>${esc(excerpt(p.body ?? '', 160))}</description></item>`);
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>オシャベ</title><link>${url('')}</link><description>オシャベの新しい記事</description><language>ja</language>\n${items.join('\n')}\n</channel></rss>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
