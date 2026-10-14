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
# 7: five deterministic evidence categories, all outputs shown on identical examples.
choices=[('Rescue','CREMA-D','rescue','clean'),('Harm','CREMA-D','harm','clean'),('Missed rescue','RAVDESS','abstained_rescue','clean'),('Clean rejection','RAVDESS','occlusion_failure','clean')];fig,axs=plt.subplots(1,4,figsize=(7.1,2.35))
for j,(title,ds,cat,cond) in enumerate(choices):
 e=sorted([x for x in data if x['dataset']==ds and x['category']==cat],key=lambda x:x['clip'])[0];ax=axs[j];ax.imshow(frame(e,cond!='clean'));ax.axis('off');ax.set_title(f'({chr(97+j)}) {title}',fontsize=7,fontweight='bold',loc='left');r=e['conditions'][cond];method='opportunity_advantage' if ds=='CREMA-D' else 'supported_gain';m=r['methods'][method];mr=r['methods']['margin'];txt=f"GT: {e['label']}\nAudio: {r['audio']}\nFusion: {r['fusion']}\nMargin: {mr['prediction']}\n{'Legacy' if ds=='CREMA-D' else 'Support'}: {m['prediction']}";ax.text(0,-.03,txt,transform=ax.transAxes,va='top',fontsize=7);record.append(dict(figure=7,category=title,clip=e['clip'],condition=cond,selection='lexicographic first archived-gallery member within stated dataset/category',method=method))
fig.subplots_adjust(wspace=.10,bottom=.35);save(fig,'fig7_examples');(P/'example_selection.json').write_text(json.dumps(record,indent=2));print('7 figures exported to PDF, SVG, PNG')

