import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
import hashlib
import requests
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger()

class ImageAnalyzer:
    def __init__(self):
        pass
    
    def extract_exif_data(self, image_url: str) -> Dict[str, Any]:
        """Extract EXIF metadata from image"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(response.content)
            
            exif_data = {}
            if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
            
            # Additional metadata
            metadata = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'has_exif': bool(exif_data),
                'exif_data': exif_data
            }
            
            # Extract GPS if available
            gps_info = self._extract_gps_info(exif_data)
            if gps_info:
                metadata['gps_coordinates'] = gps_info
            
            return metadata
            
        except Exception as e:
            logger.error(f"EXIF extraction error: {e}")
            return {'error': str(e)}
    
    def analyze_image_properties(self, image_url: str) -> Dict[str, Any]:
        """Analyze image properties and detect modifications"""
        try:
            response = requests.get(image_url, timeout=10)
            image_data = response.content
            
            # Calculate hash
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Basic analysis
            analysis = {
                'file_size': len(image_data),
                'hash_md5': image_hash,
                'dimensions': image.size,
                'color_channels': len(image_array.shape),
                'bit_depth': image_array.dtype,
                'compression_artifacts': self._detect_compression_artifacts(image_array),
                'noise_level': self._calculate_noise_level(image_array)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {'error': str(e)}
    
    def reverse_image_search_hash(self, image_url: str) -> Dict[str, Any]:
        """Generate hashes for reverse image search"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to grayscale and resize
            gray = image.convert('L').resize((8, 8))
            pixels = list(gray.getdata())
            
            # Calculate average hash
            avg = sum(pixels) / len(pixels)
            hash_bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            
            # Difference hash
            dhash_bits = ''
            for i in range(8):
                for j in range(7):
                    idx1 = i * 8 + j
                    idx2 = i * 8 + j + 1
                    dhash_bits += '1' if pixels[idx1] > pixels[idx2] else '0'
            
            return {
                'average_hash': hash_bits,
                'difference_hash': dhash_bits,
                'hash_hex': hex(int(hash_bits, 2))[2:],
                'dhash_hex': hex(int(dhash_bits, 2))[2:]
            }
            
        except Exception as e:
            logger.error(f"Hash generation error: {e}")
            return {'error': str(e)}
    
    def _extract_gps_info(self, exif_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract GPS coordinates from EXIF data"""
        try:
            if 'GPSInfo' in exif_data:
                gps_info = exif_data['GPSInfo']
                
                def convert_to_degrees(value):
                    d, m, s = value
                    return d + (m / 60.0) + (s / 3600.0)
                
                lat = convert_to_degrees(gps_info.get('GPSLatitude', [0, 0, 0]))
                lon = convert_to_degrees(gps_info.get('GPSLongitude', [0, 0, 0]))
                
                if gps_info.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_info.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                return {'latitude': lat, 'longitude': lon}
        except:
            pass
        return {}
    
    def _detect_compression_artifacts(self, image_array: np.ndarray) -> float:
        """Detect JPEG compression artifacts"""
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Compression artifacts typically show as high frequency noise
            return float(np.std(magnitude))
            
        except Exception as e:
            logger.error(f"Compression detection error: {e}")
            return 0.0
    
    def _calculate_noise_level(self, image_array: np.ndarray) -> float:
        """Calculate noise level in image"""
        try:
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Use Laplacian to detect noise
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            noise_level = laplacian.var()
            
            return float(noise_level)
            
        except Exception as e:
            logger.error(f"Noise calculation error: {e}")
            return 0.0