#!/usr/bin/env python3
"""Render the Friday 20 November 2026 news poster (1024x1024 PNG)."""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
SCALE = 2
PAPER = '#f3ecde'
INK = '#242321'
RED = '#71333a'
RULE = '#bca879'
NAVY = '#121c2a'
GOLD = '#d9b568'
PANEL = '#fffaf0'
WHITE = '#f8f1e2'
ART_INSET = 2
ART_DRAW_INSET = 6
FONTS = {
    'head': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
    'head-bold': '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    'body': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    'compact': '/usr/share/fonts/truetype/noto/NotoSansDisplay-Condensed.ttf',
    'italic': '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
    'label': '/usr/share/fonts/truetype/noto/NotoSansDisplay-CondensedBold.ttf',
}
def font(face, size):
    if size < 9.5: raise ValueError('Refusing text below 9.5px')
    return ImageFont.truetype(FONTS[face], round(size*SCALE))
def scaled(box):  # returns tuple of round(v*SCALE) for v in box
    return tuple(round(value * SCALE) for value in box)

def overlaps(first, second):  # strict AABB overlap test on (x, y, w, h) boxes
    fx, fy, fw, fh = first
    sx, sy, sw, sh = second
    return fx < sx + sw and sx < fx + fw and fy < sy + sh and sy < fy + fh

CARDS = [
    ("ODISHA · STORM", "Akvan comes ashore", "Cyclone Akvan crosses the coast by noon near Gopalpur, winds 90-100 km/h gusting to 110. 300,000 people are out of harm's way, 423 rescue teams deployed, red alerts in 11 districts.", "IMD"),
    ("WASHINGTON · IRAN", "Trump puts the Iran decision off to 2027", "Trump says no rush on Iran: he'll 'see what happens' after 1 January. Senate rejects a war-powers curb 51-48.", "Reuters"),
    ("RIYADH · ATTACK", "A missile over Riyadh", "A Houthi missile damages the KAFD tower, one of Riyadh's tallest, in the financial district. No casualties are reported as air defences answer the strike.", "Reuters"),
    ("THE HAGUE · LAW", "The world answers the genocide verdict", "Britain expels Myanmar's defence attaché; Gambia seeks reparations.", "BBC · AP"),
    ("ANTALYA · CLIMATE", "COP31's final day: fossil fuels cut from the draft", "Draft drops the phase-out pledge; plenary runs past the deadline. 23 nations back a wildfire plan.", "UN News"),
    ("NEW YORK · MARKETS", "Anthropic's debut can't stop the slide", "Dow down 1,101 points, S&P 2.02%, Nasdaq 2.25%. Anthropic opens at $111.50, closes at $97.17.", "Bloomberg"),
    ("SHENZHEN · DIPLOMACY", "After the summit: '12 out of 10'", "Trump rates three-way summit 12/10. Europe wary of carve-up; Putin may attend December G20 in Miami.", "AP"),
    ("SPACE · SCIENCE", "Voyager 1 crosses one light-day", "NASA puts Voyager 1 over one light-day from Earth: 16 billion miles, a human-made record.", "NASA"),
    ("VICE CITY · GAMES", "GTA VI passes $1.84bn", "Day-one sales beat The Odyssey's $1.80bn global run; reviews land and streams set records.", "Sensor Tower"),
    ("KYIV · WAR", "Europe ready to talk to Russia", "European leaders say they're ready for talks to end the war in Ukraine, BBC reports.", "BBC"),
    ("WELLINGTON · CRICKET", "Day two at the Basin: records fall", "Glenn Phillips (118) is the first New Zealander with centuries in all three formats vs India in a year.", "ICC · AP"),
    ("TOKYO · SPACE", "Hayabusa2 gives up its landing", "Engine trouble ends the planned asteroid landing; Japan rewrites the mission.", "JAXA"),
    ("SEOUL · LAW", "South Korea clears ex-PM Han", "Supreme Court overturns ex-PM Han Duck-soo's conviction in case tied to the 2024 martial-law declaration.", "Yonhap"),
    ("KYIV · WAR", "Russia fires ~30 ballistic missiles at Kyiv", "Seven waves hit energy and transport sites.", "Kyiv Post · Reuters"),
    ("MERCURY · SPACE", "BepiColombo knocks on Mercury's door", "Final approach after 8 years and 6bn miles; ESA-JAXA's orbit burn is Saturday.", "ESA · BBC"),
    ("BARCELONA · HEALTH", "Cancer pill shrinks pancreatic tumours", "Early trial: daraxonrasib plus chemotherapy shrinks tumours in 60.7% of patients.", "Reuters"),
    ("LAS VEGAS · FORMULA 1", "Russell rules the Strip's only dry hour", "Russell tops final practice in 1:34.041; his Turn 14 clash with Verstappen goes to the stewards.", "Reuters"),
    ("TURIN · TENNIS", "Medvedev takes the last semi-final place", "Medvedev beats Tiafoe 6-3, 6-4 to take the last semi-final place; Zverev awaits.", "ATP Tour"),
    ("CLEVELAND · NBA", "Harden's 51 makes history", "Harden scores 51 — his 26th career 50-point game — as Cleveland beat Indiana 128-119.", "Reuters"),
    ("LONDON · MUSIC", "New Music Friday: Take That's tenth", "Take That's tenth album 'Dreamers' lands with Rockstar's 34-track GTA VI album.", "Official Charts"),
]
BRIEFS = [
    "SUVA — Fiji declares drought and water shortages a national disaster.",
    "CRIMEA — Ukrainian strike on Crimean Bridge disrupts rail.",
    "CARACAS — US, Venezuela sign deal restoring military cooperation.",
    "CANBERRA — Australia sanctions Israeli settlers over West Bank expansion.",
    "SOFIA — Sunken LPG tanker was hit by projectiles, an official says.",
    "TOKYO — PM Takaichi urges more talks with China to ease tensions.",
    "FLORIDA — St. Johns River hits 38.3 ft; 100-plus rescued in Broward County.",
    "MIAMI — Vice City jersey sells out in 90 minutes. [FORECAST]",
    "ZURICH — Infantino faces two challengers in the 2027 FIFA presidential race.",
    "SEOUL — Korea's National Museum draws record crowds ahead of the year-end.",
    "JAMNAGAR — Indian Air Force opens exercise Setu 2026.",
    "DUBAI — Indian shooter wins Dubai Open bronze.",
    "MUMBAI — RBI steps in to steady rupee amid foreign outflows.",
    "LOS ANGELES — GTA VI reviews land; Rockstar claims a record.",
    "CALIFORNIA — Pacific storm brings snow to Sierra.",
    "SINGAPORE — Bitcoin steadies above $93,000 after the IPO drives crypto cash.",
    "NEW DELHI — Modi meets the Prince and Princess of Wales in Delhi.",
    "KHARTOUM — Sudan's army says it has broken the two-year siege of El Obeid.",
    "CHAKWAL — Train services restored after an accident in Pakistan.",
    "BEIJING — Xi urges APEC economies to open trade and new technology.",
    "BRUSSELS — EU Commission hit by cyberattack, Politico reports.",
    "WASHINGTON — Trump aide floated ceding Guyanese land to Venezuela. [CLAIM]",
    "AUSTIN — Musk: \"I'm not MAGA\"; regrets ~$500m spent on midterms. [CLAIM]",
    "SHENZHEN — APEC leaders meet in Shenzhen; trade and the Iran war on the agenda.",
    "WORLDWIDE — World Children's Day marked around the globe.",
    "BRUSSELS — Second EU-UK summit opens in Brussels. [Consilium]",
    "BERLIN — Kushner: Europe united on Ukraine; envoys brief Moscow.",
    "MANILA — ASEAN+3 adopt maritime, food and energy pacts.",
    "MANILA — Philippine industry urges a reciprocal US trade deal. [Context.ph]",
    "MANILA — PAL seals Boeing-GE deal for 15 Dreamliners. [Context.ph]",
    "LONDON — Gold down 2.7% to $3,625, a more-than-one-year low. [MarketIndex]",
    "SYDNEY — Asian stocks extend losses toward a three-year record.",
    "CANBERRA — Australia sheds 43,600 jobs in Oct.; jobless 4.9%.",
    "CHICAGO — Fed's Goolsbee leaves a bigger December rate rise open. [MarketIndex]",
    "SACRAMENTO — Nvidia faces inquiry over chips reaching China.",
    "HORMUZ — Four ship attacks in 96 hours, a maritime centre says. [UKMTO]",
    "TONGA — Pacific kingdom declares an emergency as El Niño drought bites. [RNZ]",
    "BOUGAINVILLE — Rio Tinto pledges $370m for the Panguna mine fleet. [Reuters]",
    "COPENHAGEN — Danish MPs pass a Greenland defence bill. [AFP]",
    "JAKARTA — Indonesian MPs pass an asset-forfeiture bill. [Reuters]",
    "NEW DELHI — Sensex surges ~1,000 points to 83,021; Goldman upgrades India.",
    "MUNICH — Bayern held 1-1 by Köln: Moore 12', Brown 37'; Kane goes off injured.",
    "TALLINN — Estonia shuts its border with Russia from 1 December.",
    "WASHINGTON — IMF: world debt nears 100% of GDP, a post-war high.",
    "WARSAW — Russian missiles violate Polish airspace; NATO jets scramble.",
    "PORT-AU-PRINCE — Police kill 34 gang suspects, retake the Martissant corridor.",
    "TURIN — Alcaraz completes a perfect group stage, beating Cobolli 6-4, 6-1. [ATP]",
    "OKLAHOMA CITY — SGA scores 40 in a comeback win over New Orleans, 126-120.",
    "DENVER — Nuggets edge Rockets 133-124 in a game with 32 lead changes.",
]

