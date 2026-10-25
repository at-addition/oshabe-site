import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { catUrl } from '../lib/themes';

// Google などに記事の一覧を伝えるサイトマップ。トップと全記事（更新日があればそれを最終更新に）
export const GET: APIRoute = async ({ site }) => {
  const base = import.meta.env.BASE_URL;
  const posts = await getCollection('posts');
  const url = (path: string) => new URL(`${base}${path}`, site).href;
  const rows = [
    `<url><loc>${url('')}</loc></url>`,
    ...[...new Set(posts.flatMap((p) => p.data.categories))].map((c) => `<url><loc>${new URL(catUrl(base, c), site).href}</loc></url>`),
    ...posts.map((p) => {
      const d = (p.data.updatedDate ?? p.data.pubDate).toISOString().slice(0, 10);
      return `<url><loc>${url(p.id + '/')}</loc><lastmod>${d}</lastmod></url>`;
    }),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${rows.join('\n')}\n</urlset>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
