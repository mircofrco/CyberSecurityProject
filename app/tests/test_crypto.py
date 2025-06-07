from random import randint

from app.api.crypto.paillier_utils import (
    generate_keypair, encrypt_ballot, decrypt_ballot, homomorphic_sum
)

def test_encrypt_decrypt_roundtrip():
    pub, priv = generate_keypair()
    vote = randint(0, 1)              # yes/no referendum
    enc = encrypt_ballot(vote, pub)
    assert decrypt_ballot(enc, pub, priv) == vote

def test_homomorphic_tally():
    pub, priv = generate_keypair()
    votes = [randint(0, 1) for _ in range(25)]
    cts  = [encrypt_ballot(v, pub) for v in votes]

    total_enc = homomorphic_sum(cts, pub)
    total_dec = priv.decrypt(total_enc)

    assert total_dec == sum(votes)
