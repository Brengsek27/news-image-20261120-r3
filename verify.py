import hashlib
import json
import os
import shutil
import struct
import subprocess
from io import BytesIO
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
from zlib import crc32

from PIL import Image

from render import BRIEFS, CARDS, DATE_CHECK, REGIONS, SCALE, build_page, overlaps

ROOT = Path(__file__).resolve().parent
SIGNATURE = b'\x89PNG\r\n\x1a\n'
LIMIT = 1_048_576
SECTION_BUDGETS = {'masthead': 96, 'timeline': 34, 'regions': 22, 'leads': 156,
                   'secondary': 292, 'strip': 96, 'map_and_briefs': 280, 'footer': 58}
IEND_TRAILER = bytes.fromhex('0000000049454e44ae426082')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(57 <= len(data) <= LIMIT, f'entry.png size {len(data)} outside [57, {LIMIT}]')
    require(data[:8] == SIGNATURE, 'entry.png has a bad PNG signature')
    ihdr_len, ihdr_type, width, height = struct.unpack('>I4sII', data[8:24])
    require((ihdr_len, ihdr_type, width, height) == (13, b'IHDR', 1024, 1024),
            'entry.png IHDR is not a 13-byte 1024x1024 header')
    require(data[-12:] == IEND_TRAILER, 'entry.png does not end with the exact IEND trailer')
    image = Image.open(BytesIO(data))
    require(image.format == 'PNG' and image.size == (1024, 1024), 'Pillow rejects entry.png geometry')
    image.verify()
    image = Image.open(BytesIO(data))
    image.load()


def check_layout(layout):
    require(layout['canvas'] == [1024, 1024], 'layout canvas is not 1024x1024')
    require(layout['stories'] == 69, f"layout stories {layout['stories']} != 69")
    require(layout['illustrated_cards'] == 20, 'layout illustrated_cards != 20')

    sections = layout['sections']
    require(set(sections) == set(SECTION_BUDGETS), 'layout section keys differ from the budgets')
    cursor = 12
    for name, (start, end) in sections.items():
        require(start == cursor, f'section {name} starts at {start}, expected {cursor}')
        require(0 < end - start <= SECTION_BUDGETS[name], f'section {name} height {end - start} over budget')
        cursor = end
    require(cursor <= 1014, f'sections end at {cursor}, past 1014')

    blocks = layout['blocks']
    keys = [b['key'] for b in blocks]
    require(len(keys) == len(set(keys)), 'layout has duplicate block keys')
    by_key = {b['key']: b for b in blocks}
    require(min(b['size'] for b in blocks) == layout['minimum_font'] >= 9.5, 'minimum font mismatch')
    all_ink = []
    for block in blocks:
        x0, y0, x1, y1 = block['box']
        require(0 <= x0 < x1 <= 1024 and 0 <= y0 < y1 <= 1024, f"block {block['key']} off canvas")
        require(block['used_width'] <= (x1 - x0) + 0.25, f"block {block['key']} ink wider than its box")
        require(block['used_height'] <= (y1 - y0) + 0.25, f"block {block['key']} ink taller than its box")
        require(block['lines'] == len(block['ink']), f"block {block['key']} line/ink count mismatch")
        for ink in block['ink']:
            ix, iy, iw, ih = (v / SCALE for v in ink)
            require(ix >= x0 - 0.25 and iy >= y0 - 0.25 and ix + iw <= x1 + 0.25 and iy + ih <= y1 + 0.25,
                    f"block {block['key']} ink escapes its box")
            all_ink.append((block['key'], (ink[0], ink[1], ink[2], ink[3])))
    for (key_a, rect_a), (key_b, rect_b) in combinations(all_ink, 2):
        if key_a == key_b:
            continue
        require(not overlaps(rect_a, rect_b), f'ink overlap: {key_a} vs {key_b}')

    panels = layout['panels']
    require([p['number'] for p in panels] == list(range(1, 21)), 'panels are not numbered 1..20 in order')
    for panel_a, panel_b in combinations(panels, 2):
        require(not overlaps(panel_a['box'], panel_b['box']), 'two panels overlap')
    tops = {}
    for panel in panels:
        tops.setdefault(panel['box'][1], []).append(panel['number'])
    counts = [len(tops[top]) for top in sorted(tops)]
    require(counts == [3, 5, 4, 4, 4], f'panel grid rows {counts} != [3, 5, 4, 4, 4]')
    section_of = {}
    for n in range(1, 21):
        section_of[n] = 'leads' if n <= 3 else ('secondary' if n <= 16 else 'strip')
    for panel in panels:
        n = panel['number']
        left, top, width, height = panel['box']
        start, end = sections[section_of[n]]
        require(start <= top and top + height <= end, f'panel {n} escapes section {section_of[n]}')
        low, high = (50, 58) if n <= 3 else ((30, 38) if n <= 16 else (28, 36))
        require(low <= height <= high, f'panel {n} art height {height} outside ({low}..{high})')
        prefix = 'lead' if n <= 3 else ('card' if n <= 16 else 'strip')
        require(by_key[f'{prefix}-title-{n}']['copy'] == CARDS[n - 1][1], f'card {n} title copy mismatch')
        require(by_key[f'{prefix}-deck-{n}']['copy'] == CARDS[n - 1][2], f'card {n} deck copy mismatch')
        source_key = f'lead-source-{n}' if n <= 3 else f'art-{n}-source'
        expected = f"{CARDS[n - 1][3]}  /  {'FORECAST' if n == 15 else 'REPORTED'}"
        require(by_key[source_key]['copy'] == expected, f'card {n} source copy mismatch')
        require(by_key[f'map-pin-{n}']['copy'] == str(n), f'map pin {n} copy mismatch')

    badges = layout['map_badges']
    require(len(badges) == 20, f'map_badges {len(badges)} != 20')
    for badge_a, badge_b in combinations(badges, 2):
        require(not overlaps(tuple(badge_a), tuple(badge_b)), 'two map badges overlap')

    brief_keys = [k for k in keys if k.startswith('brief-')]
    require(len(brief_keys) == 49, f'brief blocks {len(brief_keys)} != 49')
    sec_top, sec_bottom = sections['map_and_briefs']
    for number, copy in enumerate(BRIEFS, start=21):
        block = by_key[f'brief-{number}']
        require(block['copy'] == f'{number} {copy}', f'brief {number} copy mismatch')
        require(block['lines'] <= 2, f'brief {number} wraps past two lines')
        require(sec_top <= block['box'][1] and block['box'][3] <= sec_bottom, f'brief {number} escapes its section')

    numbers = sorted(n for _, _, group in REGIONS for n in group)
    require(numbers == list(range(1, 70)), 'REGIONS do not cover stories 1..69 exactly')
    require(by_key['date-check']['copy'] == DATE_CHECK, 'date-check copy mismatch')
    rows = layout['secondary_rows']
    require(sum(rows) == sections['secondary'][1] - sections['secondary'][0], 'secondary rows do not sum to the section')
    require(all(88 <= row <= 106 for row in rows), 'a secondary row is outside 88..106')
    print(f"PASS layout: 69 stories, 20 panels, {len(blocks)} blocks, sections within budget")


