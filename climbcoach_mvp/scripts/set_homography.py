import cv2, numpy as np, argparse
from src.perception.homography import save_wall_config

ap=argparse.ArgumentParser()
ap.add_argument('--source', default='0')
ap.add_argument('--width_m', type=float, required=True)
ap.add_argument('--height_m', type=float, required=True)
args=ap.parse_args()

cap = cv2.VideoCapture(0 if args.source=='0' else args.source)
ok, frame = cap.read()
if not ok: raise SystemExit("Cannot read source")
pts=[]
def onclick(e,x,y,flags,param):
    if e==cv2.EVENT_LBUTTONDOWN and len(pts)<4:
        pts.append((x,y))
        cv2.circle(frame,(x,y),5,(0,0,255),-1)
        cv2.imshow("click 4 corners (TL,TR,BR,BL)", frame)

cv2.imshow("click 4 corners (TL,TR,BR,BL)", frame)
cv2.setMouseCallback("click 4 corners (TL,TR,BR,BL)", onclick)
print("Click TL, TR, BR, BL then press 's' to save.")
while True:
    key=cv2.waitKey(10)&0xFF
    if key==ord('s') and len(pts)==4: break
    if key==27: break
cv2.destroyAllWindows()
if len(pts)!=4: raise SystemExit("Need 4 points")
src=np.array(pts, dtype=np.float32)
dst=np.array([[0,0],[args.width_m,0],[args.width_m,args.height_m],[0,args.height_m]], dtype=np.float32)
H, _ = cv2.findHomography(src, dst)
save_wall_config(H, args.width_m, args.height_m)
print("Saved homography to config/wall.yml")
