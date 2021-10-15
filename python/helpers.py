import base64
from algosdk import account, mnemonic
from algosdk.future import transaction


def get_funded_account(index=0):
    # this mnemonic is for a consistently generated sandbox account with lots of algos.
    sender_mnemonic = "metal morning betray sand have banner drum kiss fossil orbit pipe salt once unique fire lady bubble ethics visit junior patrol wire fortune abstract bright"

    if (index >0):
        sender_mnemonic = "kid bread axis pizza crumble wool rural tomato punch caution side legend immense search enlist exotic faculty tag wage reduce march desk vicious abandon slice"

    sender_privKey = mnemonic.to_private_key(sender_mnemonic)
    sender_addr = mnemonic.to_public_key(sender_mnemonic)
    return sender_addr,sender_privKey,sender_mnemonic

# helper function to generate a keypair
def generate_algorand_keypair():
    private_key, address = account.generate_account()
    return private_key, address

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return compile_response['result'], compile_response['hash']

# returns the contract address + the contract code as bytes for using in a
# ApplicationCreate transaction.
def compile_program_to_bytes(client, source_code) :
    compile_response = client.compile(source_code)
    return compile_response['hash'], base64.b64decode(compile_response['result'])

# create new application
def create_app(algod_client, sender_priv, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(sender_priv)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = algod_client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, \
                                            approval_program, clear_program, \
                                            global_schema, local_schema)
    # sign transaction
    signed_txn = txn.sign(sender_priv)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    algod_client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(algod_client, tx_id, 5)

    # display results
    transaction_response = algod_client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id:", app_id)

    return app_id

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