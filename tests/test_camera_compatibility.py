"""
Camera Compatibility Test Suite

Tests EXIF extraction across different camera brands and models.
Add your own camera images to tests/fixtures/images/ to verify compatibility.
"""

import pytest
from pathlib import Path
from imalink_core.metadata.exif_extractor import ExifExtractor


class TestCameraCompatibility:
    """Test EXIF extraction from different camera brands"""
    
    @pytest.fixture
    def fixtures_dir(self):
        return Path(__file__).parent / "fixtures" / "images"
    
    def print_exif_report(self, camera_name: str, image_bytes: bytes):
        """Generate detailed EXIF extraction report"""
        print(f"\n{'='*70}")
        print(f"CAMERA: {camera_name}")
        print('='*70)
        
        # Extract all metadata
        basic = ExifExtractor.extract_basic_from_bytes(image_bytes)
        camera = ExifExtractor.extract_camera_settings_from_bytes(image_bytes)
        
        # Camera info
        print(f"\n📷 CAMERA INFO:")
        print(f"  Make: {basic.camera_make or '❌ MISSING'}")
        print(f"  Model: {basic.camera_model or '❌ MISSING'}")
        
        # Camera settings
        print(f"\n⚙️  CAMERA SETTINGS:")
        settings = {
            "ISO": camera.iso,
            "Aperture": f"f/{camera.aperture}" if camera.aperture else None,
            "Shutter": camera.shutter_speed,
            "Focal Length": f"{camera.focal_length}mm" if camera.focal_length else None,
            "Lens Model": camera.lens_model,
            "Lens Make": camera.lens_make,
            "Flash": camera.flash,
            "Exposure Program": camera.exposure_program,
            "Metering Mode": camera.metering_mode,
            "White Balance": camera.white_balance,
        }
        
        settings_found = 0
        for name, value in settings.items():
            status = "✅" if value else "❌"
            display_value = value if value else "MISSING"
            print(f"  {status} {name}: {display_value}")
            if value:
                settings_found += 1
        
        # GPS data
        print(f"\n🌍 GPS DATA:")
        gps_fields = {
            "Latitude": basic.gps_latitude,
            "Longitude": basic.gps_longitude,
            "Altitude": f"{basic.gps_altitude}m" if basic.gps_altitude else None,
            "Timestamp": basic.gps_timestamp,
            "Datestamp": basic.gps_datestamp,
            "Map Datum": basic.gps_map_datum,
        }
        
        gps_found = 0
        for name, value in gps_fields.items():
            status = "✅" if value else "❌"
            display_value = value if value else "MISSING"
            print(f"  {status} {name}: {display_value}")
            if value:
                gps_found += 1
        
        # Metadata quality
        print(f"\n📊 METADATA QUALITY:")
        print(f"  Dimensions: {basic.width}x{basic.height}")
        print(f"  Taken at: {basic.taken_at or '❌ MISSING'}")
        print(f"  Camera Settings: {settings_found}/10 fields")
        print(f"  GPS Data: {gps_found}/6 fields")
        
        total_fields = 2 + settings_found + gps_found  # camera_make + camera_model + settings + gps
        print(f"\n  ✅ TOTAL: {total_fields}/18 EXIF fields extracted")
        print('='*70)
        
        return {
            "camera_make": basic.camera_make,
            "camera_model": basic.camera_model,
            "settings_found": settings_found,
            "gps_found": gps_found,
            "total_fields": total_fields,
        }
    
    def test_sony_xperia(self, fixtures_dir):
        """Test Sony Xperia smartphone (XQ-BC52)"""
        # This test requires user to add their Sony image
        # Example path: tests/fixtures/images/sony_xperia.jpg
        image_path = fixtures_dir / "sony_xperia.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Sony image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Sony Xperia", image_bytes)
        
        # Assertions for Sony
        assert report["camera_make"] == "Sony", "Camera make should be Sony"
        assert report["settings_found"] >= 6, "Sony should have at least 6 camera settings"
    
    def test_nikon_dslr(self, fixtures_dir):
        """Test Nikon DSLR camera"""
        image_path = fixtures_dir / "nikon_dslr.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Nikon DSLR image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Nikon DSLR", image_bytes)
        
        # Assertions for Nikon DSLR
        assert report["camera_make"] and "Nikon" in report["camera_make"], "Should detect Nikon"
        assert report["settings_found"] >= 8, "DSLR should have comprehensive settings"
    
    def test_canon_dslr(self, fixtures_dir):
        """Test Canon DSLR camera"""
        image_path = fixtures_dir / "canon_dslr.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Canon DSLR image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Canon DSLR", image_bytes)
        
        # Assertions for Canon DSLR
        assert report["camera_make"] and "Canon" in report["camera_make"], "Should detect Canon"
        assert report["settings_found"] >= 8, "DSLR should have comprehensive settings"
    
    def test_fujifilm_camera(self, fixtures_dir):
        """Test Fujifilm camera"""
        # Test with existing Fuji fixture
        image_path = fixtures_dir / "fuji_full_exif.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Missing test fixture: {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Fujifilm FinePix E500", image_bytes)
        
        # Assertions for Fuji
        assert report["camera_make"] and "FUJIFILM" in report["camera_make"], "Should detect Fujifilm"
        assert report["camera_model"] is not None, "Should extract camera model"
    
    def test_iphone(self, fixtures_dir):
        """Test Apple iPhone"""
        image_path = fixtures_dir / "iphone.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add iPhone image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Apple iPhone", image_bytes)
        
        # Assertions for iPhone
        assert report["camera_make"] and "Apple" in report["camera_make"], "Should detect Apple"
        assert report["settings_found"] >= 5, "iPhone should have camera settings"
    
    def test_samsung_galaxy(self, fixtures_dir):
        """Test Samsung Galaxy smartphone"""
        image_path = fixtures_dir / "samsung_galaxy.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Samsung Galaxy image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Samsung Galaxy", image_bytes)
        
        # Assertions for Samsung
        assert report["camera_make"] and "samsung" in report["camera_make"].lower(), "Should detect Samsung"
        assert report["settings_found"] >= 5, "Samsung should have camera settings"
    
    def test_olympus_camera(self, fixtures_dir):
        """Test Olympus camera"""
        image_path = fixtures_dir / "olympus.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Olympus image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Olympus", image_bytes)
        
        # Assertions for Olympus
        assert report["camera_make"] and "OLYMPUS" in report["camera_make"].upper(), "Should detect Olympus"
    
    def test_panasonic_lumix(self, fixtures_dir):
        """Test Panasonic Lumix camera"""
        image_path = fixtures_dir / "panasonic_lumix.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add Panasonic Lumix image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        report = self.print_exif_report("Panasonic Lumix", image_bytes)
        
        # Assertions for Panasonic
        assert report["camera_make"] and "Panasonic" in report["camera_make"], "Should detect Panasonic"


