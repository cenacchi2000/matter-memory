"""Original evidence-led figures; no new experiment or generated scene imagery."""
from pathlib import Path
import json,subprocess
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle,Circle,Polygon
from PIL import Image
P=Path(__file__).resolve().parent;F=P/'figures';S=P.parent/'revision56';D=json.loads((S/'site/data.js').read_text().removeprefix('window.EVIDENCE=').rstrip(';'))
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.fonttype':'none'})
ink='#243344';muted='#667589';teal='#007F78';red='#BF543F';violet='#7560A5';blue='#397FAD';gold='#DDB640';line='#9EADB9'
def canvas(h):
 fig=plt.figure(figsize=(7.1,7.1*h/1440));ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1440),ylim=(h,0));ax.axis('off');return fig,ax
def text(ax,x,y,s,size=7,color=ink,bold=False,ha='left',va='center',**kw):return ax.text(x,y,s,fontsize=size,color=color,weight='bold' if bold else 'normal',ha=ha,va=va,**kw)
def rect(ax,x,y,w,h,fc='white',ec='#DCE3E8',r=10,lw=.7,**kw):
 p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=fc,edgecolor=ec,lw=lw,**kw);ax.add_patch(p);return p
def arrow(ax,xy,to,color=line,lw=1,style='->',rad=0):ax.annotate('',xy=to,xytext=xy,arrowprops=dict(arrowstyle=style,color=color,lw=lw,connectionstyle=f'arc3,rad={rad}',shrinkA=1,shrinkB=1))
def frame(e,occ=False):
 im=np.array(Image.open(F/(e['id']+'.png')).convert('RGB'))
 if occ:im[33:191,33:191]=128
 return im

def picture(ax,e,x,y,w,h,occ=False):
 # Identical letterboxed frame, not content-dependent cropping.
 im=frame(e,occ);target=w/h;hh=int(im.shape[1]/target);start=(im.shape[0]-hh)//2;im=im[start:start+hh];ax.imshow(im,extent=(x,x+w,y+h,y),aspect='auto',zorder=2);ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='white',lw=.5,zorder=3))
def save(fig,n):
 for ext in ['pdf','svg','png']:fig.savefig(F/(n+'.'+ext),dpi=260,facecolor='white',pad_inches=0)
 p=F/(n+'.svg');p.write_text(p.read_text().replace('DejaVu Sans','Arial'));plt.close(fig)
# TEASER: measured clip pair and two population consequences, not a text inventory.
e=next(x for x in D if x['clip']=='1020_IEO_ANG_LO');a=e['conditions']['clean']['methods']['opportunity_advantage'];b=e['conditions']['video_occlude50']['methods']['opportunity_advantage']
fig,ax=canvas(464)
for x,w,col in [(0,700,'#F0F7F5'),(720,342,'#FCF4E9'),(1082,358,'#F3F0F8')]:rect(ax,x,0,w,464,col,ec='none',r=13)
text(ax,18,24,'A',8.4,teal,True);text(ax,45,24,'Evidence changes the decision.',8.4,bold=True)
text(ax,742,24,'B',8.4,'#A47517',True);text(ax,768,24,'Quota vs threshold.',8.1,bold=True)
text(ax,1103,24,'C',8.4,violet,True);text(ax,1129,24,'Clean rejection.',7.9,bold=True)
# large paired frames and prediction chips
for x,occ,title,out,col in [(22,False,'Clean evidence','KEEP AUDIO',teal),(365,True,'Constructed occlusion','SWITCH TO FUSION',red)]:
 text(ax,x,60,title,7.2,bold=True);picture(ax,e,x,77,238,171,occ)
 # paired outputs as overlays with whitespace separation
 rect(ax,x+7,213,224,29,'white','none',r=4,zorder=4);text(ax,x+15,228,'A: angry  F: disgust',5.9,bold=True,zorder=5)
 rect(ax,x,260,238,43,col,'none',r=6);text(ax,x+119,272,out,6.4,'white',True,ha='center');text(ax,x+119,289,'angry  / correct' if not occ else 'disgust  / incorrect',7.4,'white',True,ha='center')
 text(ax,x+119,323,f"score {a['score']:+.3f}" if not occ else f"score {b['score']:+.3f}",8.4,col,True,ha='center')
