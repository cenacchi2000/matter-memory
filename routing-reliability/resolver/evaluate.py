from pathlib import Path
import argparse,json,hashlib,cv2,numpy as np,time
from resolver import Resolver
p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--output',required=True);args=p.parse_args();root=Path(args.data);out=Path(args.output);out.mkdir(exist_ok=True,parents=True)
rows=[];traces={};t=time.time()
for video in sorted(root.rglob('*.mp4')):
 queries=sorted(video.parent.glob(video.stem+'_*_query.png'),key=lambda x:int(x.stem.split('_')[-2]));targets=sorted(video.parent.glob(video.stem+'_*_snitch.png'),key=lambda x:int(x.stem.split('_')[-2]))
 if not queries or not targets:continue
 q=queries[0];qframe=int(q.stem.split('_')[-2]);targets=[f for f in targets if int(f.stem.split('_')[-2])>qframe]
 if not targets:continue
 qmask=cv2.resize(cv2.imread(str(q),0),(320,240),interpolation=cv2.INTER_NEAREST);yy,xx=np.where(qmask>127)
 if len(xx)==0:continue
 bbox=[int(xx.min()),int(yy.min()),max(5,int(xx.max()-xx.min()+1)),max(5,int(yy.max()-yy.min()+1))];cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS);cap.set(0,0) if False else None;cap.set(cv2.CAP_PROP_POS_FRAMES,qframe);ok,im=cap.read()
 if not ok:continue
 im=cv2.resize(im,(320,240));models={m:Resolver(im,bbox,fps,m) for m in ['resolver','appearance']};anchor_hash=hashlib.sha256(models['resolver'].anchor.tobytes()).hexdigest();initial=models['resolver'].pos.copy();end=max(int(f.stem.split('_')[-2]) for f in targets);frames={qframe:{}};trace=[]
 for frame in range(qframe+1,end+1):
  ok,im=cap.read()
  if not ok:break
  im=cv2.resize(im,(320,240));states={m:model.step(im) for m,model in models.items()};frames[frame]=states;trace.append({'frame':frame,**states['resolver']})
 for target in targets:
  idx=int(target.stem.split('_')[-2]);state=frames.get(idx)
  if not state:continue
  mask=cv2.imread(str(target),0);H,W=mask.shape
  def hit(xy):
   x,y=np.rint(np.array(xy)*[W/320,H/240]).astype(int);return bool(0<=x<W and 0<=y<H and mask[y,x]>127)
  for method in models:
   r=state[method];rows.append({'clip':video.stem,'frame':idx,'method':method,'inside_target':hit(r['candidate']),'accepted':r['accepted'],'accepted_hit':hit(r['candidate']) and r['accepted'],'accepted_miss':not hit(r['candidate']) and r['accepted'],'age_s':r['evidence_age_s']})
  rows.append({'clip':video.stem,'frame':idx,'method':'stationary','inside_target':hit(initial),'accepted':True,'accepted_hit':hit(initial),'accepted_miss':not hit(initial),'age_s':(idx-qframe)/fps})
 assert anchor_hash==hashlib.sha256(models['resolver'].anchor.tobytes()).hexdigest();traces[video.stem]=trace;cap.release();print(video.stem,len(targets),flush=True)
(out/'endpoint_results.json').write_text(json.dumps(rows,indent=2));(out/'traces.json').write_text(json.dumps(traces));summary={m:{'endpoints':len(r:=[x for x in rows if x['method']==m]),'clips':len(set(x['clip'] for x in r)),'candidate_hits':sum(x['inside_target'] for x in r),'accepted_hits':sum(x['accepted_hit'] for x in r),'accepted_misses':sum(x['accepted_miss'] for x in r),'abstentions':sum(not x['accepted'] for x in r)} for m in ['resolver','appearance','stationary']};summary['runtime_seconds']=time.time()-t;(out/'summary.json').write_text(json.dumps(summary,indent=2));print(summary)
