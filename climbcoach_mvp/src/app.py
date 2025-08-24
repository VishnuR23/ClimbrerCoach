import argparse, cv2, numpy as np, yaml, time
from src.perception.pose_tracker import PoseTracker
from src.perception.homography import load_wall_config, img_to_wall_xy
from src.perception.holds_detector import hsv_mask, find_holds
from src.state.contacts import infer_contacts
from src.state.contact_smoother import ContactSmoother
from src.state.anthropometrics import load_anthro
from src.state.com import com_proxy
from src.planner.reachability import ReachModel
from src.planner.greedy_coach import choose_next_move
from src.planner.state_repr import State
from src.planner.successors import all_successors
from src.planner.search_astar import AStarPlanner
from src.planner.cost_models import total_cost
from src.coach.overlay import draw_holds, draw_pose, draw_suggestion
from src.coach.ai_coach import LocalTTSCoach, APICoach, build_payload_from_suggestion
from src.coach.ws_coach import WSCoachClient
from src.utils.logger import SessionLogger

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=str, default='0')
    ap.add_argument('--detector', type=str, default='hsv', choices=['hsv'])
    ap.add_argument('--planner', type=str, default='greedy', choices=['greedy','astar','beam'])
    ap.add_argument('--h_min', type=int, required=True)
    ap.add_argument('--h_max', type=int, required=True)
    ap.add_argument('--s_min', type=int, default=60)
    ap.add_argument('--s_max', type=int, default=255)
    ap.add_argument('--v_min', type=int, default=60)
    ap.add_argument('--v_max', type=int, default=255)
    ap.add_argument('--min_area', type=int, default=80)
    ap.add_argument('--contacts_dist_m', type=float, default=0.35)
    ap.add_argument('--max_expansions', type=int, default=300)
    ap.add_argument('--topk', type=int, default=3)
    ap.add_argument('--ai_coach', type=str, default='off', choices=['off','local','api','ws'])
    ap.add_argument('--api_url', type=str, default=None)
    ap.add_argument('--api_key', type=str, default=None)
    ap.add_argument('--ws_url', type=str, default=None)
    ap.add_argument('--speak_interval_ms', type=int, default=1000)
    ap.add_argument('--log_session', action='store_true')
    args = ap.parse_args()

    source = 0 if args.source == '0' else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print('Cannot open video source. If you passed a placeholder, that is expected. Exiting cleanly.')
        return

    wall_cfg = load_wall_config()
    H = None if wall_cfg is None else np.array(wall_cfg['wall']['H'], dtype=np.float32) if wall_cfg['wall']['H'] is not None else None

    anthro = load_anthro() or {'arm_reach_m':0.8,'dyn_factor':0.15,'leg_length_m':0.9}
    foot_reach = float(anthro.get('leg_length_m', 0.9)) * 0.9
    reach = ReachModel(anthro.get('arm_reach_m',0.8), foot_reach_m=foot_reach, dyn_factor=anthro.get('dyn_factor',0.15))

    # AI coach init
    coach = None
    if args.ai_coach == 'local':
        coach = LocalTTSCoach(speak_interval_sec=max(0.2, args.speak_interval_ms/1000.0), enable=True)
    elif args.ai_coach == 'api':
        coach = APICoach(api_url=args.api_url or "", api_key=args.api_key, speak_interval_sec=max(0.2, args.speak_interval_ms/1000.0), enable=True)
    elif args.ai_coach == 'ws':
        ws_url = args.ws_url or "ws://localhost:8000/ws"
        coach = WSCoachClient(ws_url, speak=True)
        try: coach.start()
        except Exception: coach=None

    pose = PoseTracker()
    smoother = ContactSmoother(switch_patience=3)
    logger = SessionLogger() if args.log_session else None
    frame_idx=0

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Pose
        mp_pts = pose.process(frame)
        named_px = PoseTracker.get_named(mp_pts) if mp_pts is not None else {}
        named_w = {k: (img_to_wall_xy(v, H) if (H is not None and v is not None) else None) for k,v in named_px.items()}

        # Holds
        mask = hsv_mask(frame, args.h_min, args.h_max, args.s_min, args.s_max, args.v_min, args.v_max)
        holds_px = find_holds(mask, min_area=args.min_area)
        holds_w = []
        for h in holds_px:
            holds_w.append(img_to_wall_xy(h['centroid'], H) if H is not None else (h['centroid'][0]/500.0, h['centroid'][1]/500.0))

        # Contacts
        extremities_w = {'LH': named_w.get('left_wrist'),'RH': named_w.get('right_wrist'),'LF': named_w.get('left_ankle'),'RF': named_w.get('right_ankle')}
        raw_contacts = infer_contacts(extremities_w, holds_w, max_dist_m=args.contacts_dist_m)
        contacts = smoother.update(raw_contacts)

        # Draw base
        out = frame.copy()
        out = draw_holds(out, holds_px)
        out = draw_pose(out, named_px)

        text=None; limb_px=None; target_px=None; sug=None

        if args.planner == 'greedy':
            sug, why = choose_next_move(holds_w, contacts, named_w, reach)
            if sug is not None:
                limb_key = 'left_wrist' if sug['limb']=='LH' else 'right_wrist'
                limb_px = named_px.get(limb_key)
                target_px = holds_px[sug['hold_index']]['centroid'] if 0<=sug['hold_index']<len(holds_px) else None
                text = f"{sug['limb']} -> H{sug['hold_index']} | {why}"

        else:
            # A* / Beam simplified to A* single-step pick
            s0 = State(LH=contacts.get('LH') if contacts.get('LH') is not None else -1,
                       RH=contacts.get('RH') if contacts.get('RH') is not None else -1,
                       LF=contacts.get('LF') if contacts.get('LF') is not None else -1,
                       RF=contacts.get('RF') if contacts.get('RF') is not None else -1)
            if -1 in [s0.LH, s0.RH, s0.LF, s0.RF]:
                pass
            else:
                LH_pos = named_w.get('left_wrist'); RH_pos = named_w.get('right_wrist')
                LF_pos = named_w.get('left_ankle'); RF_pos = named_w.get('right_ankle')
                reachable={'LH':[],'RH':[],'LF':[],'RF':[]}
                for i,h in enumerate(holds_w):
                    if reach.hand_within_reach(LH_pos,h)[0]: reachable['LH'].append(i)
                    if reach.hand_within_reach(RH_pos,h)[0]: reachable['RH'].append(i)
                    if reach.foot_within_reach(LF_pos,h)[0]: reachable['LF'].append(i)
                    if reach.foot_within_reach(RF_pos,h)[0]: reachable['RF'].append(i)

                def state_hands_xy(st):
                    lh = holds_w[st.LH] if st.LH>=0 else None
                    rh = holds_w[st.RH] if st.RH>=0 else None
                    return lh,rh
                def state_feet_xy(st):
                    lf = holds_w[st.LF] if st.LF>=0 else None
                    rf = holds_w[st.RF] if st.RF>=0 else None
                    return lf,rf

                com_xy = com_proxy({'left_shoulder':named_w.get('left_shoulder'),'right_shoulder':named_w.get('right_shoulder'),'left_hip':named_w.get('left_hip'),'right_hip':named_w.get('right_hip')})

                def successors_fn(st): return all_successors(st, reachable, allow_hand_match=True, allow_foot_match=False)
                def cost_fn(s_prev, action, s_next):
                    limb, j = action
                    prev_h = state_hands_xy(s_prev)
                    next_h = state_hands_xy(s_next)
                    from_xy = None
                    if limb=='LH': from_xy = prev_h[0]
                    elif limb=='RH': from_xy = prev_h[1]
                    elif limb=='LF': from_xy = state_feet_xy(s_prev)[0]
                    else: from_xy = state_feet_xy(s_prev)[1]
                    to_xy = holds_w[j]
                    reach_d = (np.linalg.norm(np.array(from_xy)-np.array(to_xy)) if (from_xy is not None and to_xy is not None) else 0.4)
                    return total_cost(prev_h, next_h, com_xy, state_feet_xy(s_next), reach_d, next_state=s_next)
                def heuristic_fn(st):
                    lh,rh = state_hands_xy(st)
                    ys=[p[1] for p in [lh,rh] if p is not None]
                    return ys and min(ys) or 0.0
                def goal_test(st):
                    lh,rh = state_hands_xy(st)
                    ys=[p[1] for p in [lh,rh] if p is not None]
                    return (len(ys)>0 and min(ys)<=0.05)

                planner = AStarPlanner(successors_fn, cost_fn, heuristic_fn)
                path = planner.plan(s0, goal_test, max_expansions=args.max_expansions)
                if len(path)>0:
                    action, s1 = path[0]
                    limb,j = action
                    sug = {'limb': limb, 'hold_index': j, 'target_xy': holds_w[j], 'score': 0.9}
                    limb_key = 'left_wrist' if limb=='LH' else 'right_wrist' if limb in ('RH',) else 'left_ankle' if limb=='LF' else 'right_ankle'
                    limb_px = named_px.get(limb_key)
                    target_px = holds_px[j]['centroid'] if 0<=j<len(holds_px) else None
                    text = f"{limb} -> H{j} | A*"

        out = draw_suggestion(out, limb_px, target_px, text)

        # AI Coach hook
        if coach is not None and sug is not None and target_px is not None:
            dx=dy=0.0
            target_xy = sug.get('target_xy')
            limb_xy = None
            if sug['limb']=='LH': limb_xy = named_w.get('left_wrist')
            elif sug['limb']=='RH': limb_xy = named_w.get('right_wrist')
            elif sug['limb']=='LF': limb_xy = named_w.get('left_ankle')
            elif sug['limb']=='RF': limb_xy = named_w.get('right_ankle')
            if limb_xy is not None and target_xy is not None:
                dx = float(target_xy[0]-limb_xy[0]); dy = float(limb_xy[1]-target_xy[1])
            meta_payload = {"grade":"N/A","com_margin":0.0,"dyn_factor":0.0,"hands_xy":[named_w.get('left_wrist'),named_w.get('right_wrist')],"feet_xy":[named_w.get('left_ankle'),named_w.get('right_ankle')],"topk":[], "dx_m":dx, "dy_m":dy, "micro_tip":""}
            payload = build_payload_from_suggestion(sug, meta_payload)
            try:
                coach.enqueue(payload)
            except Exception: pass

        cv2.imshow("ClimbCoach", out)
        key = cv2.waitKey(1)&0xFF
        if key==ord('q'): break

        if logger:
            logger.log_frame(frame_idx, {"pose":0,"holds":0,"planner":0}, named_w, holds_w, contacts, sug)
        frame_idx+=1

    cap.release(); cv2.destroyAllWindows()
    if logger: logger.close()

if __name__ == '__main__':
    main()