# compact causal reading direction and threshold crossing graphic
arrow(ax,(271,157),(353,157),color=red,lw=1.6);text(ax,311,126,'visual',6.2,muted,ha='center');text(ax,311,139,'change',6.2,muted,ha='center')
text(ax,311,200,'same\naudio',6.0,teal,ha='center')
x0,x1=60,632;lo,hi=-.5,.22;pos=lambda s:x0+(s-lo)/(hi-lo)*(x1-x0)
ax.plot([x0,x1],[360,360],color='#AFBDBB',lw=2);tx=pos(a['threshold']);ax.plot([tx,tx],[339,382],color=violet,lw=1,ls=(0,(3,2)))
for m,c in [(a,teal),(b,red)]:ax.scatter([pos(m['score'])],[360],s=27,color=c,zorder=5)
arrow(ax,(pos(a['score'])+12,360),(pos(b['score'])-12,360),red,lw=1.1)
text(ax,tx,397,f"frozen threshold {a['threshold']:.3f}",6.8,violet,ha='center')
text(ax,22,438,'CREMA-D • intended label: angry • whole-clip decisions',6.6,muted)
# B: explicit actual admission bars, not a decorative mini chart
text(ax,742,65,'Under the same static occluder',6.8,muted)
for y,label,v,g,col in [(112,'Batch quota',20,-7.32,blue),(215,'Fixed threshold',53.414634,-22.926829,red)]:
 text(ax,742,y,label,7.3,bold=True);text(ax,1038,y,f'{v:.1f}%',8.8,col,True,ha='right')
 rect(ax,742,y+17,296,25,'#E7E3DB','none',r=3);rect(ax,742,y+17,296*v/60,25,col,'none',r=3)
 text(ax,742,y+61,f'{g:+.2f} pp accuracy gain',7.1,col,True)
text(ax,742,330,'Actual switches',7.4,bold=True);text(ax,742,353,'Tuned at 20%; deployed at 53.4%.',5.85,muted)
text(ax,742,402,'Harm persists with either rule.',6.0,muted)
text(ax,742,438,'820 clips • 10 actors • inspected',5.85,muted)
# C: visibly clean target-domain clips plus total rejection matrix.
rv=[next(d for d in D if d['dataset']=='RAVDESS' and d['category']==cat) for cat in ['abstained_rescue','occlusion_failure']]
for x,ee in zip([1104,1268],rv):picture(ax,ee,x,61,146,112)
text(ax,1104,195,'Clean external input',7.2,bold=True)
text(ax,1104,225,'0 / 576',14,violet,True);text(ax,1276,226,'accepted',7.3,muted)
for i in range(24):
 for j in range(24):ax.add_patch(Rectangle((1104+j*6.1,253+i*3.1),4.5,1.9,facecolor='#B3A5CC',edgecolor='none'))
text(ax,1280,265,'Every clip',6.7,muted);text(ax,1280,285,'falls back',6.7,muted);text(ax,1280,305,'to audio.',6.7,muted)
text(ax,1104,353,'−4.17 pp',13,violet,True);text(ax,1104,383,'support minus margin',7.1,muted)
text(ax,1104,404,'95% actor CI [−6.42, −1.91]',6.6,muted)
text(ax,1104,438,'RAVDESS • 24 actors • locked',5.9,muted)
save(fig,'fig1_teaser')
# ARCHITECTURE: grouped observation and decision stages with a true attention-head inset.
fig,ax=canvas(585)
# dashed group frames
rect(ax,0,24,1035,308,'#F8FAFC','#BDCAD6',r=12,ls=(0,(3,3)))
rect(ax,0,356,1035,205,'#FAF9FC','#BDCAD6',r=12,ls=(0,(3,3)))
rect(ax,1057,24,383,347,'white','#C6B9DD',r=12)
rect(ax,1057,392,383,169,'#FFF9E7','#E8D18B',r=12)
text(ax,14,12,'A / OBSERVE AND PREDICT',7.2,bold=True);text(ax,14,342,'B / ESTIMATE, CALIBRATE AND SELECT',7.2,bold=True)
# helper compact module: fixed rows, no auto font shrink

