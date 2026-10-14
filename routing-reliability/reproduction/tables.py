from pathlib import Path
import numpy as np,pandas as pd,json
P=Path(__file__).resolve().parent;z=np.load(P.parent/'revision56/confirmation_seed11_clean.npz');g=z['actors'];d=z['delta'];groups=np.unique(g);draw=np.random.default_rng(5902).integers(0,24,(5000,24));ref=z['margin_fixed_0.2']*d
f=pd.read_csv(P.parent/'revision56/confirmation_results.csv');f=f[(f.seed==11)&(f.condition=='clean')&(((f['mode']=='fixed')&(f.budget==.2))|(f['mode']=='endpoint'))].set_index('method')
methods={'audio':'Audio only','fusion':'Fixed fusion','margin':'Margin','scores_gain':'Direct, 15 scores','reliable_gain':'Direct, 23 features','outcome_raw':'Three outcomes, 23','two_raw':'Structured raw, 23','two_isotonic':'Structured isotonic, 23','two_platt':'Structured sigmoid, 23','supported_gain':'Support gate, 23'}
s=['\\begin{tabular}{lrrrrrl}\\toprule','Policy & Acc. & Gain & Switch & Rescue & Harm & Difference from margin [95\\% CI]\\\\\\midrule']
for m,n in methods.items():
 r=f.loc[m];mask=np.zeros(len(d),bool) if m=='audio' else z['disagreement'] if m=='fusion' else z[m+'_fixed_0.2'];v=np.array([np.mean((mask*d-ref)[g==a]) for a in groups]);lo,hi=np.quantile(v[draw].mean(1),[.025,.975])*100
 s.append(n+' & '+' & '.join(f'{r[k]*100:.2f}' for k in ['accuracy','gain','change','rescue','harm'])+f' & {v.mean()*100:+.2f} [{lo:+.2f}, {hi:+.2f}]'+r'\\')
s+=['\\bottomrule\\end{tabular}'];(P/'main_table.tex').write_text('\n'.join(s))
