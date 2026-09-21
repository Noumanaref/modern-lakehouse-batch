import json
import hashlib

def canonical_hash(payload: dict, exclude_keys:set)-> str:
    cleaned = {k:v for k,v in payload.items() if k not in exclude_keys}
    canonical = json.dumps(cleaned, sort_keys=True, separators=(',',':'))
    return hashlib.sha256(canonical.encode()).hexdigest()
