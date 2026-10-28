"""スマホで撮った写真を、新しい記事の画像として src/content/images/ に置ける形にする。

    python -I scripts/prep_photos.py <写真のフォルダ> [--date 2026-10-28] [--sheet 一覧.jpg]

- JPEG・PNG・HEIC（iPhone の既定）を読む。HEIC には pillow-heif が要る（pip install pillow-heif）
- 撮った日時（EXIF）の順に並べ、yyyy-mm-dd-01.jpg からの連番で書き出す。日付は --date、無ければ一番早く撮った日
- 向きを直し（スマホの縦横の情報）、長辺 1600px に縮め、EXIF を全部落として保存する（位置情報を残さない）
- 同じ日付の画像がすでにあれば、その続きの番号から振る。元の写真は動かさない
- --sheet を付けると、番号入りの縮小一覧（コンタクトシート）を1枚書き出す。写真を1枚ずつ開く前の下見に使う
- 元の名前・撮った日時・新しい名前・位置情報の有無を表で出す。記事に書くのは新しい名前
"""
import argparse, datetime, os, sys

from PIL import Image, ImageDraw, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, 'src', 'content', 'images')
EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
LONG_SIDE = 1600
EXIF_DATETIME_ORIGINAL = 0x9003
EXIF_IFD = 0x8769
GPS_IFD = 0x8825


def taken_at(img, path):
    exif = img.getexif()
    raw = exif.get_ifd(EXIF_IFD).get(EXIF_DATETIME_ORIGINAL) or exif.get(0x0132)
    if raw:
        try:
            return datetime.datetime.strptime(str(raw).strip('\x00'), '%Y:%m:%d %H:%M:%S'), True
        except ValueError:
            pass
    # スクショや書き出した写真は EXIF が無い。ファイルの更新日時で代える
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)), False


def has_gps(img):
    return bool(img.getexif().get_ifd(GPS_IFD))


def next_number(date):
    os.makedirs(IMAGES, exist_ok=True)
    used = [f for f in os.listdir(IMAGES) if f.startswith(date + '-')]
    nums = [int(f[len(date) + 1:].split('.')[0]) for f in used if f[len(date) + 1:].split('.')[0].isdigit()]
    return max(nums, default=0) + 1


def contact_sheet(items, out, cols=5, cell=300):
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell, rows * (cell + 24)), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(items):
        thumb = img.copy()
        thumb.thumbnail((cell - 8, cell - 8))
        x, y = (i % cols) * cell, (i // cols) * (cell + 24)
        sheet.paste(thumb, (x + 4, y + 4))
        draw.text((x + 6, y + cell + 4), name, fill='black')
    sheet.save(out, quality=80)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--date', help='画像の名前に使う日付（yyyy-mm-dd）。記事の公開日に合わせる')
    ap.add_argument('--sheet', help='番号入りの縮小一覧を書き出す先（.jpg）')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    files = sorted(os.path.join(a.src, f) for f in os.listdir(a.src) if os.path.splitext(f)[1].lower() in EXTS)
    if not files:
        sys.exit(f'写真が見つからない: {a.src}')
    if pillow_heif is None and any(f.lower().endswith(('.heic', '.heif')) for f in files):
        sys.exit('HEIC を読むには pip install pillow-heif が要る')

    shots = []
    for f in files:
        img = Image.open(f)
        when, from_exif = taken_at(img, f)
        shots.append((when, from_exif, has_gps(img), f, img))
    shots.sort(key=lambda s: s[0])

    date = a.date or shots[0][0].strftime('%Y-%m-%d')
    n = next_number(date)
    done = []
    print('新しい名前\t元の名前\t撮った日時\t位置情報')
    for when, from_exif, gps, f, img in shots:
        img = ImageOps.exif_transpose(img).convert('RGB')
        img.thumbnail((LONG_SIDE, LONG_SIDE))
        name = f'{date}-{n:02d}.jpg'
        # exif を渡さないので、位置情報も撮影機種も残らない
        img.save(os.path.join(IMAGES, name), quality=85, optimize=True)
        stamp = when.strftime('%Y-%m-%d %H:%M') + ('' if from_exif else '（更新日時）')
        print(f'{name}\t{os.path.basename(f)}\t{stamp}\t{"あり→消した" if gps else "なし"}')
        done.append((name, img))
        n += 1

    if a.sheet:
        contact_sheet(done, a.sheet)
        print(f'一覧: {a.sheet}')


if __name__ == '__main__':
    main()
