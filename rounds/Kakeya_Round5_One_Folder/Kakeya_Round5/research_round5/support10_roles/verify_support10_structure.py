"""Replay just the complete support classification needed by the hand proof."""
from pathlib import Path
from hashlib import sha256
import json
import sys
from verify_support10_roles import enumerate_supports


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled.')
    count = enumerate_supports()
    here = Path(__file__).resolve().parent
    result = {
        'status': 'PASS_STANDALONE_SUPPORT10_CLASSIFICATION',
        'normalized_candidates': 14950,
        'difference_covers': count,
        'affine_types': 1,
        'canonical_form': '(V minus0) union (W minus0), dimV3, dimW2, V direct-sum W=F2^5.',
        'earlier_weight_profile_input_used': False,
        'verified_properties': ['Unique-edge graph K3 joined to independent7-set.',
            'Unique deleted origin gives complementary subspaces.',
            'Every vertex has a sum-free set of incident unique directions.'],
        'finite_checker_sha256': sha256((here/'verify_support10_roles.py').read_bytes()).hexdigest(),
        'scope': 'Complete normalized finite support classification; analytic affine-normalization argument proves coverage of all supports.'
    }
    (here/'SUPPORT10_STRUCTURE_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
