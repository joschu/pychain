GENESIS_DATA = {
    "header": {
        "parent_hash": "--genesis-parent-hash--",
        "beneficiary": "--genesis-beneficiary--",
        "difficulty": 100.0,
        "number": 0,
        "timestamp": 0.0,
        "nonce": 0,
        "transactions_hash": "--genesis-transactions-root-",
        "state_hash": "--genesis-state-root--",
    },
    "transactions": [],
}

MINE_RATE = 1.0
STARTING_BALANCE = 0.0
MINING_REWARD = 50.0

HASH_LENGTH_HEX = 64  # this long in hex
MAX_HASH_VALUE = 2 ** (HASH_LENGTH_HEX * 4)
MAX_NONCE_VALUE = 2 ** 64  # Just needs to be more blocks than anyone's ever gonna try
