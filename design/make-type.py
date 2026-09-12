# -*- coding: utf-8 -*-
"""서체 시안 열 장을 찍어 낸다. 크레용 차림은 그대로 두고 글자만 갈아 끼운다."""
import io, os

# (파일이름, 번호, 제목서체, 본문서체, 구글폰트 인자들, 크기배, 한 줄 설명, 걸리는 점)
PAIRS = [
    ("TypeGaegu",     1, "Gaegu",            "Hi Melody",        ["Gaegu:wght@400;700", "Hi+Melody"],
     1.00, "지금 쓰는 것. 연필로 눌러쓴 공책 글씨", "획이 가늘어 작은 글자가 흐려집니다"),
    ("TypeJua",       2, "Jua",              "Gaegu",            ["Jua", "Gaegu:wght@400;700"],
     0.94, "둥글고 통통한 글씨. 크레용 두께와 잘 맞습니다", "길어지면 글자가 다 비슷해 보입니다"),
    ("TypeDoHyeon",   3, "Do Hyeon",         "Gowun Dodum",      ["Do+Hyeon", "Gowun+Dodum"],
     0.94, "각지고 또렷합니다. 멀리서도 읽힙니다", "손맛이 없어 그림과 조금 따로 놉니다"),
    ("TypeBlackHan",  4, "Black Han Sans",   "Jua",              ["Black+Han+Sans", "Jua"],
     0.90, "제목이 아주 굵습니다. 제시어가 쿵 박힙니다", "굵기가 하나뿐이라 강약을 못 줍니다"),
    ("TypePen",       5, "Nanum Pen Script", "Gaegu",            ["Nanum+Pen+Script", "Gaegu:wght@400;700"],
     1.22, "사인펜으로 슥슥 쓴 글씨", "아주 작게 쓰면 읽기 어렵습니다"),
    ("TypeGamja",     6, "Gamja Flower",     "Gowun Dodum",      ["Gamja+Flower", "Gowun+Dodum"],
     1.12, "삐뚤빼뚤 어린이 글씨. 못 그려도 되는 판과 결이 같습니다", "진지한 안내문까지 장난스러워집니다"),
    ("TypePoor",      7, "Poor Story",       "Gowun Dodum",      ["Poor+Story", "Gowun+Dodum"],
     1.10, "동화책에서 본 듯한 글씨", "받침 많은 낱말이 좁아 보입니다"),
    ("TypeYeon",      8, "Yeon Sung",        "Jua",              ["Yeon+Sung", "Jua"],
     1.02, "두툼한 붓으로 눌러쓴 글씨", "숫자가 뭉툭해 시계가 덜 또렷합니다"),
    ("TypeKirang",    9, "Kirang Haerang",   "Gowun Dodum",      ["Kirang+Haerang", "Gowun+Dodum"],
     1.08, "옛 간판 붓글씨. 나이 든 결이 섞입니다", "크레용보다 어른스러워 따로 놉니다"),
    ("TypeGothic",   10, "Gothic A1",        "Noto Sans KR",     ["Gothic+A1:wght@400;700;800", "Noto+Sans+KR:wght@400;500;700"],
     0.92, "손글씨를 아예 뺀 대조군. 글자는 제일 잘 읽힙니다", "크레용 그림과 성격이 어긋납니다"),
]

LOGO = ["텔", "레", "스", "트", "레", "이", "션"]
LOGO_COLORS = ["#e03131", "#e8590c", "#ffd43b", "#51cf66", "#74c0fc", "#f06595", "#e8590c"]
LOGO_ROT = [-4, 3, -2, 4, -3, 2, -4]