REGIONS = [
    ("EUROPE", "#a44852", [4, 5, 10, 14, 16, 18, 20, 22, 25, 29, 41, 46, 47, 51, 59, 62, 63, 65, 67]),
    ("THE AMERICAS", "#31517d", [2, 6, 9, 17, 19, 23, 27, 28, 34, 35, 42, 43, 54, 55, 66, 68, 69]),
    ("ASIA-PACIFIC", "#2d6a4f", [1, 7, 12, 13, 26, 30, 31, 33, 36, 37, 39, 40, 44, 48, 49, 50, 52, 53, 60, 61]),
    ("MIDEAST", "#b07d2b", [3, 32, 56]),
    ("AFRICA", "#8a5a2b", [38]),
    ("OCEANIA", "#5b7f95", [11, 21, 24, 57, 58]),
    ("WORLD", "#6d597a", [8, 15, 45, 64]),
]

COLORS = {}
for _region_name, _region_colour, _region_numbers in REGIONS:
    for _story_number in _region_numbers:
        COLORS[_story_number] = _region_colour

DATE_CHECK = "The Shenzhen summit's first meeting · the ICJ's genocide verdict itself · GTA VI's midnight launch in New Zealand · Anthropic's record IPO debut · Henry Nicholls' 113 not out on day one · the first COP31 draft · a US court's summonses for Doval and Goel · the Philippines-Chile trade deal, signed Thursday · US jobless claims at 203,000, released Thursday · a Sensex 700-point rise, Thursday's close · Kenya's last Ebola patient going home, 11 November."

