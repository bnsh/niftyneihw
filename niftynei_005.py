#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Converting Custom Scripts to Pay to Script Hash Addresses"""

import hashlib

import base58

from opcodes import grab_opcodes

def ripemd160(byts):
    # RIPEMD160 doesn't seem to be a part of openssl by default.
    # I had to add these to /etc/ssl/openssl.cnf
    # 1. "legacy = legacy_sect" to [provider_sect]
    # 2. add these sections:
    #    [default_sect]
    #    activate = 1
    #    [legacy_sect]
    #    activate = 1

    ctxt = hashlib.new("ripemd160")
    ctxt.update(byts)
    return ctxt.digest()

def sha256(byts):
    return hashlib.sha256(byts).digest()

def hash160(byts):
    return ripemd160(sha256(byts))

def compactfieldish(byts):
    length = len(byts)
# N/A	1-75	0x01-0x4b	(special)	data	The next opcode bytes is data to be pushed onto the stack
# OP_PUSHDATA1	76	0x4c	(special)	data	The next byte contains the number of bytes to be pushed onto the stack.
# OP_PUSHDATA2	77	0x4d	(special)	data	The next two bytes contain the number of bytes to be pushed onto the stack in little endian order.
# OP_PUSHDATA4	78	0x4e	(special)	data	The next four bytes contain the number of bytes to be pushed onto the stack in little endian order.
    assert length >= 0
    if 0 <= length <= 75:
        return bytes([length]) + byts
    if 76 <= length < 256:
        return bytes([0x76, length]) + byts # 0x76 is OP_PUSHDATA1
    if 256 <= length < 65536:
        length_lo = (length & 0x0000ff) >> 0
        length_hi = (length & 0x00ff00) >> 8
        return bytes([0x77, length_lo, length_hi]) + byts # 0x77 is OP_PUSHDATA2
    assert length >= 65536
    length_le1 = (length & 0x00000000ff) >> 0
    length_le2 = (length & 0x000000ff00) >> 8
    length_le3 = (length & 0x0000ff0000) >> 16
    length_le4 = (length & 0x00ff000000) >> 24
    return bytes([0x78, length_le1, length_le2, length_le3, length_le4]) + byts # 0x78 is OP_PUSHDATA4

MAINNET = 0x05
TESTNET = 0xc4

def create_p2sh(net, script):
    opcodes_binary2text = grab_opcodes()
    opcodes = {txt: key for key, (txt, descr) in opcodes_binary2text.items()}

    scripthash = hash160(bytes.fromhex(script))
    address = bytes([net]) + scripthash
    checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[0:4]
    address_with_checksum = address + checksum
    p2sh_address = base58.b58encode(address_with_checksum)
    p2sh_script_pub_key = bytes([opcodes["OP_HASH160"]]) + compactfieldish(scripthash) + bytes([opcodes["OP_EQUAL"]])

    return p2sh_address.decode("utf-8"), p2sh_script_pub_key.hex()


# scriptPubKey is common nomenclature in the bitcoin world.
#pylint: disable=invalid-name
def main():
    # Run bitcoin-cli -regtest decodescript on the following raw custom scripts
    # to get their p2sh encodings for address and scriptPubKey
    # NO THANK YOU! WE WILL DO THIS ON OUR OWN! HA!

    raw_script1 = "010101029301038801027693010487"

    # DONE: filled these in for raw_script1
    p2sh_address1='2MurSWkcDqSq69nuWSBXwNraCFbHvSouGQn' # "p2sh" in the return from bitcoin-cli -regtest decodescript
    p2sh_scriptPubKey1='a9141c99440e4938b969f26e3792f85b457c0365625b87' # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo

    raw_script2 = "176567616d6965727020676e697473657265746e69206e41a820a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5887693010287"

    # DONE: filled these in for raw_script1
    p2sh_address2='2NGQ2qDNtgH9Z86gnq9qxRnJcQbYenWusD4' # "p2sh" in the return from bitcoin-cli -regtest decodescript
    p2sh_scriptPubKey2='a914fdf552e53cf30ec311f96fd009458e03bb88906c87' # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo


    #pylint: disable=line-too-long
    raw_script3 = "4d4001255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df614f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c230570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e74ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a14d4001255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474682032203020522f4865696768742033203020522f547970652034203020522f537562747970652035203020522f46696c7465722036203020522f436f6c6f7253706163652037203020522f4c656e6774682038203020522f42697473506572436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d3120697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe017346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de218f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b16e879169a77ca787"
    #pylint: enable=line-too-long

    # DONE: filled these in for raw_script1
    p2sh_address3='2NASCDwYXs5RNGvVND9H8h4YNAM88hggHXP' # "p2sh" in the return from bitcoin-cli -regtest decodescript
    p2sh_scriptPubKey3='a914bc8d3daecee5323d90014c1b2e041a9cd79b9e6c87' # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo

    p2sh_address1, p2sh_scriptPubKey1 = create_p2sh(TESTNET, raw_script1)
    print(f'{p2sh_address1=} # "p2sh" in the return from bitcoin-cli -regtest decodescript')
    print(f'{p2sh_scriptPubKey1=} # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo')
    print()

    p2sh_address2, p2sh_scriptPubKey2 = create_p2sh(TESTNET, raw_script2)
    print(f'{p2sh_address2=} # "p2sh" in the return from bitcoin-cli -regtest decodescript')
    print(f'{p2sh_scriptPubKey2=} # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo')
    print()

    p2sh_address3, p2sh_scriptPubKey3 = create_p2sh(TESTNET, raw_script3)
    print(f'{p2sh_address3=} # "p2sh" in the return from bitcoin-cli -regtest decodescript')
    print(f'{p2sh_scriptPubKey3=} # "scriptPubKey" in the return from bitcoin-cli -regtest getaddressinfo')
    print()
#pylint: enable=invalid-name




if __name__ == "__main__":
    main()
