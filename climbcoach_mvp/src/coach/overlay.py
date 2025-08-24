import cv2

def draw_holds(img, holds):
    for h in holds:
        cx,cy = h['centroid']
        cv2.circle(img, (cx,cy), 6, (0,255,0), 2)
    return img

def draw_pose(img, named_px):
    for k,p in named_px.items():
        if p is None: continue
        cv2.circle(img, p, 5, (255,0,0), -1)
    return img

def draw_suggestion(img, limb_px, target_px, text):
    if limb_px is not None and target_px is not None:
        cv2.arrowedLine(img, limb_px, target_px, (0,255,255), 3, tipLength=0.2)
    if text:
        cv2.rectangle(img, (10,10), (10+540, 50), (20,20,20), -1)
        cv2.putText(img, text, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    return img
