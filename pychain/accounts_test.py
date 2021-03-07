from .accounts import Account, verify_signature
from .types import HexStr


def test_sign():
    account = Account.new()
    data = "hello"
    data2 = "hi"
    signature = account.sign(data)
    signature2 = account.sign(data2)
    assert verify_signature(account.key_pair.public, data, signature)
    assert not verify_signature(account.key_pair.public, data, signature2)
