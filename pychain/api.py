import flask
from . import blockchain, pubsub
import argparse
import random
import requests
from threading import Thread, Lock
import logging

BLOCKCHAIN = blockchain.BlockChain.new()
LOCK = Lock()

logger = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.route("/blockchain")
def _blockchain():
    with LOCK:
        return BLOCKCHAIN.to_jsonable()


@app.route("/blockchain/mine")
def _blockchain_mine():
    with LOCK:
        lastblock = BLOCKCHAIN.get_last_block()
    newblock = blockchain.mine_block(lastblock, "me (todo)")
    pubsub.publish_block(newblock)
    return newblock.to_jsonable()


def process_subs():
    while True:
        block = pubsub.pull_block()
        logger.info("adding block")
        print("block", type(block), block)
        BLOCKCHAIN.add_block(block)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--peer", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.peer:
        resp = requests.get("http://localhost:3000/blockchain")
        new_chain = resp.json()
        port = random.randint(2000, 2999)
        BLOCKCHAIN.replace_chain(new_chain)
    else:
        port = 3000
    thread = Thread(target=process_subs)
    thread.start()
    app.run(port=port)


if __name__ == "__main__":
    main()