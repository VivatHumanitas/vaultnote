# VaultNote - Android APK Build Instructions

## Prerequisites

**Linux or macOS** (Windows users: use WSL2 or a Linux VM)

Install requirements:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip git zip unzip openjdk-17-jdk \
    build-essential libssl-dev libffi-dev python3-dev \
    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
    libreadline-dev libsqlite3-dev wget libbz2-dev

# Install Buildozer
pip3 install --user buildozer cython
```

## Build Steps

### 1. Clone/Download this project
```bash
cd /path/to/vaultnote
```

### 2. Build the APK
```bash
buildozer android debug
```

**First build takes 30-60 minutes** as it downloads:
- Android SDK (~500MB)
- Android NDK (~1GB)
- Python-for-Android (~200MB)
- Builds all dependencies

### 3. Find your APK
```bash
ls -lh bin/vaultnote-*.apk
```

The APK will be at: `bin/vaultnote-1.0-debug.apk`

### 4. Install on Android Device

**Option A: USB Connection**
```bash
# Enable USB debugging on your Android device
adb install bin/vaultnote-1.0-debug.apk
```

**Option B: Manual Install**
1. Copy APK to your phone
2. Open file manager, tap the APK
3. Allow "Install from Unknown Sources" if prompted
4. Install and open VaultNote!

## Build Configuration

The `buildozer.spec` file contains all settings:
- **Package name**: `org.vaultnote.vaultnote`
- **Permissions**: Storage read/write (for file import/export)
- **Orientation**: Portrait
- **Android API**: 31 (Android 12+)
- **Minimum API**: 21 (Android 5.0+)

## Troubleshooting

### Build fails with "SDK not found"
```bash
buildozer android clean
buildozer android debug
```

### Missing dependencies error
```bash
# Install the missing package, then rebuild
sudo apt-get install [package-name]
buildozer android debug
```

### "Permission Denied" errors
```bash
chmod +x ~/.buildozer/android/platform/android-ndk-*/build/tools/make_standalone_toolchain.py
```

### APK won't install on device
- Check Android version (need 5.0+)
- Enable "Install from Unknown Sources"
- Uninstall old version first if updating

## Release Build (For Production)

### 1. Generate signing key
```bash
keytool -genkey -v -keystore vaultnote.keystore \
    -alias vaultnote -keyalg RSA -keysize 2048 -validity 10000
```

### 2. Edit buildozer.spec
```ini
[app]
android.release_artifact = apk
```

### 3. Build release APK
```bash
buildozer android release
```

### 4. Sign the APK
```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore vaultnote.keystore \
    bin/vaultnote-1.0-release-unsigned.apk vaultnote
```

### 5. Optimize (zipalign)
```bash
zipalign -v 4 bin/vaultnote-1.0-release-unsigned.apk \
    bin/vaultnote-1.0-release.apk
```

## File Size Expectations

- **First build cache**: ~2GB (SDK + NDK)
- **APK size**: ~30-40MB (debug), ~15-25MB (release optimized)

## Alternative: Cloud Build Services

If you can't build locally, use:
- **GitHub Actions** (free for public repos)
- **GitLab CI/CD** (free tier available)
- **CircleCI** (free tier available)

See `GITHUB_ACTIONS.md` for automated build setup.

## Support

For build issues:
- Buildozer docs: https://buildozer.readthedocs.io/
- Python-for-Android: https://python-for-android.readthedocs.io/
- Kivy docs: https://kivy.org/doc/stable/

## Security Note

The debug APK is for testing only. For production:
1. Use release build with signing
2. Don't share your keystore file
3. Store keystore password securely
4. Test thoroughly before distributing
