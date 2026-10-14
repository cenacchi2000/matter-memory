from pathlib import Path
import json,subprocess
import numpy as np,pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
P=Path(__file__).resolve().parent;S=P.parent/'revision56';F=P/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
C={'rescue':'#007F73','harm':'#C35B37','neutral':'#969DA5','raw':'#476A9C','isotonic':'#AD6730','sigmoid':'#7C579A','fixed':'#476A9C','batch':'#007F73','support':'#7C579A'}
def save(fig,n):
 fig.savefig(F/(n+'.pdf'),bbox_inches='tight',pad_inches=.04);fig.savefig(F/(n+'.svg'),bbox_inches='tight',pad_inches=.04);(F/(n+'.svg')).write_text((F/(n+'.svg')).read_text().replace('DejaVu Sans','Arial'));fig.savefig(F/(n+'.png'),bbox_inches='tight',pad_inches=.04,dpi=180);plt.close(fig)
data=json.loads((S/'site/data.js').read_text().removeprefix('window.EVIDENCE=').rstrip(';'));record=[]
def frame(e,occlude=False):
 f=F/(e['id']+'.png')
 if not f.exists():subprocess.run(['/Users/filippo/miniconda3/bin/ffmpeg','-v','error','-y','-ss','1','-i',str(S/'site'/e['video']),'-frames:v','1',str(f)],check=True)
 im=np.array(Image.open(f).convert('RGB'))
 if occlude:im[33:191,33:191]=128
 return im
# 1: deterministic crossing example among archived gallery candidates.
pool=[e for e in data if e['dataset']=='CREMA-D' and e['conditions']['clean']['methods']['opportunity_advantage']['switch']==False and e['conditions']['video_occlude50']['methods']['opportunity_advantage']['switch'] and e['conditions']['video_occlude50']['delta']==-1]
e=sorted(pool,key=lambda e:e['clip'])[0];record.append(dict(figure=1,clip=e['clip'],selection='lexicographically first archived-gallery CREMA clip whose legacy score crosses threshold into harm'))
fig=plt.figure(figsize=(7.1,2.25));gs=fig.add_gridspec(1,4,width_ratios=[1,1.4,1,1.4],wspace=.16)
for j,(cond,title) in enumerate([('clean','(a) Clean input'),('video_occlude50','(b) Static occlusion')]):
 ax=fig.add_subplot(gs[0,j*2]);ax.imshow(frame(e,j==1));ax.axis('off');ax.set_title(title,loc='left',fontweight='bold',fontsize=8)
 ax=fig.add_subplot(gs[0,j*2+1]);ax.axis('off');r=e['conditions'][cond];m=r['methods']['opportunity_advantage'];lines=[('Intended label',e['label'], '#202A34'),('Audio',r['audio'],C['rescue']),('Fusion',r['fusion'],C['harm']),('Switch score',f"{m['score']:+.3f}",'#202A34'),('Locked threshold',f"{m['threshold']:.3f}",'#202A34'),('Final prediction',m['prediction'],C['harm'] if j else C['rescue'])]
 for i,(label,value,col) in enumerate(lines):
  ax.text(0,.98-i*.165,label,transform=ax.transAxes,fontsize=7,color='#626872');ax.text(0,.90-i*.165,value,transform=ax.transAxes,fontsize=9,color=col,fontweight='bold')
