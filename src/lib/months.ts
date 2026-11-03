import type { CollectionEntry } from 'astro:content';

// 月別アーカイブ（/YYYY/MM/）。昔の WordPress と同じ URL で、記事のフォルダの年月で分ける（フォルダの無い記事は公開日の年月）
export const monthOf = (p: CollectionEntry<'posts'>) => {
  const m = p.id.match(/^(\d{4})\/(\d{2})\//);
  if (m) return `${m[1]}/${m[2]}`;
  const d = p.data.pubDate.toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit' }).replace(/\D+/g, '/').replace(/\/$/, '');
  return d;
};
export const monthLabel = (ym: string) => `${Number(ym.slice(0, 4))}年${Number(ym.slice(5, 7))}月`;
export const monthUrl = (base: string, ym: string) => `${base}${ym}/`;

/** 年月 → その月の記事（新しい順）。月は新しい順 */
export function byMonth(posts: CollectionEntry<'posts'>[]) {
  const map = new Map<string, CollectionEntry<'posts'>[]>();
  for (const p of [...posts].sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())) {
    const ym = monthOf(p);
    map.set(ym, [...(map.get(ym) ?? []), p]);
  }
  return new Map([...map].sort((a, b) => (a[0] < b[0] ? 1 : -1)));
}
