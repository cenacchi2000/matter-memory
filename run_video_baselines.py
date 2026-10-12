"""Real pretrained model runs on fixed synthetic GNS particle renders.
Run from the workspace root with work/research_env/bin/python.
No query colors, reference identities or ground-truth motion enter model inputs.
"""
from pathlib import Path
import sys, json, time, hashlib, subprocess, gc
import numpy as np
import cv2
import torch
import torch.nn.functional as F
ROOT=Path.cwd(); OUT=ROOT/'outputs/revision6'; CACHE=ROOT/'work/revision6'
VIDEO=OUT/'videos'; VIDEO.mkdir(exist_ok=True,parents=True)
sys.path.insert(0,str(ROOT/'work/revision5/co-tracker'))
import hubconf
from torchvision.models.optical_flow import raft_large, Raft_Large_Weights
DATASETS=['Water-3D','Sand-3D','Goop-3D']; NFRAMES=32; SIZE=256
DEVICE='mps' if torch.backends.mps.is_available() else 'cpu'
torch.set_num_threads(4); torch.manual_seed(42)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def render(dataset):
 p=ROOT/'work/revision5/gns'/dataset/'first_train.npz'
 xyz=np.load(p)['position']; indices=np.linspace(0,len(xyz)-1,NFRAMES).astype(int)
 bounds=np.array(json.loads((p.parent/'metadata.json').read_text())['bounds'])
 pos=xyz[indices]; mid=bounds.mean(1); scale=210/(bounds[:,1]-bounds[:,0]).max()
 # Fixed orthographic camera; z is depth. Positive y is up.
 xy=(pos[:,:,:2]-mid[:2])*np.array([scale,-scale])+128
 frames=[]; buffers=[]
 for t in range(NFRAMES):
  im=np.full((SIZE,SIZE,3),(22,29,36),np.uint8); ids=np.full((SIZE,SIZE),-1,np.int32)
  for i in np.argsort(pos[t,:,2])[::-1]:
   x,y=np.rint(xy[t,i]).astype(int)
   if x<2 or y<2 or x>=254 or y>=254:continue
   depth=np.clip((pos[t,i,2]-bounds[2,0])/(bounds[2,1]-bounds[2,0]),0,1)
   shade=int(190-depth*75)
   cv2.circle(im,(x,y),2,(shade,shade+7,min(255,shade+12)),-1)
   cv2.circle(ids,(x,y),2,int(i),-1)
  frames.append(im);buffers.append(ids)
 visible=[]
 for i in np.unique(buffers[0]):
  if i<0:continue
  x,y=np.rint(xy[0,i]).astype(int)
  if 0<=x<SIZE and 0<=y<SIZE and buffers[0][y,x]==i:visible.append(i)
 # Deterministic spatial coverage; no later motion/error is used to select queries.
 visible=np.array(visible); chosen=[int(visible[0])]
 while len(chosen)<16:
  distance=((xy[0,visible,None]-xy[0,np.array(chosen)][None])**2).sum(-1).min(-1)
  chosen.append(int(visible[np.argmax(distance)]))
 chosen=np.array(chosen);truth=xy[:,chosen].astype(np.float32);vis=np.zeros((NFRAMES,len(chosen)),bool)
 for t in range(NFRAMES):
  for j,i in enumerate(chosen):
   x,y=np.rint(truth[t,j]).astype(int)
   if 0<=x<SIZE and 0<=y<SIZE:vis[t,j]=buffers[t][y,x]==i
 np.savez_compressed(CACHE/f'{dataset}_input.npz',frames=np.array(frames),queries=truth[0],truth=truth,visible=vis,frame_indices=indices,query_ids=chosen)
 return {'dataset':dataset,'source_sha256':sha(p),'frame_indices':indices.tolist(),'query_ids':chosen.tolist(),'initial_queries':len(chosen),'input_sha256':sha(CACHE/f'{dataset}_input.npz')}
def movie(path,frames):
 p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{frames[0].shape[1]}x{frames[0].shape[0]}','-r','8','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
 for im in frames:p.stdin.write(np.ascontiguousarray(im).tobytes())
 p.stdin.close();assert p.wait()==0
protocol={'status':'Synthetic development diagnostic, not a benchmark or novel-method evaluation','datasets':DATASETS,'records':'first training trajectory of each material','frames':NFRAMES,'resolution':[SIZE,SIZE],'query_selection':'16 initially visible particle centers, deterministic farthest-point sampling in first frame only','render':'opaque gray radius-2 splats; fixed orthographic camera; no unique particle texture or source-label coloring in inputs','models':['CoTracker3 offline scaled','CoTracker2','RAFT large C_T_SKHT_V2 with bilinear flow integration'],'metrics':'Mean pixel tracking error over ground-truth-visible queries, excluding initial frame; GT visibility from rendered center ID buffer. Not TAP-Vid AJ.','limitations':['One training trajectory per material','Sparse sampling with potentially severe motion aliasing','Particle-splat domain differs from natural videos','CoTracker3 uses full future clip; RAFT integrates causal pairwise flow','Models track points, not full material-origin fields','No proposed Matter Memory model evaluated'],'device':DEVICE,'seed':42,'cotracker_commit':subprocess.check_output(['git','-C','work/revision5/co-tracker','rev-parse','HEAD'],text=True).strip(),'torch':torch.__version__}
(OUT/'video_protocol.json').write_text(json.dumps(protocol,indent=2))
inputs=[]
for d in DATASETS:
 inputs.append(render(d));print('Rendered',d,flush=True)
