from dataclasses import dataclass, asdict
from typing import List
import json
import hashlib
import math
import time
import random
import dacite

HASH_LENGTH_HEX = 64  # this long in hex
MAX_HASH_VALUE = 2 ** (HASH_LENGTH_HEX * 4)
MAX_NONCE_VALUE = 2 ** 64  # Just needs to be more blocks than anyone's ever gonna try

HexStr = str

MINE_RATE = 1.0


@dataclass
class BlockHeader:
    parent_hash: HexStr  # Hash of prev block
    beneficiary: str  # Who mined it
    difficulty: float  # random block is valid with probability 1/difficulty
    number: int  # index in chain, starting at 0
    timestamp: float  # seconds since unix epoch time
    nonce: int  # dummy field used to change hash

    def to_str(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


@dataclass
class Block:
    header: BlockHeader

    def hash(self) -> HexStr:
        h = hashlib.sha256()
        h.update(self.header.to_str().encode())
        return h.hexdigest()

    def to_jsonable(self):
        return asdict(self)

    @classmethod
    def from_jsonable(cls, d: dict):
        return dacite.from_dict(cls, d)


@dataclass
class BlockChain:
    chain: List[Block]

    @classmethod
    def new(cls):
        return cls(chain=[genesis()])

    def to_jsonable(self):
        return asdict(self)

    def add_block(self, block) -> bool:
        valid = validate_block(self.chain[-1], block)
        if valid:
            self.chain.append(block)
        return valid

    def replace_chain(self, chain) -> bool:
        all_valid = all(
            validate_block(chain[i], chain[i + 1]) for i in range(len(chain) - 1)
        )
        if all_valid:
            self.chain = chain
        return all_valid

    def get_last_block(self):
        return self.chain[-1]


def mine_block(last_block: Block, beneficiary: str) -> Block:
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
    )
    newblock = Block(header=header)
    target = calculate_target_hash(last_block)
    while True:
        header.nonce = random.randint(0, MAX_NONCE_VALUE)
        if int_from_hexstr(newblock.hash()) < target:
            return newblock


def adjust_difficulty(last_block: Block, timestamp: float) -> float:
    time_elapsed = timestamp - last_block.header.timestamp
    if time_elapsed > MINE_RATE:
        scale = 0.7
    else:
        scale = 1.3
    return scale * last_block.header.difficulty


def calculate_target_hash(last_block: Block) -> int:
    return MAX_HASH_VALUE // last_block.header.difficulty


def validate_block(last_block: Block, block: Block) -> bool:
    return block.header.parent_hash == last_block.hash()


def genesis():
    return Block(
        header=BlockHeader(
            parent_hash="--genesis-parent-hash--",
            beneficiary="--genesis-beneficiary--",
            difficulty=100.0,
            number=0,
            timestamp=0,
            nonce=0,
        )
    )


def int_from_hexstr(s: HexStr):
    return int(s, 16)


def hexstr_from_int(i: int):
    return hex(i)[2:]  # get rid of 0x