# ==== layout engine and scenes are appended below in later build stages ====
class Page:
    def __init__(self):
        # Create a new canvas image
        self.image = Image.new('RGB', (1024 * SCALE, 1024 * SCALE), PAPER)
        self.ink = ImageDraw.Draw(self.image)
        self.blocks = []
        self.panels = []
        self.art_elements = []

    def rect(self, box, color):
        """Draw a filled rectangle using scaled coordinates."""
        self.ink.rectangle(scaled(box), fill=color)

    def line(self, points, color, width=1):
        """Draw a polyline. Width is scaled and at least 1 pixel."""
        pw = max(1, round(width * SCALE))
        self.ink.line([scaled(p) for p in points], fill=color, width=pw)

    def polygon(self, points, fill):
        """Draw a filled polygon through scaled points."""
        self.ink.polygon([scaled(p) for p in points], fill=fill)

    def card_surface(self, box):
        """Draw a soft drop‑shadow and then fill the box with PANEL colour.
        The shadow is an RGBA layer with a slight offset and Gaussian blur.
        """
        # Create a temporary RGBA overlay for the shadow
        overlay = Image.new('RGBA', self.image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        # shadow rectangle (offset by 1 pixel down/right)
        shadow_box = tuple(v + SCALE for v in scaled(box))
        shadow_color = (30, 27, 22, 92)
        overlay_draw.rectangle(shadow_box, fill=shadow_color)
        # blur the shadow
        blurred = overlay.filter(ImageFilter.GaussianBlur(radius=2))
        # composite shadow onto the base image
        self.image = Image.alpha_composite(self.image.convert('RGBA'), blurred).convert('RGB')
        self.ink = ImageDraw.Draw(self.image)
        # draw the actual panel rectangle
        self.ink.rectangle(scaled(box), fill=PANEL)

    def card_outline(self, box):
        """Draw a rectangle outline around a card using INK colour."""
        self.ink.rectangle(scaled(box), outline=INK, width=SCALE)

    def gradient(self, box, start, end):
        left, top, right, bottom = box
        first = tuple(bytes.fromhex(start.lstrip('#')))
        last = tuple(bytes.fromhex(end.lstrip('#')))
        pixel_left = round(left*SCALE)
        pixel_top = round(top*SCALE)
        pixel_right = round(right*SCALE)
        pixel_height = round((bottom-top)*SCALE)
        steps = 96
        for row in range(pixel_height):
            mix = round((row/max(1, pixel_height-1))**0.82*steps)/steps
            color = tuple(round(a*(1-mix)+b*mix) for a, b in zip(first, last))
            self.ink.line((pixel_left, pixel_top+row, pixel_right-1, pixel_top+row), fill=color)

    def text(self, key, copy, box, face, size, leading, color=INK, align='left', max_lines=None):
        """Render wrapped text inside *box*.
        Returns the used height in SCALE units.
        """
        # Validate box dimensions
        if box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError('Box must have positive width and height')
        # simple off‑canvas check (assuming canvas is 1024*SCALE square)
        canvas_w = 1024 * SCALE
        canvas_h = 1024 * SCALE
        if box[0] < 0 or box[1] < 0 or box[2] > canvas_w or box[3] > canvas_h:
            raise ValueError('Box lies outside the canvas')

        # Load the font
        fnt = font(face, size)
        # Prepare wrapping
        paragraphs = copy.split('\n')
        lines = []
        box_w_px = (box[2] - box[0]) * SCALE
        for para in paragraphs:
            words = para.split()
            if not words:
                lines.append('')
                continue
            cur_line = words[0]
            for w in words[1:]:
                test_line = cur_line + ' ' + w
                bbox = fnt.getbbox(test_line, anchor='ls')
                line_width = bbox[2] - bbox[0]
                if line_width <= box_w_px:
                    cur_line = test_line
                else:
                    # line full, start new line
                    lines.append(cur_line)
                    cur_line = w
            lines.append(cur_line)
        # enforce max_lines
        if max_lines is not None and len(lines) > max_lines:
            raise ValueError('Exceeded maximum number of lines')

        # Draw each line and collect ink metrics
        used_height_px = 0
        ink_metrics = []
        baseline_y = 0
        first_top = None
        last_bottom = 0
        for idx, line in enumerate(lines):
            bbox = fnt.getbbox(line, anchor='ls')
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
            # alignment offset
            spare = box_w_px - line_w
            if align == 'center':
                align_offset = spare // 2
            elif align == 'right':
                align_offset = spare
            else:
                align_offset = 0
            # compute drawing position (left, baseline)
            x = (box[0] * SCALE) + align_offset - bbox[0]
            if idx == 0:
                baseline_y = -bbox[1]
            else:
                # advance baseline respecting leading and previous line descent
                prev_bbox = fnt.getbbox(lines[idx - 1], anchor='ls')
                prev_bottom = prev_bbox[3]
                cur_top = bbox[1]
                delta = max(round(leading * SCALE), prev_bottom - cur_top)
                baseline_y += delta
            y = (box[1] * SCALE) + baseline_y
            self.ink.text((x, y), line, font=fnt, fill=color, anchor='ls')
            ink_metrics.append((x, y + bbox[1], line_w, line_h))
            if first_top is None:
                first_top = y + bbox[1]
            last_bottom = y + bbox[3]
            used_height_px = last_bottom - first_top

        used_width_px = max(fnt.getbbox(l, anchor='ls')[2] - fnt.getbbox(l, anchor='ls')[0] for l in lines) if lines else 0
        # store block metadata
        self.blocks.append({
            'key': key,
            'box': box,
            'size': size,
            'lines': len(lines),
            'used_width': used_width_px / SCALE,
            'used_height': used_height_px / SCALE,
            'ink': ink_metrics,
            'copy': copy,
        })
        return used_height_px / SCALE

    def check_layout(self):
        """Validate panels and art elements against the layout rules."""
        # Panel off‑canvas or overlap checks
        for i, panel in enumerate(self.panels):
            left, top, right, bottom = panel['box']
            # off‑canvas
            if left < 0 or top < 0 or right > 1024 * SCALE or bottom > 1024 * SCALE:
                raise ValueError('Panel off canvas')
            # inset check
            if panel.get('art_inset', 0) < ART_INSET:
                raise ValueError('Panel art inset too small')
            # overlap with other panels
            for j, other in enumerate(self.panels):
                if i == j:
                    continue
                if overlaps(panel['box'], other['box']):
                    raise ValueError('Panels overlap')
        # Art element containment
        for art in self.art_elements:
            panel_idx = art.get('panel')
            if panel_idx is None:
                continue
            panel_box = self.panels[panel_idx]['box']
            inset_box = (
                panel_box[0] + ART_INSET,
                panel_box[1] + ART_INSET,
                panel_box[2] - ART_INSET,
                panel_box[3] - ART_INSET,
            )
            if not overlaps(art['box'], inset_box) and not (
                art['box'][0] >= inset_box[0] and art['box'][1] >= inset_box[1] and
                art['box'][2] <= inset_box[2] and art['box'][3] <= inset_box[3]
            ):
                raise ValueError('Art element escapes its panel')
        # Ink overlap checks (simplified – only block‑to‑block)
        for i, b1 in enumerate(self.blocks):
            for j, b2 in enumerate(self.blocks):
                if i >= j:
                    continue
                # Skip allowed art‑inside‑panel blocks
                if b1['key'].startswith(f"art-{i}-") and b2['key'].startswith(f"art-{i}-"):
                    continue
                for ink1 in b1['ink']:
                    x1, y1, w1, h1 = ink1
                    rect1 = (x1, y1, w1, h1)
                    for ink2 in b2['ink']:
                        x2, y2, w2, h2 = ink2
                        rect2 = (x2, y2, w2, h2)
                        if overlaps(rect1, rect2):
                            raise ValueError('Ink overlap detected')
# --- Illustration engine core ---

# Palette list of 20 dark/mid hex color pairs
PALETTES = [
    ('#102b3d', '#638b84'), ('#25243a', '#9c5849'), ('#10182c', '#52526a'),
    ('#252436', '#9a6957'), ('#372329', '#cd8d53'), ('#201a31', '#754451'),
    ('#142d39', '#668d7c'), ('#11182b', '#3a4963'), ('#38213a', '#bf795f'),
    ('#17233d', '#485a70'), ('#173c37', '#799369'), ('#151d31', '#5e5a68'),
    ('#302323', '#ae8365'), ('#121a30', '#57465a'), ('#151d35', '#625b69'),
    ('#392a3e', '#b47b70'), ('#0d1526', '#7a4a56'), ('#14301f', '#7d9b6a'),
    ('#2b1a10', '#c07f3e'), ('#1d1030', '#8a5f9e')
]

class _Art:
    """Drawing context for a single card art panel (300x100 virtual space)."""
    def __init__(self, page, number, left, top, width, height):
        self.page = page
        self.number = number
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.rng = random.Random(600 + number)

    # scale a virtual point into actual canvas coordinates
    def point(self, x, y):
        return (
            self.left + ART_DRAW_INSET + x * (self.width - 2 * ART_DRAW_INSET) / 300,
            self.top + ART_DRAW_INSET + y * (self.height - 2 * ART_DRAW_INSET) / 100,
        )

    def _footprint(self, box, stroke=0):
        x0, y0, w, h = box
        pad = stroke / 2 + 0.5
        self.page.art_elements.append({
            'number': self.number,
            'box': (x0 - pad, y0 - pad, w + 2 * pad, h + 2 * pad),
        })

    def box(self, x, y, r, b):
        return (*self.point(x, y), *self.point(r, b))

    def rect(self, x, y, r, b, fill):
        self.page.rect(self.box(x, y, r, b), fill)
        self._footprint(self.box(x, y, r, b), stroke=0)

    def poly(self, points, fill):
        pts = [self.point(*p) for p in points]
        self.page.polygon(pts, fill=fill)
        xs, ys = zip(*pts)
        self._footprint((min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)), stroke=0)

    def line(self, points, fill, weight=1):
        pts = [self.point(*p) for p in points]
        width = weight * self.width / 300
        self.page.line(pts, fill, width)
        xs, ys = zip(*pts)
        self._footprint((min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)), stroke=width)

    def oval(self, x, y, r, b, fill=None, outline=None):
        box = self.box(x, y, r, b)
        self.page.ink.ellipse(scaled(box), fill=fill, outline=outline, width=SCALE)
        self._footprint(box, stroke=1)

    def soft_oval(self, x, y, r, b, blur=1.2, alpha=100):
        art_box = self.box(x, y, r, b)
        pixel_box = scaled(art_box)
        radius = blur * SCALE
        padding = math.ceil(radius * 3)
        shadow = Image.new('RGBA', (pixel_box[2] - pixel_box[0] + 2 * padding,
                                    pixel_box[3] - pixel_box[1] + 2 * padding), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((padding, padding,
                                        padding + pixel_box[2] - pixel_box[0],
                                        padding + pixel_box[3] - pixel_box[1]),
                                       fill=(12, 17, 18, alpha))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
        self.page.image.paste(shadow, (pixel_box[0] - padding, pixel_box[1] - padding), shadow)
        self.page.ink = ImageDraw.Draw(self.page.image)
        self.page.art_elements.append({'number': self.number,
                                       'box': (art_box[0] - padding / SCALE, art_box[1] - padding / SCALE,
                                               art_box[2] - art_box[0] + 2 * padding / SCALE,
                                               art_box[3] - art_box[1] + 2 * padding / SCALE)})

    def label(self, text, x, y, span, size=9.5, color=WHITE, face='label', align='left'):
        key = f'art-{self.number}-label-{x}-{y}-' + text[:8]
        x0, y0 = self.point(x, y)
        width = span * (self.width - 2 * ART_INSET) / 300
        box = (x0, y0, x0 + width, y0 + size + 4)
        self.page.text(key, text, box, face, size, size, color, align)

    def gradient(self, x, y, span, rise, start, end):
        self.page.gradient(self.box(x, y, x + span, y + rise), start, end)
        self._footprint(self.box(x, y, x + span, y + rise), stroke=0)

    def star(self, x, y, radius, fill):
        points = []
        for i in range(10):
            ang = i * math.tau / 10
            r = radius if i % 2 == 0 else radius * 0.4
            points.append((x + r * math.cos(ang), y + r * math.sin(ang)))
        self.poly(points, fill)

    def city(self, horizon, dark, light, min_height=8, max_height=36):
        x = 0
        while x < 300:
            w = self.rng.randint(8, 21)
            h = self.rng.randint(min_height, max_height)
            self.rect(x, horizon - h, x + w, horizon, dark)
            # add sparse lit windows
            for wx in range(x + 1, x + w - 1, 4):
                for wy in range(horizon - h + 2, horizon - 2, 6):
                    if self.rng.random() < 0.2:
                        self.rect(wx, wy, wx + 2, wy + 3, light)
            x += w + self.rng.randint(1, 4)

    def probe(self, x, y, wings=True):
        if wings:
            for side in (-1, 1):
                origin = x + side * 23
                self.rect(origin - 17, y - 5, origin + 17, y + 5, '#658da9')
                for rung in range(-15, 17, 6):
                    self.line([(origin + rung, y - 5), (origin + rung, y + 5)], '#c7d6d9')
                self.line([(origin - 17, y), (origin + 17, y)], '#c7d6d9')
        self.line([(x, y), (x + 24, y - 14)], GOLD, 2)
        self.rect(x - 8, y - 7, x + 8, y + 7, GOLD)
        self.oval(x - 12, y - 15, x + 12, y - 6, WHITE)
        self.line([(x, y - 10), (x + 6, y - 21)], WHITE, 2)

    def courthouse(self, x, y):
        self.poly([(x - 70, y + 15), (x, y - 12), (x + 70, y + 15)], '#dfc2a1')
        self.rect(x - 69, y + 16, x + 69, y + 20, WHITE)
        for pillar in range(-56, 61, 22):
            self.rect(x + pillar, y + 22, x + pillar + 9, y + 58, '#ead3bc')
            self.line([(x + pillar + 3, y + 24), (x + pillar + 3, y + 56)], '#a88883')
        for step in range(3):
            self.rect(x - 64 - step * 5, y + 55 + step * 3, x + 64 + step * 5, y + 57 + step * 3, '#d7ac92')

# Dispatcher and scene registry
SCENES = {}

def illustration(page, number, left, top, width, height):
    page.panels.append({
        'number': number,
        'box': (left, top, width, height),
        'art_inset': ART_INSET,
    })
    page.gradient((left, top, left + width, top + height), *PALETTES[number - 1])
    art = _Art(page, number, left, top, width, height)
    SCENES[number](art)
    if number <= 3:
        art.rect(10, 8, 181 if number == 2 else 126, 27, '#252639')
        label_texts = ('LANDFALL · NOON', 'NOT BEFORE JANUARY', 'KAFD · ~14:00 UTC')
        art.label(label_texts[number - 1], 16, 13, 156 if number == 2 else 107)
    else:
        art.rect(0, 0, 34, 29, '#222b3d')
        art.label(f'{number:02d}', 4, 5, 26, 9.5, WHITE, 'label', 'center')

# --- Scene definitions ---

def _scene_1(art):
    # coastline polygon
    coast_poly = [(0,0),(179,0),(167,10),(163,21),(143,27),(138,40),(112,53),(108,61),(91,64),(80,77),(62,83),(52,100),(0,100)]
    art.poly(coast_poly, '#849b79')
    # gold edge line
    art.line([(0,0),(179,0)], '#ffd700')
    # grid lines
    for y in range(0, 101, 8):
        art.line([(0, y), (298, y)], '#008080', weight=0.3)
    for x in range(0, 301, 15):
        art.line([(x, 0), (x, 98)], '#008080', weight=0.3)
    # cyclone arms
    cx, cy = 197, 52
    for arm in range(5):
        pts = []
        for step in range(110):
            phase = arm * math.tau / 5 + step * 0.039
            r = 7 + step * 0.66
            px = cx + r * math.cos(phase)
            py = cy + r * 0.65 * math.sin(phase)
            if 1 <= px <= 298 and 1 <= py <= 98:
                pts.append((px, py))
        if pts:
            # draw as thin lines, final segment brighter
            for i in range(len(pts)-1):
                col = '#a0e0ff' if i < len(pts)-2 else '#ffffff'
                art.line([pts[i], pts[i+1]], col, weight=0.5)
    # rain streaks
    for _ in range(45):
        sx = art.rng.randint(0, 298)
        sy = art.rng.randint(0, 98)
        art.line([(sx, sy), (sx+4, sy+4)], '#ff0000', weight=0.4)
    # marker
    art.oval(105,57,112,64, fill='#ff0000', outline='#ffffff')
    art.line([(45,72), (105,57)], '#ff0000', weight=0.7)
    art.label('Gopalpur', 43, 74, 70)
    # lighthouse
    art.poly([(22,68),(25,49),(33,49),(37,68)], fill='#ffffff')
    art.rect(25,54,34,57, '#ff0000')
    art.poly([(25,49),(33,49),(29,42)], fill='#ff0000')
    art.line([(30,48),(69,37)], '#ffd700')

def _scene_2(art):
    # medallion
    art.oval(21,16,112,88, fill='#a7564b', outline='#ffd700')
    # stars around centre (66,52)
    cx, cy = 66, 52
    for i in range(12):
        angle = i * math.tau / 12
        rad = 30
        sx = cx + rad * math.cos(angle)
        sy = cy + rad * math.sin(angle)
        art.star(sx, sy, 4, '#ffd700')
    # abstract bird
    bird = [(45,56),(65,45),(85,54),(72,59),(68,68),(62,68),(59,59)]
    art.poly(bird, '#ffd700')
    # calendar pages
    art.poly([(128,9),(262,9),(274,89),(139,92)], fill='#592932')
    art.poly([(119,6),(254,6),(267,82),(133,88)], fill='#efdcbd')
    art.rect(121,7,254,22, '#ae4c49')
    # rings
    art.oval(148,3,158,13, fill=None, outline=WHITE)
    art.oval(224,3,234,13, fill=None, outline=WHITE)
    # labels
    art.label('2027', 132, 27, 102, size=33, color=INK, face='head', align='center')
    art.label('1 JAN', 156, 85, 70, size=10, color=RED, align='center')
    # red oval outline
    art.oval(164,63,225,87, fill=None, outline=RED)

def _scene_3(art):
    # moon
    art.oval(248,9,272,32, fill='#f6dbab')
    # skyline
    art.city(89, '#242740', '#d7a782', 8, 31)
    # ground
    art.rect(0,88,299,99, '#1d2639')
    # tower
    art.poly([(156,86),(159,36),(169,17),(174,17),(179,45),(182,86)], fill='#b58b85')
    art.poly([(161,86),(164,31),(170,20),(172,86)], fill='#5b5774')
    for wy in range(34, 83, 6):
        art.line([(162, wy), (171, wy)], WHITE, weight=0.4)
    # missiles: bounded quadratic arcs converging on the tower
    import math as _math
    arcs = [((6, 26), (86, -34), (168, 30)),
            ((26, 12), (104, -30), (178, 38)),
            ((52, 6), (128, -24), (186, 46)),
            ((84, 4), (150, -18), (192, 54)),
            ((116, 6), (168, -12), (196, 62))]
    for (x0, y0), (cx, cy), (x1, y1) in arcs:
        pts = []
        for step in range(26):
            t = step / 25
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
            pts.append((bx, max(2.0, by)))
        art.line(pts, '#c0a4aa', weight=1.1)
        art.line(pts[-6:], GOLD, weight=2)
    # interceptor burst above the tower
    art.star(168, 22, 9, GOLD)

SCENES[1] = _scene_1
SCENES[2] = _scene_2
SCENES[3] = _scene_3

def _scene_4(art):
    # judgment scales
    art.courthouse(150, 37)
    # Behind the scales
    art.rect(111, 17, 189, 88, '#514755')
    # Beam
    art.line([(150,12),(150,79)], GOLD, 4)
    # Crossbar
    art.line([(113,30),(187,30)], WHITE, 3)
    # Hanger lines and pans
    for x in (114, 186):
        art.line([(x-15,57),(x,30),(x+15,57)], GOLD, 2)
        art.poly([(x-17,57),(x+17,57),(x+9,67),(x-9,67)], WHITE)
    # Base
    art.rect(131, 79, 169, 85, GOLD)

def _scene_5(art):
    # climate summit
    # Sun
    art.oval(196, 10, 255, 60, '#f9cf8d')
    # Hills
    art.poly([(0,80),(49,64),(117,45),(202,53),(299,77),(299,99),(0,99)], '#5f454c')
    # Posts
    for x in range(22, 293, 13):
        art.rect(x, 77, x+6, 90, '#ba8c78')
    # Banner
    art.rect(40, 20, 206, 54, '#f4d5ad')
    art.label('FOSSIL FUELS', 49, 24, 148, 10.5, INK, 'label', 'center')
    # strike line
    art.line([(51,41),(194,35)], RED, 3)

def _scene_6(art):
    # markets slide
    # Grid lines
    for pos in range(12, 100, 15):
        art.line([(0,pos),(299,pos)], '#a48289', .7)
    # Candles
    for i in range(17):
        x = 16 + i*16
        y = 15 + i*3.6 + art.rng.randrange(-9,10)
        paint = '#ef9a91' if i%4 else '#b3c4b2'
        art.line([(x,y-8),(x,y+13)], paint, 1.5)
        art.rect(x-3, y-3, x+3, y+7, paint)
    # Index line
    art.line([(103,12),(150,25),(191,25),(242,55),(265,55)], WHITE, 3)
    # Down arrow
    art.poly([(254,45),(279,60),(256,67)], '#f3827e')

def _scene_7(art):
    # three flags
    art.city(74, '#3e515c', '#f6c794')
    # Water background
    art.rect(0, 76, 299, 99, '#3c6571')
    # Wave streaks
    art.rng.seed(42)
    for _ in range(30):
        x = art.rng.randint(0,299)
        y = art.rng.randint(76,99)
        art.line([(x, y), (x+5, y)], '#7faaa7')
    # Flag poles and flags
    for index, x in enumerate((44, 125, 206)):
        art.line([(x,12),(x,87)], GOLD, 2.8)
        art.rect(x+2, 14, x+51, 46, WHITE)
        if index == 0:
            # China flag
            art.rect(x+2, 14, x+51, 46, '#b94345')
            art.star(x+13, 24, 6, GOLD)
            for sx, sy in [(22,19),(26,23),(26,29),(22,33)]:
                art.star(x+sx, 24+sy, 2, GOLD)
        elif index == 1:
            # US flag
            for stripe in range(0, 13, 2):
                art.rect(x+2, 14+stripe*2.45, x+51, 16.1+stripe*2.45, '#a44852')
            art.rect(x+2, 14, x+23, 31, NAVY)
            # 12 stars 4x3 grid
            rows, cols = 3, 4
            star_radius = 1.4
            for r in range(rows):
                for c in range(cols):
                    cx = x+2 + 5 + c*6
                    cy = 14 + 5 + r*6
                    art.star(cx, cy, star_radius, WHITE)
        else:
            # Russia flag
            art.rect(x+2, 25, x+51, 35, '#5a81a9')
            art.rect(x+2, 36, x+51, 46, '#9f4653')

def _scene_8(art):
    # Voyager
    # Starfield
    for i in range(60):
        x = art.rng.randint(0,299)
        y = art.rng.randint(0,99)
        color = WHITE if i%7==0 else '#8994a9'
        art.oval(x, y, x+1.5, y+1.5, color)
    # Orbit ring
    import math
    for i in range(22):
        angle = i * 0.239
        art.line([(150+111*math.cos(angle), 53+32*math.sin(angle)),
                  (150+111*math.cos(angle+0.12), 53+32*math.sin(angle+0.12))], '#9aadb8', 1.5)
    # Probe
    art.probe(140, 53, wings=False)
    # Signal path
    art.line([(140,54),(183,71),(210,71)], GOLD, 3)

# Register scenes
SCENES[4] = _scene_4
SCENES[5] = _scene_5
SCENES[6] = _scene_6
SCENES[7] = _scene_7
SCENES[8] = _scene_8


def _scene_9(art):
    art.oval(123, 7, 178, 62, '#f9c183')
    for y in range(36, 62, 6):
        art.line([(126, y), (175, y)], '#b96977', 2)
    art.city(72, '#473650', '#ebb092', 7, 27)
    art.poly([(110, 72), (185, 72), (237, 99), (63, 99)], '#3f364b')
    art.line([(149, 76), (148, 86), (145, 98)], '#dfac95', 1.5)
    for x in (34, 262):
        art.line([(x, 85), (x + 6, 42), (x + 10, 27)], '#35283d', 4)
        for offset in (-23, -13, 10, 20):
            art.poly([(x + 10, 29), (x + offset / 2, 23), (x + offset, 42), (x + offset, 32)], '#35283d')
    art.poly([(171, 88), (178, 79), (199, 76), (211, 84), (223, 87), (223, 94), (170, 94)], '#321f32')
    for x in (182, 213):
        art.oval(x - 5, 89, x + 5, 98, '#251f2c', '#b7807a')


def _scene_10(art):
    for i in range(12):
        angle = i * math.tau / 12
        art.star(148 + 65 * math.cos(angle), 50 + 38 * math.sin(angle), 4.8, GOLD)
    art.poly([(106, 49), (128, 52), (113, 29), (140, 40), (153, 48), (170, 41), (178, 34),
              (186, 36), (192, 41), (182, 43), (173, 54), (156, 63), (130, 67), (117, 77), (118, 64)], WHITE)
    art.line([(182, 43), (204, 50), (216, 44)], '#a8c4aa', 2)


def _scene_11(art):
    art.gradient(0, 0, 300, 48, '#94b4c3', '#d6b28a')
    art.rect(0, 46, 300, 100, '#315744')
    art.poly([(0, 27), (29, 22), (61, 29), (91, 20), (124, 28), (155, 19), (190, 27),
              (224, 21), (263, 28), (300, 23), (300, 57), (0, 57)], '#172a30')
    for i in range(32):
        x = 8 + (i * 47) % 286
        y = 29 + (i * 13) % 22
        art.oval(x, y, x + 2.2, y + 1.5, '#d4b577')
    art.poly([(119, 45), (181, 45), (218, 100), (82, 100)], '#b69a72')
    art.poly([(125, 47), (175, 47), (204, 100), (96, 100)], '#cdb184')
    for crease in (53, 63):
        half = 16 + (crease - 53) * .65
        art.line([(150 - half, crease), (150 + half, crease)], '#f7ecd7', 1.7)
    for x in (166, 171, 176):
        art.line([(x, 45), (x, 68)], '#f1e5ca', 2.8)
    art.line([(164, 44), (178, 44)], GOLD, 2.4)
    points = [(150 + 112 * math.cos(math.pi * .08 + i * math.pi * .84 / 33),
               67 + 43 * math.sin(math.pi * .08 + i * math.pi * .84 / 33)) for i in range(34)]
    art.line(points, '#e4d3aa', 1.8)
    art.soft_oval(91, 59, 119, 67, 1.5, 105)
    art.line([(91, 62), (108, 43)], '#4b3629', 7)
    art.line([(90, 61), (105, 43)], '#c49a5c', 4.5)
    art.line([(105, 43), (113, 34)], '#574034', 2.5)
    art.soft_oval(126, 57, 137, 64, 1.1, 120)
    art.oval(128, 55, 134, 61, '#b84d45', '#f3d5a1')


def _scene_12(art):
    for i in range(60):
        x = art.rng.uniform(2, 297)
        y = art.rng.uniform(2, 97)
        art.oval(x, y, x + 1.5, y + 1.5, WHITE if i % 7 == 0 else '#8994a9')
    for i in range(22):
        a0 = i * math.tau / 22
        a1 = (i + 1) * math.tau / 22
        art.line([(150 + 111 * math.cos(a0), 53 + 32 * math.sin(a0)),
                  (150 + 111 * math.cos(a1), 53 + 32 * math.sin(a1))], '#9aadb8', 1.5)
    art.oval(50, 5, 136, 95, '#9e9d9f', '#d8c3b6')
    art.oval(57, 11, 133, 92, '#7c7e8b')
    for i in range(16):
        angle = art.rng.uniform(0, math.tau)
        dist = art.rng.uniform(4, 30)
        pit = art.rng.uniform(2, 8)
        cx = 93 + dist * math.cos(angle)
        cy = 49 + dist * math.sin(angle) * .94
        art.oval(cx - pit, cy - pit, cx + pit, cy + pit, '#616677', '#a19a9d')
    art.probe(194, 53, wings=True)


def _scene_13(art):
    art.courthouse(113, 25)
    art.oval(190, 70, 277, 83, '#77514f', GOLD)
    art.line([(203, 55), (266, 33)], '#503535', 10)
    art.poly([(195, 38), (220, 51), (203, 69), (179, 57)], GOLD)
    art.line([(194, 41), (213, 52)], '#835f5b', 4)


SCENES[9] = _scene_9
SCENES[10] = _scene_10
SCENES[11] = _scene_11
SCENES[12] = _scene_12
SCENES[13] = _scene_13


def _scene_14(art):
    art.oval(248, 9, 272, 32, '#f6dbab')
    art.city(89, '#242740', '#d7a782', 8, 31)
    art.rect(0, 88, 299, 99, '#1d2639')
    for x in (53, 146, 240):
        for rise in (0, 6, 13):
            art.poly([(x - 6, 87), (x + rise / 2, 73 - rise / 2), (x + 7, 87)],
                     '#d38455' if rise % 2 == 0 else GOLD)
    points = [((1 - t) ** 2 * 15 + 2 * (1 - t) * t * 95 + t ** 2 * 172,
               max(2.0, (1 - t) ** 2 * 22 + 2 * (1 - t) * t * (-30) + t ** 2 * 36))
              for t in (step / 25 for step in range(26))]
    art.line(points, '#c0a4aa', 1.1)
    art.line(points[-6:], GOLD, 2)


def _scene_15(art):
    for i in range(60):
        x = art.rng.uniform(2, 297)
        y = art.rng.uniform(2, 97)
        art.oval(x, y, x + 1.5, y + 1.5, WHITE if i % 7 == 0 else '#8994a9')
    for i in range(22):
        a0 = i * math.tau / 22
        a1 = (i + 1) * math.tau / 22
        art.line([(150 + 111 * math.cos(a0), 53 + 32 * math.sin(a0)),
                  (150 + 111 * math.cos(a1), 53 + 32 * math.sin(a1))], '#9aadb8', 1.5)
    art.oval(156, 5, 252, 95, '#9e9d9f', '#d8c3b6')
    art.oval(163, 11, 249, 92, '#7c7e8b')
    for i in range(16):
        angle = art.rng.uniform(0, math.tau)
        dist = art.rng.uniform(4, 24)
        pit = art.rng.uniform(2, 7)
        cx = 204 + dist * math.cos(angle)
        cy = 49 + dist * math.sin(angle) * .94
        art.oval(cx - pit, cy - pit, cx + pit, cy + pit, '#616677', '#a19a9d')
    art.probe(103, 53, wings=True)
    for i in range(7):
        art.line([(299, 14 + i * 4), (276 - (i % 2) * 8, 5 + i * 7)], GOLD, 2)


def _scene_16(art):
    art.oval(155, 12, 228, 85, None, '#d1a4a9')
    art.oval(163, 20, 220, 77, None, '#eab5b0')
    art.oval(176, 34, 207, 65, '#d8a1a0')
    art.oval(48, 29, 95, 74, '#fff1d6')
    art.rect(71, 29, 111, 74, '#fff1d6')
    art.oval(95, 29, 142, 74, '#b7535f')
    art.rect(96, 29, 118, 74, '#b7535f')
    art.line([(151, 47), (165, 47)], WHITE, 2)
    art.label('60.7%', 223, 42, 75, 12, WHITE)


def _scene_17(art):
    art.city(78, '#1a2438', '#e8c98a', 10, 30)
    for x in (30, 120, 210, 285):
        art.line([(x, 6), (x, 40)], '#c8cfda', 2)
        art.poly([(x - 3, 40), (x + 3, 40), (x + 16, 78), (x - 16, 78)], '#54627e')
    art.poly([(0, 100), (0, 80), (90, 72), (210, 72), (299, 80), (299, 100)], '#0a0f1c')
    art.line([(20, 84), (110, 76), (200, 76), (285, 84)], GOLD, 2)
    art.poly([(52, 86), (62, 79), (96, 77), (112, 82), (118, 86)], '#d8d8e0')
    art.poly([(178, 84), (188, 77), (222, 75), (238, 80), (244, 84)], '#c03a3a')
    for x in (60, 108):
        art.oval(x - 3, 83, x + 3, 88, '#0c0c10', '#8a8f9a')
    for x in (186, 234):
        art.oval(x - 3, 81, x + 3, 86, '#0c0c10', '#8a8f9a')
    art.line([(140, 88), (176, 88)], WHITE, 2)
    art.line([(248, 86), (282, 86)], GOLD, 2)


def _scene_18(art):
    art.rect(30, 14, 270, 92, '#2e5d3a')
    art.line([(45, 24), (255, 24), (255, 84), (45, 84), (45, 24)], WHITE, 1.2)
    art.line([(45, 54), (255, 54)], WHITE, 1.2)
    art.line([(150, 24), (150, 54)], WHITE, 1.2)
    art.line([(150, 54), (150, 84)], WHITE, 1.2)
    art.line([(100, 24), (100, 84)], WHITE, 1.2)
    art.line([(200, 24), (200, 84)], WHITE, 1.2)
    art.line([(100, 54), (200, 54)], WHITE, 1.2)
    art.line([(150, 18), (150, 90)], '#10160f', 3)
    art.line([(148, 18), (152, 18)], WHITE, 2)
    points = [(60 + i * 5, 70 - 35 * math.sin(i * math.pi / 35)) for i in range(36)]
    art.line(points, GOLD, 1.5)
    art.oval(232, 31, 240, 39, '#e8f2b0')
    art.rect(30, 16, 128, 36, '#14231a')
    art.label('6-3 6-4', 38, 21, 82, 11, '#ffd75e')


def _scene_19(art):
    art.rect(196, 12, 288, 50, '#3a3f4a')
    art.rect(208, 20, 276, 44, '#e8e4da')
    art.line([(228, 50), (256, 50)], RED, 3)
    for dx in (0, 7, 14, 21, 28):
        art.line([(228 + dx, 50), (232 + dx, 62)], '#d8d8d8', 1)
    art.oval(92, 26, 132, 66, '#c96a2c', '#5a2c10')
    art.line([(92, 46), (132, 46)], '#5a2c10', 1.5)
    art.line([(112, 26), (112, 66)], '#5a2c10', 1.5)
    points = [(30 + i * 3, 88 - 62 * math.sin(i * math.pi / 44)) for i in range(22)]
    art.line(points, GOLD, 1.5)
    art.label('51', 30, 24, 62, 16, GOLD, 'head')


def _scene_20(art):
    art.oval(26, 6, 150, 94, '#14100e', '#3a3436')
    art.oval(38, 16, 138, 84, None, '#2c2729')
    art.oval(50, 25, 126, 75, None, '#2c2729')
    art.oval(74, 36, 102, 64, '#b7535f')
    art.oval(85, 47, 91, 53, '#e8e2d4')
    art.line([(214, 8), (152, 42)], '#c8c2b8', 3)
    art.poly([(152, 42), (160, 36), (166, 44), (157, 49)], '#8a8378')
    for i in range(8):
        x = 176 + i * 14
        h = 10 + art.rng.randrange(0, 24)
        art.rect(x, 92 - h, x + 9, 92, GOLD if i % 2 else RED)
    art.label('10', 234, 26, 52, 24, WHITE, 'head')


SCENES[14] = _scene_14
SCENES[15] = _scene_15
SCENES[16] = _scene_16
SCENES[17] = _scene_17
SCENES[18] = _scene_18
SCENES[19] = _scene_19
SCENES[20] = _scene_20


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_POSITIONS = [(.99,.76),(.59,.31),(.25,.55),(.879,.82),(.568,.331),(.861,.395),(.224,.433),(.232,.447),(.51,.324),(.817,.392),(.674,.472),(.641,.45),(.681,.493),(.127,.383),(.117,.358),(.769,.593),(.698,.438),(.583,.514),(.683,.414),(.812,.357),(.498,.281),(.229,.379),(.178,.415),(.793,.465),(.40,.63),(.507,.287),(.525,.274),(.804,.518),(.811,.533),(.809,.518),(.477,.275),(.894,.823),(.883,.827),(.197,.365),(.116,.36),(.633,.438),(.975,.781),(.916,.686),(.525,.248),(.78,.652),(.693,.449),(.526,.311),(.552,.232),(.228,.372),(.518,.262),(.207,.462),(.503,.298),(.152,.372),(.138,.362)]

PIN_ANCHORS = [(.72,.49),(.23,.38),(.62,.46),(.50,.28),(.58,.37),(.24,.35),(.79,.46),(.28,-.20),(.23,.43),(.57,.28),(.97,.90),(.86,.39),(.82,.39),(.57,.28),(.73,-.20),(.49,.36),(.135,.385),(.50,.29),(.205,.355),(.487,.272)]

PIN_BADGES = [(.67,.73),(.10,.25),(.57,.67),(.48,.22),(.67,.40),(.22,.08),(.79,.69),(.28,-.20),(.29,.63),(.58,.17),(.97,1.02),(.95,.23),(.91,.49),(.56,.36),(.73,-.20),(.45,.38),(.06,.36),(.36,.13),(.24,.24),(.60,.08)]

CONTINENTS = [
    [(.02,.18),(.11,.09),(.22,.13),(.31,.09),(.32,.27),(.26,.28),(.24,.39),(.19,.43),(.20,.55),(.15,.48),(.11,.33),(.06,.28)],
    [(.19,.53),(.27,.53),(.34,.64),(.30,.77),(.26,.94),(.23,.88),(.23,.73)],
    [(.31,.08),(.42,.04),(.39,.21),(.34,.20)],
    [(.44,.28),(.48,.25),(.48,.18),(.57,.12),(.62,.21),(.60,.35),(.54,.37),(.48,.43),(.44,.40)],
    [(.44,.43),(.55,.42),(.60,.55),(.56,.68),(.53,.81),(.49,.76),(.47,.57),(.43,.52)],
    [(.57,.25),(.67,.19),(.79,.18),(.87,.14),(.97,.24),(.89,.32),(.85,.49),(.80,.57),(.82,.68),(.75,.61),(.71,.51),(.68,.61),(.63,.46),(.56,.37)],
    [(.77,.72),(.86,.67),(.92,.78),(.89,.88),(.82,.86),(.77,.81)],
    [(.93,.83),(.98,.81),(.96,.94),(.93,.95)],
]


def point_in_poly(point, vertices):
    x, y = point
    inside = False
    count = len(vertices)
    for i in range(count):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % count]
        if (y1 > y) != (y2 > y):
            x_cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_cross:
                inside = not inside
    return inside


