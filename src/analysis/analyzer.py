import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple
from textblob import TextBlob
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger()

class Analyzer:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    def analyze_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis on profile data"""
        posts = data.get('posts', [])
        profile = data.get('profile', {})
        
        logger.info(f"Analyzing profile with {len(posts)} posts")
        
        analysis = {
            'post_count': len(posts),
            'profile_analysis': self._analyze_profile_info(profile),
            'content_analysis': self._analyze_content(posts),
            'sentiment_analysis': self._analyze_sentiment(posts),
            'entity_extraction': self._extract_entities(posts),
            'activity_analysis': self._analyze_activity_patterns(posts),
            'hashtag_analysis': self._analyze_hashtags(posts),
            'engagement_analysis': self._analyze_engagement(posts)
        }
        
        # Handle case when no posts available
        if len(posts) == 0:
            logger.info("No posts available for analysis - using profile data only")
            analysis['content_analysis'] = self._analyze_profile_content(profile)
            analysis['sentiment_analysis'] = self._analyze_profile_sentiment(profile)
        
        # Calculate overall sentiment score
        sentiment_scores = [s['polarity'] for s in analysis['sentiment_analysis']]
        analysis['sentiment_score'] = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Get top keywords
        analysis['top_keywords'] = self._get_top_keywords(posts)
        
        # Activity peak
        analysis['activity_peak'] = self._get_activity_peak(posts)
        
        logger.info(f"Analysis complete: {analysis['post_count']} posts, sentiment: {analysis.get('sentiment_score', 0):.2f}")
        return analysis
    
    def _analyze_profile_info(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile information"""
        bio_text = profile.get('biography', '') or profile.get('description', '')
        
        return {
            'bio_length': len(bio_text),
            'has_external_url': bool(profile.get('external_url') or profile.get('url')),
            'is_verified': profile.get('verified', False) or profile.get('is_verified', False),
            'follower_ratio': self._calculate_follower_ratio(profile),
            'extracted_entities': self._extract_entities_from_text(bio_text)
        }
    
    def _analyze_content(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze post content"""
        all_text = []
        for post in posts:
            text = post.get('caption', '') or post.get('content', '')
            if text:
                all_text.append(text)
        
        combined_text = ' '.join(all_text)
        
        return {
            'total_characters': len(combined_text),
            'avg_post_length': len(combined_text) / len(posts) if posts else 0,
            'language_detection': self._detect_languages(all_text),
            'readability_score': self._calculate_readability(combined_text)
        }
    
    def _analyze_sentiment(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of posts"""
        sentiments = []
        
        for post in posts:
            text = post.get('caption', '') or post.get('content', '')
            if text:
                blob = TextBlob(text)
                sentiments.append({
                    'post_id': post.get('shortcode') or post.get('id'),
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity,
                    'sentiment_label': self._get_sentiment_label(blob.sentiment.polarity)
                })
        
        return sentiments
    
    def _extract_entities(self, posts: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract entities from all posts"""
        emails = set()
        phones = set()
        urls = set()
        mentions = set()
        
        for post in posts:
            text = post.get('caption', '') or post.get('content', '')
            if text:
                emails.update(self.email_pattern.findall(text))
                phones.update(self.phone_pattern.findall(text))
                urls.update(self.url_pattern.findall(text))
            
            # Add mentions from post metadata
            post_mentions = post.get('mentions', [])
            mentions.update(post_mentions)
        
        return {
            'emails': list(emails),
            'phones': list(phones),
            'urls': list(urls),
            'mentions': list(mentions)
        }
    
    def _analyze_activity_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posting activity patterns"""
        if not posts:
            return {}
        
        dates = []
        hours = []
        
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(dt.date())
                    hours.append(dt.hour)
                except:
                    continue
        
        if not dates:
            return {}
        
        # Activity by hour
        hour_counts = Counter(hours)
        most_active_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
        
        # Activity by day
        date_counts = Counter(dates)
        
        return {
            'most_active_hour': most_active_hour,
            'posts_by_hour': dict(hour_counts),
            'posts_by_date': {str(k): v for k, v in date_counts.items()},
            'posting_frequency': len(dates) / max(1, (max(dates) - min(dates)).days) if len(dates) > 1 else 0
        }
    
    def _analyze_hashtags(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze hashtag usage"""
        all_hashtags = []
        
        for post in posts:
            hashtags = post.get('hashtags', [])
            all_hashtags.extend([tag.lower() for tag in hashtags])
        
        hashtag_counts = Counter(all_hashtags)
        
        return {
            'total_hashtags': len(all_hashtags),
            'unique_hashtags': len(hashtag_counts),
            'top_hashtags': hashtag_counts.most_common(10),
            'hashtag_diversity': len(hashtag_counts) / max(1, len(all_hashtags))
        }
    
    def _analyze_engagement(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement metrics"""
        likes = []
        comments = []
        
        for post in posts:
            likes.append(post.get('likes', 0) or post.get('like_count', 0))
            comments.append(post.get('comments', 0) or post.get('reply_count', 0))
        
        return {
            'avg_likes': sum(likes) / len(likes) if likes else 0,
            'avg_comments': sum(comments) / len(comments) if comments else 0,
            'total_likes': sum(likes),
            'total_comments': sum(comments),
            'engagement_rate': (sum(likes) + sum(comments)) / len(posts) if posts else 0
        }
    
    def _extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from a single text"""
        return {
            'emails': self.email_pattern.findall(text),
            'phones': self.phone_pattern.findall(text),
            'urls': self.url_pattern.findall(text)
        }
    
    def _calculate_follower_ratio(self, profile: Dict[str, Any]) -> float:
        """Calculate follower to following ratio"""
        followers = profile.get('followers', 0) or profile.get('followers_count', 0)
        following = profile.get('followees', 0) or profile.get('friends_count', 0)
        
        return followers / max(1, following)
    
    def _detect_languages(self, texts: List[str]) -> Dict[str, int]:
        """Detect languages in texts"""
        languages = []
        for text in texts:
            try:
                blob = TextBlob(text)
                lang = blob.detect_language()
                languages.append(lang)
            except:
                continue
        
        return dict(Counter(languages))
    
    def _calculate_readability(self, text: str) -> float:
        """Simple readability score based on sentence and word length"""
        if not text:
            return 0
        
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / max(1, len(sentences))
        avg_word_length = sum(len(word) for word in words) / max(1, len(words))
        
        # Simple readability score (lower is easier)
        return avg_sentence_length * avg_word_length / 100
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity to sentiment label"""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_top_keywords(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract top keywords from posts"""
        all_text = []
        for post in posts:
            text = post.get('caption', '') or post.get('content', '')
            if text:
                all_text.append(text)
        
        combined_text = ' '.join(all_text).lower()
        words = re.findall(r'\b\w+\b', combined_text)
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(10)]
    
    def _get_activity_peak(self, posts: List[Dict[str, Any]]) -> str:
        """Get peak activity time"""
        hours = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    hours.append(dt.hour)
                except:
                    continue
        
        if not hours:
            return 'Unknown'
        
        hour_counts = Counter(hours)
        peak_hour = hour_counts.most_common(1)[0][0]
        
        if 6 <= peak_hour < 12:
            return 'Morning'
        elif 12 <= peak_hour < 18:
            return 'Afternoon'
        elif 18 <= peak_hour < 24:
            return 'Evening'
        else:
            return 'Night'