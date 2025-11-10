# ImaLink Core - FastAPI Service

Run imalink-core as HTTP service for language-agnostic access.

## Quick Start

### Local Development

```bash
# Install dependencies
uv pip install -e .
uv pip install fastapi uvicorn[standard]

# Run service
python -m service.main

# Or with uvicorn directly
uvicorn service.main:app --reload --port 8765
```

Service runs on: `http://localhost:8765`

### Docker

```bash
# Build image
docker build -f service/Dockerfile -t imalink-core-api .

# Run container
docker run -p 8765:8765 -v /path/to/photos:/photos imalink-core-api
```

## API Usage

### Process Image (Minimal PhotoEgg)

```bash
curl -X POST http://localhost:8765/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/photos/IMG_1234.jpg",
    "coldpreview_size": null
  }'
```

Returns PhotoEgg with **hotpreview only** (fastest):

```json
{
  "hothash": "abc123...",
  "hotpreview_base64": "/9j/4AAQSkZJRg...",
  "hotpreview_width": 150,
  "hotpreview_height": 150,
  "coldpreview_base64": null,
  "primary_filename": "IMG_1234.jpg",
  "width": 4000,
  "height": 3000,
  "taken_at": "2024-07-15T14:30:00Z",
  "camera_make": "Nikon",
  "gps_latitude": 59.9139,
  "has_gps": true
}
```

### Process Image (Full PhotoEgg)

```bash
curl -X POST http://localhost:8765/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/photos/IMG_1234.jpg",
    "coldpreview_size": 2560
  }'
```

Returns PhotoEgg with **hotpreview + coldpreview**:

```json
{
  "hothash": "abc123...",
  "hotpreview_base64": "/9j/4AAQSkZJRg...",
  "hotpreview_width": 150,
  "hotpreview_height": 150,
  "coldpreview_base64": "/9j/4AAQSkZJRg...",
  "coldpreview_width": 2560,
  "coldpreview_height": 1920,
  "primary_filename": "IMG_1234.jpg"
}
```

### Health Check

```bash
curl http://localhost:8765/health
```

## TypeScript/JavaScript Integration

```typescript
interface ProcessImageRequest {
  file_path: string;
  coldpreview_size?: number | null;
}

interface PhotoEgg {
  hothash: string;
  hotpreview_base64: string;
  hotpreview_width: number;
  hotpreview_height: number;
  coldpreview_base64?: string | null;
  coldpreview_width?: number | null;
  coldpreview_height?: number | null;
  primary_filename: string;
  width: number;
  height: number;
  taken_at?: string | null;
  camera_make?: string | null;
  gps_latitude?: number | null;
  has_gps: boolean;
}

async function processImage(filePath: string, coldpreviewSize?: number): Promise<PhotoEgg> {
  const response = await fetch('http://localhost:8765/v1/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_path: filePath,
      coldpreview_size: coldpreviewSize ?? null
    })
  });
  
  if (!response.ok) {
    throw new Error(`Processing failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Minimal PhotoEgg (hotpreview only)
const minimal = await processImage('/photos/IMG_1234.jpg');

// Full PhotoEgg (with coldpreview)
const full = await processImage('/photos/IMG_1234.jpg', 2560);
```

## Python Client

```python
import requests
from pathlib import Path

def process_image(file_path: Path, coldpreview_size: int | None = None) -> dict:
    response = requests.post(
        'http://localhost:8765/v1/process',
        json={
            'file_path': str(file_path),
            'coldpreview_size': coldpreview_size
        }
    )
    response.raise_for_status()
    return response.json()

# Minimal PhotoEgg
photo = process_image(Path('/photos/IMG_1234.jpg'))

# Full PhotoEgg
photo = process_image(Path('/photos/IMG_1234.jpg'), coldpreview_size=2560)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root - health check |
| `/v1/process` | POST | Process image and return PhotoEgg |
| `/health` | GET | Health check for monitoring |

## Configuration

- **Port**: 8765 (default)
- **Host**: 0.0.0.0 (all interfaces)
- **CORS**: Enabled for all origins (configure for production)

## Base64 Format

All image previews use Base64 encoding (industry standard for binary data in JSON):

- `hotpreview_base64`: Base64-encoded JPEG string (~5-15KB)
- `coldpreview_base64`: Base64-encoded JPEG string (~100-200KB) or null

To decode in Python:

```python
import base64
from io import BytesIO
from PIL import Image

# Decode Base64 to image
image_bytes = base64.b64decode(photo['hotpreview_base64'])
image = Image.open(BytesIO(image_bytes))
```

To decode in JavaScript:

```typescript
// Decode Base64 to Blob
const blob = await fetch(`data:image/jpeg;base64,${photo.hotpreview_base64}`).then(r => r.blob());
const url = URL.createObjectURL(blob);

// Or use directly in <img> tag
<img src={`data:image/jpeg;base64,${photo.hotpreview_base64}`} />
```

## Development

Run with auto-reload:

```bash
uvicorn service.main:app --reload --port 8765
```

Access interactive API docs:
- Swagger UI: http://localhost:8765/docs
- ReDoc: http://localhost:8765/redoc
