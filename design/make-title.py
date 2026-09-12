# -*- coding: utf-8 -*-
"""타이틀 그림 시안 열 장. 제목·단추는 같고 가운데 그림만 다르다. Jua 는 쓰는 글자만 잘라 박아 넣는다."""
import io, os, base64
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
INK, PAPER, YEL, GRN, BLU, ORG, PNK, RED, SKY = "#3d2b1f", "#fffdf8", "#ffd43b", "#51cf66", "#339af0", "#e8590c", "#f06595", "#e03131", "#74c0fc"

# ── 공통 조각 ──
def giraffe(tx, ty, k=1.0, spots=True):
    """서툰 기린 한 마리. (tx,ty) 에 k 배로"""
    body = ('<g transform="translate(%s %s) scale(%s)">'
            '<g stroke="%s" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none">'
            '<path d="M7 65c-3-11 10-17 24-15 10 2 15 7 13 13s-10 9-21 8c-10-1-15-3-16-6z"/>'
            '<path d="M42 55l11-33"/><path d="M51 19c4-5 11-5 14 0s0 9-6 8"/><path d="M55 16l-3-7M61 16l1-7"/>'
            '<path d="M13 71v14M22 72v13M33 72v13M42 69v15"/></g>') % (tx, ty, k, INK)
    if spots:
        body += ('<g fill="#f76707"><circle cx="18" cy="59" r="2.8"/><circle cx="31" cy="54" r="2.5"/>'
                 '<circle cx="39" cy="63" r="2.2"/><circle cx="48" cy="39" r="2.3"/></g>')
    return body + '</g>'

def card(x, y, w, h, fill, rot, inner=""):
    cx, cy = x + w / 2, y + h / 2
    return ('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="%s" height="%s" rx="13" fill="%s"/>'
            '<rect x="%s" y="%s" width="%s" height="%s" rx="13" fill="%s" stroke="%s" stroke-width="3"/>%s</g>'
            % (rot, cx, cy, x + 5, y + 5, w, h, INK, x, y, w, h, fill, INK, inner))

def word(x, y, t, size=26):
    return '<text x="%s" y="%s" text-anchor="middle" font-size="%s" font-weight="700" fill="%s">%s</text>' % (x, y, size, INK, t)

def arrow(x0, x1, y, color):
    return ('<g stroke="%s" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M%s %sc%s -11 %s -11 %s 1"/><path d="M%s %sl-11-1M%s %sl0-11"/></g>'
            % (color, x0, y, (x1 - x0) * .3, (x1 - x0) * .7, x1 - x0, x1, y + 1, x1, y + 1))

def crayon(x, y, color, rot, L=48):
    return ('<g transform="rotate(%s %s %s)"><path d="M%s %sh%sl9 6-9 6H%sz" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
            '<rect x="%s" y="%s" width="17" height="16" fill="#fff6e0" stroke="%s" stroke-width="2.6"/></g>'
            % (rot, x + L / 2, y + 6, x, y, L, x, color, INK, x + L * .35, y - 2, INK))

