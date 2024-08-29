#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Read the opcodes in opcodes.json"""

import os
import re
import json

def localfile(fname):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fname)

def grab_opcodes(fname=None):
    fname = fname or localfile("opcodes.json")
    with open(fname, "rt", encoding="utf-8-sig") as jsfp:
        raw = json.load(jsfp)
        assert all(re.match(r'^0x[0-9a-f]{2}$', key) for key, _ in raw.items())
        assert all(isinstance(val, list) for _, val in raw.items())
        assert all(len(val) == 2 for _, val in raw.items())
        assert all(isinstance(val[0], str) for _, val in raw.items())
        assert all(isinstance(val[1], str) for _, val in raw.items())
        cooked = {int(re.sub(r'^0x([0-9a-f]{2})$', r'\1', key), 16): val for key, val in raw.items()}
        return cooked
