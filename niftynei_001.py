#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
# pylint: disable=invalid-name

"""Parse raw_hex transaction"""

import json
from decimal import Decimal
from bitcoin_lib import grab_raw_proxy

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

def default(val):
    if isinstance(val, Decimal):
        return float(val)
    raise TypeError(type(val))

def grab_input_amounts(txid, vout):
    proxy = grab_raw_proxy()
    raw_tx = proxy.getrawtransaction(txid)
    decoded_tx = proxy.decoderawtransaction(raw_tx)
    # print(decoded_tx["vout"][vout])
    return int(decoded_tx["vout"][vout]["value"] * 1_0000_0000)

def main():
    #pylint: disable=line-too-long
    raw_hex = '0100000003efdad76b8da190878c1de4c92fd4aaa0a287984171a4398c1140df11663cb84c010000006b483045022065db71606b84edc291eb2ec55e49ee2fd44afef8b20b4ef88fc2a01c2ba6e963022100dfb24228f2f80574d64a3a2964c5b3d054c14f0bf18c409f72345331271b5020012102a1e806a0c19aaf32363eb19e91a901eafdfc513d13f632f4e2a39f3cb894ad27ffffffff670fa789f11df8b202f380ebc6b4f76fa312f6bfb11494811f00411d7bbb0ae0010000006b4830450221009b5fe2b2bff2a9801725351ae2a8eb410b10b6fecb44edb442ee750e6825f1a4022038e19b3b0e3a95b4a3952dde87efc049d4a72a4424872ab768f7fb3220be4c1e0121032256cb5a8e6d3c9354da72369b939a35febb80d35e6afb50e6f348c20c6c6c05ffffffff52dd5a0965f2d36850f3d2ddeb1457cd72e1cd5a325656af44a3c6ba9f2d42fa010000006c4930460221008a9bf9a1ba9b4125ac9b8cf10423447ad8c7ede3414028237c4c0e0b3b3dc4fd0221009f94721c04b7d4eb33bb1aad61daf98b6ed05dfbf5e3225ae9b3afe24b8924d50121028b04194cb938044761bb93d3917abcce13f910a0500c08e61bdaaf5ea29b5ca0ffffffff02b0c39203000000001976a9148a81571528050b80099821ed0bc4e48ed33e5e4d88ac1f6ab80a010000001976a914963f47c50eaafd07c8b0a8a505c825216a4fee6d88ac00000000'
    #pylint: enable=line-too-long
    parsed = parse_transaction(raw_hex)
    input_sats = [grab_input_amounts(inp["txid"], inp["vout"]) for inp in parsed["inputs"]]
    assert len(input_sats) == 3
    input1_sats, input2_sats, input3_sats = input_sats

    print(f"{input1_sats=}\n{input2_sats=}\n{input3_sats=}\n")
    print(f'outputs = {json.dumps(parsed["outputs"], indent=4, sort_keys=True):s}')
    outputs_total = sum(output["amount"] for output in parsed["outputs"])
    print(f"{outputs_total=}")

if __name__ == "__main__":
    main()
