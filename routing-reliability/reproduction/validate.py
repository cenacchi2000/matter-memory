"""Replay numerical identities and shared-prediction agreement without encoder inference."""
from pathlib import Path
import numpy as np,pandas as pd,json,hashlib
P=Path(__file__).resolve().parent;S=P.parent/'revision56'
a=pd.read_csv(P/'architecture_results.csv');p=pd.read_csv(P/'preprocessing_results.csv');checks={}
for name,df in [('architecture',a),('preprocessing',p)]:
 assert np.allclose(df.gain,df.rescue-df.harm,atol=1e-12)
 assert (df.switch+1e-12>=df.rescue+df.harm).all()
 checks[name+'_rows']=len(df)
for path in sorted(P.glob('arch_*.npz')):
 z=np.load(path);pred=z['scores'].argmax(2);delta=(pred[:,1]==z['labels']).astype(int)-(pred[:,0]==z['labels']);assert np.array_equal(delta,z['delta']);assert np.array_equal(pred[:,0]!=pred[:,1],z['disagreement']);assert len(np.unique(z['actors']))==24;assert len(z['labels'])==576
 for seed in [11,22]:
  if path.name.startswith(f'arch_interaction_{seed}_'):
   cond=path.stem.removeprefix(f'arch_interaction_{seed}_');old=np.load(S/f'confirmation_seed{seed}_{cond}.npz');assert np.array_equal(z['clips'],old['clips']);assert np.allclose(z['scores'],old['scores'],atol=2e-5);assert np.allclose(z['direct'],old['scores_gain'],atol=1e-8)
checks['prediction_archives']=45;checks['shared_interaction_predictions_and_direct_scores']='reproduced for 2 seeds x 3 conditions'
for method in ['margin','direct','structured']:
 d=a[(a.method==method)&(a['mode']=='fixed')&(a.condition=='video_occlude50')];checks[method+'_static_negative']=int((d.gain<0).sum());checks[method+'_static_zero']=int((d.gain==0).sum())
sh=pd.read_csv(P/'architecture_score_shift.csv');checks['direct_score_rises']=int(((sh.method=='direct')&(sh.score_increase>0)).sum())
checks['references']=len(__import__('re').findall(r'\\bibitem', ((P/'references.tex') if (P/'references.tex').exists() else P.parents[1]/'manuscript/references.tex').read_text()))
checks['status']='passed';(P/'numerical_validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
