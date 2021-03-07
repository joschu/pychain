from dataclasses import dataclass, asdict
from typing import List, Dict
import time
import random
import dacite
from .types import HexStr
from . import util, config
from .transactions import Transaction, TxTypes
from .state import State
from .accounts import PublicAccountInfo


@dataclass
class BlockHeader:
    parent_hash: HexStr  # Hash of prev block
    beneficiary: str  # Who mined it
    difficulty: float  # random block is valid with probability 1/difficulty
    number: int  # index in chain, starting at 0
    timestamp: float  # seconds since unix epoch time
    nonce: int  # dummy field used to change hash
    transactions_hash: HexStr  # Hash of new transactions
    state_hash: HexStr  # Hash of previous state

    def to_jsonable(self) -> dict:
        return asdict(self)


@dataclass
class Block:
    header: BlockHeader
    transactions: List[Transaction]

    def hash(self) -> HexStr:
        return util.hash_jsonable(self.to_jsonable())

    def to_jsonable(self) -> Dict:
        return asdict(self)


@dataclass
class BlockChain:
    chain: List[Block]
    state: State

    @classmethod
    def new(cls):
        return cls(chain=[genesis()], state=State.new())

    def to_jsonable(self) -> Dict:
        return asdict(self)

    def add_block(self, block) -> bool:
        valid = validate_block(self.chain[-1], self.state, block)
        if valid:
            self.chain.append(block)
            run_block(self.state, block)
        return valid

    def replace_chain(self, chain) -> bool:
        state = State()
        all_valid = True
        for i in range(len(chain) - 1):
            all_valid = all_valid and validate_block(chain[i], state, chain[i + 1])
            if not all_valid:
                break
        return all_valid

    def get_last_block(self) -> Block:
        return self.chain[-1]


def mine_block(
    last_block: Block,
    beneficiary: str,
    transactions: List[Transaction],
    state_hash: HexStr,
) -> Block:
    """
    find a new valid block
    """
    timestamp = time.time()
    header = BlockHeader(
        parent_hash=last_block.hash(),
        beneficiary=beneficiary,
        difficulty=adjust_difficulty(last_block, timestamp),
        number=last_block.header.number + 1,
        timestamp=timestamp,
        nonce=0,
        transactions_hash=util.hash_jsonable([tx.to_jsonable() for tx in transactions]),
        state_hash=state_hash,
    )
    newblock = Block(header=header, transactions=transactions)
    target = calculate_target_hash(last_block)
    while True:
        header.nonce = random.randint(0, config.MAX_NONCE_VALUE)
        if int_from_hexstr(newblock.hash()) < target:
            return newblock


def adjust_difficulty(last_block: Block, timestamp: float) -> float:
    time_elapsed = timestamp - last_block.header.timestamp
    if time_elapsed > config.MINE_RATE:
        scale = 0.7
    else:
        scale = 1.3
    return scale * last_block.header.difficulty


def calculate_target_hash(last_block: Block) -> int:
    return config.MAX_HASH_VALUE // last_block.header.difficulty


def validate_block(last_block: Block, state: State, block: Block) -> bool:
    return block.header.parent_hash == last_block.hash()


def run_block(state: State, block: Block):
    for transaction in block.transactions:
        if transaction.ut.txtype == TxTypes.CREATE_ACCOUNT:
            state.put(
                PublicAccountInfo(transaction.ut.pk_recipient, config.STARTING_BALANCE)
            )
        elif transaction.ut.txtype == TxTypes.TRANSACT:
            from_acct = state.get(transaction.ut.pk_sender)
            from_acct.balance += transaction.ut.value
            state.put(from_acct)
            to_acct = state.get(transaction.ut.pk_recipient)
            to_acct.balance -= transaction.ut.value
            state.put(to_acct)
        elif transaction.ut.txtype == TxTypes.REWARD_MINER:
            to_acct = state.get(transaction.ut.pk_recipient)
            to_acct.balance += config.MINING_REWARD
            state.put(to_acct)
        else:
            assert 0, f"invalid txtype {transaction.ut.txtype}"


# TODO Handle invalid block


def genesis() -> Block:
    return dacite.from_dict(Block, config.GENESIS_DATA)


def int_from_hexstr(s: HexStr) -> int:
    return int(s, 16)


def hexstr_from_int(i: int) -> HexStr:
    return hex(i)[2:]  # get rid of 0x
