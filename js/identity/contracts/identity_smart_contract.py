# samplecontract.py
from pyteal import *
import os

def approval_program():
    handle_creation = Return(Int(1))
    handle_optin = Return(Int(1))
    handle_closeout = Return(Int(1))
    handle_updateapp = Return(Int(1))
    handle_deleteapp = Return(Int(1))
    
    remove_delegate = Seq([
        App.localDel(Int(0), Txn.application_args[1]),
        Return(Int(1)),
    ])

    add_delegate = Seq([
        App.localPut(Int(0), Txn.application_args[1], Txn.application_args[2]),
        Return(Int(1)),
    ])

    handle_noop = Cond(
        [And(
            Txn.application_args[0] == Bytes("Add_delegate")
        ), add_delegate],
        [And(
            Txn.application_args[0] == Bytes("Remove_delegate")
        ), remove_delegate]
    )

    program=Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return compileTeal(program, Mode.Application, version=4)


def clear_state_program():
   program=Return(Int(1))
   # Mode.Application specifies that this is a smart contract
   return compileTeal(program, Mode.Application, version=4)


def main():
    dirname = os.path.dirname(__file__)

    identity_approval_ab_path = os.path.join(dirname, "./teal/identity_approval.teal")
    with open(identity_approval_ab_path, "w") as f:
        approval_program_teal=approval_program()
        f.write(approval_program_teal)

    # compile program to TEAL assembly
    identity_clear_ab_path = os.path.join(dirname, "./teal/identity_clear.teal")
    with open(identity_clear_ab_path, "w") as f:
        clear_state_program_teal=clear_state_program()
        f.write(clear_state_program_teal)


main()
