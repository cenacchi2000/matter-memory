"""Fixed development protocol for classical material correspondence controls."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent


def observe(points, bounds):
    uv = np.floor((points[:, :2] - bounds[:2, 0]) /
                  (bounds[:2, 1] - bounds[:2, 0]) * 64).astype(int)
    valid = np.all((uv >= 0) & (uv < 64), axis=1)
    ids = np.flatnonzero(valid)
    bins = uv[ids, 0] * 64 + uv[ids, 1]
    order = np.lexsort((points[ids, 2], bins))
    _, first = np.unique(bins[order], return_index=True)
    ids = ids[order[first]]
    ids = ids[np.random.default_rng(314).permutation(len(ids))]
    if not len(ids):
        raise ValueError('No visible points: protocol requires explicit handling')
    return points[ids].copy(), ids


def metrics(cm):
    n = int(cm.sum())
    denominators = cm.sum(axis=1)
    return {'confusion': cm.tolist(), 'accuracy': float(np.trace(cm) / n) if n else None,
            'balanced_accuracy': float(np.mean(np.diag(cm) / denominators))
            if np.all(denominators > 0) else None, 'observations': n}


def main():
    protocol_bytes = (HERE / 'material_screen_protocol.json').read_bytes()
    protocol = json.loads(protocol_bytes)
    records = []
    for dataset in protocol['datasets']:
        root = Path('work/revision5/gns') / dataset
        meta = json.loads((root / 'metadata.json').read_text())
        xyz = np.load(root / 'first_train.npz')['position']
        labels_gt = (xyz[0] > np.median(xyz[0], axis=0)).astype(int)
        observations = [observe(p, np.asarray(meta['bounds'])) for p in xyz]
        initial, init_ids = observations[0]
        initial_labels = labels_gt[init_ids].copy()
        was_initial = np.zeros(xyz.shape[1], dtype=bool)
        was_initial[init_ids] = True
        initial_tree = cKDTree(initial)
        for stride in protocol['strides']:
            for method in protocol['methods']:
                previous = initial.copy()
                labels = initial_labels.copy()
                velocity = np.zeros_like(previous)
                cm = np.zeros((3, 2, 2), dtype=np.int64)
                initialized_cm = np.zeros_like(cm)
                unseen_cm = np.zeros_like(cm)
                for t in range(stride, len(xyz), stride):
                    current, ids = observations[t]
                    if method == 'nearest_initial':
                        labels = initial_labels[initial_tree.query(current)[1]]
                    elif method == 'initial_majority':
                        labels = np.broadcast_to((initial_labels.mean(axis=0) > .5).astype(int), (len(current), 3))
                    else:
                        prediction = previous + (velocity if method == 'estimated_constant_velocity' else 0)
                        _, match = cKDTree(prediction).query(current)
                        labels = labels[match]
                        velocity = current - previous[match]
                    previous = current
                    initialized = was_initial[ids]
                    for axis in range(3):
                        truth, pred = labels_gt[ids, axis], labels[:, axis]
                        np.add.at(cm[axis], (truth, pred), 1)
                        np.add.at(initialized_cm[axis], (truth[initialized], pred[initialized]), 1)
                        np.add.at(unseen_cm[axis], (truth[~initialized], pred[~initialized]), 1)
                for axis in range(3):
                    records.append({'dataset': dataset, 'axis': 'xyz'[axis], 'stride': stride, 'method': method,
                                    'initial_class_counts': np.bincount(initial_labels[:, axis], minlength=2).tolist(),
                                    'all_visible': metrics(cm[axis]),
                                    'initially_observed': metrics(initialized_cm[axis]),
                                    'initially_unobserved': metrics(unseen_cm[axis])})
        print(dataset, 'complete', flush=True)
    out = {'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(), 'protocol': protocol,
           'records': records, 'record_count': len(records),
           'interpretation': 'Classical development diagnostics only; no learned method or novelty claim'}
    (HERE / 'material_multidataset_screen.json').write_text(json.dumps(out, indent=2) + '\n')
    for dataset in protocol['datasets']:
        for stride in protocol['strides']:
            rows = [r for r in records if r['dataset'] == dataset and r['stride'] == stride]
            summary = {method: round(float(np.mean([r['all_visible']['balanced_accuracy'] for r in rows
                       if r['method'] == method and r['all_visible']['balanced_accuracy'] is not None])), 4)
                       for method in protocol['methods']}
            print(dataset, stride, summary)


if __name__ == '__main__':
    main()