def module(x,y,w,h,label,sub='',color='#DCEEF1',edge='#65B7B5'):
 rect(ax,x,y,w,h,color,edge,r=7);text(ax,x+w/2,y+(24 if h>=100 else h*.39 if sub else h/2),label,7,bold=True,ha='center');
 if sub:text(ax,x+w/2,y+h*.76,sub,6.3,muted,ha='center')
# Inputs: real frame stack, actual audio waveform from same clip
text(ax,15,52,'Input clip',6.8,bold=True)
for off in [12,6,0]:
 picture(ax,e,22+off,75-off,103,81)
text(ax,20,172,'8 RGB frames',6.0,muted)
raw=subprocess.run(['/Users/filippo/miniconda3/bin/ffmpeg','-v','error','-i',str(S/'site'/e['video']),'-f','f32le','-ac','1','-ar','16000','pipe:1'],capture_output=True,check=True).stdout
wave=np.frombuffer(raw,dtype=np.float32);chunks=np.array_split(wave,95);amp=np.array([np.max(np.abs(c)) if len(c) else 0 for c in chunks]);amp=amp/(amp.max()+1e-9)
for xx,aa in zip(np.linspace(20,128,95),amp):ax.plot([xx,xx],[246-aa*18,246+aa*18],color=teal,lw=.65)
text(ax,20,280,'Audio · 16 kHz',6.2,muted)
# encoders and projections
module(165,86,145,68,'DINOv2 B/14','768-D · frozen')
module(165,219,145,68,'WavLM Base','768-D · frozen')
arrow(ax,(138,115),(161,115));arrow(ax,(130,246),(161,246))
module(348,88,110,62,'Projection','per expert',color='#E9EFF6',edge='#AAC0D7');module(348,221,110,62,'Projection','per expert',color='#E9EFF6',edge='#AAC0D7')
arrow(ax,(312,120),(344,120));arrow(ax,(312,252),(344,252))
# token chips and expert stack
for xx,yy,c in [(485,111,blue),(485,246,teal)]:
 for j in range(3):rect(ax,xx+j*9,yy,6,18,c,'none',r=1)
text(ax,484,147,'96-D',6,muted);text(ax,484,279,'96-D',6,muted)
arrow(ax,(460,120),(482,120));arrow(ax,(460,252),(482,252))
module(553,59,165,49,'Video head','zero other token',color='#EAF4EA',edge='#94BD96')
module(553,151,165,71,'Fusion head*','2-token attention',color='#FFF0B6',edge='#DBB937')
module(553,260,165,49,'Audio head','zero other token',color='#EAF4EA',edge='#94BD96')
arrow(ax,(519,120),(549,83));arrow(ax,(519,120),(549,174));arrow(ax,(519,252),(549,199));arrow(ax,(519,252),(549,285))
# class vector schematic, deliberate equal cells not fake probabilities
for yy,c in [(84,blue),(184,gold),(285,teal)]:
 arrow(ax,(720,yy),(744,yy));
 for j in range(6):rect(ax,748+j*10,yy-8,7,16,c,'none',r=1)
