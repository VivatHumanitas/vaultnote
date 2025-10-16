# VaultNote - Secure Offline Document Encryption App

VaultNote is a fully offline mobile application for encrypting, storing, and managing sensitive documents on your phone. All data stays on your device with no cloud dependencies.

## Features

### Security
- **AES-256-GCM Encryption**: Military-grade encryption for all documents
- **Optional Vault PIN**: Lock the entire app with a PIN
- **Per-Document PIN**: Add individual PIN protection to specific documents
- **SHA-256 PIN Hashing**: Secure PIN verification
- **Offline-First**: No internet required, all data stays on your device

### Document Management
- Create, edit, and delete encrypted notes
- Import files: TXT, PDF, DOCX formats
- Export encrypted documents in proprietary format (.venc)
- Document metadata tracking (title, timestamps, lock status)
- Visual lock indicators (🔒) for protected documents

### Import/Export
- **Import**: Extract text from PDF, DOCX, and TXT files
- **Export**: Save documents as encrypted binary files (.venc) that only VaultNote can open
- Custom encryption format prevents unauthorized access

## Technology Stack

- **Framework**: Kivy (Python mobile framework)
- **Encryption**: Python cryptography library (AES-256-GCM)
- **Document Processing**: PyPDF2, python-docx
- **Platform**: Android/iOS mobile devices

## Security Details

### Encryption Algorithm
- **AES-256-GCM** (Advanced Encryption Standard with Galois/Counter Mode)
- 256-bit key length
- Authenticated encryption (detects tampering)
- PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)

### Data Storage
- Vault data: Encrypted JSON file (`vault_data.enc`)
- Settings: JSON file with hashed PINs and random device key (`vault_settings.json`)
- Export format: Base64-encoded encrypted binary (.venc files)

### Key Management
- **Device Key**: On first launch, a unique random 256-bit key is generated and stored
- **No Vault PIN**: Data encrypted with the device key (automatic, no user input required)
- **With Vault PIN**: Data encrypted with user PIN, re-encrypted automatically when PIN changes
- **PIN Changes**: Vault is automatically re-encrypted when setting or removing vault PIN

## File Structure

```
main.py                          # Main Kivy application (GUI + encryption)
encryption.py                    # Standalone encryption module (no GUI deps)
test_encryption_standalone.py   # Headless encryption tests (CI/CD ready)
buildozer.spec                  # Android APK build configuration
.github/workflows/build-apk.yml # GitHub Actions automated APK building
```

## Deployment Instructions

### Quick Start

See `QUICKSTART.md` for the fastest way to get your APK!

**Option 1: GitHub Actions (Easiest)**
- Push code to GitHub
- APK builds automatically on every commit
- Download from Actions → Artifacts

**Option 2: Local Build**
```bash
pip install buildozer cython
buildozer android debug
# APK will be in: bin/vaultnote-1.0-debug.apk
```

See `BUILD_INSTRUCTIONS.md` for detailed build steps and troubleshooting.

### For Android (Detailed)

1. Install build tools:
```ini
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
```

4. Build APK:
```bash
buildozer -v android debug
```

5. Deploy to device:
```bash
buildozer android deploy run
```

### For iOS (using Kivy-iOS)

1. Install Kivy-iOS toolchain:
```bash
pip install kivy-ios
```

2. Build dependencies:
```bash
toolchain build kivy
toolchain build cryptography
toolchain build python3
```

3. Create Xcode project:
```bash
toolchain create VaultNote /path/to/main.py
```

4. Open in Xcode and deploy to device

## Testing

Run the encryption test suite to verify functionality:

```bash
python test_encryption.py
```

Expected output:
- ✓ Encryption/Decryption successful
- ✓ Wrong password correctly rejected
- ✓ Document export/import encryption works

## Usage Guide

### First Launch
1. App opens to vault screen (no PIN set by default)
2. Click "Vault Settings" to set an optional vault PIN
3. If vault PIN is set, you'll see unlock screen on next launch

### Creating Documents
1. Enter title and content
2. Optionally enter a document PIN for extra protection
3. Click "Save" to encrypt and store

### Importing Files
1. Click "Import" button
2. Browse and select a file (TXT, PDF, or DOCX)
3. Content will be extracted and displayed
4. Add PIN if needed and click "Save"

### Exporting Documents
1. Select a document from the list
2. Click "Export" button
3. Enter an export PIN (will encrypt the file)
4. File saved with .venc extension

### Opening Protected Documents
- Documents with 🔒 symbol require PIN to open
- Enter document PIN when prompted
- Incorrect PIN will deny access

## Security Best Practices

1. **Use Strong PINs**: 6+ digits recommended
2. **Unique PINs**: Different PINs for vault and sensitive documents
3. **Backup Carefully**: Exported .venc files are encrypted but should be stored securely
4. **Remember PINs**: No recovery mechanism exists - lost PINs mean lost data
5. **Regular Exports**: Export important documents periodically

## File Storage Locations

### Android
- Default: `/storage/emulated/0/` (device storage)
- Vault data: App's internal storage directory
- Exports: Can be saved to any accessible directory

### iOS
- App sandbox directory
- Exports: App's Documents folder

## Limitations

- Cannot open/edit .venc files in other applications
- Document recovery requires correct PIN (no password reset)
- Import limited to text-extractable formats (PDF, DOCX, TXT)
- No cloud sync (by design - offline-first security)

## Privacy & Security

- **Zero Cloud Storage**: All data remains on device
- **No Network Requests**: App works completely offline
- **No Analytics**: No tracking or data collection
- **Open Encryption**: Uses proven cryptographic standards (AES-256-GCM)

## Troubleshooting

**Issue**: Cannot import PDF files
- Ensure PDF contains selectable text (not scanned images)

**Issue**: Export button not working
- Make sure a document is selected first

**Issue**: Forgot vault PIN
- Vault data cannot be recovered without PIN
- Delete vault_data.enc and vault_settings.json to reset (loses all data)

**Issue**: Forgot document PIN
- Document cannot be accessed without PIN
- No recovery mechanism available

## License

This is a personal encryption tool. Use responsibly and ensure you keep backups of important data.

## Disclaimer

This app provides strong encryption for local storage, but remember:
- Encryption is only as strong as your PIN
- Lost PINs mean lost data (no recovery)
- Physical device security is your responsibility
- Always maintain secure backups of critical information
