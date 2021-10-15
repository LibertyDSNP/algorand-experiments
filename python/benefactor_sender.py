from algosdk import mnemonic
from algosdk.v2client import algod
from pyteal import *
from helpers import compile_program, \
    get_funded_account, \
    lsig_payment_txn, \
    payment_transaction, \
    wait_for_confirmation

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config

"""Basic Donation Escrow"""

def donation_escrow_teal(benefactor_addr):
    Fee = Int(1000)

    #Only the benefactor account can withdraw from this escrow
    # This is what will run when a transaction is submitted against it?
    program = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= Fee,
        Txn.receiver() == Addr(benefactor_addr),
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
    )

    # Mode.Signature specifies that this is a smart signature
    return compileTeal(program, Mode.Signature, version=5)

def main() :
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # these are preset accounts in the local sandbox.
    sender_addr, sender_privkey, sender_mnemonic = get_funded_account(0)
    benefactor_addr, _, _ = get_funded_account(1)

    print("--------------------------------------------")
    print("Compiling Donation Smart Signature......")

    stateless_program_teal = donation_escrow_teal(benefactor_addr)
    escrow_result, escrow_address = compile_program(algod_client, stateless_program_teal)

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
    lsig_payment_txn(escrow_result, escrow_address, withdrawal_amt, benefactor_addr, algod_client)


main()