(OUT/'video_inputs.json').write_text(json.dumps(inputs,indent=2))
results=[]
for name in ['cotracker3_offline','cotracker2','raft_large']:
 DEVICE = 'cpu' if name == 'cotracker2' else ('mps' if torch.backends.mps.is_available() else 'cpu')
 print('Loading',name,DEVICE,flush=True)
 if name=='raft_large':model=raft_large(weights=Raft_Large_Weights.C_T_SKHT_V2,progress=False).eval().to(DEVICE)
 else:model=getattr(hubconf,name)().eval().to(DEVICE)
 for d in DATASETS:
  saved=OUT/f'{d}_{name}.npz';a=np.load(CACHE/f'{d}_input.npz');frames=a['frames'];q=a['queries']
  start=time.time()
  if not saved.exists():
   with torch.inference_mode():
    if name!='raft_large':
     video=torch.from_numpy(frames.copy()).permute(0,3,1,2)[None].float().to(DEVICE)
     query=torch.from_numpy(np.c_[np.zeros(len(q),np.float32),q])[None].to(DEVICE)
     tracks,visible=model(video,queries=query)
     pred=tracks[0].cpu().numpy();pv=visible[0].cpu().numpy()
     del video,query,tracks,visible
    else:
     pred=[q.copy()]
     for t in range(len(frames)-1):
      first=torch.from_numpy(frames[t].copy()).permute(2,0,1)[None].float().to(DEVICE)/127.5-1
      second=torch.from_numpy(frames[t+1].copy()).permute(2,0,1)[None].float().to(DEVICE)/127.5-1
      flow=model(first,second,num_flow_updates=12)[-1]
      grid=torch.from_numpy(pred[-1].copy()).to(DEVICE)/((SIZE-1)/2)-1
      movement=F.grid_sample(flow.cpu(),grid[None,None].cpu(),align_corners=True,padding_mode='border')[0,:,0].T.cpu().numpy()
      pred.append(pred[-1]+movement)
     pred=np.array(pred);pv=np.all((pred>=0)&(pred<SIZE),axis=-1)
    np.savez_compressed(saved,tracks=pred,visibility=pv,seconds=time.time()-start)
  saved_data=np.load(saved);pred=saved_data['tracks'];valid=a['visible'].copy();valid[0]=False
  error=np.linalg.norm(pred-a['truth'],axis=-1)
  r={'dataset':d,'model':name,'device':DEVICE,'mean_visible_error_px':float(error[valid].mean()),'median_visible_error_px':float(np.median(error[valid])),'visible_observations':int(valid.sum()),'seconds':float(saved_data['seconds']),'prediction_sha256':sha(saved)}
  results.append(r);(OUT/'video_baseline_results.json').write_text(json.dumps({'protocol':protocol,'results':results},indent=2));print(r,flush=True)
 del model;gc.collect()
 if DEVICE=='mps':torch.mps.empty_cache()
# Four synchronized panels use the same frames and queries. Colors are overlays only.
for d in DATASETS:
 a=np.load(CACHE/f'{d}_input.npz');frames=a['frames'];truth=a['truth'];colors=[tuple(int(x) for x in cv2.cvtColor(np.uint8([[[i*11,180,245]]]),cv2.COLOR_HSV2RGB)[0,0]) for i in range(16)]
 predictions=[truth]+[np.load(OUT/f'{d}_{n}.npz')['tracks'] for n in ['cotracker3_offline','cotracker2','raft_large']]
 labels=['Reference identity (oracle)','CoTracker3 / pretrained','CoTracker2 / pretrained','RAFT / integrated flow'];film=[]
 for t in range(NFRAMES):
  panels=[]
  for name,pred in zip(labels,predictions):
   im=frames[t].copy()
   for j in range(16):
    trail=np.rint(np.clip(pred[max(0,t-5):t+1,j],-1000,1000)).astype(np.int32)
    if len(trail)>1:cv2.polylines(im,[trail],False,colors[j],1,cv2.LINE_AA)
    x,y=np.rint(np.clip(pred[t,j],-1000,1000)).astype(int)
    if 0<=x<SIZE and 0<=y<SIZE:cv2.circle(im,(x,y),3,colors[j],1,cv2.LINE_AA)
   im=cv2.resize(im,(512,512),interpolation=cv2.INTER_NEAREST)
   panel=np.full((552,512,3),(22,29,36),np.uint8);panel[40:]=im
   cv2.putText(panel,name,(14,26),cv2.FONT_HERSHEY_SIMPLEX,.55,(236,239,233),1,cv2.LINE_AA);panels.append(panel)
  frame=np.concatenate([np.concatenate(panels[:2],axis=1),np.concatenate(panels[2:],axis=1)],axis=0)
  film.append(frame)
 movie(VIDEO/f'{d}-comparison.mp4',film)
 cv2.imwrite(str(VIDEO/f'{d}-poster.jpg'),cv2.cvtColor(film[16],cv2.COLOR_RGB2BGR))
 movie(VIDEO/f'{d}-input.mp4',frames)
 print('Exported videos',d,flush=True)
weights=[]
for p in (Path(torch.hub.get_dir())/'checkpoints').glob('*.pth'):
 if any(x in p.name for x in ['cotracker2','scaled_offline','raft_large']):weights.append({'filename':p.name,'sha256':sha(p)})
(OUT/'checkpoint_hashes.json').write_text(json.dumps(weights,indent=2))
print('COMPLETE',flush=True)
