import base64
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *
from helpers import \
    compile_program, \
    compile_program_to_bytes,\
    create_app, \
    get_funded_account, \
    payment_transaction, \
    wait_for_confirmation

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
def registry_smart_sig_teal():
    fee = Int(1)

    ok = Return(Int(1))
    opting_in = Return(Int(1))
    not_opting_in = Return(Int(0))

    handle_optin = If(OnComplete.OptIn == Txn.on_completion()).Then(opting_in).Else(not_opting_in)

    program = Seq([
        Cond(
            [Txn.type_enum() == TxnType.ApplicationCall, handle_optin],
            [Txn.type_enum() == TxnType.Payment, ok]
            ),
        And(
            Global.group_size() == Int(1),
            Txn.amount() == fee,
        )
    ])
    # Mode.Signature indicates that this is a smart signature and not a smart contract.
    return compileTeal(program, Mode.Signature, version=5)



def optin_transaction(sender_addr, lsig, app_id, algod_client) -> dict:
    params = algod_client.suggested_params()
    utxn = transaction.ApplicationOptInTxn(sender_addr, params, app_id)
    slsig_txn = transaction.LogicSigTransaction(utxn, lsig)
    txid = slsig_txn.transaction.get_txid()
    algod_client.send_transaction(slsig_txn)
    pmtx = wait_for_confirmation(algod_client, txid , 5)
    return pmtx

# min: 100,000 microalgos
def main():

    # reg_owner will be the owner of the registration contract.
    reg_owner_addr, reg_owner_privKey, reg_owner_mnemonic = get_funded_account(0)


    user_privKey, user_addr, user_mnemonic = get_funded_account(1)

    algod_client = algod.AlgodClient(algod_token, algod_address)
    application_owner_addr = reg_owner_addr
    registry_global_schema = transaction.StateSchema(1,1)  # DSNPid current, last called handler
    registry_local_schema = transaction.StateSchema(1, 1)  # DSNPid, handles registered
    _, approval_program = compile_program_to_bytes(algod_client, approval_program_teal(application_owner_addr))
    _, clear_program = compile_program_to_bytes(algod_client, clear_program_teal())

    mainRegistrationContract_appID = create_app(
        algod_client,
        reg_owner_privKey,
        approval_program,
        clear_program,
        registry_global_schema,
        registry_local_schema)

    print("mainRegistrationContract_appID", mainRegistrationContract_appID)

    stateless_program_teal = registry_smart_sig_teal()
    program, stateless_reg_contract_addr = compile_program(algod_client, stateless_program_teal)

    print("smart signature program:", program)
    print("smart signature hash: ", stateless_reg_contract_addr)
    print("--------------------------------------------")
    print("Activating Registration Smart Signature")

    # Activate contract by sending
    # 100k microalgo minimum balance +
    # 10k microalgo transaction fee +
    # + 168,999 for . . . ? the program size?
    # 1 microalgo for transaction fee from creator
    # Error:  balance 109001 below min 278500

    amt = 300000
    #  the DSNP user will activate the smart signature and use it to opt in to the
    # main registration contract
    payment_transaction(user_mnemonic, amt, stateless_reg_contract_addr, algod_client)
    print("--------------------------------------------")
    print("Call Smart Signature to opt in")
    encoded_prog = program.encode()
    decodedBytes = base64.decodebytes(encoded_prog)
    lsig = transaction.LogicSig(decodedBytes)

    # send an opt-in transaction to the contract, signed by smart signature contract owner
    txn = optin_transaction(stateless_reg_contract_addr, lsig, mainRegistrationContract_appID, algod_client)
    print("------------ OPT IN TXN RESULT: ------------")
    print(txn)
main()