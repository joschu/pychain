import flask
from . import blockchains, transactions
from .pubsub import PubSub, MsgTypes
from .accounts import Account
from .transactions import TxTypes
from .transaction_manager import TransactionManager
import argparse
import random
import requests
from threading import Thread, Lock
import logging
import dacite
import signal

LOCK = Lock()  # For accessing/modifying global objects BLOCKCHAIN and TX_MANAGER
BLOCKCHAIN = blockchains.BlockChain.new()
TX_MANAGER = TransactionManager()

PUBSUB = PubSub()

MINER_ACCOUNT = Account.new()

logger = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.route("/blockchain")
def _blockchain():
    with LOCK:
        return BLOCKCHAIN.to_jsonable()


@app.route("/miner/address")
def _miner_address():
    return MINER_ACCOUNT.public_key


@app.route("/miner/mine", methods=["POST"])
def _miner_mine():
    with LOCK:
        last_block = BLOCKCHAIN.get_last_block()
    tx_list = TX_MANAGER.get_all()
    tx_list.append(transactions.make_reward_miner(MINER_ACCOUNT))
    newblock = blockchains.mine_block(
        last_block=last_block,
        beneficiary=MINER_ACCOUNT.public_key,
        transactions=tx_list,
        state_hash=BLOCKCHAIN.state.root_hash,
    )
    PUBSUB.publish_block(newblock)
    return newblock.to_jsonable()


@app.route("/transact", methods=["POST"])
def _transact():
    transaction = dacite.from_dict(transactions.Transaction, flask.request.json)
    if transaction.ut.txtype == TxTypes.CREATE_ACCOUNT:
        accepted = True
    elif transaction.ut.txtype == TxTypes.TRANSACT:
        accepted = transaction.check_signature()
    else:
        assert 0, f"Invalid transaction type {transaction.ut.txtype}"
    if accepted:
        PUBSUB.publish_transaction(transaction)
    return {"accepted": accepted}


def process_subs():
    while True:
        msg_type, obj = PUBSUB.pull_message()
        if msg_type == MsgTypes.BLOCK:
            assert isinstance(obj, blockchains.Block)
            logger.info("adding block")
            with LOCK:
                BLOCKCHAIN.add_block(obj)
                TX_MANAGER.remove_transactions(obj.transactions)
        elif msg_type == MsgTypes.TRANSACTION:
            assert isinstance(obj, transactions.Transaction)
            logger.info("adding transaction")
            with LOCK:
                TX_MANAGER.add(obj)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--peer", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.peer:
        resp = requests.get("http://localhost:3000/blockchain")
        new_chain = resp.json()
        BLOCKCHAIN.replace_chain(new_chain)
        port = random.randint(2000, 2999)
    else:
        port = 3000
    thread = Thread(target=process_subs)  # Process subscriptions in background
    thread.start()
    # https://stackoverflow.com/questions/17174001/stop-pyzmq-receiver-by-keyboardinterrupt
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.run(port=port, threaded=False)


if __name__ == "__main__":
    main()