def star(x, y, k, color):
    return ('<path transform="translate(%s %s) scale(%s)" d="M20 4l4 11 12 1-9 8 3 12-10-7-10 7 3-12-9-8 12-1z" '
            'fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (x, y, k, color))

def spiral(x, y, k, color):
    return ('<path transform="translate(%s %s) scale(%s)" d="M6 30c0-10 7-18 14-18s10 6 6 11-11 2-9-5 9-11 17-9" '
            'fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % (x, y, k, color))

Q = lambda x, y, size=34: word(x, y, "???", size)

# ── 열 장 ──
ART = {}

ART["TitlePages"] = ("쪽 넘김", "지금 것. 게임 안의 쪽 세 장이 그대로 넘어간다",
    card(8, 55, 88, 66, YEL, -5, word(52, 99, "기린", 28)) + arrow(108, 138, 86, ORG)
    + card(152, 43, 88, 90, PAPER, 3, giraffe(158, 43)) + arrow(252, 282, 86, BLU)
    + card(296, 55, 88, 66, GRN, -3, Q(340, 101))
    + crayon(20, 160, PNK, -14) + crayon(320, 158, SKY, 12))

ART["TitleBook"] = ("스케치북", "공책 한 권이 주인공. 표지에 낙서와 물음표",
    '<rect x="112" y="30" width="176" height="150" rx="10" fill="%s" stroke="%s" stroke-width="3.4" transform="rotate(-3 200 105)"/>' % (PAPER, INK)
    + ''.join('<circle cx="%s" cy="33" r="6" fill="none" stroke="%s" stroke-width="3"/>' % (x, INK) for x in range(128, 280, 22))
    + giraffe(150, 68, 1.05) + word(255, 130, "?", 64)
    + crayon(20, 150, RED, -30) + crayon(44, 165, YEL, -12) + crayon(70, 176, GRN, 6)
    + '<g transform="rotate(35 330 150)"><rect x="300" y="144" width="60" height="12" rx="3" fill="%s" stroke="%s" stroke-width="2.6"/><path d="M360 144l12 6-12 6z" fill="#fff6e0" stroke="%s" stroke-width="2.6"/></g>' % (YEL, INK, INK))

ART["TitleTable"] = ("둘러앉기", "위에서 본 탁자. 공책이 한 바퀴 돈다",
    ''.join(card(*c) for c in [
        (170, 12, 44, 32, YEL, 0, word(192, 34, "기린", 15)),
        (272, 58, 44, 32, PAPER, 18, giraffe(276, 60, .5, False)),
        (250, 138, 44, 32, GRN, -12, Q(272, 162, 18)),
        (100, 138, 44, 32, PAPER, 14, spiral(104, 138, .8, PNK)),
        (60, 58, 44, 32, YEL, -18, word(82, 80, "?", 22))])
    + '<g fill="none" stroke="%s" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">' % ORG
    + '<path d="M228 30c22 6 40 16 52 30"/><path d="M280 60l-10-3M280 60l2-10"/>'
    + '<path d="M312 106c-2 18-12 34-26 44"/><path d="M286 150l3-10M286 150l10 2"/>'
    + '<path d="M230 178c-24 6-50 6-74-2"/><path d="M156 176l10-2M156 176l6 8"/>'
    + '<path d="M84 140c-14-16-20-38-16-58"/><path d="M68 82l-2 10M68 82l8 6"/>'
    + '<path d="M104 46c16-12 34-20 56-24"/><path d="M160 22l-10 4M160 22l-2 10"/></g>'
    + crayon(164, 92, RED, 20, 40) + crayon(166, 100, SKY, -25, 40))

ART["TitleCups"] = ("종이컵 전화", "실을 타고 말이 건너가다 딴 것이 된다",
    '<path d="M22 70l8 62h40l8-62z" fill="%s" stroke="%s" stroke-width="3.2" stroke-linejoin="round"/><ellipse cx="50" cy="70" rx="28" ry="7" fill="#fff" stroke="%s" stroke-width="3.2"/>' % (PAPER, INK, INK)
    + '<path d="M302 70l8 62h40l8-62z" fill="%s" stroke="%s" stroke-width="3.2" stroke-linejoin="round"/><ellipse cx="330" cy="70" rx="28" ry="7" fill="#fff" stroke="%s" stroke-width="3.2"/>' % (PAPER, INK, INK)
    + '<path d="M78 96c60 22 164 22 224 0" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 5"/>' % INK
    + card(104, 118, 52, 40, YEL, -6, word(130, 146, "기린", 18)) + '<path d="M130 106v12" stroke="%s" stroke-width="2.4"/>' % INK
    + card(164, 122, 52, 48, PAPER, 4, giraffe(166, 122, .62, False)) + '<path d="M190 111v11" stroke="%s" stroke-width="2.4"/>' % INK
    + card(224, 118, 52, 40, GRN, 7, Q(250, 148, 22)) + '<path d="M250 106v12" stroke="%s" stroke-width="2.4"/>' % INK)

ART["TitleDrift"] = ("점점 이상해지는 기린", "한 칸 넘어갈 때마다 조금씩 어긋난다",
    card(18, 60, 66, 80, PAPER, -3, giraffe(14, 68, .72, False)) + arrow(92, 108, 100, ORG)
    + card(116, 60, 66, 80, PAPER, 2,
           '<g stroke="%s" stroke-width="3.4" stroke-linecap="round" fill="none"><path d="M128 118c0-8 8-12 18-10 8 2 10 6 8 10s-8 6-16 5c-6-1-10-3-10-5z"/><path d="M152 108l6-44"/><circle cx="160" cy="62" r="5"/><path d="M132 124v10M140 125v10M150 125v10"/></g>' % INK)
    + arrow(190, 206, 100, ORG)
    + card(214, 60, 66, 80, PAPER, -2,
           '<g stroke="%s" stroke-width="3.4" stroke-linecap="round" fill="none"><ellipse cx="247" cy="100" rx="18" ry="12"/><path d="M232 110v16M239 112v16M247 112v16M255 112v16M262 110v16M268 106v14"/><circle cx="260" cy="88" r="2" fill="%s"/></g>' % (INK, INK))
    + arrow(288, 304, 100, ORG)
    + card(312, 60, 66, 80, GRN, 3,
           '<g stroke="%s" stroke-width="3.4" stroke-linecap="round" fill="none"><circle cx="345" cy="90" r="12"/><path d="M336 100c-6 10-10 18-8 26M341 101c-2 10-2 18 0 26M349 101c2 10 2 18 0 26M354 100c6 10 10 18 8 26"/></g>' % INK
           + word(345, 132, "?", 22))
    + crayon(150, 170, PNK, -8, 40))

ART["TitleQmark"] = ("큰 물음표", "물음표 하나가 화면을 차지하고, 낙서가 그 둘레에 붙는다",
    '<path d="M138 70c0-32 26-50 56-50s54 18 54 46c0 24-18 32-34 44-10 8-14 16-14 30" fill="none" stroke="%s" stroke-width="16" stroke-linecap="round"/>' % ORG
    + '<circle cx="200" cy="172" r="11" fill="%s"/>' % ORG
    + '<path d="M138 70c0-32 26-50 56-50s54 18 54 46c0 24-18 32-34 44-10 8-14 16-14 30" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % INK
    + '<circle cx="200" cy="172" r="11" fill="none" stroke="%s" stroke-width="3"/>' % INK
    + card(20, 30, 70, 52, YEL, -8, word(55, 64, "기린", 20)) + card(292, 26, 76, 58, PAPER, 7, giraffe(288, 24, .6, False))
    + star(28, 120, 1.1, PNK) + spiral(300, 116, 1.1, GRN) + star(320, 150, .8, SKY)
    + crayon(70, 168, BLU, 10, 44) + crayon(258, 172, YEL, -16, 44))

ART["TitleBubbles"] = ("말풍선", "말이 풍선을 타고 건너간다. 가운데는 생각풍선 속 그림",
    '<g transform="rotate(-4 68 70)"><rect x="14" y="40" width="108" height="58" rx="24" fill="%s" stroke="%s" stroke-width="3.2"/><path d="M40 96l-8 20 22-16z" fill="%s" stroke="%s" stroke-width="3.2" stroke-linejoin="round"/></g>' % (YEL, INK, YEL, INK)
    + word(68, 79, "기린", 26)
    + '<g stroke="%s" stroke-width="3.2" fill="%s"><ellipse cx="190" cy="92" rx="56" ry="46"/><circle cx="142" cy="140" r="9"/><circle cx="128" cy="156" r="5"/></g>' % (INK, PAPER)
    + giraffe(160, 60, .9, False)
    + '<g transform="rotate(3 310 118)"><rect x="256" y="90" width="108" height="58" rx="24" fill="%s" stroke="%s" stroke-width="3.2"/><path d="M340 146l8 20-22-16z" fill="%s" stroke="%s" stroke-width="3.2" stroke-linejoin="round"/></g>' % (GRN, INK, GRN, INK)
    + Q(310, 131, 30))

ART["TitleRainbow"] = ("크레용 무지개", "크레용 일곱 자루가 아치를 그리고 그 밑에서 게임이 벌어진다",
    ''.join(crayon(x, y, c, r, 52) for x, y, c, r in [
        (28, 150, RED, -80), (54, 96, ORG, -58), (100, 52, YEL, -34), (164, 26, GRN, -8),
        (228, 34, BLU, 18), (282, 66, "#9775fa", 44), (318, 120, PNK, 70)])
    + card(150, 118, 84, 62, PAPER, -2, giraffe(154, 116, .68, False))
    + '<path d="M60 186h260" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".5"/>' % INK
    + word(262, 176, "?", 34) + star(96, 150, .8, PNK))

ART["TitleFridge"] = ("냉장고 그림", "아이 그림 붙여 둔 냉장고 문. 자석으로 세 장",
    '<rect x="18" y="8" width="344" height="184" rx="14" fill="#f4f6f8" stroke="%s" stroke-width="3.2"/><path d="M18 60h344" stroke="%s" stroke-width="3.2"/><rect x="330" y="20" width="10" height="28" rx="3" fill="#dfe4e8" stroke="%s" stroke-width="2.4"/>' % (INK, INK, INK)
    + card(40, 76, 90, 70, YEL, -6, word(85, 120, "기린", 26)) + '<circle cx="50" cy="80" r="7" fill="%s" stroke="%s" stroke-width="2.4"/>' % (RED, INK)
    + card(146, 68, 96, 92, PAPER, 3, giraffe(150, 70)) + '<circle cx="196" cy="70" r="7" fill="%s" stroke="%s" stroke-width="2.4"/>' % (BLU, INK)
    + card(256, 80, 90, 70, GRN, 5, Q(301, 126, 30)) + '<circle cx="332" cy="84" r="7" fill="%s" stroke="%s" stroke-width="2.4"/>' % (PNK, INK)
    + '<g fill="%s" stroke="%s" stroke-width="2"><circle cx="60" cy="32" r="8"/><circle cx="90" cy="38" r="6"/></g>' % (YEL, INK))

ART["TitleSheet"] = ("낙서 도화지", "하얀 도화지 한 장에 크레용 낙서가 잔뜩",
    '<rect x="24" y="12" width="332" height="176" rx="8" fill="%s" stroke="%s" stroke-width="3.2" transform="rotate(-1.5 190 100)"/>' % (PAPER, INK)
    + '<circle cx="70" cy="50" r="16" fill="%s" stroke="%s" stroke-width="3"/><g stroke="%s" stroke-width="3" stroke-linecap="round"><path d="M70 22v-8M70 78v8M42 50h-8M98 50h8M50 30l-6-6M90 30l6-6M50 70l-6 6M90 70l6 6"/></g>' % (YEL, INK, ORG)
    + '<path d="M120 70l20-22 20 22z M124 70h32v26h-32z" fill="%s" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (SKY, INK)
    + giraffe(190, 40, .85) + star(290, 30, 1.1, PNK) + spiral(300, 90, 1.2, GRN)
    + word(120, 160, "?", 44) + '<path d="M170 150l12 12 12-14 12 14 12-12" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % RED
    + '<path d="M270 156c-6-10 6-16 10-8 4-8 16-2 10 8l-10 10z" fill="%s" stroke="%s" stroke-width="2.6"/>' % (PNK, INK)
    + '<path d="M46 130c10-8 20 8 30 0s20 8 30 0" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % BLU)

ORDER = ["TitlePages", "TitleBook", "TitleTable", "TitleCups", "TitleDrift",
         "TitleQmark", "TitleBubbles", "TitleRainbow", "TitleFridge", "TitleSheet"]

# ── Jua 잘라 넣기 ──
texts = "텔레스트레이션 게임 시작 규칙 기린 ??? 0123456789 ·" + "".join(n + d for n, d, _ in ART.values())
CHARS = "".join(sorted(set(texts)))
f = TTFont(os.path.join(HERE, "..", "public", "jua.woff2"), lazy=False)
o = subset.Options(); o.desubroutinize = True; o.notdef_outline = False; o.layout_features = ["*"]; o.name_IDs = []
sb = subset.Subsetter(options=o); sb.populate(text=CHARS); sb.subset(f)
f.flavor = "woff2"; buf = io.BytesIO(); f.save(buf); f.close()
FACE = "@font-face{font-family:'Jua';src:url(data:font/woff2;base64,%s) format('woff2')}" % base64.b64encode(buf.getvalue()).decode()
print("Jua 조각 %.0f KB, 글자 %d" % (len(buf.getvalue()) / 1024, len(CHARS)))

LOGO = "".join('<b style="color:%s;transform:rotate(%sdeg)">%s</b>' % (c, r, ch) for ch, c, r in
               zip("텔레스트레이션", [RED, ORG, YEL, GRN, SKY, PNK, ORG], [-4, 3, -2, 4, -3, 2, -4]))

TPL = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <style>
    %(face)s
    body { margin: 0; }
    a { color: #e8590c; } a:hover { color: #b34606; }
    .logo b { display: inline-block; font-size: 50px; font-weight: 700; line-height: 1; text-shadow: 2px 2px 0 #3d2b1f; }
  </style>
</helmet>
<div style="width: 390px; height: 470px; overflow: hidden; background: #fff6e0; color: #3d2b1f; font-family: 'Jua', sans-serif; box-sizing: border-box; padding: 16px 14px; display: flex; flex-direction: column; align-items: center; gap: 0; text-align: center;">
  <div style="align-self: flex-start; display: flex; align-items: center; gap: 7px; font-size: 13px;">
    <span style="background: #3d2b1f; color: #fff6e0; width: 22px; height: 22px; border-radius: 50%%; display: inline-flex; align-items: center; justify-content: center;">%(no)s</span>
    <b>%(name)s</b><span style="color: #8a7461;">%(desc)s</span>
  </div>
  <div class="logo" style="display: flex; gap: 7px; margin-top: 10px;">%(logo)s</div>
  <svg viewBox="0 0 280 11" fill="none" style="width: 250px; height: 11px; display: block; margin-top: 2px;"><path d="M3 7C28 2 52 9 78 5s48 5 74 1 47 6 73 2 48 1 48 1" stroke="#e8590c" stroke-width="4" stroke-linecap="round"/></svg>
  <svg viewBox="0 0 380 200" fill="none" style="width: 100%%; display: block; margin-top: 14px; font-family: 'Jua', sans-serif;">%(art)s</svg>
  <div style="margin-top: 14px; background: #51cf66; border: 4px solid #3d2b1f; border-radius: 16px; padding: 9px 46px; font-size: 24px; font-weight: 700; box-shadow: 5px 5px 0 #3d2b1f;">게임 시작</div>
</div>
</x-dc>
</body>
</html>
"""

for n, key in enumerate(ORDER, 1):
    name, desc, art = ART[key]
    io.open(os.path.join(HERE, key + ".dc.html"), "w", encoding="utf-8", newline="\n").write(
        TPL % dict(face=FACE, no=n, name=name, desc=desc, logo=LOGO, art=art))
    print("wrote", key)
