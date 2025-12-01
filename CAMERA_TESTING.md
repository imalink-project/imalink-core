# Camera Compatibility Test Platform

Verify EXIF extraction from different camera brands and models.

## Quick Start

### Test Your Camera (30 seconds)

1. **Copy your image**:
   ```bash
   cp ~/my_photo.jpg tests/fixtures/images/my_camera.jpg
   ```

2. **Run the test**:
   ```bash
   uv run pytest tests/test_camera_compatibility.py::TestCustomImages::test_my_custom_camera -v -s
   ```

3. **Read the report** - you'll see exactly what EXIF data was extracted.

## Example Output

```
======================================================================
CAMERA: Sony Xperia
======================================================================

📷 CAMERA INFO:
  Make: Sony
  Model: XQ-BC52

⚙️  CAMERA SETTINGS:
  ✅ ISO: 800
  ✅ Aperture: f/1.7
  ✅ Shutter: 1/6
  ✅ Focal Length: 5.11mm
  ❌ Lens Model: MISSING
  ❌ Lens Make: MISSING
  ✅ Flash: No Flash
  ❌ Exposure Program: MISSING
  ✅ Metering Mode: Spot
  ✅ White Balance: Auto

🌍 GPS DATA:
  ✅ Latitude: 59.84655305555556
  ✅ Longitude: 10.459630277777777
  ✅ Altitude: 152.44m
  ✅ Timestamp: 12:03:02
  ✅ Datestamp: 2024:02:18
  ✅ Map Datum: WGS-84

📊 METADATA QUALITY:
  Dimensions: 4032x2688
  Taken at: 2024-02-18T13:03:13
  Camera Settings: 7/10 fields
  GPS Data: 6/6 fields

  ✅ TOTAL: 15/18 EXIF fields extracted
======================================================================
```

## Test All Cameras

Run compatibility tests for all supported camera brands:

```bash
# Test specific camera
uv run pytest tests/test_camera_compatibility.py::TestCameraCompatibility::test_sony_xperia -v -s
uv run pytest tests/test_camera_compatibility.py::TestCameraCompatibility::test_nikon_dslr -v -s
uv run pytest tests/test_camera_compatibility.py::TestCameraCompatibility::test_canon_dslr -v -s

# Test all cameras with images present
uv run pytest tests/test_camera_compatibility.py -v -s

# Test all (including skipped)
uv run pytest tests/test_camera_compatibility.py -v -s -k ""
```

## Supported Cameras

### Currently Verified ✅
- **Sony Xperia XQ-BC52** - 15/18 fields (smartphone)
- **Fujifilm FinePix E500** - 10/18 fields (compact camera)

### Ready for Testing 🔄
Add images for these cameras to `tests/fixtures/images/`:

**Smartphones**:
- `iphone.jpg` - Apple iPhone
- `samsung_galaxy.jpg` - Samsung Galaxy

**DSLR**:
- `nikon_dslr.jpg` - Nikon DSLR
- `canon_dslr.jpg` - Canon DSLR

**Mirrorless/Compact**:
- `olympus.jpg` - Olympus
- `panasonic_lumix.jpg` - Panasonic Lumix

## Expected Results

### Smartphones (Modern)
- **12-14/18 fields** expected
- Full GPS data (if location enabled)
- Basic camera settings (ISO, aperture, shutter)
- Often missing: lens info, exposure program

### DSLR Cameras
- **12-16/18 fields** expected
- Comprehensive camera settings
- Lens information (if available)
- GPS depends on GPS module

### Consumer/Compact Cameras
- **6-10/18 fields** expected
- Basic camera info
- Some camera settings
- Usually no GPS

## What Gets Tested

### Camera Info (2 fields)
- Camera make (Sony, Canon, Nikon, etc.)
- Camera model (XQ-BC52, EOS 5D, D850, etc.)

### Camera Settings (10 fields)
- ISO speed
- Aperture (f-stop)
- Shutter speed
- Focal length
- Lens model
- Lens make
- Flash status
- Exposure program
- Metering mode
- White balance

### GPS Data (6 fields)
- Latitude (decimal degrees)
- Longitude (decimal degrees)
- Altitude (meters)
- GPS timestamp
- GPS datestamp
- Map datum (WGS-84, etc.)

## Troubleshooting

### Low Extraction Rate?

If your camera shows fewer fields than expected:

1. **Check EXIF data exists**:
   ```bash
   exiftool tests/fixtures/images/my_camera.jpg | grep -i "ISO\|Aperture\|Shutter\|GPS"
   ```

2. **Report the issue** on GitHub with:
   - Camera make/model
   - EXIF report output
   - Sample image (with personal data removed)

### Privacy Note

Remove GPS/personal data from test images:
```bash
exiftool -gps:all= -overwrite_original my_camera.jpg
```

## Contributing

Found a camera that doesn't extract properly? 

1. Add test image to `tests/fixtures/images/`
2. Run compatibility test
3. Report results (GitHub issue or PR)
4. We'll improve EXIF extraction for that camera model

## Architecture

The test platform verifies:
- **BasicMetadata extraction** (camera info, GPS)
- **CameraSettings extraction** (technical settings)
- **EXIF IFD support** (modern smartphones)
- **Cross-camera compatibility** (different EXIF formats)

This ensures imalink-core works with **all camera types**, not just a few.
