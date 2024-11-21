#! /usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=4
"""This will do all that setup business."""

import os
import json
import time
from subprocess import run


def launch_test_network():
    run([
        "/usr/bin/env", "bitcoind", "-regtest", "-daemon",
        "-fallbackfee=0.0000025"
    ],
        check=True)
    time.sleep(10)


def test_network_is_running():
    result = run(
        ["/usr/bin/env", "bitcoin-cli", "-regtest", "getblockchaininfo"],
        capture_output=True,
        text=True,
        check=False)
    return result.returncode == 0


def create_wallet(wallet_name):
    if not os.path.exists(
            os.path.join(os.environ["HOME"],
                         f".bitcoin/regtest/wallets/{wallet_name:s}")):
        run([
            "/usr/bin/env", "bitcoin-cli", "-regtest", "createwallet",
            wallet_name
        ],
            check=True)
    run(["/usr/bin/env", "bitcoin-cli", "-regtest", "loadwallet", wallet_name],
        capture_output=True,
        check=False)


def get_new_address(wallet_name):
    result = run([
        "/usr/bin/env", "bitcoin-cli", "-regtest", "getnewaddress", wallet_name
    ],
                 capture_output=True,
                 text=True,
                 check=True)
    return result.stdout.strip()


def mine(wallet_name, num_blocks, address):
    result = run([
        "/usr/bin/env", "bitcoin-cli", "-regtest",
        f"-rpcwallet={wallet_name:s}", "generatetoaddress",
        str(num_blocks), address
    ],
                 capture_output=True,
                 check=True)
    blocks = json.loads(result.stdout)
    return blocks


def getnewaddress(wallet_name):
    result = run([
        "/usr/bin/env", "bitcoin-cli", "-regtest",
        f"-rpcwallet={wallet_name:s}", "getnewaddress"
    ],
                 capture_output=True,
                 check=True)
    return result.stdout.strip()


def getblock(block_hash):
    result = run(
        ["/usr/bin/env", "bitcoin-cli", "-regtest", "getblock", block_hash],
        capture_output=True,
        text=True,
        check=True)
    return json.loads(result.stdout)


def gettransaction(tx_id):
    result = run(
        ["/usr/bin/env", "bitcoin-cli", "-regtest", "gettransaction", tx_id],
        capture_output=True,
        text=True,
        check=True)
    return json.loads(result.stdout)


def list_utxos():
    result = run(["/usr/bin/env", "bitcoin-cli", "-regtest", "listunspent"],
                 capture_output=True,
                 check=True)
    return json.loads(result.stdout)


def main():
    if not test_network_is_running():
        launch_test_network()
    wallet_name = "test_wallet"
    create_wallet(wallet_name)
    address = getnewaddress(wallet_name)
    block_hash = mine(wallet_name, 1, address)[-1]
    block = getblock(block_hash)
    transaction = gettransaction(block["tx"][0])
    mine(wallet_name, 100, getnewaddress(wallet_name))
    utxos = list_utxos()
    assert transaction["txid"] in set(utxo["txid"] for utxo in utxos)


if __name__ == "__main__":
    main()
