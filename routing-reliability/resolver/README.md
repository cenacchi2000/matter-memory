# Occlusion Resolver

This project replaces the earlier audio-visual routing presentation with an occlusion-only implementation, research draft, website and endpoint audit.

Implemented: immutable query RGB, multiscale grayscale proposals, color matching, repeated-frame acceptance, retained location history, three conditional location hypotheses, and a symbolic view-change request. There is no learned containment model or physical Ameca controller.

## Executed result

31 sparse target-mask endpoints from 22 eligible local Rubric Office clips. Resolver: 9 candidate hits, 7 accepted hits, 0 accepted misses, 24 abstentions. Appearance-only has the same counts. This is a conservative prototype, not a proven novel method or CVPR-ready result.

## Reproduce

```
python -m pip install -r requirements.txt
python code/test_resolver.py
python code/evaluate.py --data data/rubric_office --output results
python code/report_assets.py --data data/rubric_office
python memory_figures.py
python -m http.server 8792 --directory site
```

The complete local ZIP includes the available source corpus under data/rubric_office. It is from TCOW Rubric Office (Van Hoorick et al., CVPR 2023), https://tcow.cs.columbia.edu/ and https://github.com/basilevh/tcow . Retain original source terms and attribution; this package does not relicense upstream data. The code ZIP on the site excludes videos and annotations.

The paper is a five-page research draft, not the previously requested full eight-page CVPR submission. The appendix is 20 pages with protocol, implementation boundaries and all 22 per-clip audit records. These artifacts replace routing content, rather than relabel its results as occlusion performance.

Four implementation tests pass. No hidden-location accuracy, calibrated spatial coverage, modern learned-baseline superiority, semantic property inference or robot transfer is established. Code returns hypotheses explicitly and exposes rejection rather than pretending to see through objects.

Figure 1 no longer contains “Original recorded pixels” or “No artificial mask”. The old face gallery has been removed; the scene-memory and execution diagram replaces it. Figures now have new numbering in the standalone paper.
