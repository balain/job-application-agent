"""Data encryption module for secure caching and GDPR compliance."""

import os
import json
import secrets
from pathlib import Path
from typing import Optional, Union, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    import ykman.device
    import ykman.piv

    YUBIKEY_AVAILABLE = True
except ImportError:
    YUBIKEY_AVAILABLE = False


class DataEncryption:
    """Handles data encryption with multiple authentication methods."""

    def __init__(self, auth_method: str, credential: str, pin: Optional[str] = None):
        """
        Initialize encryption with specified authentication method.

        Args:
            auth_method: 'password', 'keyfile', or 'yubikey'
            credential: Password, keyfile path, or YubiKey serial
            pin: PIN for YubiKey authentication
        """
        self.auth_method = auth_method
        self.credential = credential
        self.pin = pin
        self._key = None
        self._salt = None

    def _derive_key(self) -> bytes:
        """Derive encryption key based on authentication method."""
        if self.auth_method == "password":
            return self._derive_key_from_password()
        elif self.auth_method == "keyfile":
            return self._derive_key_from_file()
        elif self.auth_method == "yubikey":
            return self._derive_key_from_yubikey()
        else:
            raise ValueError(f"Unsupported authentication method: {self.auth_method}")

    def _derive_key_from_password(self) -> bytes:
        """Derive key from password using PBKDF2."""
        if not self._salt:
            self._salt = secrets.token_bytes(32)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        return kdf.derive(self.credential.encode())

    def _derive_key_from_file(self) -> bytes:
        """Derive key from keyfile."""
        keyfile_path = Path(self.credential)
        if not keyfile_path.exists():
            raise FileNotFoundError(f"Keyfile not found: {keyfile_path}")

        with open(keyfile_path, "rb") as f:
            key_data = f.read()

        # Use first 32 bytes as key
        return key_data[:32]

    def _derive_key_from_yubikey(self) -> bytes:
        """Derive key from YubiKey challenge-response."""
        if not YUBIKEY_AVAILABLE:
            raise RuntimeError("YubiKey support not available. Install ykman package.")

        try:
            # Find YubiKey device
            devices = ykman.device.list_all_devices()
            if not devices:
                raise RuntimeError("No YubiKey device found")

            device = devices[0]

            # Perform challenge-response authentication
            challenge = os.urandom(20)  # 20-byte challenge
            response = device.challenge_response(challenge, slot=2)

            # Derive key from response
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"yubikey_salt",  # Fixed salt for YubiKey
                iterations=10000,
            )
            return kdf.derive(response)

        except Exception as e:
            raise RuntimeError(f"YubiKey authentication failed: {e}")

    def encrypt_data(self, data: Union[dict, str]) -> bytes:
        """
        Encrypt data using AES-256-GCM.

        Args:
            data: Dictionary or string to encrypt

        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        elif isinstance(data, str):
            data = data.encode("utf-8")

        # Get encryption key
        key = self._derive_key()

        # Generate random nonce
        nonce = secrets.token_bytes(12)

        # Encrypt with AES-GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)

        # Combine nonce + ciphertext
        encrypted_data = nonce + ciphertext

        # Store salt if using password method
        if self.auth_method == "password" and self._salt:
            encrypted_data = self._salt + encrypted_data

        return encrypted_data

    def decrypt_data(self, encrypted_data: bytes) -> Union[dict, str]:
        """
        Decrypt data using AES-256-GCM.

        Args:
            encrypted_data: Encrypted data as bytes

        Returns:
            Decrypted data (dict or str)
        """
        # Extract salt if using password method
        if self.auth_method == "password":
            if len(encrypted_data) < 32:
                raise ValueError("Invalid encrypted data")
            self._salt = encrypted_data[:32]
            encrypted_data = encrypted_data[32:]

        # Extract nonce and ciphertext
        if len(encrypted_data) < 12:
            raise ValueError("Invalid encrypted data")

        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        # Get decryption key
        key = self._derive_key()

        # Decrypt with AES-GCM
        aesgcm = AESGCM(key)
        try:
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

        # Try to parse as JSON, fallback to string
        try:
            return json.loads(decrypted_data.decode("utf-8"))
        except json.JSONDecodeError:
            return decrypted_data.decode("utf-8")

    def encrypt_file(self, file_path: Union[str, Path]) -> str:
        """
        Encrypt entire file.

        Args:
            file_path: Path to file to encrypt

        Returns:
            Path to encrypted file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Encrypt data
        encrypted_data = self.encrypt_data(file_data)

        # Write encrypted file
        encrypted_path = file_path.with_suffix(file_path.suffix + ".enc")
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        return str(encrypted_path)

    def decrypt_file(self, encrypted_path: Union[str, Path]) -> str:
        """
        Decrypt file to temporary location.

        Args:
            encrypted_path: Path to encrypted file

        Returns:
            Path to decrypted temporary file
        """
        encrypted_path = Path(encrypted_path)
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")

        # Read encrypted data
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        # Decrypt data
        decrypted_data = self.decrypt_data(encrypted_data)

        # Write to temporary file
        temp_path = Path.cwd() / f"temp_{secrets.token_hex(8)}"
        with open(temp_path, "wb") as f:
            if isinstance(decrypted_data, bytes):
                f.write(decrypted_data)
            else:
                f.write(decrypted_data.encode("utf-8"))

        return str(temp_path)

    def secure_delete(self, file_path: Union[str, Path]) -> bool:
        """
        Securely delete file by overwriting with random data.

        Args:
            file_path: Path to file to securely delete

        Returns:
            True if successful
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return True

        try:
            # Get file size
            file_size = file_path.stat().st_size

            # Overwrite with random data (3 passes)
            with open(file_path, "r+b") as f:
                for _ in range(3):
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Delete file
            file_path.unlink()
            return True

        except Exception:
            return False

    def get_key_info(self) -> Dict[str, Any]:
        """
        Get information about the encryption key.

        Returns:
            Dictionary with key information
        """
        return {
            "auth_method": self.auth_method,
            "key_length": 256,  # AES-256
            "algorithm": "AES-256-GCM",
            "salt_length": 32 if self._salt else 0,
            "iterations": 100000 if self.auth_method == "password" else 0,
        }


class EncryptionManager:
    """Manages encryption for the application."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize encryption manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self._encryption = None

    def initialize_encryption(self) -> DataEncryption:
        """Initialize encryption based on configuration."""
        if self._encryption:
            return self._encryption

        auth_method = self.config.get("CACHE_AUTH_METHOD", "password")
        credential = self.config.get("CACHE_KEYFILE_PATH", "")

        if auth_method == "password":
            # Prompt for password if not in config
            credential = self.config.get("CACHE_PASSWORD", "")
            if not credential:
                import getpass

                credential = getpass.getpass("Enter encryption password: ")

        pin = self.config.get("YUBIKEY_PIN", "")

        self._encryption = DataEncryption(auth_method, credential, pin)
        return self._encryption

    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled."""
        return self.config.get("CACHE_ENCRYPTION_ENABLED", True)

    def get_encryption(self) -> Optional[DataEncryption]:
        """Get encryption instance."""
        if not self.is_encryption_enabled():
            return None

        if not self._encryption:
            self.initialize_encryption()

        return self._encryption