def draw_map(page, top):
    page.text('map-title', 'WHERE IT HAPPENED', (18, top + 8, 160, top + 20), 'label', 10, 12, GOLD)
    map_left, map_top, map_width, map_height = 20, top + 56, 136, 150

    def coordinate(px, py):
        return (map_left + px * map_width, map_top + py * map_height)

    for row in range(34):
        for column in range(40):
            px, py = (column + .5) / 40, (row + .5) / 34
            if any(point_in_poly((px, py), continent) for continent in CONTINENTS):
                cx, cy = coordinate(px, py)
                page.ink.ellipse(scaled((cx - .6, cy - .6, cx + .6, cy + .6)), fill='#917747')
    page.ink = ImageDraw.Draw(page.image)

    for number, (px, py) in enumerate(BRIEF_POSITIONS, start=21):
        cx, cy = coordinate(px, py)
        page.ink.ellipse(scaled((cx - 1.25, cy - 1.25, cx + 1.25, cy + 1.25)), fill=COLORS[number])
    page.ink = ImageDraw.Draw(page.image)

    badges = []
    for number, (anchor, badge) in enumerate(zip(PIN_ANCHORS, PIN_BADGES), start=1):
        page.line([coordinate(*anchor), coordinate(*badge)], '#8b7958', .55)
        bx, by = coordinate(*badge)
        box = (bx - 6.5, by - 6.5, 13, 13)
        if any(overlaps(box, other) for other in badges):
            raise ValueError(f'Map badge {number} overlaps an earlier badge')
        badges.append(box)
        page.ink.ellipse(scaled((bx - 7, by - 7, bx + 7, by + 7)), fill='#806b48')
        page.ink.ellipse(scaled((bx - 5.8, by - 5.8, bx + 5.8, by + 5.8)), fill=COLORS[number], outline='#ad935d')
        page.ink = ImageDraw.Draw(page.image)
        page.text(f'map-pin-{number}', str(number), (bx - 7, by - 3.5, bx + 7, by + 4.5), 'label', 9.5, 10, WHITE, 'center')

    page.line([(18, top + 214), (156, top + 214)], '#78909e', .5)
    page.text('map-note', 'Numbers locate illustrated stories\nSmall dots locate briefs\nColours match the region strip',
              (18, top + 222, 160, top + 262), 'body', 9.5, 12, WHITE)
    return badges


