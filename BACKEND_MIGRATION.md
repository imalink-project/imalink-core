# Backend Migration: PhotoCreateSchema API Integration

## Context

imalink-core tilbyr én enkelt funksjon: konvertere en fysisk bildefil til PhotoCreateSchema JSON med klart definert skjema. Backend må støtte PhotoCreateSchema-formatet.

## Nåværende imalink-core API

```python
from pathlib import Path
from imalink_core import process_image

# Minimal response (hotpreview only, default - fastest)
result = process_image(Path("photo.jpg"))

# Full response with coldpreview (specify size)
result = process_image(Path("photo.jpg"), coldpreview_size=2560)

if result.success:
    photo_data = result.photo.to_dict()  # CorePhoto → PhotoCreateSchema JSON
    # Send to backend
```

**Core's single responsibility**: `(filepath, coldpreview_size) → PhotoCreateSchema JSON`

## PhotoCreateSchema Structure (CorePhoto.to_dict())

**CRITICAL: All image data uses Base64 encoding**
- Base64 is the industry standard for binary data in JSON
- JSON cannot contain raw bytes - only text
- `hotpreview_base64` and `coldpreview_base64` are strings, not bytes

```python
{
    # Identity
    "hothash": "abc123...",  # SHA256 hash (unique ID)
    
    # Hotpreview (150x150px, ~5-15KB) - ALWAYS INCLUDED
    # Base64-encoded JPEG string (NOT raw bytes)
    "hotpreview_base64": "/9j/4AAQ...",  # Base64 string
    "hotpreview_width": 150,
    "hotpreview_height": 113,
    
    # Coldpreview (variable size, ~100-200KB) - OPTIONAL
    # Base64-encoded JPEG string (NOT raw bytes)
    "coldpreview_base64": "/9j/4AAQ..." | null,  # Base64 string or null
    "coldpreview_width": 2560 | null,  # Example size
    "coldpreview_height": 1920 | null,  # Example size
    
    # File info
    "primary_filename": "IMG_1234.jpg",
    "width": 4032,
    "height": 3024,
    
    # Timestamps
    "taken_at": "2024-11-10T14:30:00" | null,
    "first_imported": null,  # Backend sets
    "last_imported": null,   # Backend sets
    
    # Camera metadata (98% reliable)
    "camera_make": "Canon" | null,
    "camera_model": "EOS R5" | null,
    
    # GPS (if available)
    "gps_latitude": 59.9139 | null,
    "gps_longitude": 10.7522 | null,
    "has_gps": true | false,
    
    # Camera settings (70-90% reliable)
    "iso": 400 | null,
    "aperture": 2.8 | null,
    "shutter_speed": "1/1000" | null,
    "focal_length": 85.0 | null,
    "lens_model": "RF 85mm F2" | null,
    "lens_make": "Canon" | null,
    
    # Organization (backend sets)
    "rating": null,
    "import_session_id": null,
    "has_raw_companion": false,
    
    # Backend fields
    "id": null,      # Database ID (backend sets)
    "user_id": null  # Owner (backend sets)
}
```

**Key points**:
- Hotpreview: ALWAYS present
- Coldpreview: OPTIONAL (can be null)
- EXIF fields: Often null (missing EXIF is normal)

## Task 1: Create endpoint POST /api/v1/photos

**Input**: PhotoCreateSchema (CorePhoto.to_dict())  
**Output**: Saved Photo with backend-ID

```python
@router.post("/api/v1/photos")
async def create_photo_from_schema(
    photo_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    New endpoint that receives PhotoCreateSchema directly from imalink-core.
    
    Advantages:
    - Simpler: just send result.photo.to_dict()
    - Complete: all EXIF data included
    - Flexible: coldpreview is optional
    """
    # 1. Validate PhotoCreateSchema
    if not photo_data.get("hothash"):
        raise HTTPException(400, "Missing hothash")
    
    # 2. Sjekk om photo finnes (duplicate detection)
    existing = await db.get_photo_by_hothash(
        photo_data["hothash"], 
        current_user.id
    )
    if existing:
        return existing  # Already imported
    
    # 3. Lagre hotpreview (alltid present)
    # Store in DB eller blob storage
    
    # 4. Lagre coldpreview (hvis present)
    if photo_data.get("coldpreview_base64"):
        # Store på disk/S3/cache eller skip
        pass
    
    # 5. Opprett Photo i database
    db_photo = Photo(
        hothash=photo_data["hothash"],
        user_id=current_user.id,
        primary_filename=photo_data["primary_filename"],
        taken_at=photo_data.get("taken_at"),
        width=photo_data["width"],
        height=photo_data["height"],
        camera_make=photo_data.get("camera_make"),
        camera_model=photo_data.get("camera_model"),
        gps_latitude=photo_data.get("gps_latitude"),
        gps_longitude=photo_data.get("gps_longitude"),
        has_gps=photo_data.get("has_gps", False),
        iso=photo_data.get("iso"),
        aperture=photo_data.get("aperture"),
        shutter_speed=photo_data.get("shutter_speed"),
        focal_length=photo_data.get("focal_length"),
        lens_model=photo_data.get("lens_model"),
        lens_make=photo_data.get("lens_make"),
        # Backend legger til:
        first_imported=datetime.utcnow(),
        last_imported=datetime.utcnow(),
    )
    await db.save(db_photo)
    
    return db_photo
```

