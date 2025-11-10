"""
ImaLink Core - Image processing service for ImaLink ecosystem

This service provides HTTP API for:
- EXIF metadata extraction
- Preview generation (hotpreview 150x150, coldpreview variable size)
- Hothash calculation (SHA256)
- Image validation
- RAW format support (optional)

Run the service:
    >>> uv run python -m service.main
    
API endpoint:
    POST http://localhost:8765/v1/process
    {
      "file_path": "/photos/IMG_1234.jpg",
      "coldpreview_size": null
    }
"""

from .version import __version__

# Metadata extraction
from .metadata import BasicMetadata, CameraSettings, ExifExtractor

# Preview generation
from .preview import ColdPreview, HotPreview, HothashCalculator, PreviewGenerator

# Image processing
from .image import FormatDetector, ImageFormat

# Models
from .models import CoreImageFile, ImportResult, CorePhoto, PhotoFormat

# Validation
from .validation import ImageValidator

__all__ = [
    # Version
    "__version__",
    # Metadata
    "ExifExtractor",
    "BasicMetadata",
    "CameraSettings",
    # Preview
    "PreviewGenerator",
    "HotPreview",
    "ColdPreview",
    "HothashCalculator",
    # Image
    "ImageFormat",
    "FormatDetector",
    # Models
    "CorePhoto",
    "CoreImageFile",
    "PhotoFormat",
    "ImportResult",
    # Validation
    "ImageValidator",
]
