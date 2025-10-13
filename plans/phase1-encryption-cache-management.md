# Phase 1: Data-at-Rest Encryption & Cache Management

## Overview

Implement encrypted caching system with automatic 90-day expiry (configurable), clear/export commands, and multi-factor authentication support (password, passkey, or YubiKey with PIN).

## Implementation Steps

### 1. Create Encryption Module (`src/encryption.py`)

**New file**: `src/encryption.py`

Implement `DataEncryption` class with:
- AES-256-GCM encryption using `cryptography` library
- PBKDF2 key derivation from password
- Support for three authentication methods:
  - Password-based (PBKDF2 key derivation)
  - Passkey/keyfile (read key from file)
  - Hardware key (YubiKey HMAC-SHA1 challenge-response with PIN)
- Salt generation and storage
- Encrypt/decrypt methods for JSON data

Key methods:
```python
class DataEncryption:
    def __init__(self, auth_method: str, credential: str, pin: Optional[str] = None)
    def encrypt_data(self, data: dict) -> bytes
    def decrypt_data(self, encrypted_data: bytes) -> dict
    def derive_key(self) -> bytes  # Different implementation per auth method
```

**Dependencies to add**:
- `cryptography>=41.0.0` - AES encryption
- `ykman>=5.0.0` (optional) - YubiKey support

### 2. Update Cache Module (`src/cache.py`)

**Modify existing**: `src/cache.py`

Changes to `ResumeCache` class:
- Add encryption support to `_load_cache()` and `_save_cache()`
- Add `created_at` timestamp to all cache entries
- Implement automatic expiry check in `_load_cache()` (default 90 days)
- Add `export_cache()` method to export all data as JSON
- Update `clear_cache()` to securely wipe encrypted files
- Add `get_cache_info()` method for detailed cache statistics

New methods:
```python
def _is_expired(self, entry: dict, max_age_days: int) -> bool
def export_cache(self, output_path: str) -> None
def get_cache_info(self) -> dict  # Returns entries, sizes, expiry info
```

Integration points:
- Line 29: Add encryption parameter to `__init__`
- Line 35-39: Add decryption to `_load_cache()`
- Line 43-47: Add encryption to `_save_cache()`
- Line 106-113: Add expiry timestamp to cache entries

### 3. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add new configuration options:
```python
# Encryption settings
CACHE_ENCRYPTION_ENABLED = os.getenv("CACHE_ENCRYPTION_ENABLED", "true").lower() == "true"
CACHE_AUTH_METHOD = os.getenv("CACHE_AUTH_METHOD", "password")  # password, keyfile, yubikey
CACHE_KEYFILE_PATH = os.getenv("CACHE_KEYFILE_PATH", "")
CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "90"))

# YubiKey settings (if using hardware key)
YUBIKEY_SERIAL = os.getenv("YUBIKEY_SERIAL", "")
YUBIKEY_SLOT = int(os.getenv("YUBIKEY_SLOT", "2"))
```

### 4. Add CLI Commands (`main.py`)

**Modify existing**: `main.py`

Add new command-line arguments (around line 36):
```python
parser.add_argument(
    "--clear-cache",
    action="store_true",
    help="Clear all cached data"
)

parser.add_argument(
    "--export-cache",
    metavar="OUTPUT",
    help="Export all cached data to JSON file"
)

parser.add_argument(
    "--cache-info",
    action="store_true",
    help="Display cache statistics and information"
)
```

Add command handlers before main analysis logic (around line 100):
```python
# Handle cache management commands
if args.clear_cache:
    resume_cache.clear_cache()
    return 0

if args.export_cache:
    resume_cache.export_cache(args.export_cache)
    console.print(f"[green]Cache exported to: {args.export_cache}[/green]")
    return 0

if args.cache_info:
    info = resume_cache.get_cache_info()
    # Display formatted cache information
    return 0
```

### 5. Update Documentation

**Modify**: `README.md`

Add new sections:

**Cache Management** (after "How It Works" section):
- Explain automatic 90-day expiry
- Document `--clear-cache` command
- Document `--export-cache` command
- Document `--cache-info` command

**Data Privacy & Security** (new section before "Requirements"):
- Explain encryption at rest
- Document authentication methods (password, keyfile, YubiKey)
- Explain GDPR compliance features
- Document data retention policy
- Explain what data is stored and where

**Environment Variables** (new section):
```
CACHE_ENCRYPTION_ENABLED=true
CACHE_AUTH_METHOD=password  # or keyfile, yubikey
CACHE_KEYFILE_PATH=/path/to/keyfile
CACHE_EXPIRY_DAYS=90
YUBIKEY_SERIAL=12345678
YUBIKEY_SLOT=2
```

**Create**: `.env.example`

Provide template with all configuration options and comments explaining each.

### 6. Update Dependencies

**Modify**: `pyproject.toml`

Add to dependencies array (line 7):
```toml
"cryptography>=41.0.0",  # Encryption
"ykman>=5.0.0",  # YubiKey support (optional)
```

## Testing Strategy

1. Test encryption/decryption with all three auth methods
2. Test cache expiry with different age settings
3. Test clear-cache command
4. Test export-cache command with encrypted data
5. Test backward compatibility (unencrypted → encrypted migration)
6. Test YubiKey integration with PIN

## Security Considerations

- Never log or print encryption keys or passwords
- Use secure memory wiping for sensitive data
- Validate YubiKey presence before operations
- Implement rate limiting for PIN attempts
- Store salt separately from encrypted data
- Use constant-time comparison for authentication

## Files to Create/Modify

**New Files**:
- `src/encryption.py` (new encryption module)
- `.env.example` (environment variable template)

**Modified Files**:
- `src/cache.py` (add encryption, expiry, export)
- `config.py` (add encryption config)
- `main.py` (add CLI commands)
- `README.md` (add documentation)
- `pyproject.toml` (add dependencies)

## Success Criteria

- All cached data encrypted at rest
- Cache automatically expires after configured days
- Users can clear cache with single command
- Users can export cache data to JSON
- Support for 3 authentication methods
- Clear documentation of privacy features
- Backward compatible with existing caches

## To-dos

- [ ] Create src/encryption.py with DataEncryption class supporting password/keyfile/YubiKey authentication
- [ ] Update src/cache.py to add encryption, automatic expiry, and export functionality
- [ ] Add encryption and cache configuration options to config.py
- [ ] Add --clear-cache, --export-cache, and --cache-info commands to main.py
- [ ] Update README.md with cache management, security, and GDPR compliance documentation
- [ ] Add cryptography and ykman dependencies to pyproject.toml
- [ ] Create .env.example with all encryption and cache configuration options
