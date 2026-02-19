#!/usr/bin/env python3

import requests
import hashlib
import json
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import io
import base64
from typing import Dict, List, Optional, Tuple
import imagehash
from datetime import datetime
import os

class AdvancedImageAnalyzer:
    def __init__(self):
        self.reverse_search_engines = [
            "https://www.google.com/searchbyimage?image_url=",
            "https://yandex.com/images/search?rpt=imageview&url=",
            "https://tineye.com/search?url="
        ]
    
    def analyze_profile_image(self, image_url: str, username: str) -> Dict:
        """Comprehensive profile image analysis"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return {"error": "Failed to download image"}
            
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            
            analysis = {
                "basic_info": self._get_basic_info(image, image_data),
                "metadata": self._extract_metadata(image),
                "hash_analysis": self._generate_hashes(image),
                "reverse_search_urls": self._get_reverse_search_urls(image_url),
                "similarity_check": self._check_common_patterns(image),
                "authenticity_score": 0
            }
            
            # Calculate authenticity score
            analysis["authenticity_score"] = self._calculate_authenticity_score(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}
    
    def _get_basic_info(self, image: Image.Image, image_data: bytes) -> Dict:
        """Extract basic image information"""
        return {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "file_size": len(image_data),
            "aspect_ratio": round(image.size[0] / image.size[1], 2) if image.size[1] > 0 else 0,
            "is_square": image.size[0] == image.size[1],
            "color_analysis": self._analyze_colors(image)
        }
    
    def _extract_metadata(self, image: Image.Image) -> Dict:
        """Extract EXIF and other metadata"""
        metadata = {}
        
        try:
            exifdata = image.getexif()
            if exifdata:
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', errors='ignore')
                    metadata[tag] = str(data)
        except:
            pass
        
        return {
            "exif_data": metadata,
            "has_metadata": len(metadata) > 0,
            "creation_software": metadata.get('Software', 'Unknown'),
            "camera_info": {
                "make": metadata.get('Make', 'Unknown'),
                "model": metadata.get('Model', 'Unknown')
            },
            "gps_info": self._extract_gps_info(metadata)
        }
    
    def _generate_hashes(self, image: Image.Image) -> Dict:
        """Generate various image hashes for comparison"""
        try:
            return {
                "average_hash": str(imagehash.average_hash(image)),
                "perceptual_hash": str(imagehash.phash(image)),
                "difference_hash": str(imagehash.dhash(image)),
                "wavelet_hash": str(imagehash.whash(image))
            }
        except:
            return {}
    
    def _get_reverse_search_urls(self, image_url: str) -> List[str]:
        """Generate reverse image search URLs"""
        return [engine + image_url for engine in self.reverse_search_engines]
    
    def _check_common_patterns(self, image: Image.Image) -> Dict:
        """Check for common fake profile patterns"""
        analysis = {
            "is_stock_photo_likely": False,
            "is_ai_generated_likely": False,
            "quality_indicators": {},
            "red_flags": []
        }
        
        # Check image quality and characteristics
        width, height = image.size
        
        # Stock photo indicators
        if width >= 1000 and height >= 1000:
            analysis["quality_indicators"]["high_resolution"] = True
        
        if image.mode == 'RGB' and self._has_professional_lighting(image):
            analysis["is_stock_photo_likely"] = True
            analysis["red_flags"].append("Professional studio lighting detected")
        
        # AI generation indicators
        if self._check_ai_artifacts(image):
            analysis["is_ai_generated_likely"] = True
            analysis["red_flags"].append("Possible AI generation artifacts")
        
        return analysis
    
    def _analyze_colors(self, image: Image.Image) -> Dict:
        """Analyze color distribution"""
        try:
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                dominant_color = max(colors, key=lambda x: x[0])
                return {
                    "dominant_color": dominant_color[1] if len(dominant_color) > 1 else "Unknown",
                    "color_count": len(colors),
                    "is_grayscale": image.mode in ['L', 'LA']
                }
        except:
            pass
        return {}
    
    def _extract_gps_info(self, metadata: Dict) -> Dict:
        """Extract GPS information if available"""
        gps_info = {}
        for key, value in metadata.items():
            if 'GPS' in str(key):
                gps_info[key] = value
        return gps_info
    
    def _has_professional_lighting(self, image: Image.Image) -> bool:
        """Detect professional lighting patterns"""
        # Simple heuristic - check for even lighting distribution
        try:
            grayscale = image.convert('L')
            histogram = grayscale.histogram()
            # Professional photos often have more even distribution
            variance = sum((i - 128) ** 2 * histogram[i] for i in range(256)) / sum(histogram)
            return variance < 3000  # Threshold for even lighting
        except:
            return False
    
    def _check_ai_artifacts(self, image: Image.Image) -> bool:
        """Check for AI generation artifacts"""
        # Simple checks for common AI artifacts
        try:
            # Check for unusual smoothness in skin tones (common in AI faces)
            if image.mode == 'RGB':
                # Convert to array and check for unnatural smoothness
                # This is a simplified check
                return False  # Placeholder for more complex AI detection
        except:
            pass
        return False
    
    def _calculate_authenticity_score(self, analysis: Dict) -> int:
        """Calculate overall authenticity score (0-100)"""
        score = 100
        
        # Deduct points for red flags
        red_flags = analysis.get("similarity_check", {}).get("red_flags", [])
        score -= len(red_flags) * 15
        
        # Deduct for likely stock photo
        if analysis.get("similarity_check", {}).get("is_stock_photo_likely", False):
            score -= 25
        
        # Deduct for likely AI generated
        if analysis.get("similarity_check", {}).get("is_ai_generated_likely", False):
            score -= 30
        
        # Add points for metadata presence (authentic photos often have metadata)
        if analysis.get("metadata", {}).get("has_metadata", False):
            score += 10
        
        return max(0, min(100, score))
    
    def compare_images(self, image1_url: str, image2_url: str) -> Dict:
        """Compare two images for similarity"""
        try:
            # Download both images
            img1_response = requests.get(image1_url, timeout=10)
            img2_response = requests.get(image2_url, timeout=10)
            
            if img1_response.status_code != 200 or img2_response.status_code != 200:
                return {"error": "Failed to download images"}
            
            img1 = Image.open(io.BytesIO(img1_response.content))
            img2 = Image.open(io.BytesIO(img2_response.content))
            
            # Generate hashes
            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)
            
            # Calculate similarity
            similarity = 100 - (hash1 - hash2)
            
            return {
                "similarity_percentage": max(0, similarity),
                "are_similar": similarity > 85,
                "hash_difference": hash1 - hash2,
                "comparison_method": "Average Hash"
            }
            
        except Exception as e:
            return {"error": f"Image comparison failed: {str(e)}"}
    
    def batch_analyze_images(self, image_urls: List[str], usernames: List[str]) -> Dict:
        """Analyze multiple images in batch"""
        results = {}
        
        for i, (url, username) in enumerate(zip(image_urls, usernames)):
            print(f"Analyzing image {i+1}/{len(image_urls)}: {username}")
            results[username] = self.analyze_profile_image(url, username)
        
        # Cross-compare all images
        comparisons = {}
        for i in range(len(image_urls)):
            for j in range(i+1, len(image_urls)):
                user1, user2 = usernames[i], usernames[j]
                comparison_key = f"{user1}_vs_{user2}"
                comparisons[comparison_key] = self.compare_images(image_urls[i], image_urls[j])
        
        return {
            "individual_analysis": results,
            "cross_comparisons": comparisons,
            "summary": self._generate_batch_summary(results, comparisons)
        }
    
    def _generate_batch_summary(self, results: Dict, comparisons: Dict) -> Dict:
        """Generate summary of batch analysis"""
        total_images = len(results)
        suspicious_count = sum(1 for r in results.values() 
                             if isinstance(r, dict) and r.get("authenticity_score", 100) < 70)
        
        similar_pairs = sum(1 for c in comparisons.values() 
                          if isinstance(c, dict) and c.get("are_similar", False))
        
        return {
            "total_analyzed": total_images,
            "suspicious_images": suspicious_count,
            "similar_pairs_found": similar_pairs,
            "overall_risk_level": "High" if suspicious_count > total_images * 0.3 else "Medium" if suspicious_count > 0 else "Low"
        }