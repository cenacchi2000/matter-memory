# Matter Memory — research development explorer

Interactive 3D simulation explorer, synchronized comparisons, six videos, and an original proposed architecture.

## Scientific status
This is a research concept, not a validated novel model or a CVPR publication. No Matter Memory predictions or superiority claims are presented.

CoTracker3, CoTracker2, and RAFT are actually executed pretrained baselines on three fixed synthetic clips. They are not all current state-of-the-art methods. CoTracker2 is a historical control; the CoTracker generations are related.

## Comparison protocol
One first-training trajectory each from GNS Water-3D, Sand-3D, Goop-3D. 32 evenly spaced frames, 256x256 opaque particle renders, 16 initially visible point queries. Inputs have no source colors or identity texture. Reference identities are for evaluation only.

This is a development diagnostic with strong domain shift and temporal aliasing, not a standard benchmark. Errors are mean pixel distance on ground-truth-visible queries excluding the initial frame. Not TAP-Vid AJ. Do not interpret these errors as the original papers' performance or as evidence for a new method.

See video_protocol.json, video_baseline_results.json, video_inputs.json, checkpoint_hashes.json and run_video_baselines.py. CoTracker2 runs on CPU because MPS border padding is unsupported. CoTracker3 uses MPS with the PyTorch CPU fallback for 3D grid sampling. RAFT uses MPS with CPU bilinear track integration.

## Run locally
`python3 -m http.server 8000`

## GitHub Pages
Publish main / (root) in Settings > Pages. All website paths are relative to support a project subpath. No build or external JavaScript framework is required.

## Sources and attribution
- GNS data: Sanchez-Gonzalez et al., Learning to Simulate Complex Physics with Graph Networks, ICML 2020. https://sites.google.com/view/learning-to-simulate
- CoTracker: https://github.com/facebookresearch/co-tracker — author weights and source, CC-BY-NC with exceptions documented upstream. Model weights and third-party source are not redistributed here.
- RAFT: Teed and Deng, ECCV 2020. https://github.com/princeton-vl/RAFT . Inference implementation and weights from torchvision: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.optical_flow.raft_large.html
- DoughNet: https://dough-net.github.io/ — related work only, not run in this comparison.

Rendered simulation clips and derived trajectory samples are attributed to the GNS dataset. The upstream terms remain applicable. No blanket license for third-party data is asserted.
