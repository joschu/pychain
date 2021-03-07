import hashlib
import json
from .types import HexStr
from typing import Union, Dict, List


def hash_bytes(data: bytes) -> HexStr:
    assert isinstance(data, bytes)
    return hashlib.sha256(data).hexdigest()


def hash_jsonable(data: Union[Dict, List]) -> HexStr:
    s = json.dumps(data, sort_keys=True)
    return hash_bytes(s.encode())
