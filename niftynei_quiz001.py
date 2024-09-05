#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""This is just a quiz, so I'm half-assing this, and not building a full out
   interpreter, because I'm pretty sure, that will eventually be a "real"
   assignment, and building the interpreter will delay us in watching more
   videos. So, here I'm just going to check the sha256 of these values is all.

        Question 2:
        Perform a Stack Evaluation of the following Bitcoin Script:

        hex: "176567616d6965727020676e697473657265746e69206e41a820a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5887693010287"
        asm: "6567616d6965727020676e697473657265746e69206e41 OP_SHA256 a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5 OP_EQUALVERIFY OP_DUP OP_ADD 2 OP_EQUAL

        Does this script finish execution and evaluate to True?
"""

import hashlib
from collections import deque

def main():
    stack = deque()

    # 6567616d6965727020676e697473657265746e69206e41
    stack.append(bytes.fromhex("6567616d6965727020676e697473657265746e69206e41"))

    # OP_SHA256
    operand = stack.pop()
    sha256bytes = hashlib.sha256(operand).digest()
    stack.append(sha256bytes)

    # a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5
    stack.append(bytes.fromhex("a966e2ccbbcd3814c8f913abcb1c4d487d63f23d93667c186b00a5a9181fd7b5"))

    # OP_EQUALVERIFY
    # https://github.com/bitcoin/bitcoin/blob/93e48240bfdc25c2760d33da69e739ba1f92da9b/src/script/interpreter.cpp#L887
    # This appears to simply check for equality and raise an Error if they are not equal.
    operanda = stack.pop()
    operandb = stack.pop()
    # assert operanda == operandb, "OP_EQUALVERIFY failed."

    # OP_DUP
    operand = stack.pop()
    stack.append(operand)
    stack.append(operand)

    # OP_ADD
    operanda = stack.pop()
    operandb = stack.pop()
    stack.append(operanda+operandb)

    # 2
    stack.append(2)

    # OP_EQUAL
    operanda = stack.pop()
    operandb = stack.pop()
    if operanda == operandb:
        stack.append(1)
    else:
        stack.append(0)

    assert len(stack) == 0 or (len(stack) == 1 and stack.pop() == 1)
    print("WOOT!")

# OP_EQUALVERIFY OP_DUP OP_ADD 2 OP_EQUAL

if __name__ == "__main__":
    main()
