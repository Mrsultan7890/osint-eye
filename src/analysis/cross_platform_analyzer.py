import hashlib
import re
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from typing import Dict, List, Any, Tuple, Set
from utils.logger import setup_logger

logger = setup_logger()

class CrossPlatformAnalyzer:
    def __init__(self):
        self.username_patterns = [
            r'^[a-zA-Z0-9_]+$',  # Standard username
            r'^[a-zA-Z0-9._]+$', # With dots
            r'^[a-zA-Z0-9-]+$'   # With hyphens
        ]
        
    def find_cross_platform_accounts(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find same users across different platforms"""
        potential_matches = defaultdict(list)
        
        # Group profiles by similarity indicators
        username_groups = defaultdict(list)
        bio_groups = defaultdict(list)
        name_groups = defaultdict(list)
        
        for profile_data in profiles_data:
            platform = profile_data.get('platform', '')
            profile = profile_data.get('profile', {})
            
            username = profile.get('username', '').lower()
            display_name = (profile.get('display_name') or profile.get('full_name') or '').lower()
            bio = (profile.get('biography') or profile.get('description') or '').lower()
            
            # Group by username similarity
            username_key = self._normalize_username(username)
            if username_key:
                username_groups[username_key].append((platform, profile_data))
            
            # Group by display name
            if display_name:
                name_key = self._normalize_name(display_name)
                name_groups[name_key].append((platform, profile_data))
            
            # Group by bio similarity
            if bio and len(bio) > 20:
                bio_hash = self._get_bio_hash(bio)
                bio_groups[bio_hash].append((platform, profile_data))
        
        # Find matches
        matches = []
        
        # Username matches
        for username_key, profiles in username_groups.items():
            if len(profiles) > 1:
                matches.append({
                    'match_type': 'username',
                    'confidence': 0.9,
                    'profiles': profiles,
                    'identifier': username_key
                })
        
        # Name matches
        for name_key, profiles in name_groups.items():
            if len(profiles) > 1:
                matches.append({
                    'match_type': 'display_name',
                    'confidence': 0.7,
                    'profiles': profiles,
                    'identifier': name_key
                })
        
        # Bio matches
        for bio_hash, profiles in bio_groups.items():
            if len(profiles) > 1:
                matches.append({
                    'match_type': 'biography',
                    'confidence': 0.8,
                    'profiles': profiles,
                    'identifier': bio_hash
                })
        
        return {
            'total_matches': len(matches),
            'matches': matches,
            'cross_platform_users': self._consolidate_matches(matches)
        }
    
    def analyze_writing_style_correlation(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze writing style similarities across platforms"""
        style_profiles = []
        
        for profile_data in profiles_data:
            platform = profile_data.get('platform', '')
            posts = profile_data.get('posts', [])
            
            # Extract all text content
            all_text = []
            for post in posts:
                content = post.get('caption', '') or post.get('content', '')
                if content:
                    all_text.append(content)
            
            if all_text:
                combined_text = ' '.join(all_text)
                style_features = self._extract_writing_style_features(combined_text)
                
                style_profiles.append({
                    'platform': platform,
                    'profile_data': profile_data,
                    'style_features': style_features,
                    'text_sample': combined_text[:500]
                })
        
        # Find style similarities
        similarities = []
        for i in range(len(style_profiles)):
            for j in range(i + 1, len(style_profiles)):
                similarity = self._calculate_style_similarity(
                    style_profiles[i]['style_features'],
                    style_profiles[j]['style_features']
                )
                
                if similarity > 0.7:  # High similarity threshold
                    similarities.append({
                        'profile1': style_profiles[i]['platform'],
                        'profile2': style_profiles[j]['platform'],
                        'similarity_score': similarity,
                        'matching_features': self._get_matching_features(
                            style_profiles[i]['style_features'],
                            style_profiles[j]['style_features']
                        )
                    })
        
        return {
            'style_matches': similarities,
            'total_style_matches': len(similarities)
        }
    
    def analyze_behavioral_correlation(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavioral patterns across platforms"""
        behavioral_profiles = []
        
        for profile_data in profiles_data:
            platform = profile_data.get('platform', '')
            posts = profile_data.get('posts', [])
            
            behavior_features = self._extract_behavioral_features(posts)
            
            behavioral_profiles.append({
                'platform': platform,
                'profile_data': profile_data,
                'behavior_features': behavior_features
            })
        
        # Find behavioral correlations
        correlations = []
        for i in range(len(behavioral_profiles)):
            for j in range(i + 1, len(behavioral_profiles)):
                correlation = self._calculate_behavioral_correlation(
                    behavioral_profiles[i]['behavior_features'],
                    behavioral_profiles[j]['behavior_features']
                )
                
                if correlation > 0.6:  # Correlation threshold
                    correlations.append({
                        'profile1': behavioral_profiles[i]['platform'],
                        'profile2': behavioral_profiles[j]['platform'],
                        'correlation_score': correlation,
                        'matching_behaviors': self._get_matching_behaviors(
                            behavioral_profiles[i]['behavior_features'],
                            behavioral_profiles[j]['behavior_features']
                        )
                    })
        
        return {
            'behavioral_correlations': correlations,
            'total_correlations': len(correlations)
        }
    
    def analyze_content_overlap(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content overlap and cross-posting patterns"""
        content_hashes = defaultdict(list)
        
        # Create content fingerprints
        for profile_data in profiles_data:
            platform = profile_data.get('platform', '')
            posts = profile_data.get('posts', [])
            
            for post in posts:
                content = post.get('caption', '') or post.get('content', '')
                if content and len(content) > 20:
                    # Create content hash
                    content_hash = self._create_content_hash(content)
                    content_hashes[content_hash].append({
                        'platform': platform,
                        'post': post,
                        'content': content[:200]
                    })
        
        # Find cross-posted content
        cross_posts = []
        for content_hash, posts in content_hashes.items():
            if len(posts) > 1:
                platforms = [p['platform'] for p in posts]
                if len(set(platforms)) > 1:  # Content appears on multiple platforms
                    cross_posts.append({
                        'content_hash': content_hash,
                        'platforms': platforms,
                        'posts': posts,
                        'cross_platform_count': len(set(platforms))
                    })
        
        return {
            'cross_posted_content': cross_posts,
            'total_cross_posts': len(cross_posts),
            'cross_posting_ratio': len(cross_posts) / max(1, len(content_hashes))
        }
    
    def analyze_timing_correlation(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posting time correlations across platforms"""
        platform_timings = {}
        
        for profile_data in profiles_data:
            platform = profile_data.get('platform', '')
            posts = profile_data.get('posts', [])
            
            post_times = []
            for post in posts:
                date_str = post.get('date')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        post_times.append(dt)
                    except:
                        continue
            
            if post_times:
                platform_timings[platform] = {
                    'post_times': post_times,
                    'profile_data': profile_data
                }
        
        # Find timing correlations
        timing_correlations = []
        platforms = list(platform_timings.keys())
        
        for i in range(len(platforms)):
            for j in range(i + 1, len(platforms)):
                platform1, platform2 = platforms[i], platforms[j]
                
                correlation = self._calculate_timing_correlation(
                    platform_timings[platform1]['post_times'],
                    platform_timings[platform2]['post_times']
                )
                
                if correlation > 0.5:
                    timing_correlations.append({
                        'platform1': platform1,
                        'platform2': platform2,
                        'timing_correlation': correlation,
                        'synchronized_posts': self._find_synchronized_posts(
                            platform_timings[platform1]['post_times'],
                            platform_timings[platform2]['post_times']
                        )
                    })
        
        return {
            'timing_correlations': timing_correlations,
            'total_timing_matches': len(timing_correlations)
        }
    
    def generate_identity_confidence_score(self, all_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall confidence score for cross-platform identity matching"""
        confidence_factors = []
        
        # Username matching
        if 'cross_platform_matches' in all_analyses:
            username_matches = len([m for m in all_analyses['cross_platform_matches'].get('matches', []) 
                                  if m['match_type'] == 'username'])
            if username_matches > 0:
                confidence_factors.append(('username_match', 0.9))
        
        # Writing style correlation
        if 'writing_style' in all_analyses:
            style_matches = len(all_analyses['writing_style'].get('style_matches', []))
            if style_matches > 0:
                confidence_factors.append(('writing_style', 0.8))
        
        # Behavioral correlation
        if 'behavioral_correlation' in all_analyses:
            behavior_matches = len(all_analyses['behavioral_correlation'].get('behavioral_correlations', []))
            if behavior_matches > 0:
                confidence_factors.append(('behavioral_pattern', 0.7))
        
        # Content overlap
        if 'content_overlap' in all_analyses:
            cross_posts = len(all_analyses['content_overlap'].get('cross_posted_content', []))
            if cross_posts > 0:
                confidence_factors.append(('content_overlap', 0.85))
        
        # Timing correlation
        if 'timing_correlation' in all_analyses:
            timing_matches = len(all_analyses['timing_correlation'].get('timing_correlations', []))
            if timing_matches > 0:
                confidence_factors.append(('timing_pattern', 0.6))
        
        # Calculate weighted confidence score
        if confidence_factors:
            total_weight = sum(weight for _, weight in confidence_factors)
            confidence_score = total_weight / len(confidence_factors)
        else:
            confidence_score = 0.0
        
        return {
            'overall_confidence': confidence_score,
            'confidence_factors': confidence_factors,
            'identity_likelihood': self._get_likelihood_label(confidence_score),
            'matching_indicators': len(confidence_factors)
        }
    
    def _normalize_username(self, username: str) -> str:
        """Normalize username for comparison"""
        if not username:
            return ''
        
        # Remove common variations
        normalized = username.lower()
        normalized = re.sub(r'[._-]', '', normalized)
        normalized = re.sub(r'\d+$', '', normalized)  # Remove trailing numbers
        
        return normalized
    
    def _normalize_name(self, name: str) -> str:
        """Normalize display name for comparison"""
        if not name:
            return ''
        
        # Remove common variations
        normalized = name.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _get_bio_hash(self, bio: str) -> str:
        """Create hash for bio similarity"""
        # Remove URLs, mentions, hashtags for better matching
        cleaned_bio = re.sub(r'http\S+|@\w+|#\w+', '', bio.lower())
        cleaned_bio = re.sub(r'[^\w\s]', '', cleaned_bio)
        cleaned_bio = ' '.join(cleaned_bio.split())
        
        return hashlib.md5(cleaned_bio.encode()).hexdigest()[:8]
    
    def _extract_writing_style_features(self, text: str) -> Dict[str, float]:
        """Extract writing style features from text"""
        if not text:
            return {}
        
        # Basic linguistic features
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        chars = len(text)
        
        # Punctuation usage
        exclamations = text.count('!')
        questions = text.count('?')
        commas = text.count(',')
        
        # Capitalization patterns
        uppercase_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
        
        # Emoji usage
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        
        # Hashtag and mention usage
        hashtags = len(re.findall(r'#\w+', text))
        mentions = len(re.findall(r'@\w+', text))
        
        return {
            'avg_sentence_length': words / max(1, sentences),
            'avg_word_length': chars / max(1, words),
            'exclamation_ratio': exclamations / max(1, sentences),
            'question_ratio': questions / max(1, sentences),
            'comma_ratio': commas / max(1, words),
            'uppercase_ratio': uppercase_words / max(1, words),
            'emoji_ratio': emoji_count / max(1, words),
            'hashtag_ratio': hashtags / max(1, words),
            'mention_ratio': mentions / max(1, words)
        }
    
    def _calculate_style_similarity(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Calculate similarity between writing style features"""
        if not features1 or not features2:
            return 0.0
        
        common_keys = set(features1.keys()) & set(features2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1, val2 = features1[key], features2[key]
            max_val = max(val1, val2, 1)  # Avoid division by zero
            similarity = 1 - abs(val1 - val2) / max_val
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    def _extract_behavioral_features(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract behavioral features from posts"""
        if not posts:
            return {}
        
        # Posting frequency
        post_dates = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    post_dates.append(dt)
                except:
                    continue
        
        # Time-based patterns
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        
        for dt in post_dates:
            hour_distribution[dt.hour] += 1
            day_distribution[dt.weekday()] += 1
        
        # Content patterns
        avg_content_length = np.mean([len(p.get('caption', '') or p.get('content', '')) for p in posts])
        
        # Engagement patterns
        likes = [p.get('likes', 0) or p.get('like_count', 0) for p in posts]
        avg_likes = np.mean(likes) if likes else 0
        
        return {
            'posting_frequency': len(posts),
            'avg_content_length': avg_content_length,
            'avg_engagement': avg_likes,
            'most_active_hour': max(hour_distribution, key=hour_distribution.get) if hour_distribution else 0,
            'most_active_day': max(day_distribution, key=day_distribution.get) if day_distribution else 0,
            'hour_distribution': dict(hour_distribution),
            'day_distribution': dict(day_distribution)
        }
    
    def _calculate_behavioral_correlation(self, behavior1: Dict[str, Any], behavior2: Dict[str, Any]) -> float:
        """Calculate behavioral correlation between two profiles"""
        if not behavior1 or not behavior2:
            return 0.0
        
        correlations = []
        
        # Time-based correlations
        if 'most_active_hour' in behavior1 and 'most_active_hour' in behavior2:
            hour_diff = abs(behavior1['most_active_hour'] - behavior2['most_active_hour'])
            hour_correlation = 1 - (hour_diff / 12)  # Normalize to 0-1
            correlations.append(hour_correlation)
        
        if 'most_active_day' in behavior1 and 'most_active_day' in behavior2:
            day_diff = abs(behavior1['most_active_day'] - behavior2['most_active_day'])
            day_correlation = 1 - (day_diff / 3.5)  # Normalize to 0-1
            correlations.append(max(0, day_correlation))
        
        # Content length correlation
        if 'avg_content_length' in behavior1 and 'avg_content_length' in behavior2:
            len1, len2 = behavior1['avg_content_length'], behavior2['avg_content_length']
            max_len = max(len1, len2, 1)
            length_correlation = 1 - abs(len1 - len2) / max_len
            correlations.append(length_correlation)
        
        return np.mean(correlations) if correlations else 0.0
    
    def _create_content_hash(self, content: str) -> str:
        """Create hash for content similarity detection"""
        # Normalize content for better matching
        normalized = content.lower()
        normalized = re.sub(r'http\S+', '', normalized)  # Remove URLs
        normalized = re.sub(r'@\w+', '', normalized)     # Remove mentions
        normalized = re.sub(r'#\w+', '', normalized)     # Remove hashtags
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = ' '.join(normalized.split())        # Normalize whitespace
        
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def _calculate_timing_correlation(self, times1: List[datetime], times2: List[datetime]) -> float:
        """Calculate timing correlation between two sets of post times"""
        if not times1 or not times2:
            return 0.0
        
        # Find posts within time windows
        synchronized_count = 0
        time_window = timedelta(hours=2)  # 2-hour window
        
        for t1 in times1:
            for t2 in times2:
                if abs(t1 - t2) <= time_window:
                    synchronized_count += 1
                    break
        
        # Calculate correlation based on synchronized posts
        max_possible = min(len(times1), len(times2))
        return synchronized_count / max_possible if max_possible > 0 else 0.0
    
    def _find_synchronized_posts(self, times1: List[datetime], times2: List[datetime]) -> List[Dict[str, Any]]:
        """Find posts that were made within a short time window"""
        synchronized = []
        time_window = timedelta(hours=2)
        
        for i, t1 in enumerate(times1):
            for j, t2 in enumerate(times2):
                if abs(t1 - t2) <= time_window:
                    synchronized.append({
                        'time1': t1.isoformat(),
                        'time2': t2.isoformat(),
                        'time_diff_minutes': abs(t1 - t2).total_seconds() / 60,
                        'post1_index': i,
                        'post2_index': j
                    })
        
        return synchronized
    
    def _consolidate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate multiple matches into unified user profiles"""
        consolidated = []
        processed_profiles = set()
        
        for match in matches:
            profiles = match['profiles']
            profile_key = tuple(sorted([f"{p[0]}:{p[1]['profile']['username']}" for p in profiles]))
            
            if profile_key not in processed_profiles:
                consolidated.append({
                    'user_id': hashlib.md5(str(profile_key).encode()).hexdigest()[:8],
                    'platforms': [p[0] for p in profiles],
                    'profiles': profiles,
                    'match_confidence': match['confidence'],
                    'match_type': match['match_type']
                })
                processed_profiles.add(profile_key)
        
        return consolidated
    
    def _get_matching_features(self, features1: Dict[str, float], features2: Dict[str, float]) -> List[str]:
        """Get list of matching style features"""
        matching = []
        threshold = 0.8
        
        common_keys = set(features1.keys()) & set(features2.keys())
        for key in common_keys:
            val1, val2 = features1[key], features2[key]
            max_val = max(val1, val2, 1)
            similarity = 1 - abs(val1 - val2) / max_val
            
            if similarity > threshold:
                matching.append(key)
        
        return matching
    
    def _get_matching_behaviors(self, behavior1: Dict[str, Any], behavior2: Dict[str, Any]) -> List[str]:
        """Get list of matching behavioral patterns"""
        matching = []
        
        # Check time patterns
        if abs(behavior1.get('most_active_hour', 0) - behavior2.get('most_active_hour', 0)) <= 2:
            matching.append('similar_active_hours')
        
        if abs(behavior1.get('most_active_day', 0) - behavior2.get('most_active_day', 0)) <= 1:
            matching.append('similar_active_days')
        
        # Check content patterns
        len1 = behavior1.get('avg_content_length', 0)
        len2 = behavior2.get('avg_content_length', 0)
        if len1 > 0 and len2 > 0:
            if abs(len1 - len2) / max(len1, len2) < 0.3:
                matching.append('similar_content_length')
        
        return matching
    
    def _get_likelihood_label(self, confidence_score: float) -> str:
        """Convert confidence score to likelihood label"""
        if confidence_score >= 0.8:
            return 'Very High'
        elif confidence_score >= 0.6:
            return 'High'
        elif confidence_score >= 0.4:
            return 'Medium'
        elif confidence_score >= 0.2:
            return 'Low'
        else:
            return 'Very Low'