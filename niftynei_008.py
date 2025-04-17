#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""
    This is from Nifty Nei's _second_ course: https://www.udemy.com/course-dashboard-redirect/?course_id=4892180
    Course 2: Project 2A: secp256k1 public/private key challenges

    A useful utility site: https://graui.de/code/elliptic2/
"""

# We're going to keep the names in the original.
#pylint: disable=invalid-name

from typing import Tuple

# from coincurve import PrivateKey

class ECMath:
    p = 2**256 - 2**32 - 977 # this is also from SEC256k1 https://secg.org/sec2-v2.pdf
    Gx = int("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
    Gy = int("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)
    n = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)

    a = 0
    b = 7

    @classmethod
    def modinv(cls, a, denominator=None):
        denominator = denominator or cls.p
        if a == 0:
            raise ZeroDivisionError('division by zero')
        lm, hm = 1, 0
        low, high = a % denominator, denominator
        while low > 1:
            r = high // low
            nm, new = hm - lm * r, high - low * r
            lm, low, hm, high = nm, new, lm, low
        return lm % denominator


    @classmethod
    def ec_add(cls, p1, p2):
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2 and y1 != y2:
            return None  # Point at infinity

        if p1 == p2:
            # Point doubling
            s = (3 * x1 * x1) * cls.modinv(2 * y1) % cls.p
        else:
            # Point addition
            s = (y2 - y1) * cls.modinv(x2 - x1) % cls.p

        x3 = (s * s - x1 - x2) % cls.p
        y3 = (s * (x1 - x3) - y1) % cls.p

        return (x3, y3)

    @classmethod
    def scalar_mult(cls, k, point=None):
        point = point or (cls.Gx, cls.Gy)
        result = None  # Point at infinity
        addend = point

        while k:
            if k & 1: # if k is odd.
                result = cls.ec_add(result, addend)
            addend = cls.ec_add(addend, addend)
            k >>= 1

        return result



# Challenge #1
# This is just a warm up.
def find_pubkey_point(priv_int):
    # I mean, I guess really the priv_int is just the number we're going to "multiply" (in an EC sense)
    # the generator point by...
    Px, Py = ECMath.scalar_mult(priv_int)
    return Px, Py

# Challenge #2
def find_compressed_key(priv_int):
    Px, Py = ECMath.scalar_mult(priv_int)
    prefix = "02" if Py %2 == 0 else "03"
    return prefix + f"{Px:064x}"

# Challenge #3
def find_uncompressed_key(priv_int):
    # If I remember right, the private key is how many times we have to add the public key to itself till we get back to the generator.
    # 04 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798 483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8 (from https://secg.org/sec2-v2.pdf)

    # public_key + G * privint == 0
    # public_key = - G * privint
    # (negative, means we have to flip the y coordinate. (As in subtract it from p))
    # I'm going to assume "priv_int" is the k that we're going to multiply the generator point with.
    Px, Py = ECMath.scalar_mult(priv_int)
    return "04" + f"{Px:064x}{Py:064x}"


# Challenge #4
def point_to_compressed(point: Tuple[int, int]):
    x, y = point
    parity = 2 if y % 2 == 0 else 3
    return f"{parity:02x}{x:032x}"

# Challenge #5
def compressed_to_point(compressed_key):
    p = 2**256 - 2**32 - 977 # this is also from SEC256k1 https://secg.org/sec2-v2.pdf
    parity = int(compressed_key[:2], 16)
    x = int(compressed_key[2:], 16)
    y2 = (pow(x, 3, p) + 7) % p # 7 is the constant b from SEC256k1 https://secg.org/sec2-v2.pdf
    y = pow(y2, (p+1)//4, p)

    if (y % 2) != (parity % 2):
        y = p - y

    return (x, y)

# Challenge #6
def find_privkey(compressed_key):
    priv_int = 1
    while (dummy_tbv := find_compressed_key(priv_int)) != compressed_key:
        # print(f"{priv_int:d} {tbv:s} != {compressed_key:s}")
        priv_int += 1
    return priv_int

def main():
    # Note: you can try running things here!
    # press the Run key up top to run this code.
    pubkey = "037caa72b37a8ab3bd0bac031a47606f8917d9f42c6ec2d2fb429fd9904a381f34"
    print(find_privkey(pubkey))

    # Quiz
    print(compressed_to_point("021ee150c33f1b3c0a771eba4043f9703711818367fbbf3d493dc659c0a5759a1f"))
    # (13967483450616349477689229903680325848506681557199731546200209960089289071135, 95089823123371960764939697553919321809797997505518524899406025955076401968704) Correct

    targets = ("04e9234", "041c6f9", "044193e", "045edd5")
    for idx in range(1, 1024):
        res = find_uncompressed_key(idx)
        for target in targets:
            if res.startswith(target):
                print(idx, res)

    print(find_uncompressed_key(615))
    # 0448471331eac4867028fa6642a76ca6c53380c1d90f52a4b2ea640d47f159af0ab4ea854693fde01cfb903a3118bb61f5c5047b94705a714d5b586d47a0142704 This is _not_ one of the choices and in fact it seems like the key that's correct is for key=69
    # The correct answer is the answer for priv_int=69
    # 69 045edd5cc23c51e87a497ca815d5dce0f8ab52554f849ed8995de64c5f34ce7143efae9c8dbc14130661e8cec030c89ad0c13c66c0d17a2905cdc706ab7399a868

    # I guess we just try all the keys listed in the options.
    target = "039ab8636783794de771b8ae530484154c0b4723237c89c2b851af73c8d6f5dc62"
    cands = (8281828727, 19991, 188282, 999999999)
    for cand in cands:
        if find_compressed_key(cand) == target:
            print(cand)


if __name__ == "__main__":
    main()
