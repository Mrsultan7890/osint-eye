import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
from utils.logger import setup_logger

logger = setup_logger()

class BehavioralAnalyzer:
    def __init__(self):
        self.personality_indicators = {
            'extrovert': ['party', 'friends', 'social', 'event', 'meeting', 'crowd'],
            'introvert': ['alone', 'quiet', 'home', 'reading', 'thinking', 'peaceful'],
            'creative': ['art', 'design', 'music', 'creative', 'inspiration', 'imagine'],
            'analytical': ['data', 'analysis', 'logic', 'research', 'study', 'facts'],
            'emotional': ['feel', 'heart', 'love', 'sad', 'happy', 'emotional']
        }
    
    def analyze_behavior(self, profile_data: Dict[str, Any], posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive behavioral analysis"""
        
        # Personality analysis
        personality = self._analyze_personality(posts)
        
        # Activity patterns
        activity_patterns = self._analyze_activity_patterns(posts)
        
        # Content patterns
        content_patterns = self._analyze_content_patterns(posts)
        
        # Social behavior
        social_behavior = self._analyze_social_behavior(posts, profile_data)
        
        # Risk assessment
        risk_assessment = self._assess_behavioral_risks(posts, profile_data)
        
        return {
            'personality_profile': personality,
            'activity_patterns': activity_patterns,
            'content_patterns': content_patterns,
            'social_behavior': social_behavior,
            'risk_assessment': risk_assessment,
            'behavioral_score': self._calculate_behavioral_score(personality, activity_patterns, social_behavior)
        }
    
    def _analyze_personality(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze personality traits from content"""
        all_text = ' '.join([post.get('caption', '') for post in posts]).lower()
        
        personality_scores = {}
        for trait, keywords in self.personality_indicators.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            personality_scores[trait] = min(100, score * 10)  # Normalize to 0-100
        
        # Determine dominant trait
        dominant_trait = max(personality_scores, key=personality_scores.get) if personality_scores else 'unknown'
        
        return {
            'scores': personality_scores,
            'dominant_trait': dominant_trait,
            'confidence': personality_scores.get(dominant_trait, 0)
        }
    
    def _analyze_activity_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posting activity patterns"""
        if not posts:
            return {'pattern': 'no_activity', 'regularity': 0}
        
        # Extract posting times
        post_times = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    post_times.append(dt)
                except:
                    continue
        
        if not post_times:
            return {'pattern': 'unknown', 'regularity': 0}
        
        # Analyze patterns
        hours = [dt.hour for dt in post_times]
        days = [dt.weekday() for dt in post_times]
        
        hour_distribution = Counter(hours)
        day_distribution = Counter(days)
        
        # Determine activity pattern
        peak_hour = hour_distribution.most_common(1)[0][0] if hour_distribution else 12
        peak_day = day_distribution.most_common(1)[0][0] if day_distribution else 0
        
        # Calculate regularity (how consistent posting times are)
        if len(post_times) > 1:
            intervals = [(post_times[i] - post_times[i-1]).total_seconds() / 3600 
                        for i in range(1, len(post_times))]
            regularity = 100 - min(100, (max(intervals) - min(intervals)) / 24 * 100) if intervals else 0
        else:
            regularity = 0
        
        return {
            'peak_hour': peak_hour,
            'peak_day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][peak_day],
            'hour_distribution': dict(hour_distribution),
            'day_distribution': dict(day_distribution),
            'regularity': regularity,
            'posting_frequency': len(posts) / max(1, (max(post_times) - min(post_times)).days) if len(post_times) > 1 else 0
        }
    
    def _analyze_content_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content posting patterns"""
        if not posts:
            return {}
        
        # Content types
        video_count = sum(1 for post in posts if post.get('is_video', False))
        photo_count = len(posts) - video_count
        
        # Caption analysis
        caption_lengths = [len(post.get('caption', '')) for post in posts]
        avg_caption_length = sum(caption_lengths) / len(caption_lengths) if caption_lengths else 0
        
        # Hashtag usage
        all_hashtags = []
        for post in posts:
            hashtags = post.get('hashtags', [])
            all_hashtags.extend(hashtags)
        
        hashtag_frequency = len(all_hashtags) / len(posts) if posts else 0
        
        return {
            'content_types': {
                'photos': photo_count,
                'videos': video_count,
                'photo_percentage': (photo_count / len(posts)) * 100 if posts else 0
            },
            'caption_analysis': {
                'avg_length': avg_caption_length,
                'max_length': max(caption_lengths) if caption_lengths else 0,
                'min_length': min(caption_lengths) if caption_lengths else 0
            },
            'hashtag_usage': {
                'avg_per_post': hashtag_frequency,
                'total_unique': len(set(all_hashtags)),
                'most_used': Counter(all_hashtags).most_common(5)
            }
        }
    
    def _analyze_social_behavior(self, posts: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social interaction patterns"""
        
        # Engagement analysis
        likes = [post.get('likes', 0) for post in posts]
        comments = [post.get('comments', 0) for post in posts]
        
        avg_likes = sum(likes) / len(likes) if likes else 0
        avg_comments = sum(comments) / len(comments) if comments else 0
        
        # Social connectivity
        followers = profile_data.get('followers', 0)
        following = profile_data.get('followees', 0)
        
        social_ratio = followers / max(1, following)
        
        # Interaction style
        mentions = []
        for post in posts:
            mentions.extend(post.get('mentions', []))
        
        return {
            'engagement_metrics': {
                'avg_likes': avg_likes,
                'avg_comments': avg_comments,
                'engagement_rate': (avg_likes + avg_comments) / max(1, followers) * 100
            },
            'social_connectivity': {
                'followers': followers,
                'following': following,
                'social_ratio': social_ratio,
                'connectivity_level': 'High' if social_ratio > 10 else 'Medium' if social_ratio > 1 else 'Low'
            },
            'interaction_style': {
                'mentions_per_post': len(mentions) / len(posts) if posts else 0,
                'unique_mentions': len(set(mentions)),
                'social_activity': 'Active' if len(mentions) > len(posts) * 0.5 else 'Moderate'
            }
        }
    
    def _assess_behavioral_risks(self, posts: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential behavioral risks"""
        risk_score = 0
        risk_factors = []
        
        # Check for aggressive language
        aggressive_keywords = ['hate', 'kill', 'destroy', 'attack', 'violence', 'war']
        all_text = ' '.join([post.get('caption', '') for post in posts]).lower()
        
        for keyword in aggressive_keywords:
            if keyword in all_text:
                risk_score += 10
                risk_factors.append(f'Aggressive language detected: {keyword}')
        
        # Check posting frequency (spam behavior)
        if len(posts) > 50:  # More than 50 posts in dataset
            risk_score += 5
            risk_factors.append('High posting frequency')
        
        # Check for promotional content
        promo_keywords = ['buy', 'sale', 'discount', 'offer', 'click link', 'dm me']
        promo_count = sum(1 for keyword in promo_keywords if keyword in all_text)
        
        if promo_count > 3:
            risk_score += 15
            risk_factors.append('Promotional/spam content detected')
        
        # Determine risk level
        if risk_score >= 30:
            risk_level = 'High'
        elif risk_score >= 15:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _calculate_behavioral_score(self, personality: Dict, activity: Dict, social: Dict) -> int:
        """Calculate overall behavioral score"""
        score = 50  # Base score
        
        # Personality diversity bonus
        if personality.get('confidence', 0) > 20:
            score += 10
        
        # Activity regularity bonus
        if activity.get('regularity', 0) > 50:
            score += 15
        
        # Social engagement bonus
        engagement_rate = social.get('engagement_metrics', {}).get('engagement_rate', 0)
        if engagement_rate > 1:
            score += 20
        elif engagement_rate > 0.1:
            score += 10
        
        return min(100, score)
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'Low': 'Account appears normal with low risk indicators',
            'Medium': 'Monitor account activity, some concerning patterns detected',
            'High': 'High risk account - recommend detailed investigation'
        }
        return recommendations.get(risk_level, 'Unknown risk level')