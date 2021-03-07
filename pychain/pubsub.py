import zmq
from .blockchains import Block
from .transactions import Transaction
from typing import Tuple, Union
import logging
import dacite

logger = logging.getLogger(__name__)


class MsgTypes:
    BLOCK = "BLOCK"
    TRANSACTION = "TRANSACTION"


class PubSub:
    uri = "ipc:///tmp/pychain"

    def __init__(self):
        self.context = zmq.Context()

        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(self.uri)

        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.uri)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

    def publish_block(self, block: Block):
        self.pub_socket.send_json(
            {"msg_type": MsgTypes.BLOCK, "msg_data": block.to_jsonable()}
        )

    def publish_transaction(self, transaction: Transaction):
        self.pub_socket.send_json(
            {"msg_type": MsgTypes.TRANSACTION, "msg_data": transaction.to_jsonable()}
        )

    def pull_message(self) -> Tuple[str, Union[Block, Transaction]]:
        msg = self.sub_socket.recv_json()
        msg_type = msg["msg_type"]
        if msg_type == MsgTypes.BLOCK:
            obj = dacite.from_dict(Block, msg["msg_data"])
        elif msg_type == MsgTypes.TRANSACTION:
            obj = dacite.from_dict(Transaction, msg["msg_data"])
        else:
            assert 0, f"Invalid message type: {msg_type}"
        return msg_type, obj
