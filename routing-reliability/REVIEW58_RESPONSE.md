# Revision 58: completed corrections and remaining evidence gaps

This response does not assign new reviewer scores. The changes improve validity and transparency; they do not establish an 8/10 contribution.

| Reviewer concern | Implemented change | Remaining limitation |
|---|---|---|
| R1: unsupported method claim and incomplete primary comparison | Main table now includes audio, fixed fusion, margin, score-only direct gain, reliability direct gain and support policy together. Failure remains explicit. | No successful new transferable method or independent architectural replication. |
| R2: restricted replication and missing coverage/harm uncertainty | Executed exhaustive 169 calibration-actor subsets per checkpoint, with all outcomes retained; added source-bootstrap intervals for coverage, harm, rescue and gain with source counts. | Overlapping subsets are sensitivity analyses, not independent replications. External labels had already been inspected. |
| R3: unvalidated persistence method and unequal temporal access | Scene pilot has its own entry point, explicit offline/causal access, heuristic-uncertainty and non-robot labels. Excluded from the paper's evidence. | No new tracking experiment, causal SOTA comparison, hidden trajectory score or learned association model is supplied. |
| R4: sample-dependent region invalidates fixed-region proof | Certificate gets a distinct router-only support cutoff; proof conditions on training, with no calibration inputs defining regions. Calibration-feature/label mutation tests pass. | All four repaired regions abstain. This fixes the dependence error, not useful certified coverage or external validity. |
| R4: sparse calibration anecdote | Executed all 84 three-actor, 84 six-actor and one full-nine subsets for each checkpoint; compared raw/isotonic/sigmoid heads across five archived conditions. | 5,070 metric rows reuse the same actors and encoders. No universal calibration-failure claim. |
| R5: manuscript/demo mismatch and ambiguous reproduction | Separate routing and scene pages; exact result links; inspection, score replay and full encoder extraction distinguished. Updated manuscript and supplement compiled and inspected. | Public artifact remains non-anonymous. No robot controller or physical transfer validation. |

## New measured findings

With all nine calibration actors, checkpoint 11 sigmoid calibration reduces clean RAVDESS signed-score MSE from 1.140 to 0.891, while routing gain falls from 1.74 to 0.87 percentage points and switching from 5.73% to 3.12%. Checkpoint 22 has a smaller gain decline, 5.73 to 5.56 points, despite lower error. Coverage differs; this is not a matched-rate superiority test.

A weighting consistency check was added: the full-nine-actor recalibrated procedures reproduce all 30 archived policy cases. The initial development run used disagreement-renormalized actor weights; it is superseded by the released run using the exact original actor weighting. Published tables and paper use only the corrected run.

The certificate cutoff changes from 29.981 to 20.534 for certification only. The empirical support policy and locked primary result remain unchanged. Its four lower bounds are negative. The manuscript withdraws the earlier proof justification explicitly.

## What must still happen before an 8-level scientific claim

For the routing paper, a consequential general mechanism needs evidence across independent model architectures and domains, or a revised method must beat strong controls on a new untouched evaluation while retaining useful coverage. For object memory, a distinct causal association method needs held-out full-sequence evaluation of identity, distractors, reappearance delay and calibrated localization. Neither requirement is satisfied by a website or more analyses of the same test actors.
