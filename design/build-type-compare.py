# -*- coding: utf-8 -*-
"""
서체 비교 페이지 한 장을 만든다.

구글 폰트를 링크로 불러오면 인터넷이 막히거나 느린 데서는 전부 기본 글꼴로 떨어져
열 벌이 똑같아 보인다. 그래서 화면에 쓰는 글자만 잘라내(subset) 파일 안에 박아 넣는다.
한글 폰트는 통째로 넣으면 한 벌에 몇 MB 씩이지만, 쓰는 글자 백여 개만 남기면 10KB 안팎이다.
"""
import io, os, re, base64, urllib.request
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))

# 화면에 실제로 나오는 글자들. 여기 없는 글자는 잘려 나가 안 보인다
SAMPLE = """텔레스트레이션 사면초가 이 말을 그리세요
넷 모였습니다. 넷부터 시작할 수 있고 열까지 들어옵니다.
다 그렸어요! 되돌리기 전부 지우기 이걸로 냅니다
제시어 난이도 쉬움 보통 어려움 점수 셈법 즐겁게 겨루기
낙서봇 한 바퀴 돌아옴 점 라운드 권 초 남음 방장 시작
고른 말 그림 추측 별 맞힘 합계 초대 링크 복사 한 판 더
0123456789 NPW3ABCDEFGHIJKLMNOPQRSTUVWXYZ ★☆·—…!?.,()/+"""
CHARS = "".join(sorted(set(SAMPLE)))

# (표시이름, css2 인자)
FAMS = [
    ("Gaegu",            "Gaegu:wght@400;700"),
    ("Hi Melody",        "Hi+Melody"),
    ("Jua",              "Jua"),
    ("Do Hyeon",         "Do+Hyeon"),
    ("Gowun Dodum",      "Gowun+Dodum"),
    ("Black Han Sans",   "Black+Han+Sans"),
    ("Nanum Pen Script", "Nanum+Pen+Script"),
    ("Gamja Flower",     "Gamja+Flower"),
    ("Poor Story",       "Poor+Story"),
    ("Yeon Sung",        "Yeon+Sung"),
    ("Kirang Haerang",   "Kirang+Haerang"),
    ("Gothic A1",        "Gothic+A1:wght@400;700"),
    ("Noto Sans KR",     "Noto+Sans+KR:wght@400;700"),
]

# UA 를 아예 안 보내면 구글이 굵기마다 통짜 ttf 를 준다.
# 요즘 브라우저인 척하면 한글을 유니코드 구간별로 178 조각 낸 woff2 가 와서 쓰기 어렵고,
# IE6 인 척하면 EOT 가 온다. 안 보내는 게 제일 낫다.
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url), timeout=60).read()


def faces_of(spec):
    """@font-face 덩어리마다 (굵기, 글꼴파일 주소) 를 뽑아 온다"""
    css = fetch("https://fonts.googleapis.com/css2?family=%s&display=swap" % spec).decode("utf-8")
    out = []
    for block in css.split("@font-face")[1:]:
        w = re.search(r"font-weight:\s*(\d+)", block)
        u = re.search(r"url\((https://[^)]+)\)", block)
        if u:
            out.append((int(w.group(1)) if w else 400, u.group(1)))
    # 같은 굵기가 여러 번 나오면(유니코드 구간별로 쪼갠 경우) 첫 것만
    seen, uniq = set(), []
    for w, u in out:
        if w in seen:
            continue
        seen.add(w)
        uniq.append((w, u))
    return uniq


def cut(raw):
    """쓰는 글자만 남기고 woff2 로 줄인다. 윈도우에서 파일이 잠기지 않게 메모리에서만 다룬다"""
    font = TTFont(io.BytesIO(raw), lazy=False)
    opts = subset.Options()
    opts.desubroutinize = True
    opts.notdef_outline = False
    opts.layout_features = ["*"]
    opts.name_IDs = []
    s = subset.Subsetter(options=opts)
    s.populate(text=CHARS)
    s.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    font.close()
    return buf.getvalue()


faces_css = []
total = 0
for name, spec in FAMS:
    for weight, url in faces_of(spec):
        raw = fetch(url)
        small = cut(raw)
        total += len(small)
        b64 = base64.b64encode(small).decode("ascii")
        faces_css.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}" % (name, weight, b64)
        )
        print("  %-18s %3d  %6.1f KB  (원본 %6.1f KB)" % (name, weight, len(small) / 1024, len(raw) / 1024))

print("합계 %.0f KB, 글자 %d 자" % (total / 1024, len(CHARS)))

io.open(os.path.join(HERE, "_faces.css"), "w", encoding="utf-8").write("\n".join(faces_css))
print("→ _faces.css")
