from dataclasses import dataclass, asdict
from uuid import uuid4
from . import util, accounts, config
from .types import HexStr
from typing import Optional, Dict
from copy import deepcopy


class TxTypes:
    TRANSACT = "TRANSACT"
    CREATE_ACCOUNT = "CREATE_ACCOUNT"
    REWARD_MINER = "REWARD_MINER"


@dataclass
class UnsignedTransaction:
    pk_sender: HexStr
    pk_recipient: HexStr
    value: float
    txtype: str
    uuid: str

    def to_jsonable(self):
        return asdict(self)

    def hash(self) -> HexStr:
        return util.hash_jsonable(self.to_jsonable())


@dataclass
class Transaction:
    ut: UnsignedTransaction
    signature: HexStr

    def check_signature(self) -> bool:
        return accounts.verify_signature(
            public_key=self.ut.pk_sender, data=self.ut.hash(), signature=self.signature
        )

    def to_jsonable(self):
        return asdict(self)


def make_send(
    account: accounts.Account, value: float, pk_recipient: str
) -> Transaction:
    ut = UnsignedTransaction(
        pk_sender=account.public_key,
        pk_recipient=pk_recipient,
        value=value,
        txtype=TxTypes.TRANSACT,
        uuid=str(uuid4()),
    )
    return Transaction(ut=ut, signature=account.sign(ut.hash()))


def make_create_account(pk: HexStr) -> Transaction:
    return Transaction(
        ut=UnsignedTransaction(
            pk_sender="",
            pk_recipient=pk,
            value=0.0,
            txtype=TxTypes.CREATE_ACCOUNT,
            uuid=str(uuid4()),
        ),
        signature="",
    )


def make_reward_miner(account: accounts.Account) -> Transaction:
    return Transaction(
        ut=UnsignedTransaction(
            pk_sender="",
            pk_recipient=account.public_key,
            value=config.MINING_REWARD,
            txtype=TxTypes.REWARD_MINER,
            uuid=str(uuid4()),
        ),
        signature="",
    )