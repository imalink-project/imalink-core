# Camera Compatibility Testing

This directory contains test images from different camera brands to verify EXIF extraction.

## Supported Camera Brands

Tests exist for the following camera brands. Add your images to verify compatibility:

### Smartphones
- **Sony Xperia** - `sony_xperia.jpg` (XQ-BC52 verified ✅)
- **Apple iPhone** - `iphone.jpg`
- **Samsung Galaxy** - `samsung_galaxy.jpg`

### DSLR Cameras
- **Nikon** - `nikon_dslr.jpg`
- **Canon** - `canon_dslr.jpg`
- **Fujifilm** - `fuji_full_exif.jpg` (FinePix E500 ✅)

### Mirrorless/Compact
- **Olympus** - `olympus.jpg`
- **Panasonic Lumix** - `panasonic_lumix.jpg`

## How to Test Your Camera

1. **Copy your image** to this directory with an appropriate name:
   ```bash
   cp ~/my_photo.jpg tests/fixtures/images/my_camera.jpg
   ```

2. **Run the custom test**:
   ```bash
   cd /home/kjell/imalink-core
   uv run pytest tests/test_camera_compatibility.py::TestCustomImages::test_my_custom_camera -v -s
   ```

3. **Review the EXIF report** to see what data was extracted:
   - Camera info (make, model)
   - Camera settings (ISO, aperture, shutter, focal length, etc.)
   - GPS data (coordinates, altitude, timestamp)
   - Metadata quality score (X/18 fields)

## Expected Results

### Smartphones (Modern)
- **Expected**: 12-14/18 fields
- Camera info: ✅ Make, ✅ Model
- Settings: 6-8 fields (ISO, aperture, shutter, focal, flash, metering, WB)
- GPS: 0-6 fields (depends on location services)

### DSLR Cameras
- **Expected**: 12-16/18 fields
- Camera info: ✅ Make, ✅ Model
- Settings: 8-10 fields (full camera control)
- GPS: 0-6 fields (depends on GPS module)

### Consumer/Compact Cameras
- **Expected**: 6-10/18 fields
- Camera info: ✅ Make, ✅ Model
- Settings: 4-8 fields (basic settings)
- GPS: Usually 0 fields (no GPS)

## Known Issues

Some cameras store EXIF data in non-standard locations. If your camera shows low extraction rates, please:

1. **Report the issue** with camera make/model
2. **Share a sample image** (with GPS/personal data removed if needed)
3. **Include the EXIF report output** from the test

## Privacy Note

Test images should ideally:
- Not contain sensitive GPS locations (or remove GPS data)
- Not contain personal identifying information
- Be small file size (<5MB) for fast testing