TPL = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
  <style>
    body {{ margin: 0; }}
    a {{ color: #e8590c; }} a:hover {{ color: #b34606; }}
  </style>
</helmet>

<div style="width: 390px; height: 620px; overflow: hidden; background: #fff6e0; color: #3d2b1f; box-sizing: border-box; padding: 18px 16px; display: flex; flex-direction: column; gap: 11px; font-family: {body};">

  <div style="display: flex; align-items: baseline; gap: 7px;">
    <div style="background: #3d2b1f; color: #fff6e0; font-size: 13px; font-weight: 700; width: 23px; height: 23px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex: none;">{no}</div>
    <div style="font-size: 14px; font-weight: 700;">{title} + {bodyname}</div>
  </div>

  <div style="display: flex; align-items: flex-end; gap: 1px; font-family: {display}; line-height: 1;">
{logo}
  </div>
  <svg viewBox="0 0 280 11" fill="none" style="display: block; width: 74%; height: 10px; margin-top: -3px;">
    <path d="M3 7C28 2 52 9 78 5s48 5 74 1 47 6 73 2 48 1 48 1" stroke="#e8590c" stroke-width="4" stroke-linecap="round"/>
  </svg>

  <div style="display: flex; align-items: center; gap: 7px;">
    <div style="background: #fff; border: 3px solid #3d2b1f; border-radius: 999px; padding: 0 11px; font-size: {s15}px; font-weight: 700; box-shadow: 2px 2px 0 #3d2b1f; letter-spacing: .16em;">NPW3</div>
    <div style="background: #fff; border: 3px solid #3d2b1f; border-radius: 999px; padding: 0 11px; font-size: {s15}px; font-weight: 700; box-shadow: 2px 2px 0 #3d2b1f;">2 / 4라운드</div>
    <div style="margin-left: auto; background: #ffd43b; border: 3px solid #3d2b1f; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-family: {display}; font-size: {s22}px; font-weight: 700; transform: rotate(5deg); box-shadow: 3px 3px 0 #3d2b1f; flex: none;">47</div>
  </div>

  <div style="background: #74c0fc; border: 3px solid #3d2b1f; border-radius: 16px; padding: 10px; text-align: center; box-shadow: 4px 4px 0 #3d2b1f; transform: rotate(.7deg);">
    <div style="font-size: {s16}px; color: #194663;">이 말을 그리세요</div>
    <div style="font-family: {display}; font-size: {s34}px; font-weight: 700; line-height: 1.15; color: #fff; text-shadow: 2px 2px 0 #3d2b1f;">사면초가</div>
  </div>

  <div style="font-size: {s17}px; color: #8a7461;">넷 모였습니다. 넷부터 시작할 수 있고 열까지 들어옵니다.</div>

  <div style="background: #51cf66; border: 4px solid #3d2b1f; border-radius: 16px; text-align: center; font-family: {display}; font-size: {s24}px; font-weight: 700; padding: 9px; box-shadow: 5px 5px 0 #3d2b1f;">다 그렸어요!</div>

  <div style="border-top: 3px dotted #e0d2b8; padding-top: 8px; display: flex; align-items: baseline;">
    <div style="font-size: {s18}px; font-weight: 700;">1. 낙서봇</div>
    <div style="font-size: {s14}px; color: #8a7461; margin-left: 5px;">★3 · 한 바퀴 돌아옴</div>
    <div style="margin-left: auto; font-family: {display}; font-size: {s22}px; font-weight: 700;">4점</div>
  </div>

  <div style="margin-top: auto; font-size: {s14}px; line-height: 1.45;">
    <div style="color: #3d2b1f;">{good}</div>
    <div style="color: #b08a6a;">걸리는 점 — {bad}</div>
  </div>
</div>
</x-dc>
</body>
</html>
"""

here = os.path.dirname(os.path.abspath(__file__))
for name, no, disp, body, fams, scale, good, bad in PAIRS:
    logo = "\n".join(
        '    <span style="font-size: %dpx; font-weight: 700; color: %s; display: inline-block; '
        'transform: rotate(%ddeg); text-shadow: 2px 2px 0 #3d2b1f;">%s</span>'
        % (round(38 * scale), LOGO_COLORS[i], LOGO_ROT[i], ch)
        for i, ch in enumerate(LOGO))

    q = lambda f: '"%s", "Apple SD Gothic Neo", sans-serif' % f
    out = TPL.format(
        fonts="&".join("family=" + f for f in fams),
        display=q(disp), body=q(body), bodyname=body, title=disp, no=no,
        logo=logo, good=good, bad=bad,
        s14=round(14 * scale), s15=round(15 * scale), s16=round(16 * scale),
        s17=round(17 * scale), s18=round(18 * scale), s22=round(22 * scale),
        s24=round(24 * scale), s34=round(34 * scale),
    )
    io.open(os.path.join(here, name + ".dc.html"), "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", name + ".dc.html")
