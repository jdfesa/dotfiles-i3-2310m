"""Build five original Wi-Fi glyphs. Build locally; no fontTools on laptop."""
from datetime import datetime, timezone
import math
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


def polygon(pen, points):
    # Consistent winding keeps crossing strokes filled at their overlap.
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    if area > 0:
        points = list(reversed(points))
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()


def arc(pen, radius):
    angles = [math.radians(140 - i * 100 / 24) for i in range(25)]
    points = [(round(500 + radius * math.cos(a)), round(130 + radius * math.sin(a))) for a in angles]
    points += [(round(500 + (radius - 70) * math.cos(a)), round(130 + (radius - 70) * math.sin(a))) for a in reversed(angles)]
    polygon(pen, points)


def glyph(level):
    pen = TTGlyphPen(None)
    if level == 0:
        polygon(pen, [(220, 160), (290, 90), (780, 580), (710, 650)])
        polygon(pen, [(220, 580), (290, 650), (780, 160), (710, 90)])
    else:
        polygon(pen, [(round(500 + 55 * math.cos(-i * math.pi / 12)),
                       round(130 + 55 * math.sin(-i * math.pi / 12))) for i in range(24)])
        for radius in (250, 410, 570)[:level - 1]:
            arc(pen, radius)
    return pen.glyph()


builder = FontBuilder(1000, isTTF=True)
names = [".notdef", "wifi_off", "wifi_1", "wifi_2", "wifi_3", "wifi_4"]
builder.setupGlyphOrder(names)
builder.setupCharacterMap({0xE000 + level: names[level + 1] for level in range(5)})
glyphs = {".notdef": TTGlyphPen(None).glyph()}
glyphs.update({names[level + 1]: glyph(level) for level in range(5)})
builder.setupGlyf(glyphs)
metrics = {}
for name, item in glyphs.items():
    item.recalcBounds(None)
    metrics[name] = (1000, getattr(item, "xMin", 0))
builder.setupHorizontalMetrics(metrics)
builder.setupHorizontalHeader(ascent=800, descent=-200)
builder.setupNameTable({"familyName": "BGH Status Icons", "styleName": "Regular",
                       "uniqueFontIdentifier": "BGHStatusIcons-Regular-1.0",
                       "fullName": "BGH Status Icons Regular", "psName": "BGHStatusIcons-Regular",
                       "version": "Version 1.0"})
builder.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
builder.setupPost()
builder.font.recalcTimestamp = False
timestamp = int(datetime(2026, 10, 12, tzinfo=timezone.utc).timestamp()) + 2082844800
builder.font["head"].created = timestamp
builder.font["head"].modified = timestamp
destination = Path(__file__).resolve().parents[1] / "config/bgh-status-icons.ttf"
builder.save(destination)
print(f"Built {destination}: {destination.stat().st_size} bytes")
