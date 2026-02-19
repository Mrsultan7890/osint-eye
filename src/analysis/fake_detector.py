import re
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger()

class FakeDetector:
    def __init__(self):
        self.suspicious_patterns = {
            'username': [r'.*\d{4,}$', r'.*_\d+$', r'^[a-z]+\d+[a-z]*$'],
            'bio': ['follow for follow', 'f4f', 'l4l', 'dm for promo', 'click link'],
            'profile_pic': ['default', 'generic', 'stock']
        }
    
    def detect_fake_account(self, profile_data: Dict[str, Any], posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect if account is fake/bot"""
        score = 100  # Start with 100% authentic
        red_flags = []
        
        # Username analysis
        username = profile_data.get('username', '')
        for pattern in self.suspicious_patterns['username']:
            if re.match(pattern, username):
                score -= 15
                red_flags.append(f'Suspicious username pattern: {username}')
                break
        
        # Profile completeness
        if not profile_data.get('biography', ''):
            score -= 10
            red_flags.append('Empty bio')
        
        if not profile_data.get('full_name', ''):
            score -= 10
            red_flags.append('No display name')
        
        # Follower analysis
        followers = profile_data.get('followers', 0)
        following = profile_data.get('followees', 0)
        
        if following > 0:
            ratio = followers / following
            if ratio < 0.1:  # Following too many, very few followers
                score -= 20
                red_flags.append('Suspicious follower ratio')
            elif ratio > 100:  # Too many followers compared to following
                score -= 10
                red_flags.append('Unusual follower ratio')
        
        # Post analysis
        if len(posts) == 0 and followers > 1000:
            score -= 25
            red_flags.append('High followers but no posts')
        
        # Bio analysis
        bio = profile_data.get('biography', '').lower()
        for suspicious_text in self.suspicious_patterns['bio']:
            if suspicious_text in bio:
                score -= 15
                red_flags.append(f'Suspicious bio content: {suspicious_text}')
        
        # Account age vs activity
        posts_count = profile_data.get('posts_count', 0)
        if posts_count > 0 and len(posts) > 0:
            # Check posting frequency
            if len(posts) < posts_count * 0.1:  # Very few posts extracted
                logger.info("Limited post extraction - account might be private")
        
        authenticity_level = 'High' if score >= 80 else 'Medium' if score >= 60 else 'Low'
        
        return {
            'authenticity_score': max(0, score),
            'authenticity_level': authenticity_level,
            'red_flags': red_flags,
            'is_likely_fake': score < 60,
            'confidence': min(100, abs(score - 50) * 2)
        }