import cv2, yaml, argparse
from src.perception.pose_tracker import PoseTracker

ap=argparse.ArgumentParser()
ap.add_argument('--source', default='0')
args=ap.parse_args()

cap = cv2.VideoCapture(0 if args.source=='0' else args.source)
pose=PoseTracker()
print("T-pose then press 'c' to capture.")
wingspans=[]; leglens=[]
while True:
    ok, frame = cap.read()
    if not ok: break
    pts = pose.process(frame)
    named = PoseTracker.get_named(pts) if pts is not None else {}
    if named.get('left_wrist') and named.get('right_wrist'):
        x1,_=named['left_wrist']; x2,_=named['right_wrist']
        wingspans.append(abs(x2-x1)/500.0)  # naive pixels->meters guess; user can edit later
    if named.get('left_hip') and named.get('left_ankle'):
        _,y1=named['left_hip']; _,y2=named['left_ankle']
        leglens.append(abs(y2-y1)/500.0)
    cv2.imshow("Calibration", frame)
    key=cv2.waitKey(1)&0xFF
    if key==ord('c'): break
with open("config/anthro.yml","w") as f:
    yaml.safe_dump({
        "wingspan_m": float(sum(wingspans)/max(1,len(wingspans)) or 1.7),
        "leg_length_m": float(sum(leglens)/max(1,len(leglens)) or 0.9),
        "arm_reach_m": float(0.47*(sum(wingspans)/max(1,len(wingspans)) or 1.7)),
        "dyn_factor": 0.15
    }, f)
print("Saved config/anthro.yml")
