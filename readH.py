import numpy as np

# H_cam1.npy 읽기
H = np.load("H_cam4.npy")
print(H)
print("shape:", H.shape)  # (3, 3)일 것

# 예: 픽셀 좌표 → 월드 좌표 변환
def pixel_to_world(uv, H):
    u, v = uv
    w = H @ np.array([u, v, 1.0], dtype=np.float32)
    return (float(w[0]/w[2]), float(w[1]/w[2]))

ground_uv = (1234.5, 845.2)  # 픽셀 좌표(undistort 기준)
X, Y = pixel_to_world(ground_uv, H)
print("월드 좌표:", X, Y)
