import base64

from algosdk.future import transaction
from algosdk import mnemonic
from algosdk.v2client import algod
from pyteal import *
from helpers import compile_smart_signature, \
    lsig_payment_txn, \
    payment_transaction, \
    wait_for_confirmation

# user declared account mnemonics
#benefactor_mnemonic = "REPLACE WITH YOUR OWN MNEMONIC"
#sender_mnemonic = "REPLACE WITH YOUR OWN MNEMONIC"

benefactor_mnemonic = "science opera whip diesel begin frown able forest inflict load goat matrix tent judge hole floor february similar day drip ugly very resource ability hen"
sender_mnemonic = "type own seat six margin crisp ivory alpha cross staff uphold wine dish code shoe whale cinnamon bullet vintage lucky ten stool maze absorb surround"

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config

"""Basic Donation Escrow"""

def donation_escrow(benefactor):
    Fee = Int(1000)

    #Only the benefactor account can withdraw from this escrow
    # This is what will run when a transaction is submitted against it?
    program = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= Fee,
        Txn.receiver() == Addr(benefactor),
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
    )

    # Mode.Signature specifies that this is a smart signature
    return compileTeal(program, Mode.Signature, version=5)

def main() :
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    receiver_public_key = mnemonic.to_public_key(benefactor_mnemonic)

    print("--------------------------------------------")
    print("Compiling Donation Smart Signature......")

    stateless_program_teal = donation_escrow(receiver_public_key)
    escrow_result, escrow_address= compile_smart_signature(algod_client, stateless_program_teal)

    print("Program:", escrow_result)
    print("hash: ", escrow_address)

    print("--------------------------------------------")
    print("Activating Donation Smart Signature......")

    # Activate escrow contract by sending 2 algo and 1000 microalgo for transaction fee from creator
    amt = 2001000
    payment_transaction(sender_mnemonic, amt, escrow_address, algod_client)

    print("--------------------------------------------")
    print("Withdraw from Donation Smart Signature......")

    # Withdraws 1 ALGO from smart signature using logic signature.
    withdrawal_amt = 1000000
    lsig_payment_txn(escrow_result, escrow_address, withdrawal_amt, receiver_public_key, algod_client)

main()