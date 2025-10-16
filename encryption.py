"""
VaultNote Encryption Module
Pure Python encryption utilities without GUI dependencies
"""
import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class EncryptionManager:
    """Handles AES-256-GCM encryption and decryption"""
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive a 32-byte key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def encrypt(data: str, password: str) -> str:
        """Encrypt data with AES-256-GCM"""
        salt = os.urandom(16)
        key = EncryptionManager.derive_key(password, salt)
        
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        
        encrypted_blob = salt + nonce + ciphertext
        return base64.b64encode(encrypted_blob).decode()
    
    @staticmethod
    def decrypt(encrypted_data: str, password: str) -> str:
        """Decrypt data with AES-256-GCM"""
        encrypted_blob = base64.b64decode(encrypted_data)
        
        salt = encrypted_blob[:16]
        nonce = encrypted_blob[16:28]
        ciphertext = encrypted_blob[28:]
        
        key = EncryptionManager.derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    
    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash a PIN using SHA-256"""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    @staticmethod
    def generate_device_key() -> str:
        """Generate a random device key"""
        return base64.b64encode(os.urandom(32)).decode()
