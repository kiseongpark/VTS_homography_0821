# estimate_H.py
import csv, cv2, numpy as np, sys
from collections import OrderedDict

WORLD_CSV = "world_points.csv"   # id,X,Y
PIX_CSV   = "cam2_pix.csv"       # id,u,v
OUT_H_NPY = "H_cam2.npy"

def normalize_header(h):
    # BOM 제거, 공백 제거, 소문자
    return h.replace("\ufeff", "").strip().lower()

def read_csv_as_dict(csv_path):
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        # 헤더 정규화
        field_map = {h: normalize_header(h) for h in reader.fieldnames}
        rows = []
        for r in reader:
            nr = {}
            for k, v in r.items():
                nk = field_map[k]
                nr[nk] = v.strip() if isinstance(v, str) else v
            rows.append(nr)
    return rows

def load_points(pix_csv, world_csv):
    wld_rows = read_csv_as_dict(world_csv)
    pix_rows = read_csv_as_dict(pix_csv)

    # 필수 컬럼 체크(여러 이름 허용)
    def pick(row, *candidates):
        for c in candidates:
            c2 = normalize_header(c)
            if c2 in row:
                return row[c2]
        raise KeyError(f"필수 컬럼 {candidates} 중 하나가 없음. 실제 키: {list(row.keys())}")

    world = OrderedDict()
    for r in wld_rows:
        pid = pick(r, 'id', 'name')
        X   = float(pick(r, 'x'))
        Y   = float(pick(r, 'y'))
        world[pid] = (X, Y)

    pix = OrderedDict()
    for r in pix_rows:
        pid = pick(r, 'id', 'name')
        u   = float(pick(r, 'u'))
        v   = float(pick(r, 'v'))
        pix[pid] = (u, v)

    # 교집합 id로 조인
    ids = [i for i in world.keys() if i in pix]
    if len(ids) < 4:
        raise RuntimeError(f"조인된 포인트가 4개 미만입니다. 공통 id 수: {len(ids)} (world:{len(world)} / pix:{len(pix)})")

    pix_pts = np.array([pix[i]   for i in ids], dtype=np.float32)
    wld_pts = np.array([world[i] for i in ids], dtype=np.float32)
    return pix_pts, wld_pts, ids

def project_points(H, pix_pts):
    pts = np.hstack([pix_pts, np.ones((len(pix_pts),1), np.float32)])
    w = (H @ pts.T).T
    w = w[:, :2] / w[:, 2:3]
    return w

if __name__ == "__main__":
    try:
        pix_pts, wld_pts, ids = load_points(PIX_CSV, WORLD_CSV)
        print(f"[INFO] 공통 id 개수: {len(ids)} → {ids[:10]}{' ...' if len(ids)>10 else ''}")
        H, mask = cv2.findHomography(pix_pts, wld_pts, method=cv2.RANSAC, ransacReprojThreshold=3.0)
        if H is None:
            raise RuntimeError("findHomography 실패 (H=None). 점 분포/중복/직선상 배치 여부 확인 필요.")
        np.save(OUT_H_NPY, H)
        print(f"[OK] H 저장: {OUT_H_NPY}")

        # RMSE 검증
        pred   = project_points(H, pix_pts)
        err    = pred - wld_pts
        dists  = np.sqrt((err**2).sum(axis=1))
        rmse_m = float(dists.mean())
        max_m  = float(dists.max())
        used   = int(mask.sum()) if mask is not None else len(ids)
        print(f"[RMSE] {rmse_m*100:.1f} cm  |  [MAX] {max_m*100:.1f} cm  |  사용점수 {used}/{len(ids)}")

    except Exception as e:
        print("[ERROR]", e)
        # 디버깅용: 헤더 프린트
        try:
            import io
            with open(WORLD_CSV, 'r', encoding='utf-8-sig') as f:
                head = f.readline().strip()
                print(f"[DEBUG] world 헤더: {head}")
            with open(PIX_CSV, 'r', encoding='utf-8-sig') as f:
                head = f.readline().strip()
                print(f"[DEBUG] pix 헤더:   {head}")
        except Exception as e2:
            print("[DEBUG] 헤더 읽기 실패:", e2)
        sys.exit(1)
