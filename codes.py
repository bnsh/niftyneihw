#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""This is from Nifty Nei 2: Project 2B: P2PK: It is a supporting ile, seemingly."""
import re

def parse_compact_size(data):
    first = int.from_bytes(data[0:1], 'big')
    if first < 253:
        return first, 1
    if first < 254:
        val = int.from_bytes(data[1:3], 'little')
        return val, 3
    if first < 255:
        val = int.from_bytes(data[1:5], 'little')
        return val, 5

    val = int.from_bytes(data[1:9], 'little')
    return val, 9

def size_compact_size(size):
    if size < 253:
        return (size).to_bytes(1, 'little')
    if size < 254:
        return bytes([0xfd]) + (size).to_bytes(2, 'little')
    if size < 255:
        return bytes([0xfe]) + (size).to_bytes(4, 'little')

    return bytes([0xff]) + (size).to_bytes(8, 'little')


def parse_input_bytes(tx_bytes):
    inputx = {}
    inputx['txid'] = tx_bytes[:32]
    ptr = 32
    inputx['vout'] = tx_bytes[ptr:ptr+4]
    ptr += 4

    count, size = parse_compact_size(tx_bytes[ptr:])
    ptr += size
    inputx['scriptSig'] = tx_bytes[ptr:ptr+count]
    ptr += count
    inputx['sequence'] = tx_bytes[ptr:ptr+4]
    return inputx, ptr+4


def parse_output_bytes(tx_bytes):
    outputx = {}
    ptr = 8
    outputx['amount'] = tx_bytes[:ptr]
    count, size = parse_compact_size(tx_bytes[ptr:])
    ptr += size
    outputx['scriptPubKey'] = tx_bytes[ptr:ptr+count]
    return outputx, ptr+count


def parse_tx_bytes(tx_hex):
    tx_bytes = bytes.fromhex(tx_hex)

    #pylint: disable=invalid-name
    tx = {}
    #pylint: enable=invalid-name
    ptr = 0
    tx['version'] = tx_bytes[0:4]
    ptr += 4

    if tx_bytes[ptr] == 0x00:
        assert tx_bytes[ptr+1] == 0x01
        tx['marker_flag'] = bytes([0x00, 0x01])
        ptr += 2

    count, size = parse_compact_size(tx_bytes[ptr:])
    ptr += size
    tx['inputs'] = []
    for _ in range(0, count):
        inputx, size = parse_input_bytes(tx_bytes[ptr:])
        ptr += size
        tx['inputs'].append(inputx)

    count, size = parse_compact_size(tx_bytes[ptr:])
    ptr += size
    tx['outputs'] = []
    for _ in range(0, count):
        outputx, size = parse_output_bytes(tx_bytes[ptr:])
        ptr += size
        tx['outputs'].append(outputx)

    if 'marker_flag' in tx:
        # todo, this
        assert False

    tx['locktime'] = tx_bytes[ptr:]
    return tx

def cleanup_tx(hmn_read_tx):
    """ Given a block of text, strip out everything except the hex strings"""
    ret_val = []
    lines = hmn_read_tx.split('\n')
    for line in lines:
        substr = line.split(':')[-1]    # suggested-by @chrisguida + @macaki
        ret_val += re.findall(r'[0-9a-fA-F]{2}', substr)
    return ''.join(ret_val)
