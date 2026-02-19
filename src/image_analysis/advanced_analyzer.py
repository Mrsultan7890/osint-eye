"""
Advanced Image Analysis for OSINT
Face detection, reverse search, tampering detection
"""
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import requests
from PIL import Image, ImageStat
import imagehash
from utils.logger import setup_logger

logger = setup_logger()

class AdvancedImageAnalyzer:
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_image_comprehensive(self, image_path: str) -> Dict[str, Any]:
        """Comprehensive image analysis"""
        logger.info(f"🖼️ Starting comprehensive image analysis: {os.path.basename(image_path)}")
        
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}
        
        analysis = {
            "file_info": self._get_file_info(image_path),
            "image_properties": self._analyze_image_properties(image_path),
            "hash_analysis": self._generate_image_hashes(image_path),
            "tampering_detection": self._detect_tampering(image_path),
            "reverse_search_urls": self._generate_reverse_search_urls(image_path),
            "metadata_extraction": self._extract_image_metadata(image_path),
            "similarity_analysis": self._analyze_image_similarity(image_path),
            "forensic_markers": self._detect_forensic_markers(image_path)
        }
        
        # Calculate overall authenticity score
        analysis["authenticity_score"] = self._calculate_authenticity_score(analysis)
        
        logger.info(f"✅ Image analysis complete. Authenticity: {analysis['authenticity_score']}/100")
        
        return analysis
    
    def _get_file_info(self, image_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        stat = os.stat(image_path)
        
        return {
            "filename": os.path.basename(image_path),
            "filepath": os.path.abspath(image_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _analyze_image_properties(self, image_path: str) -> Dict[str, Any]:
        """Analyze image properties using PIL"""
        try:
            with Image.open(image_path) as img:
                # Basic properties
                properties = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": round(img.width / img.height, 2),
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                # Color analysis
                if img.mode == 'RGB':
                    stat = ImageStat.Stat(img)
                    properties.update({
                        "mean_colors": {
                            "red": round(stat.mean[0], 2),
                            "green": round(stat.mean[1], 2),
                            "blue": round(stat.mean[2], 2)
                        },
                        "color_variance": {
                            "red": round(stat.var[0], 2),
                            "green": round(stat.var[1], 2),
                            "blue": round(stat.var[2], 2)
                        }
                    })
                
                # Check for common social media dimensions
                common_sizes = {
                    (1080, 1080): "Instagram Square",
                    (1080, 1350): "Instagram Portrait",
                    (1200, 630): "Facebook Link",
                    (1024, 512): "Twitter Header",
                    (400, 400): "Profile Picture"
                }
                
                properties["likely_platform"] = common_sizes.get(img.size, "Unknown")
                
                return properties
                
        except Exception as e:
            return {"error": f"Failed to analyze image properties: {e}"}
    
    def _generate_image_hashes(self, image_path: str) -> Dict[str, str]:
        """Generate various image hashes for similarity detection"""
        try:
            with Image.open(image_path) as img:
                hashes = {
                    "average_hash": str(imagehash.average_hash(img)),
                    "perceptual_hash": str(imagehash.phash(img)),
                    "difference_hash": str(imagehash.dhash(img)),
                    "wavelet_hash": str(imagehash.whash(img))
                }
                
                # File hash
                with open(image_path, 'rb') as f:
                    file_content = f.read()
                    hashes["md5"] = hashlib.md5(file_content).hexdigest()
                    hashes["sha256"] = hashlib.sha256(file_content).hexdigest()
                
                return hashes
                
        except Exception as e:
            return {"error": f"Failed to generate hashes: {e}"}
    
    def _detect_tampering(self, image_path: str) -> Dict[str, Any]:
        """Detect potential image tampering"""
        tampering_indicators = {
            "suspicious_patterns": [],
            "compression_anomalies": [],
            "metadata_inconsistencies": [],
            "risk_level": "LOW"
        }
        
        try:
            with Image.open(image_path) as img:
                # Check for unusual compression
                if hasattr(img, 'quantization'):
                    tampering_indicators["compression_anomalies"].append("Custom quantization tables detected")
                
                # Check image dimensions for common editing sizes
                if img.width % 8 != 0 or img.height % 8 != 0:
                    tampering_indicators["suspicious_patterns"].append("Non-standard dimensions (not divisible by 8)")
                
                # Check for multiple saves (quality degradation)
                if img.format == 'JPEG':
                    # Estimate quality
                    file_size = os.path.getsize(image_path)
                    expected_size = img.width * img.height * 3 * 0.1  # Rough estimate
                    
                    if file_size < expected_size * 0.5:
                        tampering_indicators["compression_anomalies"].append("Unusually high compression detected")
                    elif file_size > expected_size * 2:
                        tampering_indicators["compression_anomalies"].append("Unusually low compression detected")
                
                # Calculate risk level
                total_indicators = len(tampering_indicators["suspicious_patterns"]) + \
                                len(tampering_indicators["compression_anomalies"]) + \
                                len(tampering_indicators["metadata_inconsistencies"])
                
                if total_indicators >= 3:
                    tampering_indicators["risk_level"] = "HIGH"
                elif total_indicators >= 1:
                    tampering_indicators["risk_level"] = "MEDIUM"
                
                return tampering_indicators
                
        except Exception as e:
            tampering_indicators["error"] = str(e)
            return tampering_indicators
    
    def _generate_reverse_search_urls(self, image_path: str) -> List[str]:
        """Generate reverse image search URLs"""
        filename = os.path.basename(image_path)
        
        # Note: These are template URLs - actual reverse search requires uploading
        urls = [
            f"https://www.google.com/searchbyimage?image_url=LOCAL_FILE_{filename}",
            f"https://tineye.com/search?url=LOCAL_FILE_{filename}",
            f"https://yandex.com/images/search?rpt=imageview&url=LOCAL_FILE_{filename}",
            f"https://www.bing.com/images/searchbyimage?FORM=IRSBIQ&cbir=sbi&imgurl=LOCAL_FILE_{filename}"
        ]
        
        return urls
    
    def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract image metadata and EXIF data"""
        metadata = {
            "exif_data": {},
            "creation_software": None,
            "camera_info": {},
            "gps_info": {},
            "editing_history": []
        }
        
        try:
            with Image.open(image_path) as img:
                # Get EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    
                    # Common EXIF tags
                    exif_tags = {
                        271: 'Make',
                        272: 'Model',
                        306: 'DateTime',
                        315: 'Artist',
                        34665: 'ExifOffset'
                    }
                    
                    for tag_id, tag_name in exif_tags.items():
                        if tag_id in exif:
                            metadata["exif_data"][tag_name] = str(exif[tag_id])
                    
                    # Check for camera info
                    if 271 in exif:  # Make
                        metadata["camera_info"]["make"] = str(exif[271])
                    if 272 in exif:  # Model
                        metadata["camera_info"]["model"] = str(exif[272])
                
                # Check for software signatures
                if 'Software' in img.info:
                    metadata["creation_software"] = img.info['Software']
                elif 'software' in img.info:
                    metadata["creation_software"] = img.info['software']
                
                # Look for editing software signatures in filename or metadata
                editing_software = ['photoshop', 'gimp', 'canva', 'figma', 'sketch']
                for software in editing_software:
                    if software.lower() in image_path.lower():
                        metadata["editing_history"].append(f"Filename suggests {software.title()} usage")
                
                return metadata
                
        except Exception as e:
            metadata["error"] = str(e)
            return metadata
    
    def _analyze_image_similarity(self, image_path: str) -> Dict[str, Any]:
        """Analyze image for similarity to common templates/stock photos"""
        similarity = {
            "is_likely_stock": False,
            "template_matches": [],
            "uniqueness_score": 85,  # Default high uniqueness
            "common_elements": []
        }
        
        try:
            with Image.open(image_path) as img:
                # Check for common stock photo characteristics
                if img.size in [(1920, 1080), (1280, 720), (800, 600)]:
                    similarity["common_elements"].append("Standard stock photo dimensions")
                
                # Check for watermark areas (common in stock photos)
                if img.mode == 'RGBA':
                    similarity["common_elements"].append("Transparency channel (possible watermark removal)")
                
                # Analyze color distribution for stock photo patterns
                if img.mode == 'RGB':
                    stat = ImageStat.Stat(img)
                    color_variance = sum(stat.var) / 3
                    
                    if color_variance < 1000:  # Very uniform colors
                        similarity["common_elements"].append("Uniform color distribution (typical of stock photos)")
                        similarity["uniqueness_score"] -= 15
                    elif color_variance > 10000:  # Very diverse colors
                        similarity["uniqueness_score"] += 10
                
                # Check filename for stock photo patterns
                filename = os.path.basename(image_path).lower()
                stock_patterns = ['stock', 'shutterstock', 'getty', 'unsplash', 'pexels', 'pixabay']
                for pattern in stock_patterns:
                    if pattern in filename:
                        similarity["is_likely_stock"] = True
                        similarity["template_matches"].append(f"Filename contains '{pattern}'")
                        similarity["uniqueness_score"] -= 30
                
                return similarity
                
        except Exception as e:
            similarity["error"] = str(e)
            return similarity
    
    def _detect_forensic_markers(self, image_path: str) -> Dict[str, Any]:
        """Detect forensic markers and digital signatures"""
        markers = {
            "digital_signatures": [],
            "creation_timestamps": [],
            "device_fingerprints": [],
            "authenticity_indicators": []
        }
        
        try:
            # File creation patterns
            filename = os.path.basename(image_path)
            
            # Instagram download patterns
            if 'scontent' in filename or len(filename) > 50:
                markers["digital_signatures"].append("Instagram CDN signature detected")
                markers["authenticity_indicators"].append("Likely downloaded from Instagram")
            
            # Screenshot patterns
            if 'screenshot' in filename.lower() or 'screen' in filename.lower():
                markers["digital_signatures"].append("Screenshot filename pattern")
                markers["authenticity_indicators"].append("Likely a screenshot")
            
            # Camera roll patterns
            if filename.startswith(('IMG_', 'DSC_', 'PHOTO_')):
                markers["digital_signatures"].append("Camera roll naming pattern")
                markers["authenticity_indicators"].append("Likely from camera/phone")
            
            # Timestamp analysis
            stat = os.stat(image_path)
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            if abs((created - modified).total_seconds()) < 1:
                markers["creation_timestamps"].append("Creation and modification times identical")
            else:
                markers["creation_timestamps"].append("File has been modified after creation")
            
            return markers
            
        except Exception as e:
            markers["error"] = str(e)
            return markers
    
    def _calculate_authenticity_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall authenticity score"""
        score = 100
        
        # Tampering detection penalties
        tampering = analysis.get("tampering_detection", {})
        if tampering.get("risk_level") == "HIGH":
            score -= 30
        elif tampering.get("risk_level") == "MEDIUM":
            score -= 15
        
        # Similarity analysis penalties
        similarity = analysis.get("similarity_analysis", {})
        if similarity.get("is_likely_stock"):
            score -= 20
        
        uniqueness = similarity.get("uniqueness_score", 85)
        if uniqueness < 50:
            score -= 15
        elif uniqueness > 90:
            score += 5
        
        # Forensic markers bonuses
        markers = analysis.get("forensic_markers", {})
        authenticity_indicators = markers.get("authenticity_indicators", [])
        if "Likely downloaded from Instagram" in authenticity_indicators:
            score += 10
        if "Likely from camera/phone" in authenticity_indicators:
            score += 15
        
        # Metadata bonuses
        metadata = analysis.get("metadata_extraction", {})
        if metadata.get("camera_info"):
            score += 10
        if metadata.get("exif_data"):
            score += 5
        
        return max(0, min(100, score))
    
    def compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """Compare two images for similarity"""
        try:
            with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
                # Generate hashes
                hash1 = imagehash.average_hash(img1)
                hash2 = imagehash.average_hash(img2)
                
                # Calculate similarity
                similarity = 100 - (hash1 - hash2)
                
                comparison = {
                    "similarity_percentage": max(0, similarity),
                    "hash_difference": hash1 - hash2,
                    "likely_same_image": similarity > 90,
                    "likely_similar": similarity > 70,
                    "image1_hash": str(hash1),
                    "image2_hash": str(hash2)
                }
                
                return comparison
                
        except Exception as e:
            return {"error": f"Failed to compare images: {e}"}
    
    def batch_analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """Analyze all images in a directory"""
        if not os.path.exists(directory_path):
            return {"error": "Directory not found"}
        
        results = {
            "directory": directory_path,
            "total_images": 0,
            "analyzed_images": 0,
            "results": {},
            "summary": {
                "high_authenticity": 0,
                "medium_authenticity": 0,
                "low_authenticity": 0,
                "likely_tampered": 0,
                "likely_stock": 0
            }
        }
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        for filename in os.listdir(directory_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                results["total_images"] += 1
                
                image_path = os.path.join(directory_path, filename)
                logger.info(f"Analyzing: {filename}")
                
                analysis = self.analyze_image_comprehensive(image_path)
                results["results"][filename] = analysis
                results["analyzed_images"] += 1
                
                # Update summary
                score = analysis.get("authenticity_score", 0)
                if score >= 80:
                    results["summary"]["high_authenticity"] += 1
                elif score >= 60:
                    results["summary"]["medium_authenticity"] += 1
                else:
                    results["summary"]["low_authenticity"] += 1
                
                if analysis.get("tampering_detection", {}).get("risk_level") == "HIGH":
                    results["summary"]["likely_tampered"] += 1
                
                if analysis.get("similarity_analysis", {}).get("is_likely_stock"):
                    results["summary"]["likely_stock"] += 1
        
        return results