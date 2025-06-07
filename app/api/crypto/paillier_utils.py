"""
Light-weight helpers around the phe Paillier library.
"""
import base64
import json
from functools import reduce
from typing import List, Tuple

from phe import paillier

# ---------- key generation ------------------------------------------------- #

def generate_keypair() -> Tuple[paillier.PaillierPublicKey,
                                paillier.PaillierPrivateKey]:
    return paillier.generate_paillier_keypair()


# ---------- serialization helpers ----------------------------------------- #
# EncryptedNumber needs both 'ciphertext' and 'exponent' to be restored.

def _encnum_to_b64(enc) -> str:
    payload = json.dumps({"c": enc.ciphertext(), "e": enc.exponent})
    return base64.b64encode(payload.encode()).decode()


def _b64_to_encnum(b64: str, pubkey: paillier.PaillierPublicKey):
    raw = json.loads(base64.b64decode(b64).decode())
    return paillier.EncryptedNumber(pubkey,
                                    raw["c"],
                                    raw["e"])

# ---------- Step 3: ballot encryption ------------------------------------- #

def encrypt_ballot(vote: int,
                   pub: paillier.PaillierPublicKey) -> str:
    """
    Encrypt a single integer vote and return a Base64 string.
    """
    enc = pub.encrypt(vote)
    return _encnum_to_b64(enc)

def decrypt_ballot(b64: str,
                   pub: paillier.PaillierPublicKey,
                   priv: paillier.PaillierPrivateKey) -> int:
    return priv.decrypt(_b64_to_encnum(b64, pub))

# ---------- Step 4: homomorphic tally ------------------------------------- #

def homomorphic_sum(ciphertexts_b64: List[str],
                    pub: paillier.PaillierPublicKey):
    """
    Return an EncryptedNumber representing the sum of all encrypted ballots.
    """
    encs = [_b64_to_encnum(b, pub) for b in ciphertexts_b64]
    return reduce(lambda a, b: a + b, encs)
