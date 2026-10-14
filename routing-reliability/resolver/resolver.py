"""Causal occlusion resolver prototype. No future frames or evaluation masks enter step()."""
import cv2,numpy as np
class Resolver:
 def __init__(self, frame, bbox, fps=15., mode='resolver'):
  x,y,w,h=map(int,bbox);self.anchor=frame[y:y+h,x:x+w].copy();self.gray=cv2.cvtColor(self.anchor,cv2.COLOR_BGR2GRAY);self.pos=np.array([x+w/2,y+h/2]);self.velocity=np.zeros(2);self.last=self.pos.copy();self.age=0;self.fps=fps;self.mode=mode;self.pending=None;self.count=0;self.previous=frame.copy();self.context=self.pos.copy();self.hist=[];self.time=0
  self.hsv_hist=self.histogram(self.anchor);self.properties={'mean_rgb':self.anchor[:,:,::-1].mean((0,1)).round(2).tolist(),'query_size_px':[w,h],'appearance':'immutable query RGB; includes crop background'}
 @staticmethod
 def histogram(crop):
  hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);h=cv2.calcHist([hsv],[0,1],None,[12,8],[0,180,0,256]);return cv2.normalize(h,h).flatten()
 def step(self,frame):
  self.time+=1;self.age+=1;gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);candidate=None
  for scale in [.8,1.,1.25]:
   h,w=self.gray.shape;w=max(5,round(w*scale));h=max(5,round(h*scale))
   if h>=gray.shape[0] or w>=gray.shape[1]:continue
   template=cv2.resize(self.gray,(w,h));scores=cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED);_,ncc,_,(x,y)=cv2.minMaxLoc(scores)
   crop=frame[y:y+h,x:x+w];color=float(cv2.compareHist(self.hsv_hist,self.histogram(crop),cv2.HISTCMP_CORREL));score=.7*float(ncc)+.3*color
   suppressed=scores.copy();suppressed[max(0,y-h//2):y+h//2+1,max(0,x-w//2):x+w//2+1]=-1;gap=float(ncc-suppressed.max())
   c={'xy':np.array([x+w/2,y+h/2]),'score':score,'ncc':float(ncc),'color':color,'gap':gap}
   if candidate is None or score>candidate['score']:candidate=c
  c=candidate;xy=c['xy'];qualified=c['score']>=.72 and c['ncc']>=.55 and c['gap']>=.025
  self.count=self.count+1 if qualified and self.pending is not None and np.linalg.norm(xy-self.pending)<max(self.gray.shape)*1.5 else int(qualified);self.pending=xy.copy() if qualified else None
  accepted=qualified if self.mode=='appearance' else qualified and self.count>=2
  # Context displacement is a competing hypothesis, not a semantic container relation.
  flow=cv2.calcOpticalFlowFarneback(cv2.cvtColor(self.previous,cv2.COLOR_BGR2GRAY),gray,None,.5,2,15,2,5,1.1,0);cx,cy=np.rint(self.context).astype(int);cx=np.clip(cx,10,gray.shape[1]-11);cy=np.clip(cy,10,gray.shape[0]-11);delta=np.median(flow[cy-10:cy+11,cx-10:cx+11].reshape(-1,2),axis=0);self.context=np.clip(self.context+delta,[0,0],[gray.shape[1]-1,gray.shape[0]-1])
  if accepted:
   elapsed=self.age/self.fps;v=(xy-self.last)/max(elapsed,1/self.fps);self.velocity=.5*self.velocity+.5*v;self.pos=xy.copy();self.last=xy.copy();self.context=xy.copy();self.age=0;self.hist.append(xy.tolist())
  age=self.age/self.fps;moving=np.clip(self.last+self.velocity*min(age,1.),[0,0],[gray.shape[1]-1,gray.shape[0]-1]);radius=6+20*age
  self.previous=frame.copy()
  return {'time':self.time/self.fps,'candidate':xy.tolist(),'accepted':bool(accepted),'state':'supported' if accepted else 'unresolved','last_supported':self.last.tolist(),'evidence_age_s':age,'hypotheses':{'stationary':self.last.tolist(),'constant_velocity':moving.tolist(),'local_context_flow':self.context.tolist()},'heuristic_radius_px':radius,'ncc':c['ncc'],'color_similarity':c['color'],'appearance_score':c['score'],'ambiguity_gap':c['gap'],'properties':self.properties,'query_updates':0,'suggested_action':'continue_observing' if accepted else 'request_view_change','action_reason':'appearance_supported' if accepted else 'current_identity_or_location_unresolved'}
