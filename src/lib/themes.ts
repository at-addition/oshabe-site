// 記事のカテゴリから、カードのバッジと色に使う「テーマ」を1つ決める（上にあるほど優先）。
// 色はバッジ・見出しの帯・画像が無いときの背景に使う
export interface Theme {
  cat: string;
  label: string;
  hue: number;
  /** 明るい画面で、バッジの字の明るさ（薄い地の上で 4.5:1 に届く値。2026-11-06） */
  light: number;
}

export const THEMES: Theme[] = [
  { cat: 'USJ', label: 'USJ', hue: 215, light: 42 },
  { cat: 'ディズニーランド', label: 'ディズニー', hue: 275, light: 42 },
  { cat: 'ディズニーシー', label: 'ディズニー', hue: 275, light: 42 },
  { cat: 'ハロウィン', label: 'ハロウィン', hue: 26, light: 37 },
  { cat: 'クリスマス', label: 'クリスマス', hue: 355, light: 42 },
  { cat: 'バレンタイン', label: 'バレンタイン', hue: 330, light: 42 },
  { cat: '100均', label: '100均', hue: 175, light: 28 },
  { cat: '300均', label: '300均', hue: 150, light: 29 },
  // ガチャ（カプセルトイ）は 2026-11-04 に本人の指示で足した
  { cat: 'ガチャ', label: 'ガチャ', hue: 85, light: 28 },
  { cat: 'グッズ', label: 'グッズ', hue: 250, light: 42 },
  { cat: 'イベント', label: 'イベント', hue: 198, light: 35 },
  { cat: 'プチプラ', label: 'プチプラ', hue: 45, light: 31 },
];
const DEFAULT: Theme = { cat: '', label: 'ひとネタ', hue: 198, light: 35 };

/** 色相から、明るい画面の字の明るさ（%）。色相はテーマごとに違う */
export const lightOf = (hue: number | undefined) => (THEMES.find((t) => t.hue === hue) ?? DEFAULT).light;
/** 要素の style に付ける色の変数（--hue と、明るい画面の字の明るさ --lt） */
export const hueVars = (hue: number | undefined) => `--hue:${hue ?? DEFAULT.hue};--lt:${lightOf(hue)}%`;

export function themeOf(categories: string[]): Theme {
  return THEMES.find((t) => categories.includes(t.cat)) ?? DEFAULT;
}

// 本文から説明文を抜き出す処理は excerpt.ts（もう1つのサイトと同じファイル。2026-11-07 に分けた）
export { excerpt } from './excerpt';

// トップの一覧で最初から HTML に入れる本数（残りは cards.json から読む）
export const FIRST = 24;

// カテゴリの一覧ページの URL（/category/<slug>/）。昔の WordPress と同じにして、検索結果や他のサイトに残るリンクを生かす。
// 英字だったものだけ表に書き、ほかはカテゴリ名そのまま
const SLUGS: Record<string, string> = { USJ: 'usj', クリスマス: 'xmas', プチプラ: 'puchipura', グッズ: 'goods', イベント: 'event' };
export const catSlug = (cat: string) => SLUGS[cat] ?? cat;
export const catUrl = (base: string, cat: string) => `${base}category/${catSlug(cat)}/`;
/** 記事のパンくずに出すカテゴリ（テーマのカテゴリ、無ければ最初のカテゴリ） */
export const mainCat = (categories: string[]) => (categories.includes(themeOf(categories).cat) ? themeOf(categories).cat : categories[0]);
