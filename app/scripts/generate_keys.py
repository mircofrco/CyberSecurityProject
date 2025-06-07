#!/usr/bin/env python
"""
Interactive key-ceremony helper.

Example:
  ./generate_keys.py --shares 5 --threshold 3 --out master_key.bin
"""
import argparse
import pathlib

from app.api.crypto.paillier_utils import generate_keypair
from app.api.crypto.shamir_utils import split_secret

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shares", type=int, required=True)
    ap.add_argument("--threshold", type=int, required=True)
    ap.add_argument("--out", type=pathlib.Path, default="master_privkey.bin")
    args = ap.parse_args()

    pub, priv = generate_keypair()

    # -> store public key in clear text (safe to publish)
    (args.out.parent / "pubkey.json").write_text(
        f"{pub.n}\n")          # one-liner for MVP

    # -> split private key
    priv_bytes = priv.p.to_bytes(512, "big") + priv.q.to_bytes(512, "big")
    pieces = split_secret(priv_bytes, args.shares, args.threshold)

    for idx, share in enumerate(pieces, 1):
        fname = args.out.parent / f"priv_share_{idx}.txt"
        fname.write_text(share)
        print(f"Wrote {fname}")

if __name__ == "__main__":
    main()
