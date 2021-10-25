import base64

import algosdk.logic
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *
from helpers import *
from dsnp_contract_helpers import *

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# this is the registration contract
# TODO: it should generate a new DSNPId and update its global state to the new id.
# TODO: it should also be able to insert a new handle into a caller's local state
# global state:
#    d:  latest DSNPId, int
#    h:  last handler called, bytes:
#           c = create
#           n = no-op
#           o = optin
#           l = closeout
#           u = update
#           d = delete
def approval_program_teal(owner_addr):
    handle_creation = Seq([
        App.globalPut(Bytes("d"), Int(999)),
        App.globalPut(Bytes("h"),Bytes("c")),
        Return(Int(1))
    ])

    scratchCount = ScratchVar(TealType.uint64)

    #
    handle_optin = Seq([
        scratchCount.store(App.globalGet(Bytes("d"))),
        App.globalPut(Bytes("d"), scratchCount.load() + Int(1)),
        App.globalPut(Bytes("h"), Bytes("o")),
        App.localPut(Txn.sender(), Bytes("d"), App.globalGet(Bytes("d"))),
        Return(Int(1))
    ])

    handle_noop = Return(Int(1))

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
    #     [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
    #     [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
    #     [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )
    return compileTeal(program, Mode.Application, version=5)

def clear_program_teal():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

# only one txn allowed, no groups
# can be an application call or a payment
# must be to the opted in contract
# must pay a fee of 1 algo
def registry_smart_sig_teal(signer_addr, registry_contract_addr):
    fee = Int(1)

    ok = Return(Int(1))
    # Q: how do I tell if I'm already activated?
    # A: one way is an opt-in txn will fail

    handle_payment = If(Or(
        Txn.sender() == Addr(registry_contract_addr),
        Txn.sender() == Addr(signer_addr)
    )).Then(Return(Int(1))).Else(Return(Int(0)))

    program = Seq([
        Cond(
            [Txn.type_enum() == TxnType.ApplicationCall, ok],
            [Txn.type_enum() == TxnType.Payment, handle_payment]
            ),
        And(
            Global.group_size() == Int(1),
            Txn.amount() == fee,
        )
    ])
    # Mode.Signature indicates that this is a smart signature and not a smart contract.
    return compileTeal(program, Mode.Signature, version=5)


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # reg_owner will be the owner of the registration contract.
    reg_owner_addr, reg_owner_privKey, reg_owner_mnemonic = get_funded_account(0)

    mainRegistrationContract_appID = 0
    try:
        app_info = algod_client.application_info(mainRegistrationContract_appID)
        print(f"App app info: {app_info}")
    except algosdk.error.AlgodHTTPError:
        _, approval_program = compile_program_to_bytes(algod_client, approval_program_teal(reg_owner_addr))
        _, clear_program = compile_program_to_bytes(algod_client, clear_program_teal())
        registry_global_schema = transaction.StateSchema(1, 1)  # DSNPid current, last called handler
        registry_local_schema = transaction.StateSchema(1, 1)  # DSNPid, handles registered

        before_bal = get_account_balance(algod_client, reg_owner_addr)

        mainRegistrationContract_appID = create_app(
            algod_client,
            reg_owner_privKey,
            approval_program,
            clear_program,
            registry_global_schema,
            registry_local_schema)
        after_bal = get_account_balance(algod_client, reg_owner_addr)
        print("mainRegistrationContract created:")
        print("\tappID: ", mainRegistrationContract_appID)
        print("\towner: ", reg_owner_addr)
        print("\tcost: ", before_bal-after_bal)

    user_addr, user_privKey, user_mnemonic = get_funded_account(1)
    stateless_program_teal = registry_smart_sig_teal(user_addr, reg_owner_addr)

    smartsig_program, stateless_reg_contract_addr = compile_program(algod_client, stateless_program_teal)
    print("smart signature program:", smartsig_program)
    print("smart signature hash: ", stateless_reg_contract_addr)

    # if smart sig balance is below min for this particular
    # contract (278500), the txn will fail
    min_balance = 280000
    lsig = activate_and_sign_smart_sig(algod_client, min_balance, user_privKey, stateless_reg_contract_addr, smartsig_program)

    # Set up and fund a new user
    user2_privkey, user2_addr = generate_algorand_keypair()
    pay_and_wait(algod_client, reg_owner_privKey, min_balance+1000000, user2_addr)

    stateless_program_teal2 = registry_smart_sig_teal(user2_addr, reg_owner_addr)

    if (stateless_program_teal == stateless_program_teal2):
        raise "the two programs are identical"

    smartsig_program2, stateless_reg_contract_addr2 = compile_program(algod_client, stateless_program_teal2)
    print("smart signature program:", smartsig_program2)
    print("smart signature hash: ", stateless_reg_contract_addr2)

    lsig2 = activate_and_sign_smart_sig(algod_client, min_balance, user2_privkey, stateless_reg_contract_addr2, smartsig_program2)

    # send an opt-in transaction to the contract, signed by smart signature contract owner

    optin_txn = optin_transaction(algod_client, stateless_reg_contract_addr, lsig, mainRegistrationContract_appID)
    print(f"User addr {user_addr} opted into appID {mainRegistrationContract_appID} via smartsig #{lsig}")

    optin_txn2 = optin_transaction(algod_client, stateless_reg_contract_addr2, lsig2, mainRegistrationContract_appID)
    print(f"User addr {user2_addr} opted into appID {mainRegistrationContract_appID} via smartsig #{lsig}")

main()