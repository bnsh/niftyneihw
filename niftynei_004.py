#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Decoding Bitcoin Script"""

# Decode the following scripts into human readable assembly

# For op_codes, write them as OP_CODE, eg OP_ADD, OP_CHECKSIG, OP_EQUAL, etc.
# For data, just write the data
# eg '176567616d6965727020676e697473657265746e69206e41' is the length byte 17 and the data
# so in the assembly you'd just put '6567616d6965727020676e697473657265746e69206e41'

# N/A	1-75	0x01-0x4b	(special)	data	The next opcode bytes is data to be pushed onto the stack

import re
from opcodes import grab_opcodes

def consume_pushdata(compact_field_length, pos, raw_bytes):
    start_of_data = pos+compact_field_length
    length = int(bytes(reversed(raw_bytes[pos:start_of_data])).hex(), 16)
    end_of_data = start_of_data + length
    val = raw_bytes[start_of_data:end_of_data].hex()
    pos = end_of_data
    return pos, val

def decode_to_assembly(raw_script_hex):
    raw_bytes = bytes.fromhex(raw_script_hex)

    asm = []
    opcodes = grab_opcodes()
    pos = 0
    state = 0
    while pos < len(raw_bytes):
        opcode_or_length = raw_bytes[pos]
        # I don't know what to do with "opcode/lengths" >= 187. Are these opcodes reserved? Or do I treat them as lengths?
        # For the purposes of this assignment, I'm basically going to treat things that are _not_ in my opcodes list as
        # _lengths_. This may very well be _wrong_.
        if state == 0:
            if opcode_or_length in opcodes:
                opcode = opcode_or_length
                pos += 1
                if opcodes[opcode][0] == "OP_PUSHDATA1":
                    state = 1
                elif opcodes[opcode][0] == "OP_PUSHDATA2":
                    state = 2
                elif opcodes[opcode][0] == "OP_PUSHDATA4":
                    state = 3
                else:
                    asm.append(opcodes[opcode][0])
            else:
                length = opcode_or_length
                cur = pos+1
                pos += 1+length
                val = re.sub(r'^[0]+', '', raw_bytes[cur:pos].hex())
                asm.append(val)
        elif state == 1:
            # We just read an OP_PUSHDATA1. The next byte contains a length and then we read that number of bytes and
            # push that onto the stack.
            pos, val = consume_pushdata(1, pos, raw_bytes)
            asm.append(val)
            state = 0
        elif state == 2:
            # We just read an OP_PUSHDATA2. The next _two_ bytes contains a length and then we read that number of bytes and
            # push that onto the stack.
            pos, val = consume_pushdata(2, pos, raw_bytes)
            asm.append(val)
            state = 0
        elif state == 3:
            # We just read an OP_PUSHDATA4. The next _four_ bytes contains a length and then we read that number of bytes and
            # push that onto the stack.
            pos, val = consume_pushdata(4, pos, raw_bytes)
            asm.append(val)
            state = 0

    assert pos == len(raw_bytes), (pos, len(raw_bytes))
    return " ".join(asm)

def main():
    raw_script1 = "010101029301038801027693010487"

    asm_script1 = decode_to_assembly(raw_script1)

    raw_script2 = "176567616d6965727020676e697473657265746e69206e41a820a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5887693010287"

    asm_script2 = decode_to_assembly(raw_script2)

    # the lengths here are tricky! make sure you're careful. It's a little like compact field size, but the rules are different
    # see OP_PUSHDATA2 on https://en.bitcoin.it/wiki/Script for help
    #pylint: disable=line-too-long
    raw_script3 = "4d4001255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df614f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c230570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e74ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a14d4001255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de218f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b16e879169a77ca787"
    #pylint: enable=line-too-long

    asm_script3 = decode_to_assembly(raw_script3)
    print(f"{asm_script1=}")
    print(f"{asm_script2=}")
    print(f"{asm_script3=}")

if __name__ == "__main__":
    main()
