from dataclasses import dataclass, asdict
from . import util
from .accounts import PublicAccountInfo
from .types import HexStr
from typing import Dict
from copy import deepcopy


@dataclass
class State:
    account_map: Dict[HexStr, PublicAccountInfo]
    # ^^^ use a tree for efficiency
    root_hash: HexStr

    @classmethod
    def new(cls):
        out = cls({}, None)
        out._update_root_hash()  # pylint: disable=protected-access
        return out

    def get_root_hash(self) -> HexStr:
        return self.root_hash

    def _update_root_hash(self):
        # if we used a tree, we wouldn't have to look at the whole
        # thing to recompute the hash
        self.root_hash = util.hash_jsonable(
            {k: v.to_jsonable() for (k, v) in self.account_map.items()}
        )

    def put(self, pai: PublicAccountInfo):
        self.account_map[pai.public_key] = pai
        self._update_root_hash()

    def get(self, public_key: HexStr) -> PublicAccountInfo:
        return deepcopy(self.account_map[public_key])

    def to_jsonable(self):
        return asdict(self)