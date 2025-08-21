# collect_points_click_scaled.py
# - 큰 이미지를 화면에 맞춰 축소 표시
# - 클릭 좌표는 원본 해상도로 환산해서 CSV에 저장
# - ESC: 종료, Backspace: 마지막 클릭 되돌리기

import cv2
import csv
import numpy as np
import os

IMG_PATH   = "test24.jpg"        # undistort된 이미지
WORLD_CSV  = "world_points.csv"   # id,X,Y (UTF-8/UTF-8-SIG)
OUT_PIX_CSV= "cam1_pix.csv"       # id,u,v 저장

# =========================
# 0) 세계좌표 id 목록 로드
# =========================
ids = []
with open(WORLD_CSV, newline='', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        ids.append(r["id"])
if len(ids) < 4:
    raise SystemExit("[ERR] 최소 4개 이상의 기준점이 필요합니다.")
print("[INFO] 클릭 순서:", ids)

# =========================
# 1) 이미지 로드
# =========================
img = cv2.imread(IMG_PATH)
if img is None:
    raise SystemExit(f"[ERR] 이미지 로드 실패: {IMG_PATH}")
H, W = img.shape[:2]

# =========================
# 2) 보기용 축소 비율 계산
# =========================
MAX_WIN_W = 1280   # 원하는 창 가로
MAX_WIN_H = 800    # 원하는 창 세로
scale = min(MAX_WIN_W / W, MAX_WIN_H / H, 1.0)  # 1.0 초과 금지(확대 X)

disp = cv2.resize(img, (int(W*scale), int(H*scale))) if scale < 1.0 else img.copy()

# (선택) 시작 창 위치/크기 지정
win_name = "click points (ESC: 종료, Backspace: 되돌리기)"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, disp.shape[1], disp.shape[0])
cv2.moveWindow(win_name, 60, 40)

# =========================
# 3) 마우스 콜백
# =========================
clicks = []        # [(id, u_orig, v_orig)]
screen_marks = []  # [(x_disp, y_disp, label)]
idx = 0            # 다음 클릭할 id 인덱스

def on_mouse(event, x, y, flags, param):
    global idx, disp, clicks, screen_marks
    if event == cv2.EVENT_LBUTTONDOWN and idx < len(ids):
        # 화면 좌표 -> 원본 좌표 환산
        u_orig = int(round(x / scale))
        v_orig = int(round(y / scale))
        pid = ids[idx]

        clicks.append((pid, u_orig, v_orig))
        screen_marks.append((x, y, pid))
        idx += 1

cv2.setMouseCallback(win_name, on_mouse)

# =========================
# 4) 루프(그리기/키 입력)
# =========================
while True:
    frame = disp.copy()
    # 헤더 안내
    header = f"다음 포인트: {ids[idx] if idx < len(ids) else '완료'}  |  {idx}/{len(ids)}"
    cv2.rectangle(frame, (0,0), (frame.shape[1], 34), (0,0,0), -1)
    cv2.putText(frame, header, (10,24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

    # 찍은 점들 표시(축소 좌표)
    for (xd, yd, label) in screen_marks:
        cv2.circle(frame, (int(xd), int(yd)), 6, (0,0,255), -1)
        cv2.putText(frame, label, (int(xd)+8, int(yd)-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2, cv2.LINE_AA)

    cv2.imshow(win_name, frame)
    k = cv2.waitKey(20) & 0xFF

    if k == 27:        # ESC
        break
    elif k == 8:       # Backspace: 마지막 클릭 취소
        if clicks:
            clicks.pop()
            screen_marks.pop()
            idx = max(0, idx-1)
    elif idx == len(ids):
        # 모든 포인트 입력 완료
        break

cv2.destroyAllWindows()

if idx < len(ids):
    raise SystemExit("[ERR] 모든 포인트를 클릭하지 않았어요. (ESC로 종료됨)")

# =========================
# 5) CSV 저장(원본 좌표)
# =========================
os.makedirs(os.path.dirname(OUT_PIX_CSV) or ".", exist_ok=True)
with open(OUT_PIX_CSV, "w", newline='', encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id","u","v"])
    for pid, u, v in clicks:
        w.writerow([pid, u, v])

print(f"[OK] 픽셀 좌표 저장: {OUT_PIX_CSV}")
print("[TIP] 다음 단계: estimate_H.py로 H 계산 후 RMSE(cm) 확인하세요.")
