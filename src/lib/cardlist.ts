// 一覧の「もっと見る」で、HTML に入れていない記事のカードを cards.json から足す（トップとカテゴリの一覧で使う）。
// ページにある最初のカードを写して中身を入れ替えるので、見た目は PostCard.astro と同じになる
export type Row = { u: string; t: string; c: string; h: number; l: string; d: string; e: string; i?: string; w?: number; ht?: number };

const fmt = (iso: string) => new Date(iso).toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: 'long', day: 'numeric' });

/** cards.json を読み、ページにまだ無い記事のカードを隠した状態で grid の末尾に足す。keep で足す記事を絞れる */
export async function addCards(grid: HTMLElement, keep: (r: Row) => boolean = () => true) {
  const tpl = grid.querySelector<HTMLElement>('.card');
  if (!tpl) return;
  const have = new Set([...document.querySelectorAll<HTMLAnchorElement>('.card a')].map((a) => new URL(a.href).pathname));
  const rows: Row[] = await fetch(grid.dataset.src!).then((r) => r.json());
  for (const r of rows) {
    if (have.has(r.u) || !keep(r)) continue;
    const c = tpl.cloneNode(true) as HTMLElement;
    c.style.setProperty('--hue', String(r.h));
    c.dataset.cats = r.c;
    c.dataset.title = r.t;
    c.querySelector('a')!.href = r.u;
    const img = c.querySelector<HTMLImageElement>('.thumb img');
    const fallback = c.querySelector<HTMLElement>('.thumb-fallback');
    if (r.i && img) {
      img.removeAttribute('srcset');
      img.src = r.i; img.width = r.w ?? 480; img.height = r.ht ?? 360; img.alt = '';
    } else if (r.i && fallback) {
      const im = document.createElement('img');
      for (const a of fallback.getAttributeNames()) if (a.startsWith('data-astro')) im.setAttribute(a, '');
      im.src = r.i; im.width = r.w ?? 480; im.height = r.ht ?? 360; im.alt = ''; im.loading = 'lazy';
      fallback.replaceWith(im);
    } else if (img) {
      const s = document.createElement('span');
      for (const a of img.getAttributeNames()) if (a.startsWith('data-astro')) s.setAttribute(a, '');
      s.className = 'thumb-fallback'; s.textContent = r.l;
      img.replaceWith(s);
    } else if (fallback) {
      fallback.textContent = r.l;
    }
    c.querySelector('.theme-badge')!.textContent = r.l;
    const time = c.querySelector('time')!;
    time.dateTime = r.d; time.textContent = fmt(r.d);
    c.querySelector('h3')!.textContent = r.t;
    c.querySelector('.excerpt')!.textContent = r.e;
    c.hidden = true;
    grid.append(c);
  }
}
