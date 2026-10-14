from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];rows=json.loads((P/'results/endpoint_results.json').read_text());cases=json.loads((P/'results/case_assets.json').read_text());esc=lambda s:s.replace('_',r'\_')
parts=[r'''\documentclass[10pt,letterpaper]{article}
\usepackage[margin=.8in]{geometry}\usepackage{times,graphicx,booktabs,amsmath,longtable,hyperref,listings}
\lstset{basicstyle=\ttfamily\small,breaklines=true,columns=fullflexible}
\begin{document}
\section*{S1. Occlusion resolver: evaluation contract}
This supplement documents the executed causal prototype. It contains no audio--visual routing experiment. Initial query masks define object bounding rectangles; later target masks are used only after inference. The primary score is point membership inside a sparse target mask. It is not an amodal segmentation score, exact correspondence metric, or hidden-coordinate error.
\paragraph{Input.} A decoded RGB video resized to $320\times240$ and the earliest query mask. All frames from the query through the last evaluation endpoint are processed in temporal order. No frame after an endpoint contributes to its stored state.
\paragraph{Output.} A candidate, acceptance state, last supported point, evidence age, immutable appearance properties, and stationary/motion/context hypotheses. A view request is a symbolic action, not an executed camera command.
\paragraph{Population.} The local directory contains 37 videos. Twenty-two have an eligible query and later target annotation, giving 31 endpoints. Some clips contribute several endpoints. This is a local subset, not an official TCOW benchmark reproduction.
\paragraph{Reporting.} Candidate hits, accepted hits, accepted misses and abstentions are reported together. A rejected correct proposal is not counted as a supported answer. Missing evidence is not counted as an exact location estimate.
\begin{center}\includegraphics[width=\linewidth]{figures/results.pdf}\end{center}
The accepted-hit count is seven for both the resolver and appearance-only control; confirmation has no measured aggregate endpoint advantage. There are no accepted misses in this sample, but only seven accepted endpoints. This is not a population guarantee.
''',r'''\section*{S2. Persistent object record}
The identity record is the initial query RGB crop, grayscale template and HSV histogram. It is never overwritten during a loss interval or after reacquisition. Mean RGB and crop dimensions are directly measured properties and can include background. No material, affordance or semantic category estimator is implemented.
\begin{center}\includegraphics[width=\linewidth]{figures/fig7_memory.pdf}\end{center}
\begin{tabular}{ll}\toprule
Field&Meaning\\\midrule
Query RGB&Immutable evidence from initialization\\
Last supported point&Latest accepted appearance candidate\\
Evidence age&Elapsed frame time since acceptance\\
Velocity&Smoothed displacement across accepted matches\\
Context coordinate&Local-flow transported hypothesis\\
Pending candidate&Consecutive-frame confirmation state\\\bottomrule
\end{tabular}
\paragraph{Important boundary.} A supported match is still a model decision. A false accepted match can corrupt coordinates even though query appearance remains intact. The word supported therefore refers to the explicit appearance test, not ground-truth correctness.
''',r'''\section*{S3. Candidate generation and acceptance}
Three rescaled query templates are correlated globally with the current grayscale frame. At each scale only the strongest grayscale peak is considered. HSV histogram correlation reweights that proposal; it does not generate all possible color candidates. This is a specific weakness when a distractor dominates grayscale correlation.
\begin{align*}
z&=0.7\,\mathrm{NCC}+0.3\,\mathrm{HC},\\
q&=[z\geq0.72]\land[\mathrm{NCC}\geq0.55]\land[\mathrm{gap}\geq0.025].
\end{align*}
The gap is the strongest correlation minus the strongest value outside a neighborhood around the peak. It is not a posterior probability or conformal score. Histogram comparison uses 12 hue bins and eight saturation bins. The query bounding rectangle, not the exact mask silhouette, defines the template.
\begin{lstlisting}
for frame in observed_prefix:
    candidate = best_of_three_scales(frame, immutable_query)
    qualifies = score >= .72 and ncc >= .55 and gap >= .025
    if qualifies and near_previous_pending_candidate:
        confirmation_count += 1
    else:
        confirmation_count = int(qualifies)
    accepted = qualifies and confirmation_count >= 2
    if accepted:
        update_last_position_and_velocity()
        reset_evidence_age()
    else:
        retain_last_supported_state()
    emit_observation_and_hypotheses_separately()
\end{lstlisting}
The appearance-only ablation removes confirmation and uses the same proposal scores and thresholds. Its endpoint totals tie the resolver; that negative result is retained in the paper.
''',r'''\section*{S4. Hidden-state hypotheses}
Three locations are exposed without collapsing them into a certain answer: the last supported point, a constant-velocity extrapolation capped at one second, and a local optical-flow transport. Median flow comes from a $20\times20$ neighborhood around the previous context coordinate. The flow is computed from consecutive observed frames with Farneback's algorithm.
\paragraph{What flow cannot establish.} The tracked texture may belong to an occluder or background. No semantic container association is learned. The three hypotheses are alternative explanations, not independent measurements. Their probabilities are not calibrated and their display radius is heuristic.
\paragraph{How hypotheses are currently used.} The API and visualization expose them for inspection and explanatory recall. They do not rerank the appearance proposal. Accordingly, endpoint gains cannot be attributed to motion-aware candidate selection. A future ablation must implement that decision dependency before claiming its benefit.
\paragraph{Time.} The evaluator processes each frame at the source FPS. Age is counted in elapsed frame intervals. Motion velocity is updated only across accepted matches. A one-second extrapolation cap prevents arbitrarily large long-horizon displacement but does not make the predicted position correct.
\paragraph{View requests.} Unresolved identity or location maps to a symbolic request for a view change. This release does not predict camera poses, execute a robot gaze command or measure whether a requested view resolves uncertainty. Such measurements require interventions or alternative observations.
''',r'''\section*{S5. Baselines and information access}
The expanded evaluation compares the resolver with appearance-only acceptance and a stationary initial center. The first shares every appearance component and isolates confirmation. The second always returns the initial center and never abstains. Both use the same query rectangle.
\paragraph{Archived learned trackers.} The interactive scene explorer retains earlier CoTracker3 and CoTracker2 predictions on three selected clips. These models receive the prefix through an annotated scoring endpoint and may use future frames relative to an intermediate display. They are not causal baselines and were not newly evaluated on the expanded 22-clip set.
\paragraph{Initialization.} Archived point trackers use a query point, while the current resolver uses a query-mask bounding rectangle. This additional appearance supervision is material. The website is a qualitative comparison, not a matched-supervision leaderboard.
\paragraph{Methods not run.} TCOW, SAM 2, XMem and TAPIR are related work, not executed full-set baselines in this release. No table should suggest otherwise. A strong paper requires their evaluation or an appropriate task-matched subset, with timing, initialization and future-frame access controlled.
\paragraph{Scope of the ablation.} Confirmation and non-confirmation tie on endpoint counts. Differences in intermediate acceptance could be useful or harmful; sparse endpoint masks cannot determine which. Dense visibility and identity annotations would be needed for a temporal claim.
''']
# Page 6 table
s=r'\section*{S6. Expanded per-clip endpoint audit}\begin{center}\small\begin{tabular}{lrrrr}\toprule Clip&Endpoints&Candidate hits&Accepted hits&Accepted misses\\\midrule\n'
for c in cases:
 r=[x for x in rows if x['clip']==c['clip'] and x['method']=='resolver'];s+=esc(c['clip'])+'&'+str(len(r))+'&'+str(sum(x['inside_target'] for x in r))+'&'+str(sum(x['accepted_hit'] for x in r))+'&'+str(sum(x['accepted_miss'] for x in r))+r'\\'+'\n'
