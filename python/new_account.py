import json
import base64
from algosdk.v2client import algod
from algosdk import mnemonic

from algosdk.future.transaction import PaymentTxn
from helpers import \
    generate_algorand_keypair, \
    get_funded_account, \
    wait_for_confirmation

# Write down the address, private key, and the passphrase for later usage

def first_transaction_example(send_priv, send_addr, rcv_addr):
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    print("My address: {}".format(send_addr))
    account_info = algod_client.account_info(send_addr)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    # build transaction
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000
    note = "Hello World".encode()

    unsigned_txn = PaymentTxn(send_addr, params, rcv_addr, 1000000, None, note)

    # sign transaction
    signed_txn = unsigned_txn.sign(send_priv)

    # submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))

    account_info = algod_client.account_info(send_addr)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

sender_addr,sender_privKey,sender_mnemonic = get_funded_account()
recipient_privKey, recipentAddr = generate_algorand_keypair()
print("My address: {}".format(recipentAddr))
print("My private key: {}".format(recipient_privKey))
print("My passphrase: {}".format(mnemonic.from_private_key(recipient_privKey)))

first_transaction_example(sender_privKey, sender_addr, recipentAddr)

