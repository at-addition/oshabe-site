// 記事のカテゴリから、カードのバッジと色に使う「テーマ」を1つ決める（上にあるほど優先）。
// 色はバッジ・見出しの帯・画像が無いときの背景に使う
export interface Theme {
  cat: string;
  label: string;
  hue: number;
}

export const THEMES: Theme[] = [
  { cat: 'USJ', label: 'USJ', hue: 215 },
  { cat: 'ディズニーランド', label: 'ディズニー', hue: 275 },
  { cat: 'ディズニーシー', label: 'ディズニー', hue: 275 },
  { cat: 'ハロウィン', label: 'ハロウィン', hue: 26 },
  { cat: 'クリスマス', label: 'クリスマス', hue: 355 },
  { cat: 'バレンタイン', label: 'バレンタイン', hue: 330 },
  { cat: '100均', label: '100均', hue: 175 },
  { cat: '300均', label: '300均', hue: 150 },
  { cat: 'おでかけ', label: 'おでかけ', hue: 120 },
  { cat: 'グッズ', label: 'グッズ', hue: 250 },
  { cat: 'イベント', label: 'イベント', hue: 198 },
  { cat: 'プチプラ', label: 'プチプラ', hue: 45 },
];
const DEFAULT: Theme = { cat: '', label: 'ひとネタ', hue: 198 };

export function themeOf(categories: string[]): Theme {
  return THEMES.find((t) => categories.includes(t.cat)) ?? DEFAULT;
}

/** Markdown の本文から、カードに出す短い抜き出しを作る */
export function excerpt(body: string | undefined, len = 70): string {
  const text = (body ?? '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#+\s.*$/gm, '')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/[*_`>|-]/g, '')
    .replace(/\s+/g, '')
    .trim();
  return text.length > len ? text.slice(0, len) + '…' : text;
}

// トップの一覧で最初から HTML に入れる本数（残りは cards.json から読む）
export const FIRST = 24;

// カテゴリの一覧ページの URL（/category/<slug>/）。昔の WordPress と同じにして、検索結果や他のサイトに残るリンクを生かす。
// 英字だったものだけ表に書き、ほかはカテゴリ名そのまま
const SLUGS: Record<string, string> = { USJ: 'usj', クリスマス: 'xmas', プチプラ: 'puchipura', グッズ: 'goods', イベント: 'event' };
export const catSlug = (cat: string) => SLUGS[cat] ?? cat;
export const catUrl = (base: string, cat: string) => `${base}category/${catSlug(cat)}/`;
/** 記事のパンくずに出すカテゴリ（テーマのカテゴリ、無ければ最初のカテゴリ） */
export const mainCat = (categories: string[]) => (categories.includes(themeOf(categories).cat) ? themeOf(categories).cat : categories[0]);
