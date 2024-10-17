#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Nifty Nei Homework 6"""

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

    ## Locking our Bitcoin to the P2SH

    # Alrighty! We've got everything we need to do the funding transaction locking bitcoin to our Pay to Script Hash
    # Bitcoin did all the conversions for us!
    # The "p2sh" value is the encoding of the scripthash where the redeem script is our custom script
    # We're going to do a transaction locking 10.0000025BTC to that "p2sh" address
    # Run the following command:
    #
    # bcr sendtoaddress 'the-psh-address-it-starts-with-2' 10.0000025
    #
    # The returned hash is the txid, in big endian, of that transaction, copy it below:
    funding_txid_big_endian = bcr("sendtoaddress", decodescript["p2sh"], "10.0000025").strip()

    # Remember, we're in regtest no we control block production! Let's mine a block to confirm the funding tx
    #
    # bcr generatetoaddress 1 $(bcr getnewaddress)
    #
    newaddress = bcr("getnewaddress").strip()
    res = bcr("generatetoaddress", "1", newaddress)
    # This seems to be an array: ["411306ebc09ce504202eb12de6639c079f7df2349ada88887e51d42b02f507af"]

    ## Preparing the input to unlock our Bitcoin

    # If you'll recall, the input skeleton for a legacy transaction looks like this:
    # input_skeleton = {'txid': '', 'vout': '', 'scriptSig': '', 'sequence': ''}
    # we've already got the txid from before, but it's in big endian!
    # Bitcoin wants the input txid in little endian, so let's flip it here:
    funding_txid_little_endian = bytes.fromhex(funding_txid_big_endian)[::-1].hex()

    # Now we need to fill in the vout. It'll either be 0 or 1, you can check in the funding tx with the command:
    #
    # bcr gettransaction funding_txid_big_endian
    #
    # In the returned json under the "details" key, you'll see the payment and whether the vout was 0 or 1
    # input whether it was 0 or 1 here, and convert it to 4 byte little endian while you're at it eg '01000000':
    res = json.loads(bcr("gettransaction", funding_txid_big_endian))
    vout_raw = res["details"][0]["vout"]
    vout = bytes([vout_raw, 0, 0, 0]).hex() # This is bad. Really we should be converting this to an _int_ and then using pack or something to turn the int into a byte array.

    # We're not using sequence for anything fancy here, so let's just set it to 'ffffffff', the max val
    sequence = 'ffffffff'

    ## Assembling the ScriptSig

    # To Unlock this P2SH we have to provide 2 elements: the preimage, and the redeem script
    # we've got both of these above, we just need te turn them into script data fields by adding lengths
    # Reminder, the length is in hex, so 2 characters, and it's the number of bytes that make up the data field
    preimage_len = (len(preimage)).to_bytes(1, 'little').hex()

    # DONE set the len, in hex for the redeem script like we did above for the preimage
    # we declared the redeem script as the variable redeem_script_hex
    redeem_script_hex_len = f"{len(redeem_script_bytearray):02x}"

    # Finally we need to combine the 2 datafields into a single scriptSig and add a scriptSigLen
    scriptSig = preimage_len + preimage_hex + \
        redeem_script_hex_len + redeem_script_hex
    scriptSig_len = (len(scriptSig) // 2).to_bytes(1, 'little').hex()

    # We've now got our input ready!
    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('scriptSig_hex: ', scriptSig, '\n')

    # Exercise: Fill in the following input skeleton as hex with your calculated values:
    inp = {
        'txid': funding_txid_little_endian,  # 32 bytes, little endian
        'vout': vout,  # 4 bytes, little endian
        'scriptSig_len': scriptSig_len,  # Compact field size
        'scriptSig': scriptSig,  # big endian
        'sequence': sequence,  # 4 bytes, little endian
    }
    # Then let's squash it all together into a single hex string
    input_hex = inp['txid'] + inp['vout'] + inp['scriptSig_len'] + inp[
        'scriptSig'] + inp['sequence']

    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('input_hex: ', input_hex, '\n')

    ## Building our Unlocking TX

    # Let's use the bitcoin-cli to create the framework for our TX.
    # We'll pass in the output back to ourself, but leave the inputs empty
    # Then we'll just plug our input hex string we made above into the TX

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
    raw_tx_hex_no_input = bcr("createrawtransaction", "[]", json.dumps([{sweep_address: 10}])).strip()

    # The rawtx should start with: 020000000001.... : Version 2, 0 inputs, 1 output
    # The following code will insert the input we made above, tack on your raw_tx_hex output and locktime, and put it back together as a completed transaction
    version = '02000000'
    input_count = '01'
    raw_tx_done = version + input_count + input_hex + raw_tx_hex_no_input[10:]

    # DONE uncomment the print statement and hit the Green 'Run' button to see your work so far in the console.
    print('raw_tx_done: ', raw_tx_done, '\n')

    ## Testing and Sending our Unlocking TX:

    # Our TX is ready to broadcast! If you did everything per the instructions above, you should be able to run:
    #
    # bcr testmempoolaccept '["your-completed-tx-hex"]'

    # rnd was just testing to see what happens on a failure.
    # rnd = "".join("0123456789abcdef"[random.randrange(0, 16)] for _ in raw_tx_done)

    res = json.loads(bcr("testmempoolaccept", json.dumps([raw_tx_done])))
    assert all(val["allowed"] for val in res)
    print("raw_tx_done looks good!")
    #
    # and it should return 'complete: true' in the json

    # If it returned true, it's valid and ready to send!! Let's sweep our bitcoin back, unlocking the P2SH, by running,
    #
    # bcr sendrawtransaction your-complete-tx-hex
    res = bcr("sendrawtransaction", raw_tx_done)
    print(res)

    ### CONGRATULATIONS!! YOU'VE JUST BUILT YOUR FIRST P2SH LOCKING AND UNLOCKING TXS BY HAND!!!
#pylint: enable=too-many-locals,invalid-name

if __name__ == "__main__":
    main()
