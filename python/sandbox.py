import base64
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *
from helpers import \
    compile_program, \
    compile_program_to_bytes,\
    create_app, \
    decode_note, \
    get_account_balance, \
    get_funded_account, \
    pay_and_wait_with_note, \
    wait_for_confirmation

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def main():
    algod_client = algod.AlgodClient(algod_token, algod_address)

    reg_owner_addr, reg_owner_privKey, reg_owner_mnemonic = get_funded_account(0)
    balance = get_account_balance(algod_client, reg_owner_addr)
    user_addr, user_privKey, user_mnemonic = get_funded_account(1)
    amt = 1
    txn = pay_and_wait_with_note(algod_client, reg_owner_mnemonic, amt, user_addr, "WAT IS THIS")
    new_balance = get_account_balance(algod_client, reg_owner_addr)
    print(f"cost: {balance - new_balance}")

    print(f"Decoded note: {decode_note(txn)}")

main()