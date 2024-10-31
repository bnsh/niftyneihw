#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""
Question 1:
Run the following command in bitcoin-cli, or parse the raw transaction and calculate the hashes by hand:

bitcoin-cli decoderawtransaction 010000000001014bd289251780cf66c55ec09706eec00e031101bb3b7bd0aa9a815136389923e5010000000000000000020065cd1d0000000017a914b4c405153d385a21e5691c8f83fcdae8b97241f587acea645900000000160014db7ac922e011e579ff3f84623b7d9d6944b5c8d3024830450221008b09269cd88bcdc5681a4dddbbbad506ee85f4445418046f6d175f2f380259850220497427ad95e78448434c7d6bcb6d8c1828613c256309ee6ad2da7b0dc3d7e53e0121027a919db019d6ad889c682e446f6b91b7c02fba7f0c9164e331374545adce1ee000000000

What is the txid of this transaction?
"""

# import json
from hashlib import sha256

def hash256(data):
    return sha256(sha256(data).digest()).digest()[::-1].hex()

def reverseendian(val):
    return "".join(reversed([val[idx:idx+2] for idx in range(0, len(val), 2)]))

#pylint: disable=too-many-locals
def segwit_parse_transaction(raw_hex):
    pos = 0

    version = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
    pos += 8

    input_count = int(raw_hex[pos:(pos+2)], 16)
    pos += 2

    segwit = False
    if input_count == 0:
        flag = int(raw_hex[pos:(pos+2)], 16)
        pos += 2
        assert flag == 1, f"Segwit transaction, but flag=0x{flag:02x} expected 0x01"

        input_count = int(raw_hex[pos:(pos+2)], 16)
        pos += 2

        segwit = True

    inputs = []
    for dummy_input_idx in range(0, input_count):
        txid = reverseendian(raw_hex[pos:(pos+64)])
        pos += 64

        vout = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
        pos += 8

        scriptSig_len = int(raw_hex[pos:(pos+2)], 16)
        pos += 2

        scriptSig = raw_hex[pos:(pos+scriptSig_len*2)]
        pos += scriptSig_len*2

        sequence = int(raw_hex[pos:(pos+8)], 16) # Should this be "reverseendian"?
        pos += 8
        inputs.append({
            "txid": txid,
            "vout": vout,
            "scriptSig_len": scriptSig_len,
            "scriptSig": scriptSig,
            "sequence": sequence
        })

    output_count = int(raw_hex[pos:(pos+2)], 16)
    pos += 2

    outputs = []
    for dummy_oidx in range(0, output_count):
        amount = int(reverseendian(raw_hex[pos:(pos+16)]), 16)
        pos += 16

        scriptPubKey_len = int(raw_hex[pos:(pos+2)], 16)
        pos += 2

        scriptPubKey = raw_hex[pos:(pos+scriptPubKey_len*2)]
        pos += scriptPubKey_len*2

        outputs.append({
            "amount": amount,
            "scriptPubKey_len": scriptPubKey_len,
            "scriptPubKey": scriptPubKey
        })

    witness_count = 0
    witnesses = []
    if segwit:
        witness_count = int(raw_hex[pos:(pos+2)], 16)
        pos += 2

        for _ in range(0, witness_count):
            single_witness_len = int(raw_hex[pos:(pos+2)], 16)
            pos += 2

            single_witness = raw_hex[pos:pos+(single_witness_len*2)]
            pos += single_witness_len * 2
            witnesses.append(f"{single_witness_len:02x}{single_witness:s}")

    locktime = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
    pos += 8

    assert len(raw_hex) == pos

    parsed_tx = {
        "version": version,
        "segwit": segwit,
        "input_count": input_count,
                # Make sure you're parsing the txid here as big endian!!
                # You'll know you parsed this correctly if you can find the txid when you search for it in a block explorer
        "inputs": inputs,
        "output_count": output_count,
        "outputs": outputs,
        "witness_count": witness_count,
        "witnesses": witnesses,
        "locktime": locktime
    }
    return parsed_tx
#pylint: enable=too-many-locals

def back2hex(txstruct, omitsegwit):
    version = txstruct["version"]
    segwit = txstruct["segwit"]
    input_count = txstruct["input_count"]
    inputs = txstruct["inputs"]
    output_count = txstruct["output_count"]
    outputs = txstruct["outputs"]
    witness_count = txstruct["witness_count"]
    witnesses = txstruct["witnesses"]
    locktime = txstruct["locktime"]
    retval = []
    retval.append((version).to_bytes(4, 'little').hex())
    if segwit and not omitsegwit:
        retval.append("0001")
    retval.append((input_count).to_bytes(1, 'little').hex())
    for inp in inputs:
        retval.append(bytes.fromhex(inp["txid"])[::-1].hex())
        retval.append((inp["vout"]).to_bytes(4, 'little').hex())
        retval.append((inp["scriptSig_len"]).to_bytes(1, 'little').hex())
        retval.append(inp["scriptSig"])
        retval.append((inp["sequence"]).to_bytes(4, 'little').hex())

    retval.append((output_count).to_bytes(1, 'little').hex())
    for outp in outputs:
        retval.append((outp["amount"]).to_bytes(8, 'little').hex())
        retval.append((outp["scriptPubKey_len"]).to_bytes(1, 'little').hex())
        retval.append(outp["scriptPubKey"])

    if segwit and not omitsegwit:
        retval.append((witness_count).to_bytes(1, 'little').hex())
        for witness in witnesses:
            retval.append(witness)

    retval.append((locktime).to_bytes(4, 'little').hex())
    return "".join(retval)

def main():
    txbytes = "010000000001014bd289251780cf66c55ec09706eec00e031101bb3b7bd0aa9a815136389923e5010000000000000000020065cd1d0000000017a914b4c405153d385a21e5691c8f83fcdae8b97241f587acea645900000000160014db7ac922e011e579ff3f84623b7d9d6944b5c8d3024830450221008b09269cd88bcdc5681a4dddbbbad506ee85f4445418046f6d175f2f380259850220497427ad95e78448434c7d6bcb6d8c1828613c256309ee6ad2da7b0dc3d7e53e0121027a919db019d6ad889c682e446f6b91b7c02fba7f0c9164e331374545adce1ee000000000"
    segwit_parsed = segwit_parse_transaction(txbytes)
    txbv = back2hex(segwit_parsed, omitsegwit=False)
    assert txbv == txbytes
    # print(json.dumps(segwit_parsed, indent=4, sort_keys=False))
    txwosegwit = back2hex(segwit_parsed, omitsegwit=True)
    print(hash256(bytes.fromhex(txwosegwit)))

if __name__ == "__main__":
    main()
