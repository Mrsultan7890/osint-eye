import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
from typing import Dict, List, Any, Tuple
from utils.logger import setup_logger

logger = setup_logger()

class AdvancedSocialAnalyzer:
    def __init__(self):
        self.personality_keywords = {
            'extroversion': ['party', 'social', 'friends', 'crowd', 'event', 'meeting'],
            'neuroticism': ['stress', 'worry', 'anxiety', 'nervous', 'upset', 'sad'],
            'openness': ['art', 'creative', 'new', 'explore', 'adventure', 'culture'],
            'conscientiousness': ['plan', 'organize', 'schedule', 'goal', 'achieve', 'work'],
            'agreeableness': ['help', 'kind', 'support', 'care', 'love', 'family']
        }
        
    def analyze_profile_authenticity(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect fake profiles using multiple indicators"""
        profile = profile_data.get('profile', {})
        posts = profile_data.get('posts', [])
        
        authenticity_score = 100
        red_flags = []
        
        # Profile completeness check
        if not profile.get('biography') or len(profile.get('biography', '')) < 10:
            authenticity_score -= 15
            red_flags.append('Incomplete bio')
        
        # Follower-to-following ratio
        followers = profile.get('followers', 0)
        following = profile.get('following', 0)
        if following > 0:
            ratio = followers / following
            if ratio < 0.1 or ratio > 100:
                authenticity_score -= 20
                red_flags.append('Suspicious follower ratio')
        
        # Post frequency analysis
        if posts:
            post_dates = [p.get('date') for p in posts if p.get('date')]
            if len(post_dates) > 1:
                intervals = self._calculate_posting_intervals(post_dates)
                if self._detect_bot_patterns(intervals):
                    authenticity_score -= 25
                    red_flags.append('Bot-like posting pattern')
        
        # Content diversity
        content_diversity = self._analyze_content_diversity(posts)
        if content_diversity < 0.3:
            authenticity_score -= 15
            red_flags.append('Low content diversity')
        
        return {
            'authenticity_score': max(0, authenticity_score),
            'red_flags': red_flags,
            'risk_level': 'High' if authenticity_score < 50 else 'Medium' if authenticity_score < 75 else 'Low'
        }
    
    def analyze_personality_traits(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract Big Five personality traits from content"""
        all_text = ' '.join([p.get('caption', '') or p.get('content', '') for p in posts])
        
        trait_scores = {}
        for trait, keywords in self.personality_keywords.items():
            score = 0
            for keyword in keywords:
                score += all_text.lower().count(keyword)
            
            # Normalize score
            trait_scores[trait] = min(1.0, score / max(1, len(posts)))
        
        return trait_scores
    
    def analyze_behavioral_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavioral patterns and routines"""
        if not posts:
            return {}
        
        # Time-based patterns
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    hour_activity[dt.hour] += 1
                    day_activity[dt.strftime('%A')] += 1
                except:
                    continue
        
        # Device/platform patterns
        platform_usage = self._analyze_platform_patterns(posts)
        
        # Content patterns
        content_patterns = self._analyze_content_patterns(posts)
        
        return {
            'time_patterns': {
                'most_active_hour': max(hour_activity, key=hour_activity.get) if hour_activity else None,
                'most_active_day': max(day_activity, key=day_activity.get) if day_activity else None,
                'activity_distribution': dict(hour_activity)
            },
            'platform_patterns': platform_usage,
            'content_patterns': content_patterns,
            'routine_score': self._calculate_routine_score(hour_activity, day_activity)
        }
    
    def analyze_social_connections(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze social connections and interaction patterns"""
        mentions = []
        hashtags = []
        interaction_strength = defaultdict(int)
        
        for post in posts:
            post_mentions = post.get('mentions', [])
            post_hashtags = post.get('hashtags', [])
            
            mentions.extend(post_mentions)
            hashtags.extend(post_hashtags)
            
            # Calculate interaction strength
            for mention in post_mentions:
                interaction_strength[mention] += 1
        
        # Find communities/groups
        communities = self._detect_communities(mentions, hashtags)
        
        return {
            'total_unique_mentions': len(set(mentions)),
            'top_connections': dict(Counter(mentions).most_common(10)),
            'interaction_strength': dict(interaction_strength),
            'communities': communities,
            'social_diversity': len(set(mentions)) / max(1, len(mentions)) if mentions else 0
        }
    
    def analyze_content_evolution(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track content and behavior evolution over time"""
        if len(posts) < 2:
            return {}
        
        # Sort posts by date
        dated_posts = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dated_posts.append((dt, post))
                except:
                    continue
        
        dated_posts.sort(key=lambda x: x[0])
        
        # Analyze sentiment evolution
        sentiment_evolution = self._analyze_sentiment_evolution(dated_posts)
        
        # Analyze topic evolution
        topic_evolution = self._analyze_topic_evolution(dated_posts)
        
        # Analyze language evolution
        language_evolution = self._analyze_language_evolution(dated_posts)
        
        return {
            'sentiment_evolution': sentiment_evolution,
            'topic_evolution': topic_evolution,
            'language_evolution': language_evolution,
            'content_maturity': self._calculate_content_maturity(dated_posts)
        }
    
    def analyze_influence_network(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze influence and information propagation"""
        repost_patterns = []
        original_content_ratio = 0
        influence_indicators = []
        
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            
            # Check for repost indicators
            if any(indicator in content.lower() for indicator in ['rt @', 'repost', 'via @', 'credit:']):
                repost_patterns.append(post)
            else:
                original_content_ratio += 1
        
        original_content_ratio = original_content_ratio / len(posts) if posts else 0
        
        # Analyze engagement patterns
        engagement_analysis = self._analyze_engagement_patterns(posts)
        
        return {
            'original_content_ratio': original_content_ratio,
            'repost_frequency': len(repost_patterns) / len(posts) if posts else 0,
            'engagement_analysis': engagement_analysis,
            'influence_score': self._calculate_influence_score(posts, original_content_ratio)
        }
    
    def detect_anomalies(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect unusual behavior patterns"""
        anomalies = []
        
        if not posts:
            return {'anomalies': anomalies}
        
        # Posting frequency anomalies
        posting_intervals = self._get_posting_intervals(posts)
        if posting_intervals:
            avg_interval = np.mean(posting_intervals)
            std_interval = np.std(posting_intervals)
            
            for i, interval in enumerate(posting_intervals):
                if abs(interval - avg_interval) > 2 * std_interval:
                    anomalies.append({
                        'type': 'posting_frequency',
                        'description': f'Unusual posting interval: {interval:.2f} hours',
                        'post_index': i
                    })
        
        # Content length anomalies
        content_lengths = [len(p.get('caption', '') or p.get('content', '')) for p in posts]
        if content_lengths:
            avg_length = np.mean(content_lengths)
            std_length = np.std(content_lengths)
            
            for i, length in enumerate(content_lengths):
                if abs(length - avg_length) > 2 * std_length:
                    anomalies.append({
                        'type': 'content_length',
                        'description': f'Unusual content length: {length} characters',
                        'post_index': i
                    })
        
        # Sentiment anomalies
        sentiments = []
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                sentiment = TextBlob(content).sentiment.polarity
                sentiments.append(sentiment)
        
        if sentiments:
            avg_sentiment = np.mean(sentiments)
            std_sentiment = np.std(sentiments)
            
            for i, sentiment in enumerate(sentiments):
                if abs(sentiment - avg_sentiment) > 2 * std_sentiment:
                    anomalies.append({
                        'type': 'sentiment',
                        'description': f'Unusual sentiment: {sentiment:.2f}',
                        'post_index': i
                    })
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'risk_score': min(100, len(anomalies) * 10)
        }
    
    def _calculate_posting_intervals(self, post_dates: List[str]) -> List[float]:
        """Calculate intervals between posts in hours"""
        intervals = []
        dates = []
        
        for date_str in post_dates:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                dates.append(dt)
            except:
                continue
        
        dates.sort()
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).total_seconds() / 3600
            intervals.append(interval)
        
        return intervals
    
    def _detect_bot_patterns(self, intervals: List[float]) -> bool:
        """Detect bot-like posting patterns"""
        if len(intervals) < 3:
            return False
        
        # Check for too regular intervals
        std_dev = np.std(intervals)
        mean_interval = np.mean(intervals)
        
        # Very regular posting (low variance) might indicate bot
        if std_dev < mean_interval * 0.1 and mean_interval < 1:  # Less than 1 hour
            return True
        
        # Check for burst patterns
        short_intervals = [i for i in intervals if i < 0.1]  # Less than 6 minutes
        if len(short_intervals) > len(intervals) * 0.3:
            return True
        
        return False
    
    def _analyze_content_diversity(self, posts: List[Dict[str, Any]]) -> float:
        """Calculate content diversity score"""
        if not posts:
            return 0
        
        contents = []
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                contents.append(content)
        
        if len(contents) < 2:
            return 0
        
        # Use TF-IDF to measure content similarity
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(contents)
            
            # Calculate average pairwise similarity
            similarities = []
            for i in range(len(contents)):
                for j in range(i+1, len(contents)):
                    sim = cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])[0][0]
                    similarities.append(sim)
            
            avg_similarity = np.mean(similarities) if similarities else 0
            diversity_score = 1 - avg_similarity
            
            return max(0, min(1, diversity_score))
        except:
            return 0.5  # Default moderate diversity
    
    def _analyze_platform_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze platform usage patterns"""
        # This would analyze posting patterns across different platforms
        # For now, return basic analysis
        return {
            'cross_platform_consistency': 0.8,  # Placeholder
            'platform_preference': 'mobile',     # Placeholder
            'posting_method': 'manual'           # Placeholder
        }
    
    def _analyze_content_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content type and style patterns"""
        content_types = {'text': 0, 'image': 0, 'video': 0, 'link': 0}
        
        for post in posts:
            if post.get('is_video'):
                content_types['video'] += 1
            elif post.get('url'):
                content_types['link'] += 1
            elif post.get('caption') or post.get('content'):
                content_types['text'] += 1
            else:
                content_types['image'] += 1
        
        total = sum(content_types.values())
        if total > 0:
            content_types = {k: v/total for k, v in content_types.items()}
        
        return content_types
    
    def _calculate_routine_score(self, hour_activity: Dict, day_activity: Dict) -> float:
        """Calculate how routine/predictable the posting behavior is"""
        if not hour_activity or not day_activity:
            return 0
        
        # Calculate variance in posting times
        hour_variance = np.var(list(hour_activity.values())) if hour_activity else 0
        day_variance = np.var(list(day_activity.values())) if day_activity else 0
        
        # Higher variance = less routine
        routine_score = 1 / (1 + hour_variance + day_variance)
        return min(1, routine_score)
    
    def _detect_communities(self, mentions: List[str], hashtags: List[str]) -> List[Dict[str, Any]]:
        """Detect communities based on mentions and hashtags"""
        communities = []
        
        # Group by common hashtags
        hashtag_groups = defaultdict(list)
        for hashtag in set(hashtags):
            if hashtags.count(hashtag) > 1:
                hashtag_groups[hashtag] = [m for m in mentions if hashtag in hashtags]
        
        for hashtag, members in hashtag_groups.items():
            if len(members) > 2:
                communities.append({
                    'type': 'hashtag_community',
                    'identifier': hashtag,
                    'members': list(set(members)),
                    'strength': len(members)
                })
        
        return communities
    
    def _analyze_sentiment_evolution(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze how sentiment changes over time"""
        sentiments = []
        dates = []
        
        for date, post in dated_posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                sentiment = TextBlob(content).sentiment.polarity
                sentiments.append(sentiment)
                dates.append(date)
        
        if len(sentiments) < 2:
            return {}
        
        # Calculate trend
        x = np.arange(len(sentiments))
        trend = np.polyfit(x, sentiments, 1)[0]
        
        return {
            'sentiment_trend': 'improving' if trend > 0.01 else 'declining' if trend < -0.01 else 'stable',
            'trend_strength': abs(trend),
            'average_sentiment': np.mean(sentiments),
            'sentiment_volatility': np.std(sentiments)
        }
    
    def _analyze_topic_evolution(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze how topics change over time"""
        # Simple topic analysis using keyword frequency
        early_posts = dated_posts[:len(dated_posts)//2]
        recent_posts = dated_posts[len(dated_posts)//2:]
        
        early_text = ' '.join([post.get('caption', '') or post.get('content', '') for _, post in early_posts])
        recent_text = ' '.join([post.get('caption', '') or post.get('content', '') for _, post in recent_posts])
        
        early_words = Counter(re.findall(r'\b\w+\b', early_text.lower()))
        recent_words = Counter(re.findall(r'\b\w+\b', recent_text.lower()))
        
        # Find emerging and declining topics
        emerging_topics = []
        declining_topics = []
        
        for word, count in recent_words.most_common(10):
            if word not in early_words or early_words[word] < count * 0.5:
                emerging_topics.append(word)
        
        for word, count in early_words.most_common(10):
            if word not in recent_words or recent_words[word] < count * 0.5:
                declining_topics.append(word)
        
        return {
            'emerging_topics': emerging_topics[:5],
            'declining_topics': declining_topics[:5],
            'topic_stability': len(set(early_words.keys()) & set(recent_words.keys())) / max(1, len(set(early_words.keys()) | set(recent_words.keys())))
        }
    
    def _analyze_language_evolution(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze language and writing style evolution"""
        early_posts = dated_posts[:len(dated_posts)//2]
        recent_posts = dated_posts[len(dated_posts)//2:]
        
        early_text = ' '.join([post.get('caption', '') or post.get('content', '') for _, post in early_posts])
        recent_text = ' '.join([post.get('caption', '') or post.get('content', '') for _, post in recent_posts])
        
        # Calculate readability and complexity metrics
        early_complexity = self._calculate_text_complexity(early_text)
        recent_complexity = self._calculate_text_complexity(recent_text)
        
        return {
            'complexity_change': recent_complexity - early_complexity,
            'language_maturity': 'improving' if recent_complexity > early_complexity else 'declining' if recent_complexity < early_complexity else 'stable'
        }
    
    def _calculate_content_maturity(self, dated_posts: List[Tuple]) -> float:
        """Calculate overall content maturity score"""
        if len(dated_posts) < 2:
            return 0.5
        
        # Analyze various maturity indicators
        maturity_indicators = []
        
        for _, post in dated_posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                # Length indicator
                length_score = min(1, len(content) / 200)
                
                # Punctuation usage
                punct_score = len(re.findall(r'[.!?]', content)) / max(1, len(content.split()))
                
                # Vocabulary diversity
                words = re.findall(r'\b\w+\b', content.lower())
                vocab_score = len(set(words)) / max(1, len(words)) if words else 0
                
                maturity_indicators.append((length_score + punct_score + vocab_score) / 3)
        
        return np.mean(maturity_indicators) if maturity_indicators else 0.5
    
    def _analyze_engagement_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns and quality"""
        likes = [p.get('likes', 0) or p.get('like_count', 0) for p in posts]
        comments = [p.get('comments', 0) or p.get('reply_count', 0) for p in posts]
        
        if not likes and not comments:
            return {}
        
        # Calculate engagement metrics
        avg_likes = np.mean(likes) if likes else 0
        avg_comments = np.mean(comments) if comments else 0
        
        # Engagement consistency
        like_consistency = 1 - (np.std(likes) / max(1, avg_likes)) if likes else 0
        comment_consistency = 1 - (np.std(comments) / max(1, avg_comments)) if comments else 0
        
        return {
            'average_likes': avg_likes,
            'average_comments': avg_comments,
            'engagement_consistency': (like_consistency + comment_consistency) / 2,
            'engagement_ratio': avg_comments / max(1, avg_likes) if avg_likes > 0 else 0
        }
    
    def _calculate_influence_score(self, posts: List[Dict[str, Any]], original_ratio: float) -> float:
        """Calculate overall influence score"""
        if not posts:
            return 0
        
        # Base score from original content ratio
        base_score = original_ratio * 50
        
        # Engagement bonus
        total_engagement = sum([
            (p.get('likes', 0) or p.get('like_count', 0)) + 
            (p.get('comments', 0) or p.get('reply_count', 0))
            for p in posts
        ])
        engagement_score = min(30, total_engagement / len(posts) / 10)
        
        # Consistency bonus
        consistency_score = 20 if len(posts) > 10 else len(posts) * 2
        
        return min(100, base_score + engagement_score + consistency_score)
    
    def _get_posting_intervals(self, posts: List[Dict[str, Any]]) -> List[float]:
        """Get posting intervals in hours"""
        dates = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(dt)
                except:
                    continue
        
        dates.sort()
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).total_seconds() / 3600
            intervals.append(interval)
        
        return intervals
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        if not text:
            return 0
        
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0:
            return 0
        
        avg_sentence_length = words / sentences
        avg_word_length = sum(len(word) for word in text.split()) / max(1, words)
        
        # Simple complexity score
        complexity = (avg_sentence_length * avg_word_length) / 100
        return min(1, complexity)