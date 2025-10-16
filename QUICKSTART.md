# VaultNote - Quick Start Guide

## 🚀 Get Your APK in 3 Ways

### ⚡ Option 1: Download & Build Locally (30-60 min first time)

**On Linux/Mac:**
```bash
# Download this project
# Navigate to project folder
pip3 install buildozer cython
buildozer android debug

# Your APK will be in: bin/vaultnote-1.0-debug.apk
```

**Full instructions**: See `BUILD_INSTRUCTIONS.md`

---

### ☁️ Option 2: Automated Build with GitHub (Easiest!)

1. **Push this code to GitHub**
2. **GitHub Actions will automatically build the APK** 
3. **Download APK from "Actions" tab** → Latest workflow → "Artifacts"

The workflow is already configured in `.github/workflows/build-apk.yml`

**On every push, you get a fresh APK automatically!**

---

### 🔧 Option 3: Manual Android Studio Build

1. Export as Android Studio project
2. Build using Gradle
3. Advanced users only

---

## 📱 Install APK on Your Phone

1. Copy `vaultnote-1.0-debug.apk` to your Android device
2. Open file manager, tap the APK
3. Enable "Install from Unknown Sources" if prompted
4. Install and launch VaultNote!

**Minimum requirement**: Android 5.0 (API 21) or higher

---

## 🔒 What You Get

✅ **Fully encrypted document vault**
- AES-256-GCM encryption (military-grade)
- Optional vault PIN protection  
- Optional per-document PINs
- Completely offline - no cloud, no internet

✅ **File support**
- Import: TXT, PDF, DOCX files
- Export: Encrypted .venc format (only VaultNote can open)

✅ **100% Privacy**
- All data stays on your device
- No tracking, no analytics
- No recovery mechanism (secure by design)

---

## 🧪 Already Tested & Working

All encryption and security features pass comprehensive tests:
- ✅ AES-256-GCM encryption
- ✅ Device key generation
- ✅ Vault PIN protection
- ✅ Document PIN protection
- ✅ Password re-encryption
- ✅ Wrong password rejection
- ✅ File import/export encryption

Run tests: `python test_encryption.py`

---

## 📦 What's Included

```
VaultNote/
├── main.py                    # Main application
├── test_encryption.py         # Security tests
├── buildozer.spec            # Android build config
├── BUILD_INSTRUCTIONS.md     # Detailed build guide
├── README.md                 # Full documentation
├── .github/workflows/        # Auto-build setup
└── replit.md                 # Development notes
```

---

## 🎯 Next Steps

**For Testing:**
1. Build APK (pick option 1 or 2 above)
2. Install on Android device
3. Create encrypted documents
4. Test import/export features

**For Production:**
1. Create release APK (see BUILD_INSTRUCTIONS.md)
2. Sign with your keystore
3. Optimize with zipalign
4. Distribute or publish to Play Store

---

## 💡 Tips

- **First build slow?** Android SDK/NDK downloads ~2GB
- **Want updates?** Use GitHub Actions - every push = new APK
- **Building fails?** Check BUILD_INSTRUCTIONS.md troubleshooting
- **Security questions?** All code is open - audit the encryption in main.py

---

## ⚠️ Important Security Notes

**Debug APK (testing only):**
- Not optimized for production
- Larger file size
- Contains debug symbols

**For production:**
- Use release build
- Sign with your keystore  
- Test thoroughly
- Store keystore password securely

---

## 🆘 Support

**Build issues:** See `BUILD_INSTRUCTIONS.md`  
**Encryption logic:** Review `test_encryption.py`  
**App features:** Read `README.md`

**Framework docs:**
- Buildozer: https://buildozer.readthedocs.io/
- Kivy: https://kivy.org/doc/stable/
- Cryptography: https://cryptography.io/