arrow(ax,(810,84),(848,131));arrow(ax,(810,184),(848,184));arrow(ax,(810,285),(848,240))
text(ax,776,312,'6 logits / head',6,muted,ha='center')
module(854,93,163,174,'Score features','',color='#EAF0F7',edge='#9FB5CC')
# cover blank middle then precise feature list
rect(ax,861,138,149,119,'#EAF0F7','none',r=0)
for y,ss in zip([151,177,203,229],['Max · margin','Entropy','JS divergences','Top-1 agreements']):text(ax,935,y,ss,6.8,ha='center')
# second stage feature group and connections
a=arrow
module(18,385,172,59,'8 visual probes','time / crop / pixels',color='#EAF0F7',edge='#9FB5CC')
text(ax,21,469,'+4 crop encodings',6.6,muted);text(ax,21,494,'Combined with scores',6.6,muted);text(ax,21,518,'15 or 23 features',7,bold=True)
# raw visual arrow down group margin, no crossing the internals
arrow(ax,(8,151),(8,414));arrow(ax,(8,414),(16,414))
# top output down through right stage boundary to feature join
ax.plot([936,1025,1025,224,224],[270,270,370,370,414],color=line,lw=1);arrow(ax,(192,414),(240,414));arrow(ax,(224,414),(240,414))
module(244,383,214,128,'Router family','',color='#E9F4EB',edge='#98C59E');rect(ax,252,427,198,76,'#E9F4EB','none',r=0)
text(ax,351,437,'Direct gain: Δ',6.4,ha='center');text(ax,351,463,'3 outcomes: R / N / H',6.1,ha='center');text(ax,351,489,'q × (2r − 1)',6.5,ha='center')
module(501,384,202,126,'Calibration','',color='#EEE9F7',edge='#B4A4D0');rect(ax,508,427,188,75,'#EEE9F7','none',r=0)
text(ax,602,439,'Raw / isotonic / sigmoid',5.8,ha='center');text(ax,602,466,'Separate fitting role',6.1,muted,ha='center');text(ax,602,491,'Direct scores bypass',5.9,muted,ha='center')
arrow(ax,(460,449),(497,449))
module(746,383,270,128,'Decision rule','',color='#FCEEDC',edge='#D4B187');rect(ax,753,427,254,75,'#FCEEDC','none',r=0)
text(ax,881,440,'Threshold  |  batch quota',6.1,ha='center');text(ax,881,466,'Optional support gate',6.1,ha='center');text(ax,881,491,'Fusion if selected; else audio',5.8,ha='center')
arrow(ax,(705,449),(742,449))
text(ax,350,537,'Fit: router actors',6.4,teal,ha='center');text(ax,602,537,'Fit: calibration actors',6.4,violet,ha='center');text(ax,881,537,'Tune: clean actors',6.4,'#9C7139',ha='center')
# inset actual fusion internals, separate modalities then residual attention
text(ax,1075,49,'* FUSION HEAD DETAIL',7.0,bold=True)
for xx,col,label in [(1090,teal,'Audio token'),(1260,blue,'Video token')]:
 module(xx, seventy:=77,145,36,label,'',color='#EAF0F7' if col==blue else '#E5F2EE',edge=col)
 arrow(ax,(xx+72,115),(xx+72,136))
module(1090,138,315,48,'4-head self-attention','Q = K = V = [audio; video]',color='#F1EDF8',edge='#B4A4D0')
arrow(ax,(1247,188),(1247,210));ax.add_patch(Circle((1247,223),12,facecolor='white',edgecolor=violet,lw=1));text(ax,1247,223,'+',9,violet,True,ha='center')
# residual from token inputs around attention, clearly schematic
ax.plot([1081,1068,1068,1230],[95,95,223,223],color=violet,lw=.8);arrow(ax,(1230,223),(1235,223),violet)
text(ax,1090,247,'Residual → concatenate tokens',5.9,muted)
arrow(ax,(1247,238),(1247,269));module(1090,271,315,44,'192 → 96 → 6','GELU between linear layers',color='#EAF4EA',edge='#94BD96')
text(ax,1090,342,'Trained head on frozen features',5.9,muted)
# outcome legend / no false new-method claims
text(ax,1075,416,'WHAT IS MEASURED',7.3,bold=True)
for x,y,label,col in [(1078,449,'Rescue  Δ = +1',teal),(1262,449,'Harm  Δ = −1',red),(1078,478,'Neutral  Δ = 0',muted)]:
 ax.add_patch(Circle((x+4,y),3.5,facecolor=col,edgecolor='none'));text(ax,x+16,y,label,6.6,col)
text(ax,1075,512,'Gain = rescue − harm',7.1,bold=True)
text(ax,1075,538,'All experts execute before routing.',6.5,muted)
text(ax,0,575,'Frozen encoders',6.3,muted);text(ax,223,575,'Trained heads / routers',6.3,teal);text(ax,534,575,'Calibration maps',6.3,violet);text(ax,783,575,'Selection logic',6.3,'#9C7139');text(ax,1135,575,'No encoder-compute saving',6.3,muted)
save(fig,'fig2_pipeline')
(P/'figure_redesign.json').write_text(json.dumps({'release':60,'experiments_changed':False,'teaser_example':e['clip'],'teaser_support_inputs':[r['clip'] for r in rv],'source':'recorded gallery and release59 measured aggregates','encoders':'WavLM Base, DINOv2 ViT-B/14','expert_model_source':'outputs/revision56/expert_architecture.py','outputs':['fig1_teaser','fig2_pipeline']},indent=2))