def run_copier(cwd, output_dir, script=None):
    env = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(output_dir))
    return subprocess.run(['node', str(script or (ROOT / 'main.ts'))],
                          cwd=cwd, env=env, capture_output=True, text=True, timeout=120)


def verify():
    entry = (ROOT / 'entry.png').read_bytes()
    validate(entry)
    digest = hashlib.sha256(entry).hexdigest()
    print(f'PASS entry.png: {len(entry)} bytes, sha256 {digest}')

    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        first, second = tmp / 'first', tmp / 'second'
        build_page(first)
        build_page(second)
        png_a, png_b = (first / 'entry.png').read_bytes(), (second / 'entry.png').read_bytes()
        json_a, json_b = (first / 'layout.json').read_bytes(), (second / 'layout.json').read_bytes()
        require(png_a == png_b == entry, 'rebuilt entry.png differs from the committed file')
        require(json_a == json_b, 'rebuilt layout.json is not deterministic')
        print('PASS determinism: two rebuilds are byte-identical to the committed entry.png')
        layout = json.loads(json_a.decode('utf-8'))

    check_layout(layout)

    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for attempt in (1, 2):
            out = tmp / f'out{attempt}'
            result = run_copier(tmp, out)
            require(result.returncode == 0, f'copier run {attempt} failed: {result.stderr.strip()}')
            require((out / 'entry.png').read_bytes() == entry, f'copier run {attempt} output differs')
        print('PASS copier: main.ts reproduces entry.png from a foreign cwd, twice')

    variants = {}

    def variant(name, mutate):
        data = bytearray(entry)
        mutate(data)
        variants[name] = bytes(data)

    variant('bad signature byte', lambda d: d.__setitem__(0, d[0] ^ 0xFF))
    variant('IHDR tag replaced', lambda d: d.__setitem__(slice(12, 16), b'IDAT'))
    variant('width 1023', lambda d: d.__setitem__(slice(16, 20), struct.pack('>I', 1023)))

    def flip_depth(d):
        d[24] = 4
        d[29:33] = struct.pack('>I', crc32(bytes(d[12:29])) & 0xFFFFFFFF)
    variant('bit depth invalid for colour type, CRC fixed', flip_depth)
    variant('one CRC byte flipped', lambda d: d.__setitem__(29, d[29] ^ 0x01))
    variants['truncated to 18 bytes'] = entry[:18]
    variants['missing IEND'] = entry[:-12]
    variants['oversize padding'] = entry + bytes(LIMIT)

    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name, data in variants.items():
            fixture = tmp / 'fixture'
            if fixture.exists():
                shutil.rmtree(fixture)
            fixture.mkdir()
            shutil.copy(ROOT / 'main.ts', fixture / 'main.ts')
            (fixture / 'entry.png').write_bytes(data)
            out = fixture / 'out'
            result = run_copier(fixture, out, script=fixture / 'main.ts')
            require(result.returncode != 0, f'fixture {name}: copier unexpectedly succeeded')
            require('Error:' in result.stderr, f'fixture {name}: no Error: in stderr')
            require(not out.exists(), f'fixture {name}: copier created an output directory')
            print(f'PASS fixture: {name}')


if __name__ == '__main__':
    verify()
    print('ALL CHECKS PASSED')
