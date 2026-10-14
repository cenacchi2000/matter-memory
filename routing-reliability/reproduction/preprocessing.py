"""Exploratory information ablation on archived logits; no new external confirmation."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np,pandas as pd
from scipy.special import softmax,logsumexp
from scipy.optimize import minimize_scalar
from sklearn.ensemble import HistGradientBoostingRegressor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'revision58'))
from legacy_router import features,weights
from reliability_router import cutoff,batch,KW
P=Path(__file__).resolve().parent;S=P.parent/'revision56'
protocol={'timestamp':time.time(),'status':'exploratory reused data','inputs':['within-clip standardized softmax','raw softmax','temperature-calibrated softmax'],'dimensions':15,'training':'same HGB regressor, router disagreements only, original actor weights','temperature':'one scalar per expert fitted on calibration clips across three conditions by actor-weighted cross entropy','threshold':'clean tune actors, at most 20%, nonnegative','matched':'rank-only batch 5,10,20%; no positivity filter, lexicographic ID tie break; same actual rate','evaluation':'all five archived conditions per checkpoint'}
(P/'preprocessing_protocol.json').write_text(json.dumps(protocol,indent=2))
def stats(p,s):
 sort=np.sort(p,2);ent=-(p*np.log(p.clip(1e-30))).sum(2)/np.log(s.shape[2]);js=[];agree=[]
 for a,b in [(0,1),(0,2),(1,2)]:
  mid=(p[:,a]+p[:,b])/2;js.append(.5*((p[:,a]*np.log((p[:,a]/mid).clip(1e-30))).sum(1)+(p[:,b]*np.log((p[:,b]/mid).clip(1e-30))).sum(1)));agree.append(s[:,a].argmax(1)==s[:,b].argmax(1))
 return np.c_[p.max(2),sort[:,:,-1]-sort[:,:,-2],ent,np.array(js).T,np.array(agree).T]
rows=[];fits={};preds={}
for seed in [11,22]:
 z=np.load(S/f'development_seed{seed}.npz');s=z['scores'];y=z['labels'];g=z['actors'];tr=z['roles']=='router';ca=z['roles']=='calibration';tu=(z['roles']=='tune')&(z['conditions']=='clean');delta=(s[:,1].argmax(1)==y).astype(int)-(s[:,0].argmax(1)==y);d=s[:,0].argmax(1)!=s[:,1].argmax(1);wt=np.zeros(len(g));wt[tr]=weights(g[tr]);wc=weights(g[ca]);temperatures=[]
 for h in range(3):
  def nll(logt):
   zz=s[ca,h]/np.exp(logt);return wc@(logsumexp(zz,axis=1)-zz[np.arange(ca.sum()),y[ca]])
  temperatures.append(float(np.exp(minimize_scalar(nll,bounds=(-4,4),method='bounded').x)))
 fits[seed]={'temperatures':temperatures}
 def featurize(s,kind):
  return features(s) if kind=='standardized' else stats(softmax(s/(np.array(temperatures)[None,:,None] if kind=='temperature' else 1),axis=2),s)
 for kind in ['standardized','raw','temperature']:
  x=featurize(s,kind);ix=tr&d;model=HistGradientBoostingRegressor(**KW).fit(x[ix],delta[ix],sample_weight=wt[ix]/wt[ix].sum()*ix.sum());threshold=cutoff(model.predict(x[tu]),d[tu],g[tu],.2);fits[seed][kind]={'threshold':threshold}
  for file in list(S.glob(f'diagnostic_seed{seed}_*.npz'))+list(S.glob(f'confirmation_seed{seed}_*.npz')):
   e=np.load(file);score=model.predict(featurize(e['scores'],kind));w=weights(e['actors']);di=e['disagreement'];de=e['delta'];correct=e['scores'][:,0].argmax(1)==e['labels'];preds[(file.stem,kind)]=score
   for mode,budget in [('fixed',.2),('matched',.05),('matched',.1),('matched',.2)]:
    sw=(score>threshold)&di if mode=='fixed' else batch(score,di,e['actors'],budget,e['clips'],positive=False)
    rows.append(dict(seed=seed,dataset=file.stem,features=kind,mode=mode,budget=budget,actors=len(np.unique(e['actors'])),accuracy=float(w@(correct+sw*de)),gain=float(w@(sw*de)),switch=float(w@sw),rescue=float(w@(sw&(de==1))),harm=float(w@(sw&(de==-1)))))
 # Batch matched quantities for score-family controls on exactly the same cohorts.
 for file in list(S.glob(f'diagnostic_seed{seed}_*.npz'))+list(S.glob(f'confirmation_seed{seed}_*.npz')):
  e=np.load(file);w=weights(e['actors']);di=e['disagreement'];de=e['delta'];correct=e['scores'][:,0].argmax(1)==e['labels']
  for name in ['margin','reliable_gain','two_raw','two_isotonic','two_platt']:
   for b in [.05,.1,.2]:
    sw=batch(e[name],di,e['actors'],b,e['clips'],positive=False);rows.append(dict(seed=seed,dataset=file.stem,features=name,mode='matched',budget=b,actors=len(np.unique(e['actors'])),accuracy=float(w@(correct+sw*de)),gain=float(w@(sw*de)),switch=float(w@sw),rescue=float(w@(sw&(de==1))),harm=float(w@(sw&(de==-1)))))
f=pd.DataFrame(rows);f.to_csv(P/'preprocessing_results.csv',index=False);(P/'preprocessing_fits.json').write_text(json.dumps(fits,indent=2))
# Refitting the standardized condition must reproduce the archived direct-gain score.
checks=[]
for (dataset,kind),score in preds.items():
 if kind=='standardized':
  e=np.load(S/(dataset+'.npz'));err=float(np.max(abs(score-e['scores_gain'])));assert err<1e-10,err;checks.append(dict(dataset=dataset,max_abs_error=err))
(P/'preprocessing_validation.json').write_text(json.dumps(checks,indent=2));print(f[(f.dataset.str.endswith('_clean'))&(f.dataset.str.startswith('confirmation'))].to_string(index=False))
