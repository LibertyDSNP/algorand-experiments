import base64
from algosdk import mnemonic
from algosdk.future import transaction

# helper function to compile program source
def compile_smart_signature(client, source_code):
    compile_response = client.compile(source_code)
    return compile_response['result'], compile_response['hash']


# Accounts can only opt into up to 50 smart contracts. Accounts may only create 10 smart contracts.
# This creates a Logic Signature transaction using the provided logic 'registry_smart_sig_program'
def lsig_payment_txn(smart_sig_program, smart_sig_addr, amt, receiver_addr, algod_client):
    params = algod_client.suggested_params()
    upayment_txn = transaction.PaymentTxn(smart_sig_addr, params, receiver_addr, amt)
    encoded_prog = smart_sig_program.encode()
    program = base64.decodebytes(encoded_prog)
    lsig = transaction.LogicSig(program)
    slsig_txn = transaction.LogicSigTransaction(upayment_txn, lsig)
    if slsig_txn.verify(): print("verified logic signature transaction")
    tx_id = algod_client.send_transaction(slsig_txn)
    pmtx = wait_for_confirmation(algod_client, tx_id, 10)
    return pmtx

def payment_transaction(creator_mnemonic, amt, rcv, algod_client)->dict:
    params = algod_client.suggested_params()
    senderAddr = mnemonic.to_public_key(creator_mnemonic)
    senderPrivKey = mnemonic.to_private_key(creator_mnemonic)
    utxn = transaction.PaymentTxn(senderAddr, params, rcv, amt)
    stxn = utxn.sign(senderPrivKey)
    txid = algod_client.send_transaction(stxn)
    pmtx = wait_for_confirmation(algod_client, txid , 5)
    return pmtx


def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))