import re
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from textblob import TextBlob
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import hashlib
from typing import Dict, List, Any, Tuple
from utils.logger import setup_logger

logger = setup_logger()

class BehavioralProfiler:
    def __init__(self):
        self.personality_indicators = {
            'extroversion': {
                'high': ['party', 'social', 'friends', 'crowd', 'event', 'meeting', 'gathering'],
                'low': ['alone', 'quiet', 'solitude', 'private', 'introvert', 'home']
            },
            'neuroticism': {
                'high': ['stress', 'worry', 'anxiety', 'nervous', 'upset', 'sad', 'depressed'],
                'low': ['calm', 'relaxed', 'peaceful', 'stable', 'confident', 'secure']
            },
            'openness': {
                'high': ['art', 'creative', 'new', 'explore', 'adventure', 'culture', 'innovative'],
                'low': ['traditional', 'conventional', 'routine', 'familiar', 'conservative']
            },
            'conscientiousness': {
                'high': ['plan', 'organize', 'schedule', 'goal', 'achieve', 'work', 'discipline'],
                'low': ['spontaneous', 'flexible', 'casual', 'relaxed', 'unplanned']
            },
            'agreeableness': {
                'high': ['help', 'kind', 'support', 'care', 'love', 'family', 'compassion'],
                'low': ['compete', 'argue', 'disagree', 'conflict', 'challenge', 'critical']
            }
        }
        
        self.lifestyle_indicators = {
            'health_conscious': ['gym', 'workout', 'healthy', 'fitness', 'exercise', 'nutrition'],
            'tech_savvy': ['tech', 'coding', 'programming', 'software', 'digital', 'app'],
            'travel_enthusiast': ['travel', 'trip', 'vacation', 'explore', 'adventure', 'journey'],
            'foodie': ['food', 'restaurant', 'cooking', 'recipe', 'cuisine', 'delicious'],
            'career_focused': ['work', 'career', 'professional', 'business', 'success', 'achievement'],
            'family_oriented': ['family', 'kids', 'children', 'parents', 'home', 'together']
        }
        
    def create_comprehensive_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive behavioral profile"""
        posts = profile_data.get('posts', [])
        profile = profile_data.get('profile', {})
        
        # Personality analysis
        personality_traits = self._analyze_personality_traits(posts)
        
        # Lifestyle analysis
        lifestyle_profile = self._analyze_lifestyle_patterns(posts)
        
        # Communication style
        communication_style = self._analyze_communication_style(posts)
        
        # Emotional patterns
        emotional_profile = self._analyze_emotional_patterns(posts)
        
        # Social behavior
        social_behavior = self._analyze_social_behavior(posts, profile)
        
        # Routine analysis
        routine_patterns = self._analyze_routine_patterns(posts)
        
        # Risk assessment
        risk_profile = self._assess_behavioral_risks(posts)
        
        # Generate insights
        behavioral_insights = self._generate_behavioral_insights(
            personality_traits, lifestyle_profile, communication_style, 
            emotional_profile, social_behavior
        )
        
        return {
            'personality_traits': personality_traits,
            'lifestyle_profile': lifestyle_profile,
            'communication_style': communication_style,
            'emotional_profile': emotional_profile,
            'social_behavior': social_behavior,
            'routine_patterns': routine_patterns,
            'risk_profile': risk_profile,
            'behavioral_insights': behavioral_insights,
            'profile_completeness': self._calculate_profile_completeness(posts, profile)
        }
    
    def predict_future_behavior(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future behavior based on historical patterns"""
        if len(posts) < 5:
            return {'error': 'Insufficient data for prediction'}
        
        # Sort posts by date
        dated_posts = self._sort_posts_by_date(posts)
        
        # Analyze trends
        activity_trend = self._analyze_activity_trend(dated_posts)
        sentiment_trend = self._analyze_sentiment_trend(dated_posts)
        engagement_trend = self._analyze_engagement_trend(dated_posts)
        content_evolution = self._analyze_content_evolution(dated_posts)
        
        # Generate predictions
        predictions = {
            'activity_prediction': self._predict_activity_level(activity_trend),
            'sentiment_prediction': self._predict_sentiment_direction(sentiment_trend),
            'engagement_prediction': self._predict_engagement_pattern(engagement_trend),
            'content_prediction': self._predict_content_themes(content_evolution),
            'risk_prediction': self._predict_risk_escalation(dated_posts)
        }
        
        return {
            'predictions': predictions,
            'confidence_score': self._calculate_prediction_confidence(dated_posts),
            'trend_analysis': {
                'activity_trend': activity_trend,
                'sentiment_trend': sentiment_trend,
                'engagement_trend': engagement_trend
            }
        }
    
    def analyze_influence_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze influence and persuasion patterns"""
        influence_indicators = {
            'authority': 0,
            'social_proof': 0,
            'reciprocity': 0,
            'commitment': 0,
            'liking': 0,
            'scarcity': 0
        }
        
        authority_keywords = ['expert', 'professional', 'certified', 'qualified', 'experienced']
        social_proof_keywords = ['everyone', 'popular', 'trending', 'viral', 'thousands']
        reciprocity_keywords = ['free', 'gift', 'bonus', 'exclusive', 'special offer']
        commitment_keywords = ['promise', 'guarantee', 'commit', 'pledge', 'assure']
        liking_keywords = ['like me', 'similar', 'understand', 'relate', 'connect']
        scarcity_keywords = ['limited', 'rare', 'exclusive', 'only', 'last chance']
        
        keyword_groups = {
            'authority': authority_keywords,
            'social_proof': social_proof_keywords,
            'reciprocity': reciprocity_keywords,
            'commitment': commitment_keywords,
            'liking': liking_keywords,
            'scarcity': scarcity_keywords
        }
        
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            for influence_type, keywords in keyword_groups.items():
                for keyword in keywords:
                    if keyword in content:
                        influence_indicators[influence_type] += 1
        
        # Calculate influence score
        total_posts = len(posts)
        influence_scores = {k: v / max(1, total_posts) for k, v in influence_indicators.items()}
        overall_influence = sum(influence_scores.values()) / len(influence_scores)
        
        return {
            'influence_techniques': influence_scores,
            'overall_influence_score': overall_influence,
            'primary_influence_method': max(influence_scores, key=influence_scores.get),
            'persuasion_style': self._determine_persuasion_style(influence_scores)
        }
    
    def detect_behavioral_anomalies(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect unusual behavioral patterns"""
        if len(posts) < 10:
            return {'error': 'Insufficient data for anomaly detection'}
        
        anomalies = []
        
        # Posting frequency anomalies
        posting_intervals = self._calculate_posting_intervals(posts)
        if posting_intervals:
            freq_anomalies = self._detect_frequency_anomalies(posting_intervals)
            anomalies.extend(freq_anomalies)
        
        # Content length anomalies
        content_lengths = [len(p.get('caption', '') or p.get('content', '')) for p in posts]
        length_anomalies = self._detect_length_anomalies(content_lengths)
        anomalies.extend(length_anomalies)
        
        # Sentiment anomalies
        sentiment_anomalies = self._detect_sentiment_anomalies(posts)
        anomalies.extend(sentiment_anomalies)
        
        # Engagement anomalies
        engagement_anomalies = self._detect_engagement_anomalies(posts)
        anomalies.extend(engagement_anomalies)
        
        # Topic shift anomalies
        topic_anomalies = self._detect_topic_shift_anomalies(posts)
        anomalies.extend(topic_anomalies)
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'anomaly_score': min(100, len(anomalies) * 10),
            'behavioral_consistency': 100 - min(100, len(anomalies) * 10)
        }
    
    def _analyze_personality_traits(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze Big Five personality traits"""
        trait_scores = {}
        
        for trait, indicators in self.personality_indicators.items():
            high_score = 0
            low_score = 0
            
            for post in posts:
                content = (post.get('caption', '') or post.get('content', '')).lower()
                
                for keyword in indicators['high']:
                    high_score += content.count(keyword)
                
                for keyword in indicators['low']:
                    low_score += content.count(keyword)
            
            # Calculate normalized score (-1 to 1, where 1 is high trait, -1 is low trait)
            total_indicators = high_score + low_score
            if total_indicators > 0:
                trait_scores[trait] = (high_score - low_score) / total_indicators
            else:
                trait_scores[trait] = 0.0
        
        return trait_scores
    
    def _analyze_lifestyle_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze lifestyle and interest patterns"""
        lifestyle_scores = {}
        
        for lifestyle, keywords in self.lifestyle_indicators.items():
            score = 0
            
            for post in posts:
                content = (post.get('caption', '') or post.get('content', '')).lower()
                
                for keyword in keywords:
                    score += content.count(keyword)
            
            # Normalize by post count
            lifestyle_scores[lifestyle] = score / max(1, len(posts))
        
        return lifestyle_scores
    
    def _analyze_communication_style(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication style and patterns"""
        if not posts:
            return {}
        
        all_text = ' '.join([p.get('caption', '') or p.get('content', '') for p in posts])
        
        # Basic metrics
        total_chars = len(all_text)
        total_words = len(all_text.split())
        sentences = len(re.findall(r'[.!?]+', all_text))
        
        # Punctuation analysis
        exclamations = all_text.count('!')
        questions = all_text.count('?')
        
        # Capitalization
        uppercase_words = len(re.findall(r'\b[A-Z]{2,}\b', all_text))
        
        # Emoji usage
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', all_text))
        
        # Formality indicators
        formal_words = ['therefore', 'however', 'furthermore', 'consequently', 'nevertheless']
        informal_words = ['lol', 'omg', 'btw', 'tbh', 'imo', 'gonna', 'wanna']
        
        formal_count = sum(all_text.lower().count(word) for word in formal_words)
        informal_count = sum(all_text.lower().count(word) for word in informal_words)
        
        return {
            'avg_post_length': total_chars / max(1, len(posts)),
            'avg_words_per_post': total_words / max(1, len(posts)),
            'avg_sentence_length': total_words / max(1, sentences),
            'exclamation_ratio': exclamations / max(1, sentences),
            'question_ratio': questions / max(1, sentences),
            'uppercase_usage': uppercase_words / max(1, total_words),
            'emoji_usage': emoji_count / max(1, total_words),
            'formality_score': (formal_count - informal_count) / max(1, formal_count + informal_count),
            'communication_style': self._determine_communication_style(formal_count, informal_count, emoji_count)
        }
    
    def _analyze_emotional_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotional patterns and stability"""
        emotions = []
        sentiment_scores = []
        
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                blob = TextBlob(content)
                sentiment_scores.append(blob.sentiment.polarity)
                
                # Emotion detection (simplified)
                emotion = self._detect_emotion(content.lower())
                emotions.append(emotion)
        
        if not sentiment_scores:
            return {}
        
        # Calculate emotional metrics
        avg_sentiment = np.mean(sentiment_scores)
        sentiment_volatility = np.std(sentiment_scores)
        emotion_distribution = Counter(emotions)
        
        # Emotional stability
        stability_score = 1 - min(1, sentiment_volatility * 2)
        
        return {
            'average_sentiment': avg_sentiment,
            'sentiment_volatility': sentiment_volatility,
            'emotional_stability': stability_score,
            'dominant_emotion': emotion_distribution.most_common(1)[0][0] if emotions else 'neutral',
            'emotion_distribution': dict(emotion_distribution),
            'emotional_range': max(sentiment_scores) - min(sentiment_scores) if sentiment_scores else 0
        }
    
    def _analyze_social_behavior(self, posts: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social interaction patterns"""
        mentions = []
        hashtags = []
        
        for post in posts:
            mentions.extend(post.get('mentions', []))
            hashtags.extend(post.get('hashtags', []))
        
        # Social metrics
        unique_mentions = len(set(mentions))
        unique_hashtags = len(set(hashtags))
        
        # Engagement metrics
        total_likes = sum([p.get('likes', 0) or p.get('like_count', 0) for p in posts])
        total_comments = sum([p.get('comments', 0) or p.get('reply_count', 0) for p in posts])
        
        # Social network size indicators
        followers = profile.get('followers', 0) or profile.get('followers_count', 0)
        following = profile.get('following', 0) or profile.get('friends_count', 0)
        
        return {
            'social_reach': unique_mentions,
            'community_participation': unique_hashtags,
            'avg_engagement': (total_likes + total_comments) / max(1, len(posts)),
            'follower_ratio': followers / max(1, following) if following > 0 else 0,
            'social_activity_level': (len(mentions) + len(hashtags)) / max(1, len(posts)),
            'interaction_style': self._determine_interaction_style(mentions, hashtags, posts)
        }
    
    def _analyze_routine_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posting routines and patterns"""
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
            return {}
        
        # Time-based analysis
        hours = [dt.hour for dt in post_times]
        days = [dt.weekday() for dt in post_times]
        
        hour_distribution = Counter(hours)
        day_distribution = Counter(days)
        
        # Routine strength
        routine_strength = self._calculate_routine_strength(hour_distribution, day_distribution)
        
        return {
            'most_active_hour': hour_distribution.most_common(1)[0][0] if hours else None,
            'most_active_day': day_distribution.most_common(1)[0][0] if days else None,
            'posting_consistency': routine_strength,
            'time_distribution': dict(hour_distribution),
            'day_distribution': dict(day_distribution),
            'routine_type': self._classify_routine_type(hour_distribution)
        }
    
    def _assess_behavioral_risks(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess behavioral risk indicators"""
        risk_indicators = {
            'impulsivity': 0,
            'aggression': 0,
            'isolation': 0,
            'instability': 0
        }
        
        # Risk keyword mapping
        risk_keywords = {
            'impulsivity': ['impulse', 'sudden', 'immediately', 'right now', 'can\'t wait'],
            'aggression': ['angry', 'hate', 'fight', 'destroy', 'kill', 'attack'],
            'isolation': ['alone', 'nobody', 'isolated', 'lonely', 'abandoned'],
            'instability': ['chaos', 'unstable', 'crazy', 'insane', 'losing it']
        }
        
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            for risk_type, keywords in risk_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        risk_indicators[risk_type] += 1
        
        # Normalize scores
        total_posts = len(posts)
        normalized_risks = {k: v / max(1, total_posts) for k, v in risk_indicators.items()}
        
        # Overall risk score
        overall_risk = sum(normalized_risks.values()) / len(normalized_risks)
        
        return {
            'risk_indicators': normalized_risks,
            'overall_risk_score': overall_risk,
            'risk_level': self._classify_risk_level(overall_risk),
            'primary_risk_factor': max(normalized_risks, key=normalized_risks.get) if any(normalized_risks.values()) else None
        }
    
    def _generate_behavioral_insights(self, personality, lifestyle, communication, emotional, social) -> List[str]:
        """Generate behavioral insights and recommendations"""
        insights = []
        
        # Personality insights
        if personality.get('extroversion', 0) > 0.5:
            insights.append("Highly social and outgoing personality")
        elif personality.get('extroversion', 0) < -0.5:
            insights.append("Prefers solitude and quiet environments")
        
        if personality.get('neuroticism', 0) > 0.5:
            insights.append("Shows signs of emotional instability or stress")
        
        # Communication insights
        if communication.get('formality_score', 0) > 0.3:
            insights.append("Uses formal, professional communication style")
        elif communication.get('formality_score', 0) < -0.3:
            insights.append("Prefers casual, informal communication")
        
        # Emotional insights
        if emotional.get('emotional_stability', 0) < 0.3:
            insights.append("Displays high emotional volatility")
        elif emotional.get('emotional_stability', 0) > 0.7:
            insights.append("Shows consistent emotional stability")
        
        # Social insights
        if social.get('social_activity_level', 0) > 2:
            insights.append("Highly active in social interactions")
        elif social.get('social_activity_level', 0) < 0.5:
            insights.append("Limited social media interaction")
        
        return insights
    
    def _calculate_profile_completeness(self, posts: List[Dict[str, Any]], profile: Dict[str, Any]) -> float:
        """Calculate how complete the behavioral profile is"""
        completeness_factors = []
        
        # Post volume
        post_score = min(1.0, len(posts) / 50)  # 50 posts = full score
        completeness_factors.append(post_score)
        
        # Profile information
        profile_fields = ['biography', 'description', 'followers', 'following']
        profile_score = sum(1 for field in profile_fields if profile.get(field)) / len(profile_fields)
        completeness_factors.append(profile_score)
        
        # Content diversity
        if posts:
            content_types = set()
            for post in posts:
                if post.get('is_video'):
                    content_types.add('video')
                elif post.get('caption'):
                    content_types.add('text')
                else:
                    content_types.add('image')
            
            diversity_score = len(content_types) / 3  # 3 types max
            completeness_factors.append(diversity_score)
        
        return np.mean(completeness_factors)
    
    def _sort_posts_by_date(self, posts: List[Dict[str, Any]]) -> List[Tuple]:
        """Sort posts by date and return tuples of (datetime, post)"""
        dated_posts = []
        
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dated_posts.append((dt, post))
                except:
                    continue
        
        return sorted(dated_posts, key=lambda x: x[0])
    
    def _detect_emotion(self, content: str) -> str:
        """Simple emotion detection from content"""
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful', 'great'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'disappointed'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'unexpected']
        }
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(content.count(keyword) for keyword in keywords)
            emotion_scores[emotion] = score
        
        if any(emotion_scores.values()):
            return max(emotion_scores, key=emotion_scores.get)
        else:
            return 'neutral'
    
    def _determine_communication_style(self, formal_count: int, informal_count: int, emoji_count: int) -> str:
        """Determine overall communication style"""
        if formal_count > informal_count and emoji_count < 5:
            return 'formal'
        elif informal_count > formal_count or emoji_count > 10:
            return 'casual'
        else:
            return 'mixed'
    
    def _determine_interaction_style(self, mentions: List[str], hashtags: List[str], posts: List[Dict]) -> str:
        """Determine social interaction style"""
        mention_ratio = len(mentions) / max(1, len(posts))
        hashtag_ratio = len(hashtags) / max(1, len(posts))
        
        if mention_ratio > 2:
            return 'highly_interactive'
        elif hashtag_ratio > 3:
            return 'community_focused'
        elif mention_ratio < 0.5 and hashtag_ratio < 0.5:
            return 'broadcasting'
        else:
            return 'balanced'
    
    def _calculate_routine_strength(self, hour_dist: Counter, day_dist: Counter) -> float:
        """Calculate how routine/predictable the behavior is"""
        # Higher concentration = stronger routine
        total_hours = sum(hour_dist.values())
        total_days = sum(day_dist.values())
        
        if total_hours == 0 or total_days == 0:
            return 0
        
        # Calculate entropy (lower entropy = more routine)
        hour_entropy = -sum((count/total_hours) * np.log2(count/total_hours) for count in hour_dist.values() if count > 0)
        day_entropy = -sum((count/total_days) * np.log2(count/total_days) for count in day_dist.values() if count > 0)
        
        # Normalize and invert (higher score = more routine)
        max_hour_entropy = np.log2(24)  # Maximum possible entropy for hours
        max_day_entropy = np.log2(7)    # Maximum possible entropy for days
        
        routine_score = 1 - ((hour_entropy / max_hour_entropy + day_entropy / max_day_entropy) / 2)
        return max(0, routine_score)
    
    def _classify_routine_type(self, hour_dist: Counter) -> str:
        """Classify the type of posting routine"""
        if not hour_dist:
            return 'irregular'
        
        peak_hour = hour_dist.most_common(1)[0][0]
        
        if 6 <= peak_hour <= 9:
            return 'morning_routine'
        elif 12 <= peak_hour <= 14:
            return 'lunch_routine'
        elif 17 <= peak_hour <= 20:
            return 'evening_routine'
        elif 21 <= peak_hour <= 23:
            return 'night_routine'
        else:
            return 'irregular'
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify overall risk level"""
        if risk_score > 0.7:
            return 'high'
        elif risk_score > 0.4:
            return 'medium'
        elif risk_score > 0.1:
            return 'low'
        else:
            return 'minimal'
    
    def _calculate_posting_intervals(self, posts: List[Dict[str, Any]]) -> List[float]:
        """Calculate intervals between posts in hours"""
        post_times = []
        
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    post_times.append(dt)
                except:
                    continue
        
        post_times.sort()
        intervals = []
        
        for i in range(1, len(post_times)):
            interval = (post_times[i] - post_times[i-1]).total_seconds() / 3600
            intervals.append(interval)
        
        return intervals
    
    def _detect_frequency_anomalies(self, intervals: List[float]) -> List[Dict[str, Any]]:
        """Detect posting frequency anomalies"""
        if len(intervals) < 3:
            return []
        
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        anomalies = []
        for i, interval in enumerate(intervals):
            if abs(interval - mean_interval) > 2 * std_interval:
                anomalies.append({
                    'type': 'posting_frequency',
                    'description': f'Unusual posting interval: {interval:.2f} hours',
                    'severity': 'high' if abs(interval - mean_interval) > 3 * std_interval else 'medium',
                    'position': i
                })
        
        return anomalies
    
    def _detect_length_anomalies(self, lengths: List[int]) -> List[Dict[str, Any]]:
        """Detect content length anomalies"""
        if len(lengths) < 3:
            return []
        
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        anomalies = []
        for i, length in enumerate(lengths):
            if abs(length - mean_length) > 2 * std_length:
                anomalies.append({
                    'type': 'content_length',
                    'description': f'Unusual content length: {length} characters',
                    'severity': 'high' if abs(length - mean_length) > 3 * std_length else 'medium',
                    'position': i
                })
        
        return anomalies
    
    def _detect_sentiment_anomalies(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sentiment anomalies"""
        sentiments = []
        
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                sentiment = TextBlob(content).sentiment.polarity
                sentiments.append(sentiment)
        
        if len(sentiments) < 3:
            return []
        
        mean_sentiment = np.mean(sentiments)
        std_sentiment = np.std(sentiments)
        
        anomalies = []
        for i, sentiment in enumerate(sentiments):
            if abs(sentiment - mean_sentiment) > 2 * std_sentiment:
                anomalies.append({
                    'type': 'sentiment',
                    'description': f'Unusual sentiment: {sentiment:.2f}',
                    'severity': 'high' if abs(sentiment - mean_sentiment) > 3 * std_sentiment else 'medium',
                    'position': i
                })
        
        return anomalies
    
    def _detect_engagement_anomalies(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect engagement anomalies"""
        engagements = []
        
        for post in posts:
            likes = post.get('likes', 0) or post.get('like_count', 0)
            comments = post.get('comments', 0) or post.get('reply_count', 0)
            engagement = likes + comments
            engagements.append(engagement)
        
        if len(engagements) < 3:
            return []
        
        mean_engagement = np.mean(engagements)
        std_engagement = np.std(engagements)
        
        anomalies = []
        for i, engagement in enumerate(engagements):
            if abs(engagement - mean_engagement) > 2 * std_engagement:
                anomalies.append({
                    'type': 'engagement',
                    'description': f'Unusual engagement: {engagement} interactions',
                    'severity': 'high' if abs(engagement - mean_engagement) > 3 * std_engagement else 'medium',
                    'position': i
                })
        
        return anomalies
    
    def _detect_topic_shift_anomalies(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sudden topic shifts"""
        # Simplified topic shift detection
        # In a full implementation, this would use more sophisticated NLP
        
        anomalies = []
        
        # Look for sudden changes in hashtag usage or keyword patterns
        if len(posts) < 5:
            return anomalies
        
        # Analyze hashtag patterns in windows
        window_size = 3
        for i in range(len(posts) - window_size):
            window1_hashtags = set()
            window2_hashtags = set()
            
            for j in range(window_size):
                window1_hashtags.update(posts[i + j].get('hashtags', []))
                window2_hashtags.update(posts[i + j + window_size].get('hashtags', []))
            
            # Calculate overlap
            if window1_hashtags and window2_hashtags:
                overlap = len(window1_hashtags & window2_hashtags)
                total = len(window1_hashtags | window2_hashtags)
                similarity = overlap / total if total > 0 else 0
                
                if similarity < 0.2:  # Very low similarity
                    anomalies.append({
                        'type': 'topic_shift',
                        'description': f'Sudden topic change detected at position {i + window_size}',
                        'severity': 'medium',
                        'position': i + window_size
                    })
        
        return anomalies
    
    # Prediction methods (simplified implementations)
    def _analyze_activity_trend(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze activity trend over time"""
        if len(dated_posts) < 2:
            return {}
        
        # Simple linear trend analysis
        dates = [dt.timestamp() for dt, _ in dated_posts]
        activity_counts = [1] * len(dates)  # Each post counts as 1 activity
        
        # Calculate trend
        x = np.arange(len(dates))
        trend = np.polyfit(x, activity_counts, 1)[0]
        
        return {
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'trend_strength': abs(trend)
        }
    
    def _analyze_sentiment_trend(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze sentiment trend over time"""
        sentiments = []
        
        for _, post in dated_posts:
            content = post.get('caption', '') or post.get('content', '')
            if content:
                sentiment = TextBlob(content).sentiment.polarity
                sentiments.append(sentiment)
        
        if len(sentiments) < 2:
            return {}
        
        # Calculate trend
        x = np.arange(len(sentiments))
        trend = np.polyfit(x, sentiments, 1)[0]
        
        return {
            'trend_direction': 'improving' if trend > 0 else 'declining' if trend < 0 else 'stable',
            'trend_strength': abs(trend),
            'current_sentiment': sentiments[-1] if sentiments else 0
        }
    
    def _analyze_engagement_trend(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze engagement trend over time"""
        engagements = []
        
        for _, post in dated_posts:
            likes = post.get('likes', 0) or post.get('like_count', 0)
            comments = post.get('comments', 0) or post.get('reply_count', 0)
            engagement = likes + comments
            engagements.append(engagement)
        
        if len(engagements) < 2:
            return {}
        
        # Calculate trend
        x = np.arange(len(engagements))
        trend = np.polyfit(x, engagements, 1)[0]
        
        return {
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'trend_strength': abs(trend),
            'current_engagement': engagements[-1] if engagements else 0
        }
    
    def _analyze_content_evolution(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Analyze content evolution over time"""
        # Simplified content evolution analysis
        early_posts = dated_posts[:len(dated_posts)//2]
        recent_posts = dated_posts[len(dated_posts)//2:]
        
        early_hashtags = set()
        recent_hashtags = set()
        
        for _, post in early_posts:
            early_hashtags.update(post.get('hashtags', []))
        
        for _, post in recent_posts:
            recent_hashtags.update(post.get('hashtags', []))
        
        return {
            'topic_stability': len(early_hashtags & recent_hashtags) / max(1, len(early_hashtags | recent_hashtags)),
            'new_topics': list(recent_hashtags - early_hashtags)[:5],
            'abandoned_topics': list(early_hashtags - recent_hashtags)[:5]
        }
    
    # Prediction methods (placeholder implementations)
    def _predict_activity_level(self, activity_trend: Dict[str, Any]) -> str:
        """Predict future activity level"""
        direction = activity_trend.get('trend_direction', 'stable')
        if direction == 'increasing':
            return 'likely_to_increase'
        elif direction == 'decreasing':
            return 'likely_to_decrease'
        else:
            return 'likely_to_remain_stable'
    
    def _predict_sentiment_direction(self, sentiment_trend: Dict[str, Any]) -> str:
        """Predict sentiment direction"""
        direction = sentiment_trend.get('trend_direction', 'stable')
        if direction == 'improving':
            return 'sentiment_likely_to_improve'
        elif direction == 'declining':
            return 'sentiment_likely_to_decline'
        else:
            return 'sentiment_likely_stable'
    
    def _predict_engagement_pattern(self, engagement_trend: Dict[str, Any]) -> str:
        """Predict engagement patterns"""
        direction = engagement_trend.get('trend_direction', 'stable')
        if direction == 'increasing':
            return 'engagement_likely_to_grow'
        elif direction == 'decreasing':
            return 'engagement_likely_to_decline'
        else:
            return 'engagement_likely_stable'
    
    def _predict_content_themes(self, content_evolution: Dict[str, Any]) -> List[str]:
        """Predict future content themes"""
        new_topics = content_evolution.get('new_topics', [])
        return new_topics[:3] if new_topics else ['similar_to_current_themes']
    
    def _predict_risk_escalation(self, dated_posts: List[Tuple]) -> str:
        """Predict risk escalation"""
        # Simplified risk prediction
        recent_posts = dated_posts[-5:] if len(dated_posts) >= 5 else dated_posts
        
        risk_keywords = ['angry', 'hate', 'violence', 'threat', 'harm']
        risk_count = 0
        
        for _, post in recent_posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            for keyword in risk_keywords:
                if keyword in content:
                    risk_count += 1
        
        if risk_count > 2:
            return 'risk_escalation_likely'
        elif risk_count > 0:
            return 'moderate_risk_increase'
        else:
            return 'low_risk_of_escalation'
    
    def _calculate_prediction_confidence(self, dated_posts: List[Tuple]) -> float:
        """Calculate confidence in predictions"""
        # Base confidence on data quantity and recency
        data_points = len(dated_posts)
        
        if data_points >= 20:
            base_confidence = 0.8
        elif data_points >= 10:
            base_confidence = 0.6
        elif data_points >= 5:
            base_confidence = 0.4
        else:
            base_confidence = 0.2
        
        # Adjust for recency
        if dated_posts:
            latest_post = dated_posts[-1][0]
            days_since_latest = (datetime.now(latest_post.tzinfo) - latest_post).days
            
            if days_since_latest <= 7:
                recency_bonus = 0.2
            elif days_since_latest <= 30:
                recency_bonus = 0.1
            else:
                recency_bonus = 0
            
            return min(1.0, base_confidence + recency_bonus)
        
        return base_confidence
    
    def _determine_persuasion_style(self, influence_scores: Dict[str, float]) -> str:
        """Determine primary persuasion style"""
        max_score = max(influence_scores.values()) if influence_scores.values() else 0
        
        if max_score < 0.1:
            return 'non_persuasive'
        
        primary_method = max(influence_scores, key=influence_scores.get)
        
        style_mapping = {
            'authority': 'expert_based',
            'social_proof': 'popularity_based',
            'reciprocity': 'give_and_take',
            'commitment': 'promise_based',
            'liking': 'relationship_based',
            'scarcity': 'urgency_based'
        }
        
        return style_mapping.get(primary_method, 'mixed_approach')