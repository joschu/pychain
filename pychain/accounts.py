from dataclasses import dataclass, asdict
from typing import Any, Dict
from py_ecc.bls import G2ProofOfPossession as bls_pop
import random
from . import util
from .types import HexStr

# pylint:disable=no-member
STARTING_BALANCE = 1000


@dataclass
class KeyPair:
    private: int
    public: HexStr

    @classmethod
    def new(cls):
        private = random.randint(0, 2 ** 64)
        public = bls_pop.SkToPk(private).hex()
        return cls(private, public)


@dataclass
class PublicAccountInfo:
    public_key: HexStr
    balance: float

    def to_jsonable(self):
        return asdict(self)


@dataclass
class Account:
    key_pair: KeyPair
    balance: float

    @property
    def public_key(self) -> HexStr:
        return self.key_pair.public

    @classmethod
    def new(cls):
        return Account(key_pair=KeyPair.new(), balance=STARTING_BALANCE)

    def sign(self, data: str) -> HexStr:
        return bls_pop.Sign(SK=self.key_pair.private, message=data.encode()).hex()

    def to_jsonable(self) -> Dict:
        return dict(address=self.address, balance=self.balance)

    def public_info(self) -> PublicAccountInfo:
        return PublicAccountInfo(self.public_key, self.balance)


def verify_signature(public_key: HexStr, data: str, signature: HexStr) -> bool:
    return bls_pop.Verify(
        PK=bytes.fromhex(public_key),
        message=data.encode(),
        signature=bytes.fromhex(signature),
    )
