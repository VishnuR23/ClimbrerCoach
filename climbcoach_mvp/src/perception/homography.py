import cv2, yaml, numpy as np, os

CFG_PATH = "config/wall.yml"

def save_wall_config(H, width_m, height_m):
    data = {"wall": {"H": H.tolist() if H is not None else None, "width_m": float(width_m), "height_m": float(height_m)}}
    with open(CFG_PATH, "w") as f:
        yaml.safe_dump(data, f)

def load_wall_config():
    if not os.path.exists(CFG_PATH):
        return None
    with open(CFG_PATH, "r") as f:
        return yaml.safe_load(f)

def img_to_wall_xy(pt, H):
    if pt is None or H is None: return None
    x, y = pt
    p = np.array([x, y, 1.0], dtype=np.float32)
    q = H @ p
    q = q / (q[2] + 1e-6)
    return float(q[0]), float(q[1])
