import base64
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *
from helpers import compile_smart_signature, \
    lsig_payment_txn, \
    payment_transaction, \
    wait_for_confirmation

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# this is the registration contract
# TODO: it should generate a new DSNPId and update its global state to the new id.
# TODO: it should also be able to insert a new handle into a caller's local state
def approval_program(owner_addr):
    # program = Cond(
    #     [Txn.application_id() == Int(0), handle_creation],
    #     [Txn.on_completion() == OnComplete.OptIn, handle_optin],
    #     [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
    #     [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
    #     [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
    #     [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    # )
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

def clear_program()
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

# only one txn allowed, no groups
# can be an application call or a payment
# must be to the opted in contract
# must pay a fee of 1 algo
def registry_smart_sig(optin_addr):
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
            Txn.receiver() == Addr(optin_addr),
            Txn.amount() == fee,
        )
    ])
    # Mode.Signature indicates that this is a smart signature and not a smart contract.
    return compileTeal(program, Mode.Signature, version=5)


def optin_transaction(senderAddr, sender_logic_sig, amount, receiverAddr, algod_client) -> dict:
    params = algod_client.suggested_params()
    utxn = transaction.ApplicationOptInTxn(senderAddr, params, receiverAddr, amount)
    stxn = utxn.sign(sender_logic_sig)
    txid = algod_client.send_transaction()
    pmtx = wait_for_confirmation(algod_client, txid , 5)
    return pmtx

# min: 100,000 microalgos
def main():
    algod_client = algod.AlgodClient(algod_token, algod_address)
    application_owner_addr = "W5SZASJBHX7SXDZ7D65G75AWLTCFOPJMNWMQRYPUOWK6R4NGU3CKSL65MA"
    registry_global_schema = transaction.StateSchema(1)  # DSNPid current
    registry_local_schema = transaction.StateSchema(1, 15)  # DSNPid, handles

    # create the registraton contract by calling ApplicationCreateTxn
    txn = transaction.ApplicationCreateTxn(
        application_owner_addr,
        transaction.OnComplete.NoOpOC,
        approval_program(application_owner_addr),
        clear_program,
        registry_global_schema,
        registry_local_schema,

    )
    mainRegistrationContract =
    sender_mnemonic = addr0Phr

    stateless_program_teal = registry_smart_sig(mainRegistrationContract)

    program, stateless_reg_contract_addr = compile_smart_signature(algod_client, stateless_program_teal)

    print(compileTeal(approval_program()))

    print("Program:", program)
    print("hash: ", stateless_reg_contract_addr)
    print("--------------------------------------------")
    print("Activating Donation Smart Signature......")

    # Activate contract by sending
    # 100k microalgo minimum balance +
    # 10k microalgo transaction fee +
    # 1 microalgo for transaction fee from creator
    amt = 110001
    payment_transaction(sender_mnemonic, amt, stateless_reg_contract_addr, algod_client)

    print("--------------------------------------------")
    print("Withdraw from Donation Smart Signature......")

    # send a test transaction to the contract.
    lsig_payment_txn(program, stateless_reg_contract_addr, 0, mainRegistrationContract, algod_client)

    # send an opt-in transaction to the contract.
    encoded_prog = program.encode()
    decodedBytes = base64.decodebytes(encoded_prog)
    lsig = transaction.LogicSig(decodedBytes)

    # should we be sending the application id, can't just use any value
    optin_transaction(stateless_reg_contract_addr, lsig, 1000,  mainRegistrationContractId, algod_client)

main()
