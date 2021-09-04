# Requires python-requests. Install with pip:
#
#   pip install requests


import json, hmac, hashlib, time, requests
from requests.auth import AuthBase

# Before implementation, set environmental variables with the names API_KEY and API_SECRET
API_KEY = ''
API_SECRET = ''

# Create custom authentication for Coinbase API
class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))

        # https://stackoverflow.com/questions/66619124/coinbase-api-standard-python-example-returns-invalid-signature
        try:
            body = request.body.decode()
            if body == "{}":
                request.body = b""
                body = ''
        except AttributeError:
            request.body = b""
            body = ''

        message = timestamp + request.method + request.path_url + body
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })

        print(f"request.path_url: {request.path_url}")
        print(f"request.method: {request.method}")
        print(f"request.headers: {request.headers}")
        print()
        return request

api_url = 'https://api.coinbase.com'
auth = CoinbaseWalletAuth(API_KEY, API_SECRET)

# Get current user
# uri = '/v2/user'
# r = requests.get(api_url + uri, auth=auth)
# print(r.json())

# List accounts
print()
accounts = {}
uri = '/v2/accounts?limit=100'
while True:
    response = requests.get(api_url + uri, auth=auth).json()

    for account in response['data']:
        accounts[account['name']] = account
    uri = response['pagination']['next_uri']
    if not uri:
        break
# print(f"Accounts dict: {json.dumps(accounts, indent=4, sort_keys=True, default=str)}")
# print(sorted(accounts.keys()))
# for x in accounts.values():
#     if x.get('id') and x.get('currency') == 'USD':
#         print(x['name'])

# USD
wallet_name = 'USD Wallet'
# BTC
# wallet_name = 'My Wallet'
# ETH
# wallet_name = 'ETH Wallet'

# list deposits
print()
print("DEPOSITS ----")
print(f"Account: {accounts[wallet_name]}")
uri = f"/v2/accounts/{accounts[wallet_name]['id']}/deposits"
response = requests.get(api_url + uri, auth=auth).json()
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
deposits = []
for deposit in response['data']:
    deposits.append({
        'id': deposit['id'],
        'amount': deposit['amount']['amount'],
        'currency': deposit['amount']['currency'],
        'created_at': deposit['created_at'],
    })
deposits = sorted(deposits, key=lambda k: k['created_at']) 
print(json.dumps(deposits, indent=4, sort_keys=True, default=str))

# list withdrawls
print()
print("WITHDRAWALS ----")
print(f"Account: {accounts[wallet_name]}")
uri = f"/v2/accounts/{accounts[wallet_name]['id']}/withdrawals"
response = requests.get(api_url + uri, auth=auth).json()
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
withdrawals = []
for withdrawal in response['data']:
    withdrawals.append({
        'id': withdrawal['id'],
        'amount': withdrawal['amount']['amount'],
        'currency': withdrawal['amount']['currency'],
        'created_at': withdrawal['created_at'],
    })
withdrawals = sorted(withdrawals, key=lambda k: k['created_at']) 
print(json.dumps(withdrawals, indent=4, sort_keys=True, default=str))

# list transactions
print()
print("TRANSACTIONS ----")
print(f"Account: {accounts[wallet_name]}")
uri = f"/v2/accounts/{accounts[wallet_name]['id']}/transactions"
response = requests.get(api_url + uri, auth=auth).json()
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
txs = []
for tx in response['data']:
    txs.append(tx)
txs = filter(lambda t: t.get('type') not in ['buy', 'sell', 'pro_deposit', 'pro_withdrawal'], txs)
txs = sorted(txs, key=lambda k: k['created_at']) 
print(json.dumps(txs, indent=4, sort_keys=True, default=str))