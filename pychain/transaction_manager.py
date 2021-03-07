from .transactions import Transaction
from typing import List


class TransactionManager:
    def __init__(self):
        self.transactions = {}

    def add(self, transaction: Transaction):
        self.transactions[transaction.ut.uuid] = transaction

    def get_all(self) -> List[Transaction]:
        return list(self.transactions.values())

    def remove_transactions(self, transactions: List[Transaction]):
        for tx in transactions:
            self.transactions.pop(tx.ut.uuid, None)
