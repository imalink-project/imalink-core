# RAW File Support

imalink-core now supports RAW camera files (CR2, NEF, ARW, DNG, etc.) through the `rawpy` library.

## Installation

RAW support is optional. Install it with:

```bash
uv pip install rawpy
```

Or install imalink-core with RAW support:

```bash
uv pip install "imalink-core[raw]"
```

## Supported RAW Formats

- **NEF** - Nikon RAW
- **CR2** - Canon RAW
- **ARW** - Sony RAW
- **DNG** - Adobe Digital Negative (universal RAW)
- **ORF** - Olympus RAW
- **RW2** - Panasonic RAW
- **RAF** - Fujifilm RAW

## API Usage

**The API interface is identical for RAW and JPEG/PNG files** - no changes needed!

### Upload RAW File

```bash
# Same endpoint, same parameters
curl -X POST http://localhost:8765/v1/process \
  -F "file=@photo.NEF" \
  -F "coldpreview_size=2560"
```

### Response

RAW files return the same PhotoCreateSchema JSON as JPEG/PNG:

```json
{
  "hothash": "abc123...",
  "hotpreview_base64": "/9j/4AAQSkZJRg...",
  "coldpreview_base64": "/9j/4AAQSkZJRg...",
  "width": 6000,
  "height": 4000,
  "camera_make": "Nikon",
  "camera_model": "D850",
  "iso": 800,
  "aperture": 2.8,
  "taken_at": "2024-12-04T15:30:00Z"
}
```

## How It Works

1. **Detection**: Core detects RAW files by extension (NEF, CR2, etc.)
2. **Conversion**: `rawpy` converts RAW → RGB array
3. **Processing**: Converted image processed like any JPEG:
   - EXIF extraction
   - Preview generation (hot + cold)
   - Hothash calculation

**Zero API changes** - RAW support is completely transparent to clients.

## Architecture

```
RAW File Upload
    ↓
RawProcessor.is_raw_file(filename)
    ↓
RawProcessor.convert_raw_to_image(bytes)
    ↓
PIL Image (RGB)
    ↓
Normal Processing Pipeline
    ↓
PhotoCreateSchema JSON
```

## Error Handling

If `rawpy` is not installed:

```json
{
  "error": "RAW file support not installed. Install with: uv pip install rawpy"
}
```

If RAW file is corrupt:

```json
{
  "error": "Failed to process RAW file: LibRaw error: invalid file format"
}
```

## Testing

Test RAW support:

```bash
# Run RAW tests
uv run pytest tests/test_raw_processing.py -v

# Test with your own RAW file
curl -X POST http://localhost:8765/v1/process \
  -F "file=@/path/to/photo.NEF" \
  -F "coldpreview_size=2560"
```

## Performance

RAW processing is slower than JPEG (2-5x):

- **JPEG**: ~50-100ms
- **RAW**: ~200-500ms (depending on file size)

This is expected - RAW files contain unprocessed sensor data that must be:
1. Demosaiced (Bayer pattern → RGB)
2. White balanced
3. Color corrected
4. Tone mapped

## Camera Compatibility

RAW support uses LibRaw (via rawpy), which supports 900+ camera models.

Verified cameras:
- Nikon D850, D7500, Z6, Z7
- Canon 5D Mark IV, EOS R, EOS R5
- Sony A7R III, A7R IV, A9
- Fujifilm X-T3, X-T4
- Olympus OM-D E-M1
- Panasonic Lumix GH5

If your camera's RAW format works with Adobe Lightroom, it will work with imalink-core.

## EXIF Data

EXIF extraction works the same for RAW files:

- BasicMetadata: Camera make/model, dimensions, GPS, timestamp
- CameraSettings: ISO, aperture, shutter, focal length

RAW files often have **richer EXIF data** than JPEGs since they come directly from camera.

## Development

Add RAW test fixtures:

```bash
# Copy your camera's RAW file
cp ~/photos/test.NEF tests/fixtures/images/

# Run tests
uv run pytest tests/test_raw_processing.py::TestRawProcessor::test_convert_real_raw -v -s
```

## Production Deployment

Install rawpy on server:

```bash
ssh kjell@core.trollfjell.com
cd /home/kjell/imalink-core
uv pip install rawpy
sudo systemctl restart imalink-core
```

Check it's working:

```bash
curl -X POST https://core.trollfjell.com/v1/process \
  -F "file=@photo.NEF" \
  -F "coldpreview_size=2560"
```

## Limitations

1. **No lens correction**: RAW files processed without lens distortion correction
2. **Default color profile**: Uses sRGB color space (not Adobe RGB or ProPhoto)
3. **No custom processing**: Uses rawpy defaults (can't customize demosaic algorithm, etc.)

These limitations match the project's goal: **extract metadata and generate previews**, not replace Lightroom/Capture One.

## Future Enhancements

Potential improvements:
- Custom white balance adjustment
- Exposure compensation
- Lens correction profiles
- Multiple RAW processing profiles (quality vs speed)

Not planned (out of scope):
- Full RAW editing capabilities
- Custom color profiles
- Advanced noise reduction

## Questions?

See `tests/test_raw_processing.py` for examples and `src/imalink_core/image/raw_processor.py` for implementation.
