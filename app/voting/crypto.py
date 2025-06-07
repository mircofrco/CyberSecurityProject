from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import json
import base64
import secrets


class VoteEncryption:
    @staticmethod
    def generate_election_keypair():
        """Generate RSA keypair for election"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode(), public_pem.decode()

    @staticmethod
    def encrypt_vote(vote_data, public_key_pem):
        """Encrypt vote using election public key"""
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        # Convert vote to JSON and encrypt
        vote_json = json.dumps(vote_data).encode()

        # Use hybrid encryption: RSA for symmetric key, AES for data
        symmetric_key = Fernet.generate_key()
        f = Fernet(symmetric_key)
        encrypted_vote = f.encrypt(vote_json)

        # Encrypt symmetric key with RSA
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Combine encrypted key and vote
        result = {
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'encrypted_vote': base64.b64encode(encrypted_vote).decode()
        }

        return json.dumps(result)

    @staticmethod
    def decrypt_vote(encrypted_data, private_key_pem):
        """Decrypt vote using election private key"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )

        data = json.loads(encrypted_data)
        encrypted_key = base64.b64decode(data['encrypted_key'])
        encrypted_vote = base64.b64decode(data['encrypted_vote'])

        # Decrypt symmetric key
        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt vote
        f = Fernet(symmetric_key)
        vote_json = f.decrypt(encrypted_vote)

        return json.loads(vote_json.decode())

    @staticmethod
    def generate_vote_hash(user_id, election_id, salt=None):
        """Generate anonymous hash for vote tracking"""
        if salt is None:
            salt = secrets.token_hex(16)

        hash_input = f"{user_id}:{election_id}:{salt}".encode()
        vote_hash = hashlib.sha256(hash_input).hexdigest()
        return vote_hash