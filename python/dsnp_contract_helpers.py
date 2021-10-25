import base64
from algosdk.future import transaction
from pyteal import *
from helpers import pay_and_wait, wait_for_confirmation


# Activate smartsig contract by sending
# 100k microalgo minimum balance +
# 10k microalgo transaction fee +
# + 168,999 for . . . ? the program size?
# 1 microalgo for transaction fee from creator
# if smart sig balance is below min  the txn will fail
def activate_and_sign_smart_sig(algod_client, amt, signer_privkey, smartsig_addr, smartsig_program, ):
    #  the DSNP user will activate the smart signature and use it to opt in to the
    # main registration contract by sending it the minimum required balance.
    pay_and_wait(algod_client, signer_privkey, amt, smartsig_addr)
    encoded_prog = smartsig_program.encode()
    decodedBytes = base64.decodebytes(encoded_prog)
    return transaction.LogicSig(decodedBytes)

def optin_transaction(algod_client, sender_addr, lsig, app_id) -> dict:
    params = algod_client.suggested_params()
    utxn = transaction.ApplicationOptInTxn(sender_addr, params, app_id)
    slsig_txn = transaction.LogicSigTransaction(utxn, lsig)
    txid = slsig_txn.transaction.get_txid()
    algod_client.send_transaction(slsig_txn)
    return wait_for_confirmation(algod_client, txid , 5)
