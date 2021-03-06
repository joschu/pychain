import zmq
from . import blockchain
from typing import List
import logging

logger = logging.getLogger(__name__)

BLOCKS_URI = "ipc:///tmp/blocks"
CONTEXT = zmq.Context()
PUB_SOCKET = CONTEXT.socket(zmq.PUB)
PUB_SOCKET.bind(BLOCKS_URI)
SUB_SOCKET = CONTEXT.socket(zmq.SUB)
SUB_SOCKET.connect(BLOCKS_URI)
SUB_SOCKET.setsockopt(zmq.SUBSCRIBE, b"")


def publish_block(block: blockchain.Block):
    PUB_SOCKET.send_json(block.to_jsonable())


def pull_block() -> blockchain.Block:
    retval = SUB_SOCKET.recv_json()
    return blockchain.Block.from_jsonable(retval)
