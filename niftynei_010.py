#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4

"""Nifty Nei Homework: Course 2: Project 3: ECDSA Sign + Verify
https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm
"""

import coincurve
from niftynei_008 import ECMath, compressed_to_point

# We are trying to keep our variables consistent with
# the wikipedia variables.
#pylint: disable=invalid-name

def make_sig(digest_bytes, privkey_int, nonce_int):
    # `e` in the wiki is `digest_bytes` in python.
    # `d_A` in the wiki is `privkey_int` in python.
    # `k` in the wiki is `nonce_int` in python.
    # `z` is _also_ `e` in our case anyway
    x1, dummy_y1 = ECMath.scalar_mult(nonce_int)
    k = nonce_int
    kinv = ECMath.modinv(k, ECMath.n)
    z = int(digest_bytes.hex(), 16)
    r = x1 % ECMath.n
    d_A = privkey_int
    assert r != 0

    s = (kinv * (z + r * d_A)) % ECMath.n
    return (r, s)

def verify_sig(digest_bytes, pubkey_hex, signature):
    z = int(digest_bytes.hex(), 16)
    r, s = signature
    sinv = ECMath.modinv(s, ECMath.n)

    u1 = z * sinv
    u2 = r * sinv

    Q_A = compressed_to_point(pubkey_hex)

    x1, dummy_y1 = ECMath.ec_add(
        ECMath.scalar_mult(u1, point=(ECMath.Gx, ECMath.Gy)),
        ECMath.scalar_mult(u2, point=Q_A)
    )

    assert r == x1, "This is not a valid signature"
    return True


def main():
    # Let's sign our message!
    privkey_int = 489274845958 # 888
    nonce_int = 42009000000890890900 # 42
    digest_hex = 'fbced109229e2ab9f5f0766b830b9273ed0afe34dd10276bfce43f796e9ce2b0'
    digest_bytes = bytes.fromhex(digest_hex)
    sig = make_sig(digest_bytes, privkey_int, nonce_int)
    print("signature: ", sig)

    # And now verify that our signature is correct
    pubkey_hex = coincurve.PrivateKey.from_int(privkey_int).public_key.format().hex()
    print(verify_sig(digest_bytes, pubkey_hex, sig))
    print(pubkey_hex)

if __name__ == "__main__":
    main()