s+=r'\bottomrule\end{tabular}\end{center}Repeated endpoints from a clip are clustered observations. The table includes every eligible clip, not only the three shown on the website. Candidate membership is scored even when the resolver rejects it. The complete machine-readable table also contains every baseline row.';parts.append(s.replace('\\n','\n'))
parts.append(r'''\section*{S7. Implementation verification}
Four tests execute: immutable memory and retained coordinates during loss; two-frame confirmation; deterministic prefix behaviour; finite separate hypotheses and an unresolved-state view request. All pass. Synthetic test images exercise code invariants only and are not visual benchmark results.
\paragraph{Replay integrity.} A query-anchor byte hash is checked before and after every evaluated clip. The evaluator checks that the immutable RGB crop has not changed. This does not certify correct localization: it certifies the intended memory policy.
\paragraph{No endpoint leakage.} The inference loop reads RGB frames only. Target masks are opened in the following scoring loop. Query annotations are permitted initialization. Offline tracker traces are used only by the qualitative website and are not read by the resolver.
\paragraph{Known limits.} Global template search is sensitive to texture, crop background and viewpoint. Correlation is not identity. The current rejection policy gives low answer coverage. Testing code invariants must not be described as proving perception robustness.
''')
parts.append(r'''\section*{S8. Evidence and claim ledger}
\begin{tabular}{p{.39\linewidth}p{.54\linewidth}}\toprule
Claim&Status\\\midrule
Immutable appearance record&Implemented and unit-tested\\
Causal frame processing&Executed on 22 eligible clips\\
Two-frame confirmation&Implemented; no endpoint gain over appearance control\\
Accepted target-mask hits&7 of 31 endpoints\\
Accepted out-of-mask predictions&0 of 31 endpoints, with 24 abstentions\\
Exact hidden position&Not measured or established\\
Semantic object properties&Not inferred; stored RGB and crop dimensions only\\
Container-aware tracking&Not implemented; local flow is a hypothesis\\
Robot conversation&Deterministic state-to-text template\\
Ameca control or transfer&Not executed\\
Novelty or state-of-the-art superiority&Not established\\\bottomrule
\end{tabular}
\paragraph{Research direction.} A useful next mechanism must change a measured decision: containment inference could propagate a target with a moved container; an active-view policy could reduce ambiguity; learned re-identification could recover appearance changes. None should be presented as an achieved capability before it is implemented and compared.
''')
parts.append(r'''\section*{S9. Reproduction and machine interface}
\begin{lstlisting}
python -m pip install -r requirements.txt
python code/test_resolver.py
python code/evaluate.py --data /path/to/rubric_office --output results
python code/report_assets.py
python memory_figures.py
\end{lstlisting}
The data must be acquired from the TCOW project with its original terms and attribution. The ZIP includes the three demonstration videos already used by the site, not the entire upstream dataset. Scripts use deterministic matching; no training seed or learned checkpoint is needed for the new resolver.
\paragraph{Records.} Each trace contains frame, candidate, accepted flag, state, last supported coordinate, evidence age, three hypotheses, a heuristic radius, NCC, color similarity, appearance score, ambiguity gap and query properties. The current code additionally emits a symbolic view request or continued-observation action.
\paragraph{Units.} Positions and radii use the $320\times240$ evaluation raster. Velocity uses pixels per second. Masks are evaluated after scaling and rounding coordinates to annotation resolution. These are not metric robot-space coordinates.
\paragraph{Case pages.} The next eleven pages show two clips each. Query RGB appears on the left; the last scored endpoint appears on the right with a green evaluation-mask outline. The outline is not supplied to inference. Tables include all scored endpoints for the resolver. Appearance and stationary records are in the JSON. No hidden-location ground truth is invented.
''')
for i in range(0,len(cases),2):
 s='\\section*{S'+str(10+i//2)+'. Per-clip records}\n'
 for c in cases[i:i+2]:
  n=c['clip'];s+='\\subsection*{'+esc(n)+'}\n'+r'\noindent\includegraphics[width=.48\linewidth]{case_assets/'+n+r'_query.jpg}\hfill\includegraphics[width=.48\linewidth]{case_assets/'+n+r'_endpoint.jpg}'+'\n'
  s+=f"Query frame {c['query_frame']}; displayed endpoint {c['endpoint_frame']}. Green outline: evaluation target mask, not model input.\n"
  s+=r'\begin{center}\small\begin{tabular}{rrrr}\toprule Frame&Candidate inside&Accepted&Evidence age (s)\\\midrule'+'\n'
  for r in rows:
   if r['clip']==n and r['method']=='resolver':s+=f"{r['frame']}&{int(r['inside_target'])}&{int(r['accepted'])}&{r['age_s']:.2f}"+r'\\'+'\n'
  s+=r'\bottomrule\end{tabular}\end{center}'+'\n'
 parts.append(s)
assert len(parts)==20
(P/'supplement.tex').write_text('\n\\clearpage\n'.join(parts)+'\n\\end{document}\n')
