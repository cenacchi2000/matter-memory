"""New external head inference / router refits; exploratory on already inspected RAVDESS."""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np,pandas as pd,torch
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
P=Path(__file__).resolve().parent;S=P.parent/'revision56';E=P.parent/'revision42/cremad_experts';ROOT=P.parents[1]
sys.path.insert(0,str(S));from expert_architecture import Expert
from legacy_router import features,weights
from reliability_router import cutoff,KW,batch
seeds=[11,22,33,44,55];archs=['late','interaction','capacity_control'];conds=['clean','video_occlude50','video_moving_occluder']
protocol={'timestamp':time.time(),'status':'exploratory new head inference and router fitting on an inspected external population','architectures':archs,'seeds':seeds,'encoders':'shared frozen WavLM/DINOv2; NOT independent encoder replication','router':'15 standardized score statistics; HGB direct gain or two conditional heads plus isotonic','fit':'original router/calibration/tune roles, three development conditions; clean tune positive threshold at 20%','no_external_fitting':True,'checkpoint_hashes':{f'{k}_{s}':hashlib.sha256((E/f'{k}_seed{s}/model.pt').read_bytes()).hexdigest() for k in ['audio','video']+archs for s in seeds}}
(P/'architecture_protocol.json').write_text(json.dumps(protocol,indent=2));norm=np.load(E/'normalization.npz');torch.set_num_threads(2)
rows=json.loads((S/'crema_selection.json').read_text());dev={k:[] for k in ['audio','video','roles','actors','labels','clips','condition']}
for row in rows:
 z=np.load(ROOT/'work/revision56/crema_features'/(row['clips']+'.npz'))
 for cond in ['clean','video_occlude25','video_blur2']:
  for k,v in [('audio',z['audio']),('video',z[cond]),('roles',row['splits']),('actors',row['actors']),('labels',row['labels']),('clips',row['clips']),('condition',cond)]:dev[k].append(v)
dev={k:np.array(v) for k,v in dev.items()}
rows=json.loads((S/'ravdess_manifest.json').read_text());mapping={'01':4,'03':3,'04':5,'05':0,'06':2,'07':1};ext={'actors':np.array([r['actor'] for r in rows]),'clips':np.array([r['clip'] for r in rows]),'labels':np.array([mapping[r['emotion_code']] for r in rows])};zs=[np.load(ROOT/'work/revision56/ravdess_features'/(r['clip']+'.npz')) for r in rows];ext['audio']=np.stack([z['audio'] for z in zs]);ext.update({c:np.stack([z[c] for z in zs]) for c in conds})
def tensor(a,v):return torch.tensor((a-norm['audio_mean'])/norm['audio_std'],dtype=torch.float32),torch.tensor((v-norm['video_mean'])/norm['video_std'],dtype=torch.float32)
da,dv=tensor(dev['audio'],dev['video']);ev={c:tensor(ext['audio'],ext[c]) for c in conds};results=[];inversion=[]
for seed in seeds:
 models={}
 for k in ['audio','video']+archs:
  m=Expert(k);m.load_state_dict(torch.load(E/f'{k}_seed{seed}/model.pt',weights_only=True));models[k]=m.eval()
 for arch in archs:
  with torch.no_grad():s=np.stack([models[k](da,dv).numpy() for k in ['audio',arch,'video']],1)
  x=features(s);pr=s.argmax(2);de=(pr[:,1]==dev['labels']).astype(int)-(pr[:,0]==dev['labels']);d=pr[:,0]!=pr[:,1];tr=(dev['roles']=='router')&d;ca=(dev['roles']=='calibration')&d;tu=(dev['roles']=='tune')&(dev['condition']=='clean');wt=np.zeros(len(d));wc=wt.copy();rt=dev['roles']=='router';rc=dev['roles']=='calibration';wt[rt]=weights(dev['actors'][rt]);wc[rc]=weights(dev['actors'][rc]);sw=lambda w,i:w[i]/w[i].sum()*i.sum()
  gain=HistGradientBoostingRegressor(**KW).fit(x[tr],de[tr],sample_weight=sw(wt,tr));q=HistGradientBoostingClassifier(**KW).fit(x[tr],de[tr]!=0,sample_weight=sw(wt,tr));rn=tr&(de!=0);cn=ca&(de!=0);r=HistGradientBoostingClassifier(**KW).fit(x[rn],de[rn]==1,sample_weight=sw(wt,rn));iq=IsotonicRegression(out_of_bounds='clip').fit(q.predict_proba(x[ca])[:,1],de[ca]!=0,sample_weight=sw(wc,ca));ir=IsotonicRegression(out_of_bounds='clip').fit(r.predict_proba(x[cn])[:,1],de[cn]==1,sample_weight=sw(wc,cn))
  def predict(s):
   xx=features(s);return {'margin':xx[:,4]-xx[:,3],'direct':gain.predict(xx),'structured':iq.predict(q.predict_proba(xx)[:,1])*(2*ir.predict(r.predict_proba(xx)[:,1])-1)}
  train=predict(s);cuts={k:cutoff(v[tu],d[tu],dev['actors'][tu],.2) for k,v in train.items()};stored={}
  for cond in conds:
   with torch.no_grad():s=np.stack([models[k](*ev[cond]).numpy() for k in ['audio',arch,'video']],1)
   pr=s.argmax(2);a=pr[:,0]==ext['labels'];de=(pr[:,1]==ext['labels']).astype(int)-a;d=pr[:,0]!=pr[:,1];scores=predict(s);w=weights(ext['actors']);groups=np.unique(ext['actors']);draw=np.random.default_rng(5901).integers(0,len(groups),(3000,len(groups)))
   def interval(values):
    v=np.array([np.mean(values[ext['actors']==g]) for g in groups]);b=v[draw].mean(1);return float(v.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975))
   for name,score in scores.items():
    for mode in ['fixed','matched']:
     mask=(score>cuts[name])&d if mode=='fixed' else batch(score,d,ext['actors'],.2,ext['clips'],positive=False);point,lo,hi=interval(mask*de) if mode=='fixed' else (float(w@(mask*de)),np.nan,np.nan)
     results.append(dict(seed=seed,architecture=arch,condition=cond,method=name,mode=mode,n_actors=len(groups),accuracy=float(w@(a+mask*de)),audio_accuracy=float(w@a),fusion_accuracy=float(w@(a+de)),gain=point,gain_low=lo,gain_high=hi,switch=float(w@mask),rescue=float(w@(mask&(de==1))),harm=float(w@(mask&(de==-1))),threshold=cuts[name]))
   stored[cond]=(scores,de,d);np.savez_compressed(P/f'arch_{arch}_{seed}_{cond}.npz',scores=s,labels=ext['labels'],actors=ext['actors'],clips=ext['clips'],delta=de,disagreement=d,**scores)
  for method in ['margin','direct','structured']:
   clean=stored['clean'][0][method];bad=stored['video_occlude50'][0][method];sc,lo,hi=interval(bad-clean);inversion.append(dict(seed=seed,architecture=arch,method=method,score_increase=sc,low=lo,high=hi))
  print(seed,arch,'done',flush=True)
pd.DataFrame(results).to_csv(P/'architecture_results.csv',index=False);pd.DataFrame(inversion).to_csv(P/'architecture_score_shift.csv',index=False);print('DONE',len(results),flush=True)
