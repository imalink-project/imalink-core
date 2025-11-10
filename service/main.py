"""
FastAPI service for imalink-core

Exposes image processing as HTTP API for language-agnostic access.
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from imalink_core.metadata.exif_extractor import ExifExtractor
from imalink_core.models.import_result import ImportResult
from imalink_core.models.photo import CorePhoto
from imalink_core.preview.generator import PreviewGenerator
from imalink_core.validation.image_validator import ImageValidator

# Initialize FastAPI app
app = FastAPI(
    title="ImaLink Core API",
    description="Image processing service - converts images to PhotoEgg JSON",
    version="1.0.0",
)

# CORS - allow backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ProcessImageRequest(BaseModel):
    """Request to process an image file"""
    file_path: str = Field(..., description="Absolute path to image file on disk")
    coldpreview_size: Optional[int] = Field(
        None, 
        description="Size for coldpreview (e.g., 2560). None = skip coldpreview. Must be >= 150.",
        ge=150
    )


class PhotoEggResponse(BaseModel):
    """PhotoEgg - complete image data in JSON format"""
    # Identity
    hothash: str
    
    # Hotpreview (always included) - Base64-encoded JPEG
    hotpreview_base64: str
    hotpreview_width: int
    hotpreview_height: int
    
    # Coldpreview (optional) - Base64-encoded JPEG
    coldpreview_base64: Optional[str] = None
    coldpreview_width: Optional[int] = None
    coldpreview_height: Optional[int] = None
    
    # File info
    primary_filename: str
    width: int
    height: int
    
    # Timestamps
    taken_at: Optional[str] = None
    
    # Camera metadata
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    
    # GPS
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    has_gps: bool
    
    # Camera settings
    iso: Optional[int] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    focal_length: Optional[float] = None
    lens_model: Optional[str] = None
    lens_make: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None


# API Endpoints
@app.get("/")
def root():
    """API root - health check"""
    return {
        "service": "ImaLink Core API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.post("/v1/process", response_model=PhotoEggResponse, responses={400: {"model": ErrorResponse}})
def process_image_endpoint(request: ProcessImageRequest):
    """
    Process image file and return PhotoEgg JSON.
    
    Core's single responsibility: (filepath, coldpreview_size) → PhotoEgg
    
    PhotoEgg always includes:
    - Hotpreview (150x150px thumbnail) as Base64
    - Complete EXIF metadata
    - Hothash (unique identifier)
    
    PhotoEgg optionally includes:
    - Coldpreview (larger preview) as Base64
    
    Args:
        request: ProcessImageRequest with file_path and optional coldpreview_size
        
    Returns:
        PhotoEggResponse: Complete image data in JSON format
        
    Raises:
        HTTPException 400: If file not found or processing fails
        HTTPException 422: If validation fails (e.g., coldpreview_size < 150)
    """
    # Validate coldpreview_size if provided
    if request.coldpreview_size is not None and request.coldpreview_size < 150:
        raise HTTPException(
            status_code=400,
            detail=f"coldpreview_size must be >= 150 (hotpreview size), got {request.coldpreview_size}"
        )
    
    # Validate file exists
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"File not found: {request.file_path}"
        )
    
    # Validate file
    is_valid, error = ImageValidator.validate_file(file_path)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    try:
        # Extract metadata
        metadata = ExifExtractor.extract_basic(file_path)
        camera_settings = ExifExtractor.extract_camera_settings(file_path)
        
        # Generate hotpreview (always required)
        hotpreview = PreviewGenerator.generate_hotpreview(file_path)
        
        # Generate coldpreview (optional)
        if request.coldpreview_size is not None:
            coldpreview = PreviewGenerator.generate_coldpreview(
                file_path,
                max_size=request.coldpreview_size
            )
            coldpreview_base64 = coldpreview.base64
            coldpreview_width = coldpreview.width
            coldpreview_height = coldpreview.height
        else:
            coldpreview_base64 = None
            coldpreview_width = None
            coldpreview_height = None
        
        # Build CorePhoto object
        photo = CorePhoto(
            hothash=hotpreview.hothash,
            hotpreview_base64=hotpreview.base64,
            hotpreview_width=hotpreview.width,
            hotpreview_height=hotpreview.height,
            coldpreview_base64=coldpreview_base64,
            coldpreview_width=coldpreview_width,
            coldpreview_height=coldpreview_height,
            primary_filename=file_path.name,
            taken_at=metadata.taken_at,
            width=metadata.width,
            height=metadata.height,
            camera_make=metadata.camera_make,
            camera_model=metadata.camera_model,
            gps_latitude=metadata.gps_latitude,
            gps_longitude=metadata.gps_longitude,
            has_gps=metadata.gps_latitude is not None,
            iso=camera_settings.iso,
            aperture=camera_settings.aperture,
            shutter_speed=camera_settings.shutter_speed,
            focal_length=camera_settings.focal_length,
            lens_model=camera_settings.lens_model,
            lens_make=camera_settings.lens_make,
        )
        
        # Convert CorePhoto to PhotoEgg JSON
        photo_dict = photo.to_dict()
        
        return PhotoEggResponse(**photo_dict)
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Processing failed: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
