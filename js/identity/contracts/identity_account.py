from pyteal import *
import os

def identity_account():
    # program = And(
    #     Int(1) == Int(1),
    #     Return(Int(1))
    # )
    program = Return(Int(1))

    return compileTeal(program, Mode.Signature, version=4)

def main():
    dirname = os.path.dirname(__file__)
    identity_account_ab_path = os.path.join(dirname, "./teal/identity_clear.teal")
    with open(identity_account_ab_path, "w") as f:
        identity_account_program_teal = identity_account()
        f.write(identity_account_program_teal)

main()