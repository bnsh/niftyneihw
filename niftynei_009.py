#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""This is Nifty Nei 2: Project 2B: P2PK"""

# Open the Tutorial for instructions.
# import secrets
from codes import cleanup_tx

from opcodes import grab_mnemonic2code
from niftynei_008 import find_compressed_key


def main():
    spend_tx_parts = """
    version: 02000000
    num inputs: 01
      txid: <todo!!> hint: don't forget to reverse it
      vout: 00000000
      scriptSig: 00
      sequence: feffffff
    num outputs: 01
      amount: 7cee052a01000000
      scriptPubKey: 1600142e280d852d48fc17784b4b1e39764fb34949cbf8
    locktime: 00000000
    """

    mnemonic2code = grab_mnemonic2code()

    # upper = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    private_key = 0x402a5527a83efd05e29e753432fdbb25b8b6654608592626abf5769d60da81f7 # secrets.randbelow(upper)
    public_key = find_compressed_key(private_key)
    len_public_key = len(public_key) // 2
    op_checksig = mnemonic2code["OP_CHECKSIG"]
    p2pk_script = f"{len_public_key:02x}{public_key:s}{op_checksig:02x}"
    len_p2pk_script = len(p2pk_script) // 2

    lock_tx_parts = f"""
    version: 02000000
    num inputs: 01
      txid: 9aef57862f85a169f6e154e3df34a53bcac8511b33882a6ec1d64e618e268570
      vout: 00000000
      scriptSig: 00
      sequence: feffffff
    num outputs: 01
      amount: 3ef0052a01000000
      scriptPubKey: {len_p2pk_script:02x}{p2pk_script:s}
    locktime: 00000000
    """

    #TODO: I _think_ lock_tx_parts is "done"... I think where we have to go from here
    #      is to actually lock up this transaction. Then the second part of all this
    #      is to _spend_ this money in _another_ transaction.

    dummy_p2pk_info = {
      # Fill this in with your private key
      'private_key': private_key,
      # Fill this in with the pubkey for your private key, compressed
      'pubkey': public_key,
      # Fill this in with the P2PK script for your pubkey
      'p2pk_script': p2pk_script,
      # Add a scriptPubKey and amount to the `tx_parts`, above.
      'tx': cleanup_tx(lock_tx_parts),
      # TXID of the signed and sent transaction
      'sent_txid': '{',
      # TX that spends the above txid
      'spend_tx': cleanup_tx(spend_tx_parts),
    }

    print("Locking TX:", cleanup_tx(lock_tx_parts))
    print("Spending TX:", cleanup_tx(spend_tx_parts))

if __name__ == "__main__":
    main()