## Oppgave 2: Coldpreview Storage Strategy

**Velg én av disse strategiene:**

### A. Lagre i database (enklest, men stor database)
```python
photo.coldpreview_base64 = photo_data.get("coldpreview_base64")
```
- ✅ Enklest å implementere
- ❌ Database blir stor (~200KB per foto)

### B. Lagre på disk (balansert)
```python
if photo_data.get("coldpreview_base64"):
    coldpreview_path = f"storage/coldpreviews/{photo_data['hothash']}.jpg"
    save_base64_to_file(coldpreview_path, photo_data["coldpreview_base64"])
    photo.coldpreview_path = coldpreview_path  # Lagre path i DB
```
- ✅ Database forblir liten
- ✅ Rask tilgang
- ❌ Krever disk space management

### C. Lagre i S3/blob storage (produksjonsklart)
```python
if photo_data.get("coldpreview_base64"):
    s3_key = f"coldpreviews/{photo_data['hothash']}.jpg"
    await s3.upload_base64(s3_key, photo_data["coldpreview_base64"])
    photo.coldpreview_s3_key = s3_key
```
- ✅ Skalerbart
- ✅ CDN-klart
- ❌ Krever S3/blob setup

### D. Skip coldpreview (regenerer on-demand)
```python
# Ikke lagre coldpreview
# Frontend kan regenerere ved behov fra original fil
```
- ✅ Minst lagring
- ❌ Krever tilgang til original fil

**Anbefaling**: Start med **B (disk)**, migrer til **C (S3)** senere.

## Oppgave 3: Bakoverkompatibilitet

**Behold eksisterende endpoints**:
- `POST /api/v1/photos` (gammelt skjema)
- `PUT /api/v1/photos/{id}` (gammelt skjema)

Legg til deprecation warning:
```python
@router.post("/api/v1/photos")
async def create_photo_legacy(...):
    # Gammelt endpoint
    response.headers["X-API-Deprecation"] = "Use /api/v1/photos"
    response.headers["X-API-Sunset"] = "2026-01-01"
    # ... existing logic
```

## Oppgave 4: Pydantic Schema (anbefalt)

```python
from pydantic import BaseModel, Field
from typing import Optional

class PhotoCreateSchema(BaseModel):
    """
    Schema for PhotoCreateSchema (imalink-core output)
    
    CRITICAL: Image fields use Base64 encoding
    - hotpreview_base64: Base64-encoded JPEG string (NOT bytes)
    - coldpreview_base64: Base64-encoded JPEG string or null (NOT bytes)
    - This is the industry standard for binary data in JSON
    """
    
    # Identity (required)
    hothash: str = Field(..., min_length=64, max_length=64)
    
    # Hotpreview (required) - Base64 string
    hotpreview_base64: str  # Base64-encoded JPEG
    hotpreview_width: int = Field(..., gt=0)
    hotpreview_height: int = Field(..., gt=0)
    
    # Coldpreview (optional) - Base64 string or null
    coldpreview_base64: Optional[str] = None  # Base64-encoded JPEG or null
    coldpreview_width: Optional[int] = None
    coldpreview_height: Optional[int] = None
    
    # File info (required)
    primary_filename: str
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    
    # Metadata (optional)
    taken_at: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    
    # GPS (optional)
    gps_latitude: Optional[float] = Field(None, ge=-90, le=90)
    gps_longitude: Optional[float] = Field(None, ge=-180, le=180)
    has_gps: bool = False
    
    # Camera settings (optional)
    iso: Optional[int] = Field(None, gt=0)
    aperture: Optional[float] = Field(None, gt=0)
    shutter_speed: Optional[str] = None
    focal_length: Optional[float] = Field(None, gt=0)
    lens_model: Optional[str] = None
    lens_make: Optional[str] = None
```

