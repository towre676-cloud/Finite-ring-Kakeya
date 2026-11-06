"""Build finite examples and exact integer certificates for the type model."""
from itertools import combinations
from pathlib import Path
import json
from type_model import build_model, unique_low_fibre_certificate

HERE = Path(__file__).resolve().parent
output = HERE / 'demo'
output.mkdir(exist_ok=True)
manifest = []
for low in (0, 1, 2):
    domains = {a: [list(t) for t in combinations(range(4), 2)] if a == low else [list(range(4))]
               for a in (0, 1, 2)}
    for ring in ('dual', 'z4'):
        for mode in ('capacity', 'labels'):
            name = f'n2_442_low{low}_{ring}_{mode}'
            data = dict(scope='Complete assigned-weight domain on support{0,1,2}; all low-fibre translations and orientations.',
                        model=build_model(2, domains, ring, mode),
                        expected_integer_feasible_assignments=0)
            data['certificate'] = unique_low_fibre_certificate(data['model'], low)
            (output / (name + '.json')).write_text(json.dumps(data, separators=(',', ':')) + '\n')
            manifest.append(name)
for ring in ('dual', 'z4'):
    domains = {a: [list(t) for t in combinations(range(4), 3)] for a in range(4)}
    model = build_model(2, domains, ring, 'labels')
    witness = {name: '1/4' if name.startswith('x:') else '1/16' for name in model['variables']}
    name = f'n2_3333_{ring}_labels'
    data = dict(scope='All256 embedded shape assignments, weights(3,3,3,3), full residue support.',
                model=model, fractional_lp_witness=witness,
                expected_integer_feasible_assignments=64 if ring == 'z4' else 0,
                explanation='The same fractional local-marginal witness works for both rings; their exact integer feasibility differs.')
    (output / (name + '.json')).write_text(json.dumps(data, separators=(',', ':')) + '\n')
    manifest.append(name)
(HERE / 'DEMO_MANIFEST.json').write_text(json.dumps({'examples': manifest}, indent=2) + '\n')
print(json.dumps({'examples': len(manifest), 'directory': str(output)}))
