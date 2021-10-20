from pyteal import *

# The transaction type is first verified to be a payment transaction,
# the transaction receiver is compared to the benefactor’s address
# the group size is verified to guarantee that this transaction is not submitted with other transactions in a group
# his prevents the escrow from being rekeyed to another account
# With escrows, any account can fund these accounts. 

def donation_escrow(benefactor):
    Fee = Int(1000)

    program = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= Fee,
        Txn.receiver() == Addr(benefactor),
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
    )

    return compileTeal(program, Mode.Signature, version=4)

def main():
    # compile program to TEAL assembly
    test_benefactor = "NZHJVFZNVQGCKVMSHZC2QCB22EO7CU6ZXPH3XFRS5RENGVLUTI2K3J2ALA"
    with open("./teal/sample_smart_sig.teal", "w") as f:
        smart_signature_program_teal = donation_escrow(test_benefactor)
        f.write(smart_signature_program_teal)

main()