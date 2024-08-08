#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
# pylint: disable=invalid-name

"""Parse raw_hex transaction"""

import json
from decimal import Decimal
from bitcoin_lib import grab_raw_proxy

def reverseendian(val):
    return "".join(reversed([val[idx:idx+2] for idx in range(0, len(val), 2)]))

def satoshis(hexval):
    return int(reverseendian(hexval), 16)

def read_compact_size(raw_hex, pos):
    # Remember that raw_hex is a hexadecimal _STRING_, not bytes, hence all the multiplications by 2.. (pos:pos+4) for the unsigned short,
    # which in principle should be 2 _bytes_, but a _byte_ is 2 hexadecimal digits.
    value = int(raw_hex[pos:(pos+2)], 16)
    pos += 2
    if value == 0xfd: # Read an unsigned short (u16)
        value = int(reverseendian(raw_hex[pos:pos+4]), 16)
        pos += 4
    elif value == 0xfe: # Read an unsigned int (u32)
        value = int(reverseendian(raw_hex[pos:pos+8]), 16)
        pos += 8
    elif value == 0xff: # Read an unsigned long (u64)
        value = int(reverseendian(raw_hex[pos:pos+16]), 16)
        pos += 16
    return pos, value

#pylint: disable=too-many-locals
def parse_transaction(raw_hex):
    pos = 0

    version = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
    pos += 8

    pos, input_count = read_compact_size(raw_hex, pos)

    inputs = []
    for dummy_input_idx in range(0, input_count):
        txid = reverseendian(raw_hex[pos:(pos+64)])
        pos += 64

        vout = int(reverseendian(raw_hex[pos:(pos+8)]), 16)
        pos += 8

        pos, scriptSig_len = read_compact_size(raw_hex, pos)

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

    pos, output_count = read_compact_size(raw_hex, pos)

    outputs = []
    for dummy_oidx in range(0, output_count):
        amount = int(reverseendian(raw_hex[pos:(pos+16)]), 16)
        pos += 16

        pos, scriptPubKey_len = read_compact_size(raw_hex, pos)

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
    raw_hex = '0100000001bbb397fdf39cf8b14a49148861c751543172a6f6500e679e079a7aecfbf7aac400000000fdb50500483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401483045022100e222a0a6816475d85ad28fbeb66e97c931081076dc9655da3afc6c1d81b43f9802204681f9ea9d52a31c9c47cf78b71410ecae6188d7c31495f5f1adfe0df5864a7401ffffffff0180841e00000000001976a9144663e5aab48b092c7478620d867ef2976bce149a88ac00000000'
    #pylint: enable=line-too-long
    parsed = parse_transaction(raw_hex)
    print("parsed_tx=", json.dumps(parsed, indent=4))

if __name__ == "__main__":
    main()
