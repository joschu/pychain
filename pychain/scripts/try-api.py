import requests
from pychain import transactions, accounts
from pprint import pprint

base_url = "http://localhost:3000"

new_account = accounts.Account.new()
miner_address = requests.get(url=base_url + "/miner/address").text
requests.post(
    url=base_url + "/transact",
    json=transactions.make_create_account(miner_address).to_jsonable(),
)
requests.post(
    url=base_url + "/transact",
    json=transactions.make_create_account(new_account.public_key).to_jsonable(),
)
requests.post(
    url=base_url + "/transact",
    json=transactions.make_send(new_account, 100, new_account.public_key).to_jsonable(),
)
requests.post(url=base_url + "/miner/mine")
pprint(requests.get(url=base_url + "/blockchain").json()["state"])
