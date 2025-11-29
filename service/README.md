# ImaLink Core - FastAPI Service

Image processing HTTP service. Upload image → get photo data JSON.

## Quick Start

```bash
# Install
pip install -e .

# Start service
python -m service.main
```

Service runs on: `http://localhost:8765`

## API: POST /v1/process

**Upload image file (multipart/form-data)**

### curl Examples

```bash
# Minimal response (hotpreview only)
curl -X POST http://localhost:8765/v1/process \
  -F "file=@photo.jpg"

# Full response (with coldpreview)
curl -X POST http://localhost:8765/v1/process \
  -F "file=@photo.jpg" \
  -F "coldpreview_size=2560"
```

### Response (PhotoCreateSchema JSON)

```json
{
  "hothash": "abc123...",
  "hotpreview_base64": "/9j/4AAQSkZJRg...",
  "hotpreview_width": 150,
  "hotpreview_height": 150,
  "coldpreview_base64": null,
  "primary_filename": "photo.jpg",
  "width": 4000,
  "height": 3000,
  "taken_at": "2024-07-15T14:30:00Z",
  "camera_make": "Nikon",
  "gps_latitude": 59.9139,
  "has_gps": true
}
```

## Integration Examples

### TypeScript/JavaScript (Browser)

```typescript
// HTML: <input type="file" id="fileInput">

const fileInput = document.getElementById('fileInput') as HTMLInputElement;
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);
formData.append('coldpreview_size', '2560');  // optional

const response = await fetch('http://localhost:8765/v1/process', {
  method: 'POST',
  body: formData
});

const photoData = await response.json();
console.log('Hothash:', photoData.hothash);
```

### TypeScript/JavaScript (Node.js)

```typescript
import fs from 'fs';
import FormData from 'form-data';

const formData = new FormData();
formData.append('file', fs.createReadStream('/photos/IMG_1234.jpg'));
formData.append('coldpreview_size', '2560');

const response = await fetch('http://localhost:8765/v1/process', {
  method: 'POST',
  body: formData
});

const photoData = await response.json();
```

### Python

```python
import requests

with open('/photos/IMG_1234.jpg', 'rb') as f:
    files = {'file': f}
    data = {'coldpreview_size': 2560}
    
    response = requests.post(
        'http://localhost:8765/v1/process',
        files=files,
        data=data
    )
    
photo_data = response.json()
print(f"Hothash: {photo_data['hothash']}")
```

### Electron/Tauri (Desktop App)

```typescript
// User selects file
const filePath = await open({
  filters: [{
    name: 'Images',
    extensions: ['jpg', 'jpeg', 'png']
  }]
});

// Read file
const fileBuffer = await readBinaryFile(filePath);
const blob = new Blob([fileBuffer]);
const file = new File([blob], 'photo.jpg');

// Upload to local core service
const formData = new FormData();
formData.append('file', file);

const response = await fetch('http://localhost:8765/v1/process', {
  method: 'POST',
  body: formData
});

const photoData = await response.json();

// Send photo data to remote backend
await fetch('https://backend.com/api/photos', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(photoData)
});
```

## API Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Image file (JPEG, PNG, etc.) |
| `coldpreview_size` | int | No | Size for coldpreview (e.g., 2560). Omit for minimal response. Must be >= 150. |

## Response Fields (PhotoCreateSchema)

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `hothash` | string | ✅ | SHA256 hash of hotpreview (unique ID) |
| `hotpreview_base64` | string | ✅ | 150x150 thumbnail (Base64 JPEG) |
| `hotpreview_width` | int | ✅ | Hotpreview width (usually 150) |
| `hotpreview_height` | int | ✅ | Hotpreview height (usually 150) |
| `coldpreview_base64` | string/null | ✅ | Larger preview (Base64 JPEG) or null |
| `coldpreview_width` | int/null | ✅ | Coldpreview width or null |
| `coldpreview_height` | int/null | ✅ | Coldpreview height or null |
| `primary_filename` | string | ✅ | Original filename |
| `width` | int | ✅ | Original image width |
| `height` | int | ✅ | Original image height |
| `taken_at` | string/null | ✅ | ISO 8601 timestamp from EXIF |
| `camera_make` | string/null | ✅ | Camera manufacturer |
| `camera_model` | string/null | ✅ | Camera model |
| `gps_latitude` | float/null | ✅ | GPS latitude |
| `gps_longitude` | float/null | ✅ | GPS longitude |
| `has_gps` | boolean | ✅ | Whether GPS data exists |
| `iso` | int/null | ✅ | ISO speed |
| `aperture` | float/null | ✅ | Aperture (f-stop) |
| `shutter_speed` | string/null | ✅ | Shutter speed |
| `focal_length` | float/null | ✅ | Focal length (mm) |
| `lens_model` | string/null | ✅ | Lens model |
| `lens_make` | string/null | ✅ | Lens manufacturer |

## Docker Deployment

```bash
# Build
docker build -f service/Dockerfile -t imalink-core:latest .

# Run
docker run -p 8765:8765 imalink-core:latest
```

## Interactive API Docs

When service is running:
- Swagger UI: http://localhost:8765/docs
- ReDoc: http://localhost:8765/redoc
