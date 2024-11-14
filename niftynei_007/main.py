#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
"""Nifty Nei Homework 7"""

import os
import json
# import random
import hashlib
from subprocess import run

from opcodes import grab_mnemonic2code


def bcr(*args, check=True, capture_output=True):
    cmd = ["/usr/bin/env", "bitcoin-cli", "-regtest"] + list(args)
    print(" ".join(cmd))
    if os.environ.get("BYPASS_BCR", "false") != "true":
        res = run(cmd, check=check, capture_output=capture_output)
        return res.stdout.decode("utf-8")
    return ""


### Set up your Replit Regtest environment.
# See replitsetup.txt for step by step instructions on how to start bitcoind in regtest here and get some coins to play with.

# If you're here, you should have a spendable coin in your regtest wallet.

# Click into the "Shell" to run all the bitcoin-cli commands

# We'll use the following alias for 'bitcoin-cli -regtest', run this command in your shell to use the same alias if you want
#
# alias bcr="bitcoin-cli -regtest"
#
# The following command should return some json with at least 1 spendable coin:
#
# bcr listunspent
#
# If you got json back with at least one 50BTC coin, you're ready to go. If not, go through replitsetup.py to get ready.

### Writing our P2SH Locking and Unlocking Scripts


# Binesh - scriptSig is common bitcoin terminology (hence disabling invalid-name)
#pylint: disable=too-many-locals,invalid-name
def main():
    """This is the main program"""
    # We're going to write a custom locking script.
    # We want to lock our bitcoin to the sha256 of some input preimage, such that only the person who knows the preimage can unlock it.
    # Our preimage will be the bytes encoding of the string: 'Zero conf channels were a mistake'
    # (Python has nice syntactic sugar that converts a string to bytes by putting a b in front of it, see below)
    # '5a65726f20636f6e66206368616e6e656c7320776572652061206d697374616b65'
    preimage = b'Zero conf channels were a mistake'
    preimage_hex = preimage.hex()

    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('preimage_hex: ', preimage_hex, '\n')

    # The "lock" will be the sha256 digest of the above preimage. We've provided this lock in hexadecimal below.
    # '8539f59ef34c750ab9d9f2a1071f2cd7542e318955be8e9e9eab5ab32037b2de'
    lock = hashlib.sha256(preimage).digest()
    lock_hex = lock.hex()
    lock_hex_bytes = bytes.fromhex(lock_hex)
    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('lock_hex: ', lock_hex, '\n')

    # DONE Convert the Lock into the following bitcoin script, then encode it as hex: OP_SHA256 <lock_hex> OP_EQUAL
    mnemonic2code = grab_mnemonic2code()

    redeem_script_bytearray = bytearray()
    redeem_script_bytearray.append(mnemonic2code["OP_SHA256"])
    redeem_script_bytearray.append(len(lock_hex_bytes))
    redeem_script_bytearray.extend(lock_hex_bytes)
    redeem_script_bytearray.append(mnemonic2code["OP_EQUAL"])
    redeem_script_hex = redeem_script_bytearray.hex()
    # Tip: op_codes are a single byte, you can look them up on https://en.bitcoin.it/wiki/Script
    # Tip: data is the hex encoding, prefaced by the length. A sha256 digest is always 32 bytes, which is '20' as hex
    # For a P2SH, this locking script will also be called our 'redeem script' which will be the last argument in our scriptSig unlocking the TX.

    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('redeem_script_hex: ', redeem_script_hex, '\n')

    # If you did it correctly, you should be able to run the following bitcoin-cli command:
    #
    # bcr decodescript my-locking-script-in-hex
    res = bcr("decodescript", redeem_script_hex)
    #
    # and part of its output should look like the skeleton below:
    # DONE Fill in the rest of the decodescript details returned by the bitcoin-cli. Your 'asm' should look the same as below, if not you didn't write the locking script correctly so check your work there
    decodescript = json.loads(res)
    #     decodescript = {
    #         "asm":
    #         "OP_SHA256 8539f59ef34c750ab9d9f2a1071f2cd7542e318955be8e9e9eab5ab32037b2de OP_EQUAL",
    #         "type": "",
    #         "p2sh": "",
    #         "segwit": {
    #             "asm": "",
    #             "hex": "",
    #             "address": "",
    #             "type": "",
    #             "p2sh-segwit": ""
    #         },
    #     }

    # The address we'll be locking to and from is the P2WSH, which is witness_v0_scripthash. (the one starting with 'bcrt1q...')

    ## Locking our Bitcoin to the WP2SH

    # We've got everything we need to do the funding transaction locking bitcoin to our Pay to Witness Script Hash
    # The "p2wsh", or witness_v0_scripthash, is the segwit version encoding of the scripthash where the redeem script is our custom locking script.

    # We're going to do a transaction locking 10.0000025BTC to that "p2wsh" address
    # Run the following command:
    #
    # bcr sendtoaddress 'the-pwsh-address-it-starts-with-bcrt1q' 10.0000025
    #
    # The returned hash is the txid, in big endian, of that transaction, copy it below:
    funding_txid_big_endian = bcr("sendtoaddress",
                                  decodescript["segwit"]["p2sh-segwit"],
                                  "10.0000025").strip()
    # Bitcoin wants the input txid in little endian, so let's flip it here:
    # Binesh - This bears further investigation. In niftynei_006 we
    #          we didn't do this... (Actually, it _is_ in niftynei_006
    #          just on line 129.
    funding_txid_little_endian = bytes.fromhex(
        funding_txid_big_endian)[::-1].hex()

    # Remember, we're in regtest so we control block production! Let's mine a block to confirm the funding tx
    #
    # bcr generatetoaddress 1 $(bcr getnewaddress)
    #
    newaddress = bcr("getnewaddress").strip()
    res = bcr("generatetoaddress", "1", newaddress)
    # This seems to be an array: ["411306ebc09ce504202eb12de6639c079f7df2349ada88887e51d42b02f507af"]

    ## Preparing the input to unlock our Bitcoin

    # If you'll recall, the input skeleton for a legacy transaction looks like this:
    # input_skeleton = {'txid': '', 'vout': '', 'scriptSig': '', 'sequence': ''}

    # But we're in segwit world now, where scriptSigs are always 00!!
    input_skeleton_segwit = {
        'txid': '',
        'vout': '',
        'scriptSig': '00',
        'sequence': ''
    }
    # We've already got the little endian txid from before

    # Now we need to fill in the vout. It'll either be 0 or 1, you can check in the funding tx with the command:
    #
    # bcr gettransaction funding_txid_big_endian
    res = json.loads(bcr("gettransaction", funding_txid_big_endian))
    #
    # In the returned json under the "details" key, you'll see the payment and whether the vout was 0 or 1
    # input whether it was 0 or 1 here, and convert it to 4 byte little endian while you're at it eg '01000000':
    vout = res["details"][0]["vout"]

    # We're not using sequence for anything fancy here, so let's just set it to 'ffffffff', the max val
    sequence = 'ffffffff'

    # That's everything for our input, because the scriptSig for segwit is just '00'
    # TODO: Fill in the following segwit input skeleton with your info
    input_segwit = {
        'txid': res["txid"],
        'vout': f"{vout:02x}",
        'scriptSig': '00',
        'sequence': sequence
    }

    # That's our input done, so let's squash it all together into a hex_string
    input_segwit_hex = input_segwit['txid'] + \
        input_segwit['vout'] + \
        input_segwit['scriptSig'] + \
        input_segwit['sequence']

    # TODO: uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    # print('input_segwit_hex: ', input_segwit_hex, '\n')

    ## Setting up the Witness Section

    # To Unlock this P2WSH we have to provide the same 2 elements we did for the P2SH: the preimage, and the redeem script
    # However! Instead of putting these in the scriptSig, we're going to put them in a new 'witness' section.
    # The witness section skeleton looks like this:
    witness_skeleton = [
        [],  # Input1's witness stack
        [],  # Input2's witness stack
        [],  # Input3's Witness stack
    ]
    # Every input, regardless of its type, will have a witness stack, prefaced by a compact field size stating how many elements are in each stack. If you're paying from a legacy address that has no witness data, that input will have a witness stack of '00'
    # Our transaction only has 1 input, and it's a p2wsh input that will have 2 elements in its witness stack: the preimage and the redeem script.
    # So our skeleton for the witness section will look like this:
    # input1_witness_stack_size = '02'
    # input1_witness_stack = ['len + preimage-hex', 'len + redeemscript-hex']

    # TODO: Fill in input1's witness elements: our preimage followed by our redeem script
    # Reminder: each data field needs a length prefix! So make sure to add the length byte to each witness stack element
    input1_witness_stack_size = '02'
    preimage_len = len(preimage_hex) // 2
    redeem_script_len = len(redeem_script_hex) // 2
    input1_witness_stack = [
        f"{preimage_len:02x}{preimage_hex:s}",
        f"{redeem_script_len:02x}{redeem_script_hex:s}"
    ]

    # Finally let's squash it into a witness_hex string for when we plug it into the tx
    witness_hex = input1_witness_stack_size + \
        input1_witness_stack[0] + \
        input1_witness_stack[1]

    # TODO: uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    # print('witness_hex: ', witness_hex, '\n')

    ## Building our Unlocking TX

    # Let's use the bitcoin-cli again to create the framework for our TX.
    # We'll pass in the output back to ourself, but leave the inputs empty
    # Then we'll just plug our input hex string we made above into the TX
    # Finally we'll input our witness data where the witness section goes: between the outputs and the locktime
    # and let's not forget that we also need to add the segwit marker and flag after the version to tell bitcoin to parse the TX as segwit!

    # get a new address you'll sweep the funds back to when we unlock from the P2SH:
    #
    # bcr getnewaddress
    #
    # Copy it below
    sweep_address = bcr("getnewaddress").strip()

    # Use the bitcoin-cli to create the transaction structure with the command,
    #
    # bcr createrawtransaction '[]' '[{"your-address-here": 10}]'
    #
    # We're creating a single output, and not passing in any inputs
    # copy the returned raw transaction hex here:
    raw_tx_hex_no_input = bcr("createrawtransaction", "[]",
                              json.dumps([{
                                  sweep_address: 10
                              }])).strip()

    # TODO: uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('raw_tx_hex_no_input:', raw_tx_hex_no_input, '\n')

    # TODO: parse out that transaction data to fill in the following fields, all as hex:
    outaddrlen = int(raw_tx_hex_no_input[28:30], 16) * 2
    raw_tx = {
        'version': raw_tx_hex_no_input[:8],
        'input_count': '01',
        'inputs': [],
        'output_count': '01',
        'outputs': [
            raw_tx_hex_no_input[30:30 + outaddrlen]
        ],  # just copy the hex string for the output here, amount and scriptPubKey
        'locktime': raw_tx_hex_no_input[30 + outaddrlen:]
    }
    print(json.dumps(raw_tx, indent=4))

    ## Inserting our Input and Witness data

    # The first thing we can do is plug our segwit input in:
    raw_tx['inputs'].append(input_segwit_hex)

    # and set the input_count to match the correct number of inputs
    raw_tx['input_count'] = (len(raw_tx['inputs'])).to_bytes(1, 'little').hex()

    # The raw_tx as we have it right now is all that legacy bitcoin nodes would see. But we're using segwit, we have witness data!
    # Let's input the witness data into our raw_tx
    raw_tx['witness'] = witness_hex

    # And we have to add the segwit marker and flag, 0001, after the version to let the parser know about the witness data we included
    raw_tx['marker_and_flag'] = '0001'

    # Finally, let's squash the whole thing together into a hex string
    raw_tx_final_hex = raw_tx['version'] + \
        raw_tx['marker_and_flag'] + \
        raw_tx['input_count'] + \
        raw_tx['inputs'][0] + \
        raw_tx['output_count'] + \
        raw_tx['outputs'][0] + \
        raw_tx['witness'] + raw_tx['locktime']
    print(json.dumps(raw_tx, indent=4))

    # TODO: uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    # print('raw_tx_final_hex:', raw_tx_final_hex, '\n')

    ## Testing and Sending our Unlocking TX:

    # Our TX is ready to broadcast! If you did everything per the instructions above, you should be able to run:
    #
    # bcr testmempoolaccept '["your-final-tx-hex"]'
    # Binesh TODO: This is failing
    bcr("testmempoolaccept", json.dumps([raw_tx_final_hex]))
    #
    # and it should return 'allowed: true' in the json

    # If it returned true, it's valid and ready to send!! Let's sweep our bitcoin back, unlocking the P2WSH, by running,
    #
    # bcr sendrawtransaction your-complete-tx-hex

    ### CONGRATULATIONS!! YOUVE JUST BUILT YOUR FIRST PW2SH LOCKING AND UNLOCKING TXS BY HAND!!!


#pylint: enable=too-many-locals,invalid-name

if __name__ == "__main__":
    main()
