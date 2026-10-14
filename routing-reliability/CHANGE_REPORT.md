# Release 59 — rewritten paper and new executed experiments

## What was executed

- New external head inference for three existing trained fusion-head families × five matching checkpoints × three input conditions: 45 prediction archives. Fifteen-statistic direct and structured routers were refit on the original source roles; margin was retained as a control. Fixed and matched-rate evaluation produces 270 rows.
- Logit-preprocessing ablation: within-clip standardization, raw softmax, and calibration-fitted temperature softmax, plus equal-volume comparisons against existing score families. Two checkpoints, all five archived evaluation conditions, 270 rows.
- Numerical replay verifies gain = rescue − harm, 45 prediction/outcome archives, and exact shared interaction-head routing-score reproduction for six archived settings. Ten standardized preprocessing refits reproduce their reference predictions with zero maximum score difference.

## What the new evidence supports

Static-occluder direct-routing gain is negative in 15/15 fixed-threshold head/checkpoint combinations. At 19.97% matched switching, it remains negative in 14/15 (mean −2.05 points). Thus excess admissions alone do not explain the failure. Clean direct gains are positive in all fifteen under both rules.

Mean direct scores rise in only 6/15 static comparisons. A universal confidence-inversion claim is therefore unsupported. All added analyses are exploratory on an inspected external population; all heads share frozen WavLM/DINOv2 encoders. The experiment reuses trained expert weights, rather than claiming new expert training.

The original primary comparison remains failed: support rejects every clean external clip and trails margin by 4.17 points, paired 95% actor interval [−6.42, −1.91]. This result is not replaced by the best new control.

## Manuscript and figure changes

The main paper is rewritten as one audio–visual reliability analysis. It contains eight main pages plus two reference pages, 41 references, seven original vector figures, explicit information/fitting roles, new controls and paired primary comparisons. The 20-page technical supplement includes all 270 architecture outcomes in paired fixed/matched columns, preprocessing results, actor outcomes, calibration ranges, proof assumptions, source chronology and reproduction instructions.

The seven figures are newly generated from executed predictions and real source-video frames. SAM 3D was studied for organization and visual hierarchy only; its text, figures, results and scientific task were not copied. Object-memory/Ameca pilots remain separate.

## Packaging correction

The prior complete ZIP incorrectly exposed an older manuscript at its top-level manuscript path. This release uses one canonical manuscript directory. Paper PDFs on the website are byte-identical to that directory. Historical experimental directories remain solely as reproducibility dependencies; obsolete paper-facing files are removed from this ZIP.

## Evidence gaps

- No independent encoder family or natural-visibility benchmark.
- No new untouched reserve for selecting a remedy after these analyses.
- No physical robot/Ameca validation, streaming inference claim, or hidden-object localization evidence from these emotion experiments.
- The repaired fixed-region certificate is valid only under its stated sampling assumptions and remains vacuous at nine calibration actors.
- The paper is an expanded empirical reliability analysis, not an established novel winning method. Neither more experiment rows nor redesigned figures justify a promised reviewer score.
