#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Nifty Nei Homework: Course 2: Project 4: DER Encoding Parsers
Nifty used this transaction:
    https://mempool.space/tx/946e7b72a183814ab2713cb8f42f95c20b85cae29ef51cb529912a009331c3bd
"""

from niftynei_008 import ECMath

# Follow the tutorial to implement a to/from DER converter

#pylint: disable=unused-argument
def decode_der(raw, *, depth):
    # we expect raw to be tlv
    res = []
    ptr = 0

    while ptr < len(raw):
        type_ = int.from_bytes(raw[ptr+0:(ptr+1)], signed=False)
        len_ = int.from_bytes(raw[ptr+1:(ptr+2)], signed=False)
        # print("\t" * depth, f"ptr={ptr:d}, type={type_:02x}, len_={len_:d}")
        data = raw[(ptr+2):(ptr + len_ + 2)]
        if type_ == 1:
            ptr += 1
        else:
            if type_ == 2:
                res.append((type_, len_, int.from_bytes(data, byteorder="big", signed=False)))
            elif type_ == 0x30:
                res.append((type_, len_, decode_der(data, depth=depth+1)))
            ptr += 2 + len_
    return res
#pylint: enable=unused-argument

def flip_s(s_int):
    if s_int > ECMath.n // 2:
        return ECMath.n - s_int
    return s_int

def convert_bytes(val_int):
    val_bytes = val_int.to_bytes(32, byteorder="big", signed=False)
    if val_bytes[0] >= 0x80:
        val_bytes = [0] + val_bytes
    return val_bytes

def build_tlv(type_val, val_bytes):
    return bytes([type_val, len(val_bytes)]) + val_bytes

def sig_to_der(r_int, s_int):
    r_bytes = convert_bytes(r_int)
    s_bytes = convert_bytes(flip_s(s_int))

    r_tlv = build_tlv(2, r_bytes) # "2" is a "integer"
    s_tlv = build_tlv(2, s_bytes) # "2" is a "integer"

    der = build_tlv(0x30, r_tlv + s_tlv) # "0x30" is a "compound object"
    return bytes(der + bytes([0x01])).hex() # Trailing 0x01.

def sig_from_der(der_hex):
    data = bytes.fromhex(der_hex)
    res = decode_der(data, depth=0)

    # We expect a _single_ compound object.
    assert len(res) == 1
    dummy_type, dummy_len, compound_object = res[0]

    # We expect the compound_object to consist of _only_ two integers.
    assert len(compound_object) == 2

    # We expect them _all_ to be of type "2" (integer)
    assert all(subobj[0] == 2 for subobj in compound_object)

    dummy_type, dummy_len, r_int = compound_object[0]
    dummy_type, dummy_len, s_int = compound_object[1]
    return r_int, s_int

def main():
    der = "3044022040e8c365b7fcae6071dcc9ef1ff14db8d98890096631dba4f803991a276818c202204ed39038370f4f4bc51d9cb90e23a57d860f8975a58b14411af4f87ed0265a4901"
    der = "304402202817e9d8d106069c6f2f9be7c4ace6764e514f8bb979bdad30baca616efe6b0a022016c7f704051f02ae2796fb81aa062f28adb43a3e5b2440d5ed4217ccdcbc2b4301"
    r_int, s_int = sig_from_der(der)
    print(r_int)
    print(s_int)
    tbv = sig_to_der(r_int, s_int) # Trust but verify
    print(der)
    print(tbv)
    assert der == tbv

if __name__ == "__main__":
    main()
