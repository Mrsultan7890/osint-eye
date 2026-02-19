import re
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher
from utils.logger import setup_logger

logger = setup_logger()

class CrossPlatformCorrelator:
    def __init__(self):
        self.platforms = ['instagram', 'twitter', 'youtube', 'tiktok', 'linkedin']
        
    def correlate_accounts(self, username: str, data_dir: str = 'data') -> Dict[str, Any]:
        """Find and correlate accounts across platforms"""
        correlations = {}
        
        # Check each platform for the same username
        for platform in self.platforms:
            try:
                platform_data = self._load_platform_data(platform, username, data_dir)
                if platform_data:
                    correlations[platform] = {
                        'found': True,
                        'profile': platform_data.get('profile', {}),
                        'confidence': 100  # Same username = high confidence
                    }
                else:
                    correlations[platform] = {'found': False, 'confidence': 0}
            except Exception as e:
                logger.warning(f"Error checking {platform}: {e}")
                correlations[platform] = {'found': False, 'confidence': 0}
        
        # Analyze correlations
        correlation_analysis = self._analyze_correlations(correlations)
        
        return {
            'username': username,
            'platform_presence': correlations,
            'correlation_analysis': correlation_analysis,
            'total_platforms': sum(1 for p in correlations.values() if p['found']),
            'digital_footprint_score': self._calculate_footprint_score(correlations)
        }
    
    def find_similar_profiles(self, base_profile: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
        """Find similar profiles on same platform"""
        similar_profiles = []
        
        # Generate potential similar usernames
        base_username = base_profile.get('username', '')
        variations = self._generate_username_variations(base_username)
        
        for variation in variations:
            similarity_score = self._calculate_username_similarity(base_username, variation)
            if similarity_score > 0.7:  # 70% similarity threshold
                similar_profiles.append({
                    'username': variation,
                    'similarity_score': similarity_score,
                    'platform': platform,
                    'variation_type': self._get_variation_type(base_username, variation)
                })
        
        return similar_profiles
    
    def _load_platform_data(self, platform: str, username: str, data_dir: str) -> Dict[str, Any]:
        """Load data from platform directory"""
        import json
        import os
        from pathlib import Path
        
        platform_dir = Path(data_dir) / platform / username
        if not platform_dir.exists():
            return None
        
        # Find the latest data file
        data_files = list(platform_dir.glob('data_*.json'))
        if not data_files:
            return None
        
        latest_file = max(data_files, key=os.path.getctime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {latest_file}: {e}")
            return None
    
    def _analyze_correlations(self, correlations: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze cross-platform correlations"""
        found_platforms = [p for p, data in correlations.items() if data['found']]
        
        if len(found_platforms) < 2:
            return {
                'correlation_strength': 'Low',
                'common_elements': [],
                'discrepancies': [],
                'identity_confidence': 50
            }
        
        # Compare profile elements across platforms
        common_elements = []
        discrepancies = []
        
        # Get all profiles
        profiles = {p: data['profile'] for p, data in correlations.items() if data['found']}
        
        # Compare names
        names = [p.get('full_name', '') or p.get('display_name', '') or p.get('channel_name', '') 
                for p in profiles.values()]
        names = [n for n in names if n]  # Remove empty names
        
        if len(set(names)) == 1 and names:
            common_elements.append(f"Consistent name: {names[0]}")
        elif len(set(names)) > 1:
            discrepancies.append(f"Different names: {', '.join(set(names))}")
        
        # Compare bio/descriptions
        bios = [p.get('biography', '') or p.get('bio', '') or p.get('description', '') 
               for p in profiles.values()]
        bios = [b for b in bios if b]  # Remove empty bios
        
        if bios:
            bio_similarity = self._calculate_text_similarity(bios)
            if bio_similarity > 0.7:
                common_elements.append("Similar bio/description content")
            elif bio_similarity < 0.3:
                discrepancies.append("Very different bio/description content")
        
        # Calculate identity confidence
        identity_confidence = self._calculate_identity_confidence(common_elements, discrepancies, len(found_platforms))
        
        correlation_strength = 'High' if identity_confidence > 80 else 'Medium' if identity_confidence > 60 else 'Low'
        
        return {
            'correlation_strength': correlation_strength,
            'common_elements': common_elements,
            'discrepancies': discrepancies,
            'identity_confidence': identity_confidence,
            'platforms_found': found_platforms
        }
    
    def _generate_username_variations(self, username: str) -> List[str]:
        """Generate potential username variations"""
        variations = []
        
        # Add numbers
        for i in range(1, 100):
            variations.extend([
                f"{username}{i}",
                f"{username}_{i}",
                f"{username}.{i}",
                f"{i}{username}"
            ])
        
        # Add common suffixes
        suffixes = ['official', 'real', 'original', 'new', 'backup', '2024', '2023']
        for suffix in suffixes:
            variations.extend([
                f"{username}_{suffix}",
                f"{username}.{suffix}",
                f"{username}{suffix}"
            ])
        
        # Add underscores and dots
        variations.extend([
            username.replace('_', '.'),
            username.replace('.', '_'),
            f"_{username}",
            f"{username}_",
            f".{username}",
            f"{username}."
        ])
        
        return list(set(variations))  # Remove duplicates
    
    def _calculate_username_similarity(self, username1: str, username2: str) -> float:
        """Calculate similarity between usernames"""
        return SequenceMatcher(None, username1.lower(), username2.lower()).ratio()
    
    def _calculate_text_similarity(self, texts: List[str]) -> float:
        """Calculate similarity between multiple texts"""
        if len(texts) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity = SequenceMatcher(None, texts[i].lower(), texts[j].lower()).ratio()
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0
    
    def _get_variation_type(self, original: str, variation: str) -> str:
        """Determine type of username variation"""
        if variation.endswith(tuple('0123456789')):
            return 'numeric_suffix'
        elif '_' in variation and '_' not in original:
            return 'underscore_added'
        elif '.' in variation and '.' not in original:
            return 'dot_added'
        elif any(suffix in variation for suffix in ['official', 'real', 'new']):
            return 'descriptive_suffix'
        else:
            return 'other'
    
    def _calculate_identity_confidence(self, common_elements: List[str], discrepancies: List[str], platform_count: int) -> int:
        """Calculate confidence that accounts belong to same person"""
        base_score = 30  # Base score for same username
        
        # Bonus for multiple platforms
        base_score += min(40, platform_count * 10)
        
        # Bonus for common elements
        base_score += len(common_elements) * 10
        
        # Penalty for discrepancies
        base_score -= len(discrepancies) * 15
        
        return max(0, min(100, base_score))
    
    def _calculate_footprint_score(self, correlations: Dict[str, Dict]) -> int:
        """Calculate digital footprint score"""
        found_count = sum(1 for data in correlations.values() if data['found'])
        total_platforms = len(self.platforms)
        
        # Base score from platform presence
        presence_score = (found_count / total_platforms) * 60
        
        # Bonus for high-confidence matches
        confidence_bonus = sum(data.get('confidence', 0) for data in correlations.values() if data['found']) / max(1, found_count) * 0.4
        
        return min(100, int(presence_score + confidence_bonus))