class TestCustomImages:
    """
    Add your own camera images for testing
    
    Instructions:
    1. Copy image to: tests/fixtures/images/my_camera.jpg
    2. Update test name and camera description
    3. Run: pytest tests/test_camera_compatibility.py::TestCustomImages -v -s
    """
    
    @pytest.fixture
    def fixtures_dir(self):
        return Path(__file__).parent / "fixtures" / "images"
    
    def print_exif_report(self, camera_name: str, image_bytes: bytes):
        """Generate detailed EXIF extraction report"""
        print(f"\n{'='*70}")
        print(f"CAMERA: {camera_name}")
        print('='*70)
        
        # Extract all metadata
        basic = ExifExtractor.extract_basic_from_bytes(image_bytes)
        camera = ExifExtractor.extract_camera_settings_from_bytes(image_bytes)
        
        # Camera info
        print(f"\n📷 CAMERA INFO:")
        print(f"  Make: {basic.camera_make or '❌ MISSING'}")
        print(f"  Model: {basic.camera_model or '❌ MISSING'}")
        
        # Camera settings
        print(f"\n⚙️  CAMERA SETTINGS:")
        settings = {
            "ISO": camera.iso,
            "Aperture": f"f/{camera.aperture}" if camera.aperture else None,
            "Shutter": camera.shutter_speed,
            "Focal Length": f"{camera.focal_length}mm" if camera.focal_length else None,
            "Lens Model": camera.lens_model,
            "Lens Make": camera.lens_make,
            "Flash": camera.flash,
            "Exposure Program": camera.exposure_program,
            "Metering Mode": camera.metering_mode,
            "White Balance": camera.white_balance,
        }
        
        settings_found = 0
        for name, value in settings.items():
            status = "✅" if value else "❌"
            display_value = value if value else "MISSING"
            print(f"  {status} {name}: {display_value}")
            if value:
                settings_found += 1
        
        # GPS data
        print(f"\n🌍 GPS DATA:")
        gps_fields = {
            "Latitude": basic.gps_latitude,
            "Longitude": basic.gps_longitude,
            "Altitude": f"{basic.gps_altitude}m" if basic.gps_altitude else None,
            "Timestamp": basic.gps_timestamp,
            "Datestamp": basic.gps_datestamp,
            "Map Datum": basic.gps_map_datum,
        }
        
        gps_found = 0
        for name, value in gps_fields.items():
            status = "✅" if value else "❌"
            display_value = value if value else "MISSING"
            print(f"  {status} {name}: {display_value}")
            if value:
                gps_found += 1
        
        # Metadata quality
        print(f"\n📊 METADATA QUALITY:")
        print(f"  Dimensions: {basic.width}x{basic.height}")
        print(f"  Taken at: {basic.taken_at or '❌ MISSING'}")
        print(f"  Camera Settings: {settings_found}/10 fields")
        print(f"  GPS Data: {gps_found}/6 fields")
        
        total_fields = 2 + settings_found + gps_found
        print(f"\n  ✅ TOTAL: {total_fields}/18 EXIF fields extracted")
        print('='*70)
    
    def test_my_custom_camera(self, fixtures_dir):
        """
        Test your own camera image
        
        INSTRUCTIONS:
        1. Copy your image to: tests/fixtures/images/my_camera.jpg
        2. Run: pytest tests/test_camera_compatibility.py::TestCustomImages::test_my_custom_camera -v -s
        """
        image_path = fixtures_dir / "my_camera.jpg"
        
        if not image_path.exists():
            pytest.skip(f"Add your camera image to {image_path}")
        
        image_bytes = image_path.read_bytes()
        self.print_exif_report("My Custom Camera", image_bytes)
