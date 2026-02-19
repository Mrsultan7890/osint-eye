"""
Digital Forensics - Metadata Extractor
Extracts EXIF, file metadata, and hidden information
"""
import os
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
import json
import struct

class MetadataExtractor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.mp4', '.avi']
    
    def extract_file_metadata(self, file_path):
        """Extract comprehensive file metadata"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        stat = os.stat(file_path)
        file_hash = self._calculate_hashes(file_path)
        
        metadata = {
            "file_info": {
                "name": os.path.basename(file_path),
                "path": os.path.abspath(file_path),
                "size": stat.st_size,
                "mime_type": mimetypes.guess_type(file_path)[0],
                "extension": Path(file_path).suffix.lower()
            },
            "timestamps": {
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat()
            },
            "hashes": file_hash,
            "forensic_data": {}
        }
        
        # Extract format-specific metadata
        ext = Path(file_path).suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            metadata["forensic_data"] = self._extract_jpeg_metadata(file_path)
        elif ext == '.png':
            metadata["forensic_data"] = self._extract_png_metadata(file_path)
        elif ext == '.pdf':
            metadata["forensic_data"] = self._extract_pdf_metadata(file_path)
        
        return metadata
    
    def _calculate_hashes(self, file_path):
        """Calculate MD5, SHA1, SHA256 hashes"""
        hashes = {}
        hash_algorithms = {
            'md5': hashlib.md5(),
            'sha1': hashlib.sha1(),
            'sha256': hashlib.sha256()
        }
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    for algo in hash_algorithms.values():
                        algo.update(chunk)
            
            for name, algo in hash_algorithms.items():
                hashes[name] = algo.hexdigest()
        except Exception as e:
            hashes['error'] = str(e)
        
        return hashes
    
    def _extract_jpeg_metadata(self, file_path):
        """Extract JPEG EXIF data"""
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                # Look for EXIF marker
                data = f.read(2)
                if data != b'\xff\xd8':
                    return {"error": "Not a valid JPEG"}
                
                while True:
                    marker = f.read(2)
                    if not marker:
                        break
                    
                    if marker == b'\xff\xe1':  # EXIF marker
                        length = struct.unpack('>H', f.read(2))[0]
                        exif_data = f.read(length - 2)
                        
                        if exif_data.startswith(b'Exif\x00\x00'):
                            metadata["has_exif"] = True
                            metadata["exif_size"] = len(exif_data)
                            # Basic EXIF parsing
                            metadata["camera_info"] = self._parse_basic_exif(exif_data)
                        break
                    else:
                        # Skip this segment
                        try:
                            length = struct.unpack('>H', f.read(2))[0]
                            f.seek(length - 2, 1)
                        except:
                            break
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def _parse_basic_exif(self, exif_data):
        """Basic EXIF parsing for camera info"""
        info = {}
        try:
            # Look for common EXIF tags
            if b'Canon' in exif_data:
                info["camera_make"] = "Canon"
            elif b'Nikon' in exif_data:
                info["camera_make"] = "Nikon"
            elif b'Sony' in exif_data:
                info["camera_make"] = "Sony"
            elif b'Apple' in exif_data:
                info["camera_make"] = "Apple"
            
            # GPS coordinates indicator
            if b'GPS' in exif_data:
                info["has_gps"] = True
            
            # Software info
            if b'Photoshop' in exif_data:
                info["edited_with"] = "Adobe Photoshop"
            elif b'GIMP' in exif_data:
                info["edited_with"] = "GIMP"
        except:
            pass
        
        return info
    
    def _extract_png_metadata(self, file_path):
        """Extract PNG metadata"""
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                # Check PNG signature
                if f.read(8) != b'\x89PNG\r\n\x1a\n':
                    return {"error": "Not a valid PNG"}
                
                chunks = []
                while True:
                    try:
                        length = struct.unpack('>I', f.read(4))[0]
                        chunk_type = f.read(4).decode('ascii')
                        chunk_data = f.read(length)
                        crc = f.read(4)
                        
                        chunks.append(chunk_type)
                        
                        if chunk_type == 'tEXt':
                            # Text metadata
                            text_data = chunk_data.decode('latin1', errors='ignore')
                            if '\x00' in text_data:
                                key, value = text_data.split('\x00', 1)
                                metadata[f"text_{key}"] = value
                        
                        if chunk_type == 'IEND':
                            break
                    except:
                        break
                
                metadata["chunks"] = chunks
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def _extract_pdf_metadata(self, file_path):
        """Extract PDF metadata"""
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB
                
                if not content.startswith(b'%PDF'):
                    return {"error": "Not a valid PDF"}
                
                # Look for metadata
                content_str = content.decode('latin1', errors='ignore')
                
                if '/Creator' in content_str:
                    metadata["has_creator_info"] = True
                if '/Producer' in content_str:
                    metadata["has_producer_info"] = True
                if '/CreationDate' in content_str:
                    metadata["has_creation_date"] = True
                
                # PDF version
                if content.startswith(b'%PDF-'):
                    version = content[5:8].decode('ascii', errors='ignore')
                    metadata["pdf_version"] = version
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def analyze_directory(self, directory_path):
        """Analyze all files in directory"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if Path(file_path).suffix.lower() in self.supported_formats:
                    metadata = self.extract_file_metadata(file_path)
                    results.append(metadata)
        
        return results
    
    def find_hidden_files(self, directory_path):
        """Find hidden and suspicious files"""
        hidden_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Hidden files (starting with .)
            for file in files:
                if file.startswith('.') and not file.startswith('..'):
                    hidden_files.append({
                        "type": "hidden",
                        "path": os.path.join(root, file),
                        "name": file
                    })
            
            # Files with no extension
            for file in files:
                if '.' not in file:
                    hidden_files.append({
                        "type": "no_extension",
                        "path": os.path.join(root, file),
                        "name": file
                    })
            
            # Suspicious extensions
            suspicious_exts = ['.tmp', '.bak', '.old', '.log']
            for file in files:
                if any(file.endswith(ext) for ext in suspicious_exts):
                    hidden_files.append({
                        "type": "suspicious",
                        "path": os.path.join(root, file),
                        "name": file
                    })
        
        return hidden_files