"""サイトに置いた画像に、位置情報などの撮影情報（EXIF・XMP）が残っていないかを調べる（2026-11-14）。

    python3 -I scripts/check_exif.py [フォルダ …]   # 省略時は src/content と public

残っていたらファイル名を出して終了コード 1 で止まる。PR の検査（check.yml）と公開（deploy.yml）の前に動かす
（オシャベはフォームからの PR を作る auto-pr.yml でも）。写真は置く前に撮影情報を落とす決まりだが（オシャベは scripts/prep_photos.py）、
それを通さずに置かれた写真を見逃さないための見張り。Pillow を使わず、ファイルの中身を直接読む。
もう1つのサイトと中身をそろえている（README の「もう1つのサイトと共通のファイル」）。

- JPEG: APP1 の「Exif」と XMP
- PNG: eXIf・zTXt / tEXt / iTXt の撮影情報
- WebP: EXIF・XMP のチャンク
- HEIC / HEIF / TIFF はサイトに置かない形式なので、それだけで止める
"""
import os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = sys.argv[1:] or [os.path.join(ROOT, 'src', 'content'), os.path.join(ROOT, 'public')]
NG_EXT = {'.heic', '.heif', '.tif', '.tiff'}
GPS_WORDS = (b'GPSLatitude', b'GPSLongitude', b'exif:GPS')


def jpeg(data):
    found = []
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker = data[i + 1]
        if marker == 0xD9 or marker == 0xDA:   # 画像の終わり・本体の始まりより後には撮影情報は無い
            break
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:
            i += 2
            continue
        size = struct.unpack('>H', data[i + 2:i + 4])[0]
        body = data[i + 4:i + 2 + size]
        if marker == 0xE1 and body.startswith(b'Exif\0'):
            found.append('EXIF')
        if marker == 0xE1 and body.startswith(b'http://ns.adobe.com/xap/') and any(w in body for w in GPS_WORDS):
            found.append('XMP の位置情報')
        i += 2 + size
    return found


def png(data):
    found = []
    i = 8
    while i + 8 <= len(data):
        size, kind = struct.unpack('>I4s', data[i:i + 8])
        body = data[i + 8:i + 8 + size]
        if kind == b'eXIf':
            found.append('EXIF')
        if kind in (b'tEXt', b'zTXt', b'iTXt') and (body.startswith(b'Raw profile type exif') or any(w in body for w in GPS_WORDS)):
            found.append('撮影情報のテキスト')
        if kind == b'IEND':
            break
        i += 12 + size
    return found


def webp(data):
    found = []
    i = 12
    while i + 8 <= len(data):
        kind, size = struct.unpack('<4sI', data[i:i + 8])
        if kind == b'EXIF':
            found.append('EXIF')
        if kind == b'XMP ' and any(w in data[i + 8:i + 8 + size] for w in GPS_WORDS):
            found.append('XMP の位置情報')
        i += 8 + size + (size & 1)
    return found


bad = []
count = 0
for top in DIRS:
    for d, _, files in os.walk(top):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            p = os.path.join(d, f)
            if ext in NG_EXT:
                bad.append((p, 'サイトに置かない形式'))
                continue
            if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
                continue
            count += 1
            data = open(p, 'rb').read()
            if data[:2] == b'\xff\xd8':
                found = jpeg(data)
            elif data[:8] == b'\x89PNG\r\n\x1a\n':
                found = png(data)
            elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
                found = webp(data)
            else:
                found = []
            if found:
                bad.append((p, '・'.join(dict.fromkeys(found))))

for p, why in bad:
    print(f'{os.path.relpath(p, ROOT)}: {why}')
print(f'画像 {count} 枚を調べ、撮影情報が残っていたのは {len(bad)} 枚')
if bad:
    print('撮影情報を落としてから置き直す（位置情報は公開リポジトリの履歴に残るので、push 前に直す）')
    sys.exit(1)
