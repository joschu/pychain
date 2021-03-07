from . import transactions, accounts


def test_transactions():
    account = accounts.Account.new()
    transaction = transactions.make_send(account, pk_recipient="abcd", value=50)
    assert transaction.check_signature()
