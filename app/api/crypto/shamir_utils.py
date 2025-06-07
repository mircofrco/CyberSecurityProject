"""
Very thin wrapper around secretsharing to split & recover a private key.
"""
import base64
from typing import List

from secretsharing import PlaintextToHexSecretSharer as S


def split_secret(secret_bytes: bytes,
                 shares: int,
                 threshold: int) -> List[str]:
    """
    Return `shares` hex-encoded pieces (only `threshold`
    of them are needed to reconstruct).
    """
    b64 = base64.b64encode(secret_bytes).decode()
    return S.split_secret(b64, threshold, shares)


def recover_secret(pieces: List[str]) -> bytes:
    b64 = S.recover_secret(pieces)
    return base64.b64decode(b64.encode())
