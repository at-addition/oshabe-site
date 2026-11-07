// Markdown の本文から、説明文（検索結果・共有・RSS・一覧のカード）に使う短い抜き出しを作る。
// ハジエッセイ（hazieta-site）とオシャベ（oshabe-site）で同じファイル。片方を直したらもう片方も直す（README の「もう1つのサイトと共通のファイル」）
export function excerpt(body: string | undefined, len = 70): string {
  const text = (body ?? '')
    // 説明にしない行: 他の年の記事への案内や更新の注記（↓↓↓2018年版はこちら↓↓↓・※９月１２日更新・▼…）、
    // リンクだけの行（関連記事のカード）と、その抜粋（末尾が ... の行）
    .replace(/^[ 　]*(?:[↓▼※]|.*年(?:版|度)はこちら).*$/gm, '')
    .replace(/^[ 　]*(?:[-*][ 　]+)?\[.*\]\([^)]*\)[ 　]*$/gm, '')
    .replace(/^.*(?:\.\.\.|…)[ 　]*$/gm, '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#+\s.*$/gm, '')
    .replace(/https?:\/\/\S+/g, '')
    // Markdown の記号だけを消す。行頭の箇条書き・引用・区切り線と、強調・表の記号。語の中の - と _ は残す（#C-pla など。2026-11-06）
    .replace(/^[ 　]*(?:[-*_]{3,})[ 　]*$/gm, '')
    .replace(/^[ 　]*(?:[-*+>]|\d+\.)[ 　]+/gm, '')
    .replace(/[*`|]/g, '')
    // 空白と改行は詰める。ただし英語の語の間（Koala's March など）は1つ残す
    .replace(/\s+/g, (_, i: number, s: string) => (/[A-Za-z0-9'’.,!?]/.test(s[i - 1] ?? '') && /[A-Za-z0-9]/.test(s[i + _.length] ?? '') ? ' ' : ''))
    .trim();
  return text.length > len ? text.slice(0, len) + '…' : text;
}
