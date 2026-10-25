// パンくずを検索エンジン向けの BreadcrumbList にする（最後の項目はそのページ自身）
export function breadcrumbLd(items: { name: string; href?: string }[], self: string, site: URL | undefined) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem', position: i + 1, name: it.name, item: new URL(it.href ?? self, site).href,
    })),
  };
}
