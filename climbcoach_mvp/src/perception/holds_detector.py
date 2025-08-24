import cv2, numpy as np

def hsv_mask(frame_bgr, h_min, h_max, s_min, s_max, v_min, v_max):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.medianBlur(mask, 5)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask

def find_holds(mask, min_area=80):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    holds = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0: 
            continue
        cx = int(M["m10"]/M["m00"]); cy = int(M["m01"]/M["m00"])
        holds.append({"centroid": (cx, cy), "area": area})
    return holds