save(fig,'fig1_teaser')
# 2: detailed executed graph, explicit module types and fitting roles.
fig,ax=plt.subplots(figsize=(7.1,3.0));ax.set(xlim=(0,16),ylim=(0,6));ax.axis('off')
def box(x,y,w,h,title,sub,color='#EEF3F6',edge='#718697'):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.04',facecolor=color,edgecolor=edge,lw=.7));ax.text(x+w/2,y+h*.73,title,ha='center',va='center',fontsize=7.2,fontweight='bold');ax.text(x+w/2,y+h*.30,sub,ha='center',va='center',fontsize=6.8)
def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',lw=.8,color='#687880'))
ax.text(.1,5.7,'(a) Encode and fuse',fontweight='bold',fontsize=8)
ax.text(6.65,5.7,'(b) Measure',fontweight='bold',fontsize=8)
ax.text(10.1,5.7,'(c) Fit, calibrate, select',fontweight='bold',fontsize=8)
box(.1,4,2.5,1.1,'WavLM Base','Audio · 16 kHz\nfrozen encoder')
box(.1,2.35,2.5,1.1,'DINOv2 B/14','Video · 8 frames\nfrozen encoder')
box(3.3,4.25,2.4,.85,'Audio head','6 logits','#E6F1EC')
box(3.3,2.85,2.4,1.1,'Fusion head','2 tokens\n4-head attention','#E6F1EC')
box(3.3,1.7,2.4,.85,'Video head','6 logits','#E6F1EC')
for a,b in [((2.65,4.6),(3.25,4.7)),((2.65,4.4),(3.25,3.55)),((2.65,3),(3.25,3.35)),((2.65,2.65),(3.25,2.2))]:arrow(a,b)
box(6.65,3.5,2.6,1.6,'15 score features','Max / margin\nentropy / JS\nagreement')
for a,b in [((5.75,4.7),(6.6,4.7)),((5.75,3.35),(6.6,4.1)),((5.75,2.15),(6.6,3.65))]:arrow(a,b)
box(.1,.15,2.5,1.05,'4 extra crops','DINOv2 encodings');arrow((1.35,2.3),(1.35,1.25))
box(3.3,.15,5.95,1.05,'8 visual probes','Temporal / crop distances; pixel statistics')
arrow((2.65,.65),(3.25,.65));arrow((2.6,2.3),(3.3,1.25))
box(10.1,3.5,2.65,1.6,'Router controls','Direct gain\n3-class outcome\nq × (2r − 1)','#E6F1EC')
arrow((9.3,4.3),(10.05,4.3));arrow((9.3,.8),(10.4,3.45))
box(10.1,1.7,2.65,1.25,'Calibration','Isotonic / sigmoid\nor raw scores','#F2EAF5');arrow((11.4,3.45),(11.4,3))
box(13.4,1.7,2.5,3.4,'Decisions','Fixed threshold\n\nbatch budget\n\nsupport gate','#F8EEE3');arrow((12.8,2.3),(13.35,2.3));arrow((12.8,4.3),(13.35,4.3))
ax.text(10.15,1.1,'Predictors: router actors',fontsize=6.8);ax.text(10.15,.65,'Maps: calibration actors',fontsize=6.8);ax.text(10.15,.2,'Thresholds: clean tune actors',fontsize=6.8)
save(fig,'fig2_pipeline')
# 3: volume / composition / gain from exact archived policy outcomes.
r=pd.read_csv(S/'revision55_policy_diagnosis.csv');r=r[(r.method=='opportunity_advantage')&(r.budget==.2)&r['mode'].isin(['forced','original_fixed'])];fig,axs=plt.subplots(1,3,figsize=(7.1,2.35));order=[('clean','forced'),('clean','original_fixed'),('video_occlude50','forced'),('video_occlude50','original_fixed')];a=pd.DataFrame([r[(r.condition==c)&(r['mode']==m)].iloc[0] for c,m in order]);labels=['Clean\nbatch','Clean\nfixed','Static\nbatch','Static\nfixed'];x=np.arange(4)
axs[0].bar(x,a.change*100,color=[C['batch'],C['fixed']]*2,hatch=['','//','','//']);axs[0].set_ylabel('Actual switches (%)');axs[0].set_title('(a) Switch volume',loc='left')
bot=np.zeros(4)
for key in ['rescue','harm','neutral']:
 vals=a[key].to_numpy()/a.change.to_numpy()*100;axs[1].bar(x,vals,bottom=bot,color=C[key],label=key);bot+=vals
axs[1].set_ylabel('Among selected switches (%)');axs[1].set_title('(b) Selected outcomes',loc='left');axs[1].legend(fontsize=6,loc='upper center',bbox_to_anchor=(.5,1.0))
axs[2].bar(x,a.gain*100,color=[C['batch'],C['fixed']]*2,hatch=['','//','','//']);axs[2].axhline(0,color='#555',lw=.6);axs[2].set_ylabel('Gain over audio (pp)');axs[2].set_title('(c) Decision value',loc='left')
for ax in axs:ax.set_xticks(x,labels,fontsize=6.8)
fig.tight_layout(w_pad=1.2);save(fig,'fig3_operating')
# 4: fitted mapping and evidence counts, no implication zero means certainty.
k=json.loads((S/'isotonic_knots.json').read_text())['r'];cal=pd.read_csv(S/'calibration_support_cases.csv').query('delta!=0');test=pd.read_csv(S/'near_zero_rescue_cases.csv');fig,axs=plt.subplots(1,3,figsize=(7.1,2.05));axs[0].plot(k['x'],k['y'],color=C['isotonic']);axs[0].set(xlim=(0,1),ylim=(-.05,1.05),xlabel='Raw conditional score',ylabel='Isotonic output');axs[0].set_title('(a) Fitted map',loc='left');zero=max(x for x,y in zip(k['x'],k['y']) if y==0);axs[0].axvspan(0,zero,color=C['harm'],alpha=.1)
for target,col,lab in [(1,C['rescue'],'Rescue'),(-1,C['harm'],'Harm')]:
 axs[1].hist(cal[cal.delta==target].r_raw,bins=np.linspace(0,1,16),alpha=.6,color=col,label=lab);ii=test.delta==target;axs[2].scatter(test.r_raw[ii],test.r_iso[ii],marker='o' if target==1 else 'x',s=24,color=col,label=lab)