BRIEF_GAP = 0.5


def build_page(output=ROOT):
    output = Path(output)
    page = Page()
    sections = {'masthead': (12, 102), 'timeline': (102, 134), 'regions': (134, 152),
                'leads': (152, 304), 'secondary': (304, 592), 'strip': (592, 684),
                'map_and_briefs': (684, 958), 'footer': (958, 1014)}

    # Masthead
    page.rect((12, 12, 1012, 102), '#211f1b')
    page.line([(14, 12), (1010, 12)], GOLD, .8)
    page.text('brand', 'THE WORLD IN ONE DAY', (14, 13, 404, 26), 'label', 11, 11, GOLD)
    page.text('edition', "FRIDAY'S NEWS · ONE PAGE · 69 STORIES", (605, 13, 1010, 26), 'label', 10, 10, WHITE, 'right')
    page.line([(14, 26), (1010, 26)], GOLD, 1)
    page.text('date', 'Friday 20 November 2026', (12, 28, 1012, 86), 'head', 60, 60, WHITE, 'center', max_lines=1)
    page.line([(14, 88), (1010, 88)], GOLD, .65)
    page.text('kicker', 'Cyclone Akvan strikes India • Ballistic missiles hit Kyiv • COP31 deadlocked on final day • Harden drops 51 in Cleveland',
              (12, 90, 1012, 101), 'italic', 12, 12, GOLD, 'center', max_lines=1)

    # Timeline
    page.rect((12, 102, 1012, 134), '#292722')
    stops = [("OVERNIGHT", "Seven missile waves hit Kyiv"),
             ("~06:00 UTC", "APEC leaders meet in Shenzhen"),
             ("~10:00 UTC", "Trilateral declaration issued"),
             ("~14:00 UTC", "Houthi missile hits Riyadh KAFD"),
             ("BY NOON LOCAL", "Akvan makes landfall in Odisha"),
             ("LATE", "Wall Street slides; Dow -1,101"),
             ("20:30 UTC", "Bayern held 1-1 by Köln; Kane injured")]
    segment = 1000 / 7
    for index, (when, event) in enumerate(stops):
        x = 12 + index * segment
        if index > 0:
            page.line([(x, 104), (x, 132)], '#454138', .5)
        page.text(f'timeline-time-{index}', when, (x + 5, 104, x + segment - 5, 113), 'label', 9.5, 9.5, GOLD, 'center', max_lines=1)
        page.text(f'timeline-event-{index}', event, (x + 5, 114, x + segment - 5, 133), 'body', 9.5, 9.5, WHITE, 'center', max_lines=2)

    # Regions
    page.text('region-caption', '69 STORIES FROM 7 REGIONS', (14, 138, 184, 148), 'label', 9.5, 9.5, INK)
    for index, (name, color, numbers) in enumerate(REGIONS):
        x = 186 + index * 118
        page.rect((x, 136, x + 116, 150), '#292722')
        page.rect((x, 136, x + 4, 150), color)
        page.text(f'region-{name}', f'{name}  {len(numbers)}', (x + 2, 138, x + 114, 148), 'label', 9.5, 9.5, WHITE, 'center', max_lines=1)

    def card(number, left, top, width, height, art_height, kind):
        kicker, headline, deck, source = CARDS[number - 1]
        status = 'FORECAST' if number == 15 else 'REPORTED'
        source_copy = f'{source}  /  {status}'
        page.card_surface((left, top, left + width, top + height))
        illustration(page, number, left, top, width, art_height)
        if kind == 'lead':
            cursor = top + art_height + 3
            page.text(f'lead-kicker-{number}', f'{number:02d}  {kicker}', (left, cursor, left + width, cursor + 9),
                      'label', 9.5, 9.5, GOLD, max_lines=1)
            page.line([(left, cursor + 9.5), (left + width, cursor + 9.5)], GOLD, .8)
            cursor += 11
            source_top = top + height - 11
            page.text(f'lead-source-{number}', source_copy, (left, source_top, left + width, source_top + 9),
                      'label', 9.5, 9.5, INK, max_lines=1)
            deck_end = source_top - 2
        else:
            chip_w = math.ceil(font('label', 9.5).getlength(source_copy) / SCALE) + 10
            right = left + width
            page.rect((right - chip_w, top, right - .5, top + 11), '#1c2023')
            page.text(f'art-{number}-source', source_copy, (right - chip_w + 3, top + 0.5, right - 3.5, top + 11),
                      'label', 9.5, 9.5, GOLD, 'center', max_lines=1)
            page.rect((left, top + art_height - 11, right - .5, top + art_height - .5), '#1c2023')
            page.text(f'art-{number}-kicker', kicker, (left + 4, top + art_height - 9, left + width - 4, top + art_height),
                      'label', 9.5, 9.5, GOLD, max_lines=1)
            page.line([(left, top + art_height), (right - .5, top + art_height)], GOLD, .8)
            cursor = top + art_height + 3
            deck_end = top + height - 1
        size, leading, box_h = {'lead': (26, 25, 55), 'card': (15, 14, 33), 'strip': (13, 12, 26)}[kind]
        cursor += page.text(f'{kind}-title-{number}', headline, (left, cursor, left + width, cursor + box_h),
                            'head', size, leading, max_lines=2) + 3
        face, dsize, dleading, maxl = {'lead': ('body', 11, 11, 3), 'card': ('compact', 10.5, 10, 4),
                                       'strip': ('compact', 9.5, 9.5, 2)}[kind]
        page.text(f'{kind}-deck-{number}', deck, (left, cursor, left + width, deck_end),
                  face, dsize, dleading, max_lines=maxl)
        page.card_outline((left, top, left + width, top + height))

    # Leads
    lead_width = (1000 - 20) / 3
    for i in range(3):
        card(i + 1, 12 + i * (lead_width + 10), 152, lead_width, 150, 54, 'lead')

    # Secondary rows
    for first, count, top, row_height, art_height in [(4, 5, 304, 102, 34), (9, 4, 406, 94, 34), (13, 4, 500, 92, 34)]:
        width = (1000 - (count - 1) * 8) / count
        for j in range(count):
            card(first + j, 12 + j * (width + 8), top, width, row_height - 4, art_height, 'card')

    # Results strip
    for j, n in enumerate(range(17, 21)):
        card(n, 12 + j * 252, 592, 244, 88, 32, 'strip')

    # Map and briefs
    page.rect((12, 684, 1012, 957), NAVY)
    badges = draw_map(page, 684)
    page.line([(168, 691), (168, 950)], '#78909e', .65)
    page.text('briefs-title', 'ALSO ON FRIDAY 20 NOVEMBER — 49 MORE STORIES', (176, 692, 996, 704), 'label', 10, 10, GOLD)
    for first, last, x in [(21, 39, 176), (39, 56, 448), (56, 70, 720)]:
        y = 706
        for n in range(first, last):
            used = page.text(f'brief-{n}', f'{n} {BRIEFS[n - 21]}', (x, y, x + 264, y + min(27, 950 - y)),
                             'compact', 9.5, 9.5, WHITE, max_lines=2)
            y += used + BRIEF_GAP

    # Footer
    page.text('certainty', "HOW SURE ARE WE?   ·   REPORTED = confirmed by wires   ·   CLAIM = one side's claim, attributed   ·   FORECAST = expected, not yet happened",
              (14, 959, 1010, 970), 'label', 9.5, 9.5, INK, 'center', max_lines=1)
    page.rect((12, 970, 1012, 993), '#292722')
    page.rect((12, 970, 15, 993), RED)
    page.text('date-check-label', 'DATE CHECK\nTHU + BEFORE', (19, 972, 106, 991), 'label', 9.5, 9.5, GOLD, max_lines=2)
    page.text('date-check', DATE_CHECK, (110, 971, 1005, 991), 'compact', 9.5, 9.5, PANEL, max_lines=2)
    page.text('sourcing', 'Sources: Reuters, AP, AFP, BBC, IMD, NASA, ESA, ICC, ATP, Bundesliga, UKMTO, Consilium, MarketIndex, NewKerala. Original drawings.',
              (14, 994, 1010, 1003), 'body', 9.5, 9.5, INK, 'center', max_lines=1)
    page.text('truth', 'Every story here happened, or was first reported, on Friday 20 November 2026. Disputed claims are attributed, not stated as fact.',
              (14, 1003, 1010, 1012), 'body', 9.5, 9.5, INK, 'center', max_lines=1)

    page.check_layout()
    report = {'canvas': [1024, 1024], 'stories': len(CARDS) + len(BRIEFS),
              'illustrated_cards': len(page.panels),
              'minimum_font': min(b['size'] for b in page.blocks),
              'sections': sections, 'secondary_rows': [102, 94, 92],
              'blocks': page.blocks, 'panels': page.panels, 'map_badges': badges}
    output.mkdir(parents=True, exist_ok=True)
    page.image.resize((1024, 1024), Image.Resampling.LANCZOS).save(output / 'entry.png', format='PNG', optimize=True)
    (output / 'layout.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report


if __name__ == '__main__':
    result = build_page()
    size = (ROOT / 'entry.png').stat().st_size
    print(json.dumps({key: result[key] for key in ('canvas', 'stories', 'illustrated_cards', 'minimum_font', 'sections', 'secondary_rows')}, indent=2, ensure_ascii=False))
    print('entry.png bytes:', size, 'over_limit:', size > 1_048_576)
