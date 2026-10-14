"""Development-only candidate and confirmation audit; target masks never rank proposals."""
from pathlib import Path
import argparse, collections, hashlib, json, cv2, numpy as np
from resolver import Resolver

def proposals(frame, anchor, per_scale=20):
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY); template=cv2.cvtColor(anchor,cv2.COLOR_BGR2GRAY)
    hist=Resolver.histogram(anchor); candidates=[]
    for scale in (.8,1.,1.25):
        h,w=template.shape; w=max(5,round(w*scale)); h=max(5,round(h*scale))
        if h>=gray.shape[0] or w>=gray.shape[1]: continue
        scores=cv2.matchTemplate(gray,cv2.resize(template,(w,h)),cv2.TM_CCOEFF_NORMED)
        for _ in range(per_scale):
            _,ncc,_,(x,y)=cv2.minMaxLoc(scores)
            if ncc<=-1: break
            color=float(cv2.compareHist(hist,Resolver.histogram(frame[y:y+h,x:x+w]),cv2.HISTCMP_CORREL))
            candidates.append(dict(xy=[x+w/2,y+h/2],score=.7*ncc+.3*color,scale=scale,ncc=ncc,color=color))
            scores[max(0,y-h//2):y+h//2+1,max(0,x-w//2):x+w//2+1]=-1
    candidates.sort(key=lambda c:-c['score'])
    unique=[]
    for c in candidates:
        if all(np.linalg.norm(np.array(c['xy'])-p['xy'])>=max(3,min(template.shape)*.25) for p in unique): unique.append(c)
    return unique[:20]

def run(root, project):
    research=project/'research'; research.mkdir(exist_ok=True)
    endpoints=json.loads((project/'results/endpoint_results.json').read_text())
    traces=json.loads((project/'results/traces.json').read_text())
    index={(r['clip'],r['frame']):r for r in endpoints if r['method']=='resolver'}
    inventory=[]; records=[]; rejected=collections.Counter(); frame_disagreements=0; frame_count=0
    for video in sorted(root.rglob('*.mp4')):
        qs=sorted(video.parent.glob(video.stem+'_*_query.png'),key=lambda p:int(p.stem.split('_')[-2]))
        ts=sorted(video.parent.glob(video.stem+'_*_snitch.png'),key=lambda p:int(p.stem.split('_')[-2]))
        qframe=int(qs[0].stem.split('_')[-2]) if qs else None
        eligible=[p for p in ts if qframe is not None and int(p.stem.split('_')[-2])>qframe]
        reason='eligible' if eligible else ('missing_query' if not qs else 'no_later_target_mask')
        row=dict(video=str(video.relative_to(root)),sha256=hashlib.sha256(video.read_bytes()).hexdigest(),queries=len(qs),target_masks=len(ts),eligible_endpoints=len(eligible),status=reason)
        inventory.append(row)
        if not eligible: continue
        mask=cv2.resize(cv2.imread(str(qs[0]),0),(320,240),interpolation=cv2.INTER_NEAREST)
        yy,xx=np.where(mask>127)
        if not len(xx): row['status']='empty_query_mask';continue
        cap=cv2.VideoCapture(str(video));cap.set(cv2.CAP_PROP_POS_FRAMES,qframe);ok,frame=cap.read()
        if not ok: row['status']='query_decode_failure';continue
        x,y,w,h=int(xx.min()),int(yy.min()),max(5,int(xx.max()-xx.min()+1)),max(5,int(yy.max()-yy.min()+1))
        anchor=cv2.resize(frame,(320,240))[y:y+h,x:x+w].copy()
        lookup={r['frame']:r for r in traces[video.stem]}
        for state in lookup.values():
            qualified=state['appearance_score']>=.72 and state['ncc']>=.55 and state['ambiguity_gap']>=.025
            frame_disagreements+=int(qualified!=state['accepted']);frame_count+=1
        for target in eligible:
            f=int(target.stem.split('_')[-2]);cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,frame=cap.read()
            if not ok: continue
            bank=proposals(cv2.resize(frame,(320,240)),anchor)
            # Evaluation-only target access occurs AFTER candidate generation and ordering.
            gt=cv2.imread(str(target),0);H,W=gt.shape
            for c in bank:
                px,py=np.rint(np.array(c['xy'])*[W/320,H/240]).astype(int)
                c['inside_target']=bool(0<=px<W and 0<=py<H and gt[py,px]>127)
            state=lookup[f];old=index[(video.stem,f)]
            failed=[n for n,v,threshold in [('score',state['appearance_score'],.72),('ncc',state['ncc'],.55),('gap',state['ambiguity_gap'],.025)] if v<threshold]
            if not old['accepted']:rejected['+'.join(failed) if failed else 'confirmation_only']+=1
            records.append(dict(clip=video.stem,frame=f,original=old,failed_gates=failed,rank_of_first_hit=next((i+1 for i,c in enumerate(bank) if c['inside_target']),None),candidates=bank))
        cap.release()
    summary=dict(scope='inspected development corpus; oracle proposal recall is NOT deployed accuracy',videos=len(inventory),eligible_clips=sum(r['status']=='eligible' for r in inventory),eligible_endpoints=len(records),excluded=collections.Counter(r['status'] for r in inventory if r['status']!='eligible'),rejection_reasons=dict(rejected),confirmation_rejects_otherwise_qualified_frames=frame_disagreements,frames_audited=frame_count,top_k_candidate_recall_counts={str(k):sum(r['rank_of_first_hit'] is not None and r['rank_of_first_hit']<=k for r in records) for k in (1,3,5,10,20)},original_candidate_hits=sum(r['original']['inside_target'] for r in records))
    (research/'corpus_inventory.json').write_text(json.dumps(inventory,indent=2))
    (research/'candidate_audit.json').write_text(json.dumps(records,indent=2))
    (research/'diagnostic_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--project',required=True);a=p.parse_args();run(Path(a.data),Path(a.project))
