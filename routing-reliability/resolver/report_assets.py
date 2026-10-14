from pathlib import Path
import json,numpy as np,cv2,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];r=json.loads((P/'results/endpoint_results.json').read_text());clips=sorted(set(x['clip'] for x in r));plt.rcParams.update({'font.size':8,'pdf.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(7.1,2.6));names=['resolver','appearance','stationary'];a=np.array([[sum(x[k] for x in r if x['method']==m) for k in ['accepted_hit','accepted_miss']] for m in names]);axs[0].barh(names,a[:,0],color='#008C83',label='Accepted hit');axs[0].barh(names,a[:,1],left=a[:,0],color='#C46D43',label='Accepted miss');axs[0].barh(names,31-a.sum(1),left=a.sum(1),color='#CFD9DE',label='Abstention');axs[0].set_xlabel('Annotated endpoints');axs[0].legend(fontsize=6);axs[0].set_title('Admission and correctness')
vals=[[sum(x['inside_target'] for x in r if x['method']==m),sum(x['accepted_hit'] for x in r if x['method']==m)] for m in names];xx=np.arange(3);axs[1].bar(xx-.17,np.array(vals)[:,0],.34,color='#4389A7',label='Candidate in mask');axs[1].bar(xx+.17,np.array(vals)[:,1],.34,color='#008C83',label='Accepted in mask');axs[1].set_xticks(xx,names,rotation=15);axs[1].set_ylim(0,31);axs[1].legend(fontsize=6);axs[1].set_title('Candidate recovery versus acceptance');fig.tight_layout();fig.savefig(P/'figures/results.pdf');fig.savefig(P/'figures/results.png',dpi=220);plt.close(fig)
# Source assets for a per-clip appendix, evaluation masks never enter resolver.
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);args=ap.parse_args();root=Path(args.data);a=P/'case_assets';a.mkdir(exist_ok=True);records=[]
for clip in clips:
 v=next(root.rglob(clip+'.mp4'));q=sorted(v.parent.glob(clip+'_*_query.png'),key=lambda f:int(f.stem.split('_')[-2]))[0];qf=int(q.stem.split('_')[-2]);final=max(x['frame'] for x in r if x['clip']==clip);cap=cv2.VideoCapture(str(v));imgs=[]
 for idx in [qf,final]:
  cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,im=cap.read();assert ok;im=cv2.resize(im,(320,240));imgs.append(im)
 target=v.parent/(clip+'_'+str(final)+'_snitch.png');mask=cv2.resize(cv2.imread(str(target),0),(320,240),interpolation=cv2.INTER_NEAREST);overlay=imgs[1].copy();contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(overlay,contours,-1,(70,220,150),2)
 cv2.imwrite(str(a/(clip+'_query.jpg')),imgs[0]);cv2.imwrite(str(a/(clip+'_endpoint.jpg')),overlay);records.append({'clip':clip,'query_frame':qf,'endpoint_frame':final,'annotation':'green outline is evaluation mask only','source':str(v)})
(P/'results/case_assets.json').write_text(json.dumps(records,indent=2))
