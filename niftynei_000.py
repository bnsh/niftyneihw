#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
# pylint: disable=invalid-name

"""Parse raw_hex transaction"""

import json

def reverseendian(val):
    return "".join(reversed([val[idx:idx+2] for idx in range(0, len(val), 2)]))

#pylint: disable=too-many-locals
def parse_transaction(raw_hex):
    pos = 0

    version = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
    pos += 8

    input_count = int(raw_hex[pos:(pos+2)], 16)
    pos += 2

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

        sequence = int(raw_hex[pos:(pos+8)], 16)
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

    locktime = int(reverseendian(raw_hex[pos:(pos+8)]), 8)
    pos += 8

    assert len(raw_hex) == pos

    parsed_tx = {
        "version": version,
        "input_count": input_count,
                # Make sure you're parsing the txid here as big endian!!
                # You'll know you parsed this correctly if you can find the txid when you search for it in a block explorer
        "inputs": inputs,
        "output_count": output_count,
        "outputs": outputs,
        "locktime": locktime
    }
    return parsed_tx
#pylint: enable=too-many-locals

def main():
    #pylint: disable=line-too-long
    raw_hex = '01000000038b9896d07dd8f694b72e750a69105e0f134837500a020ebb8fc77380973075bc000000008a47304402206213230eddf32c60167e654e3934602c0e46308932ea344a0e242699c1818f51022044895b0fc7adef9e551777d0de789d508fb56785ca80fbbfeec01b9d07b4fb7901410450128ec8ff327d0cd782702a32f51b14149d8a19b89075a56ead462363fa29ae9b35ca4f71ae8d5cd78803d835d05451ebb3ee861c80746f0e4fd5316ec306a7ffffffff92491ce956f3a52074ee8ab024069bc14c8396c33d8bb43de1ef1cc7f9f01a46000000008b48304502207fec947609bd275a32cfd058c76678fe868c12b681c9ab0c31f716a92ba5fed0022100cd95a9ff2036a7ee0babe268ac64b425b4490be36609452ec01c11b8eaf14665014104b5a08389cbbf01178c5451f9e1c09265e73ef7bc4a1bc6761143593134e5c6460ab31ae2d5f09140a5e95a58538fd4651cb966a86de41c1a6a79b6045ecc0312ffffffff3ca3845de7916e872570ce1676dedc3151717b7d345affa188eaa7baad3bd1a1000000006b483045022100a53211eed0e857dfab414f106190780c3791797b81aaf5a8a8f997681f6ea660022030a00ef0733bafa5f05026e027ac6f230c3929f9c766ef31edeabf2bcaed81740121036ec01e60571b5050bafb2d77063061a487228da342e996003e35ac7b5519e2e7ffffffff048e2e1601000000001976a9142b18e0074aad70661b6fecf742cbefab4a145d1188ac40420f00000000001976a914a229e570ef0c11b6a20451d65047b0fbe2c96a2f88ac40420f00000000001976a91408536923b85945c704b47bb2657294757bc417dc88ac40420f00000000001976a91415c307a88533528de8414fc2fc96b4e67ac0e0ef88ac00000000'
    #pylint: enable=line-too-long
    parsed = parse_transaction(raw_hex)
    print(json.dumps(parsed, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
