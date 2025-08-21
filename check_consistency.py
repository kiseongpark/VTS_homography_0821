# check_consistency.py
import numpy as np, csv

H_PATHS = {
    1: "H_cam1.npy",
    2: "H_cam2.npy",
    3: "H_cam3.npy",
    4: "H_cam4.npy",
}

# 각 카메라에서 측정한 동일 '정지 기준점'들의 픽셀 좌표 파일 (undistort 영상 기준)
# 형식: id,u,v  (id는 world_points.csv와 동일 라벨)
PIX_CSVS = {
    1: "cam1_check_pix.csv",
    2: "cam2_check_pix.csv",
    3: "cam3_check_pix.csv",
    4: "cam4_check_pix.csv",
}

WORLD_CSV = "world_points.csv"  # 실측 좌표(진실값) 비교용, 선택

def load_csv_dict(path):
    rows = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows[r['id']] = (float(r.get('u',0.0)), float(r.get('v',0.0)))
    return rows

def load_world(path):
    rows = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows[r['id']] = (float(r['X']), float(r['Y']))
    return rows

def px_to_world(uv, H):
    u,v = uv
    w = H @ np.array([u,v,1.0], dtype=np.float32)
    return (float(w[0]/w[2]), float(w[1]/w[2]))

if __name__ == "__main__":
    Hs = {cid: np.load(p) for cid,p in H_PATHS.items()}
    pix = {cid: load_csv_dict(csvp) for cid,csvp in PIX_CSVS.items()}
    truth = load_world(WORLD_CSV)

    # 공통 id 집합
    ids = set.intersection(*(set(p.keys()) for p in pix.values()))
    ids = sorted(list(ids))
    print("[INFO] 공통 기준점 수:", len(ids), ids)

    # 각 id에 대해 카메라별 월드 좌표 계산
    diffs = []
    for pid in ids:
        ws = []
        for cid in Hs:
            uv = pix[cid][pid]
            w  = px_to_world(uv, Hs[cid])
            ws.append((cid, w))
        # 카메라쌍 평균 거리
        pair_d = []
        for i in range(len(ws)):
            for j in range(i+1, len(ws)):
                d = np.hypot(ws[i][1][0]-ws[j][1][0], ws[i][1][1]-ws[j][1][1])
                pair_d.append(d)
        mean_pair = np.mean(pair_d) if pair_d else 0.0
        max_pair  = np.max(pair_d)  if pair_d else 0.0

        # 진실값(있다면)과 평균 거리
        gt = truth.get(pid, None)
        gt_err = None
        if gt:
            gt_err = np.mean([np.hypot(w[0]-gt[0], w[1]-gt[1]) for _,w in ws])

        print(f"ID {pid}: mean_pair={mean_pair:.3f} m, max_pair={max_pair:.3f} m, gt_err={gt_err:.3f} m" if gt else
              f"ID {pid}: mean_pair={mean_pair:.3f} m, max_pair={max_pair:.3f} m")
        diffs += pair_d

    if diffs:
        print(f"\n[OVERALL] 카메라간 평균 거리 = {np.mean(diffs)*100:.1f} cm | 최대 = {np.max(diffs)*100:.1f} cm")