Bruk i endpoint:
```python
@router.post("/api/v1/photos")
async def create_photo_from_schema(
    photo_data: PhotoCreateSchema,  # Type-safe validation
    current_user: User = Depends(get_current_user)
):
    # photo_data er nå validert og type-safe
    pass
```

## Migrasjonsstrategi (Inkrementell)

### Fase 1: Nytt endpoint (INGEN breaking changes)
```
✓ POST /api/v1/photos (ny - støtter PhotoCreateSchema)
✓ POST /api/v1/photos/legacy (gammel - fortsatt fungerer)
```

### Fase 2: Oppdater Qt-frontend
```python
# Qt-frontend kode
result = process_image(file_path)
if result.success:
    response = await api.post(
        "/api/v1/photos",
        result.photo.to_dict()
    )
```

### Fase 3: Deprecate gammelt endpoint
```python
# Legg til deprecation warnings
# Sett sunset date: 2026-01-01
```

### Fase 4: Fjern gammelt endpoint
```python
# Når alle klienter er migrert (6+ måneder)
# DELETE /api/v1/photos (gammelt endpoint)
```

## Testing Checklist

Test at PhotoCreateSchema endpoint håndterer:

- [ ] Komplett PhotoCreateSchema (med coldpreview)
- [ ] PhotoCreateSchema uten coldpreview (coldpreview_base64=null)
- [ ] PhotoCreateSchema med GPS
- [ ] PhotoCreateSchema uten GPS
- [ ] PhotoCreateSchema med kamerainnstillinger
- [ ] PhotoCreateSchema uten kamerainnstillinger (null values OK)
- [ ] Duplicate detection (samme hothash)
- [ ] Invalid hothash (feil lengde, format)
- [ ] Missing required fields
- [ ] Invalid GPS coordinates (out of range)

## Spørsmål å besvare

1. **Coldpreview storage**: Database, Disk, S3, eller Skip?
2. **Deprecation timeline**: Hvor lenge skal gammelt endpoint støttes?
3. **Validation**: Strict (reject invalid) eller lenient (accept missing)?
4. **Schema**: Bruke Pydantic eller plain dict?

## Eksempel Test Data

```python
# Komplett PhotoCreateSchema
complete_data = {
    "hothash": "abc123" * 10 + "abcd",  # 64 chars
    "hotpreview_base64": "...",
    "hotpreview_width": 150,
    "hotpreview_height": 113,
    "coldpreview_base64": "...",
    "coldpreview_width": 2560,
    "coldpreview_height": 1920,
    "primary_filename": "IMG_1234.jpg",
    "width": 4032,
    "height": 3024,
    "taken_at": "2024-11-10T14:30:00",
    "camera_make": "Canon",
    "camera_model": "EOS R5",
    "gps_latitude": 59.9139,
    "gps_longitude": 10.7522,
    "has_gps": True,
    "iso": 400,
    "aperture": 2.8,
    "shutter_speed": "1/1000",
    "focal_length": 85.0,
    "lens_model": "RF 85mm F2",
    "lens_make": "Canon",
}

# Minimal PhotoCreateSchema (kun påkrevde felter)
minimal_data = {
    "hothash": "xyz789" * 10 + "wxyz",
    "hotpreview_base64": "...",
    "hotpreview_width": 150,
    "hotpreview_height": 100,
    "coldpreview_base64": None,  # Skipped
    "primary_filename": "photo.jpg",
    "width": 800,
    "height": 600,
    "taken_at": None,
    "has_gps": False,
}
```

## Viktige Notater

**PhotoCreateSchema er IKKE en erstatning for hele backend Photo-modellen.**

Backend legger til:
- `user_id` (eierskap)
- `id` (database ID)
- `rating`, `tags`, `albums` (brukerorganisering)
- `import_session_id` (tracking)
- `first_imported`, `last_imported` (timestamps)

**PhotoCreateSchema = rådata fra bildefil**  
**Backend Photo = PhotoCreateSchema + brukerdata + organisering**

## Neste Steg

1. [ ] Implementer `POST /api/v1/photos` endpoint
2. [ ] Velg coldpreview storage strategy
3. [ ] Lag Pydantic schema for PhotoCreateSchema
4. [ ] Skriv tester for nytt endpoint
5. [ ] Test med ekte PhotoCreateSchema data fra imalink-core
6. [ ] Oppdater Qt-frontend til å bruke nytt endpoint
7. [ ] Deprecate gammelt endpoint (6+ måneders varsel)
