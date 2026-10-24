"""数色のロゴ（ベタ塗り）を色ごとに分けてなぞり、1枚の SVG にまとめる。
背景（外周につながった白）は透明にし、絵の中の白（目など）は白の層として残す。

    python trace_color.py <元の画像> <出力.svg> <色1> <色2> ...   色は 231815 のような16進
"""
import re, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import vtracer

src, out, inks = sys.argv[1], sys.argv[2], ['#' + c for c in sys.argv[3:]]
S = 8
im = Image.open(src).convert('RGBA')
w, h = im.size
bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
big = np.asarray(bg.convert('RGB').resize((w * S, h * S), Image.LANCZOS)).astype(np.int32)

pal = [(255, 255, 255)] + [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in inks]
alpha = np.asarray(im.getchannel('A').resize((w * S, h * S), Image.LANCZOS)).astype(np.int32)
transparent = alpha.min() < 250
# 透過のある画像は、細い文字が半透明で白に寄ってしまうので、色は透過を外した RGB で見て、塗りの有無は透明度で決める
rgb = np.asarray(im.convert('RGB').resize((w * S, h * S), Image.LANCZOS)).astype(np.int32) if transparent else big


def classify(px):
    """色の薄い（鮮やかでない）画素は白と無彩色のインクだけから選ぶ。黒と白の境目のにじみが青に化けるのを防ぐ"""
    chroma = px.max(-1) - px.min(-1)
    d = np.stack([((px - np.array(p)) ** 2).sum(-1) for p in pal])
    achrom = np.array([max(p) - min(p) < 60 for p in pal])
    d_ach = np.where(achrom[:, None, None], d, 1 << 40)
    return np.where(chroma < 70, d_ach.argmin(0), d.argmin(0))


cls = classify(rgb)                                 # 0 = 白、1.. = インクの色
if transparent:
    cls = np.where(alpha > 90, cls, 0)
    # 半透明の細い線は RGB が白に寄るので、透明度が高く白と判定されたところはいちばん濃いインクにする
    lum = rgb.mean(-1)
    cls = np.where((alpha > 90) & (cls == 0) & (lum > 200) & (alpha < 230), 1, cls)

# 外周につながった白を背景として塗りつぶして見分ける
white = Image.fromarray(np.where(cls == 0, 255, 0).astype(np.uint8))
pad = Image.new('L', (white.width + 2, white.height + 2), 255); pad.paste(white, (1, 1))
ImageDraw.floodfill(pad, (0, 0), 128)
bgmask = np.asarray(pad)[1:-1, 1:-1] == 128

layers = [('#FFFFFF', (cls == 0) & ~bgmask)] + [(c, cls == i + 1) for i, c in enumerate(inks)]
paths = []
raster = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))   # なぞる前のくっきりした絵（アイコンの PNG を作るのに使う）
for color, mask in layers:
    if mask.sum() == 0:
        continue
    m = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S * 0.25))
    m = m.point(lambda v: 0 if v < 128 else 255)
    raster.paste(Image.new('RGBA', raster.size, color), (0, 0), m.point(lambda v: 255 - v))
    tmp = out + '.layer.png'; m.convert('RGB').save(tmp)
    vtracer.convert_image_to_svg_py(tmp, tmp + '.svg', colormode='binary', mode='spline', filter_speckle=S,
                                    corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1)
    body = open(tmp + '.svg', encoding='utf-8').read()
    for tag in re.findall(r'<path[^>]*/>', body):
        paths.append(re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{color}"', tag))
    os.remove(tmp); os.remove(tmp + '.svg')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w * S} {h * S}" width="{w}" height="{h}">\n'
       + '\n'.join(paths) + '\n</svg>\n')
open(out, 'w', encoding='utf-8').write(svg)
raster.save(out + '.raster.png')
print(out, len(svg), 'bytes', len(paths), 'paths')