axs[1].set(xlabel='Raw conditional score',ylabel='Calibration clips');axs[1].set_title('(b) Calibration support',loc='left');axs[1].legend(fontsize=6);axs[2].set(xlabel='Raw conditional score',ylabel='Mapped score',ylim=(-.004,.068));axs[2].set_title('(c) Inspected test bin',loc='left');axs[2].legend(fontsize=6);fig.tight_layout();save(fig,'fig4_calibration')
# 5: direct transfer distribution and coverage / gain.
dev=np.load(S/'development_seed11.npz');rc=(dev['roles']=='calibration')&(dev['conditions']=='clean');ext=np.load(S/'confirmation_seed11_clean.npz');fig,axs=plt.subplots(1,3,figsize=(7.1,2.2));bins=np.linspace(0,12,35)
axs[0].hist(np.log1p(dev['support_distance'][rc]),bins=bins,density=True,histtype='step',lw=1.5,label='CREMA calibration',color=C['raw']);axs[0].hist(np.log1p(ext['support_distance']),bins=bins,density=True,histtype='step',lw=1.5,label='RAVDESS clean',color=C['harm']);axs[0].axvline(np.log1p(29.9809889793396),color=C['support'],ls='--');axs[0].set(xlabel='log(1 + support distance)',ylabel='Density');axs[0].set_title('(a) Clean domain shift',loc='left');axs[0].legend(fontsize=6)
axs[1].bar(['CREMA\ncalibration','RAVDESS\nclean'],[100*dev['support'][rc].mean(),100*ext['support'].mean()],color=[C['raw'],C['harm']]);axs[1].set_ylabel('Support accepted (%)');axs[1].set_title('(b) Reference acceptance',loc='left')
r=pd.read_csv(S/'confirmation_results.csv');r=r[(r.seed==11)&(r.condition=='clean')&(r['mode']=='fixed')&(r.budget==.2)].set_index('method');names=['margin','scores_gain','supported_gain'];axs[2].bar(['Margin','Direct','Support'],r.loc[names,'gain']*100,color=[C['raw'],C['rescue'],C['support']]);axs[2].set_ylabel('Gain over audio (pp)');axs[2].set_title('(c) Retained benefit',loc='left');fig.tight_layout();save(fig,'fig5_support')
# 6: matched display both checkpoints, all subset sizes, three outcomes.
r=pd.read_csv(P.parent/'revision58/calibration_summary.csv');fig,axs=plt.subplots(2,3,figsize=(7.1,3.7),sharex=True)
for row,seed in enumerate([11,22]):
 for col,metric in enumerate(['signed_mse','gain','coverage']):
  ax=axs[row,col]
  for kind in ['raw','isotonic','sigmoid']:
   a=r[(r.seed==seed)&(r.calibrator==kind)&(r.dataset==f'confirmation_seed{seed}_clean')];scale=1 if col==0 else 100;ax.plot(a['size'],a[metric+'_mean']*scale,'o-',color=C[kind],ms=3,label=kind);ax.fill_between(a['size'],a[metric+'_min']*scale,a[metric+'_max']*scale,color=C[kind],alpha=.12)
  ax.set_xticks([3,6,9]);ax.set_title(f'({chr(97+row*3+col)}) Checkpoint {seed}',loc='left');ax.set_ylabel(['Signed-score MSE','Gain (pp)','Switches (%)'][col]);
  if row:ax.set_xlabel('Calibration actors')
axs[0,0].legend(fontsize=6);fig.tight_layout();save(fig,'fig6_sensitivity')
# 7: five deterministic evidence categories, all outputs shown on identical examples.
choices=[('Rescue','CREMA-D','rescue','clean'),('Harm','CREMA-D','harm','clean'),('Missed rescue','RAVDESS','abstained_rescue','clean'),('Avoided harm','RAVDESS','harm_avoided','video_occlude50'),('Clean rejection','RAVDESS','occlusion_failure','clean')];fig,axs=plt.subplots(1,5,figsize=(7.1,2.35))
for j,(title,ds,cat,cond) in enumerate(choices):
 e=sorted([x for x in data if x['dataset']==ds and x['category']==cat],key=lambda x:x['clip'])[0];ax=axs[j];ax.imshow(frame(e,cond!='clean'));ax.axis('off');ax.set_title(f'({chr(97+j)}) {title}',fontsize=7,fontweight='bold',loc='left');r=e['conditions'][cond];method='opportunity_advantage' if ds=='CREMA-D' else 'supported_gain';m=r['methods'][method];mr=r['methods']['margin'];txt=f"GT: {e['label']}\nAudio: {r['audio']}\nFusion: {r['fusion']}\nMargin: {mr['prediction']}\n{'Legacy' if ds=='CREMA-D' else 'Support'}: {m['prediction']}";ax.text(0,-.03,txt,transform=ax.transAxes,va='top',fontsize=7);record.append(dict(figure=7,category=title,clip=e['clip'],condition=cond,selection='lexicographic first archived-gallery member within stated dataset/category',method=method))
fig.subplots_adjust(wspace=.10,bottom=.35);save(fig,'fig7_examples');(P/'example_selection.json').write_text(json.dumps(record,indent=2));print('7 figures exported to PDF, SVG, PNG')
