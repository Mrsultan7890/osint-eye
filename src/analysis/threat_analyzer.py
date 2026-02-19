import re
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import numpy as np
from textblob import TextBlob
from typing import Dict, List, Any, Tuple
from utils.logger import setup_logger

logger = setup_logger()

class ThreatAnalyzer:
    def __init__(self):
        self.threat_keywords = {
            'violence': ['kill', 'murder', 'attack', 'bomb', 'weapon', 'gun', 'knife', 'hurt', 'harm'],
            'harassment': ['stalk', 'follow', 'watch', 'hunt', 'track', 'find you', 'get you'],
            'extremism': ['jihad', 'crusade', 'revolution', 'uprising', 'overthrow', 'destroy'],
            'self_harm': ['suicide', 'kill myself', 'end it all', 'not worth living', 'hurt myself'],
            'hate_speech': ['hate', 'nazi', 'terrorist', 'inferior', 'subhuman', 'scum'],
            'cybercrime': ['hack', 'ddos', 'malware', 'phishing', 'fraud', 'scam', 'steal']
        }
        
        self.risk_indicators = {
            'isolation': ['alone', 'nobody', 'isolated', 'no friends', 'lonely'],
            'anger': ['angry', 'rage', 'furious', 'mad', 'hate everyone'],
            'depression': ['depressed', 'hopeless', 'worthless', 'empty', 'dark'],
            'paranoia': ['watching me', 'following', 'conspiracy', 'they know', 'spying']
        }
        
    def assess_threat_level(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive threat assessment"""
        posts = profile_data.get('posts', [])
        profile = profile_data.get('profile', {})
        
        # Analyze content for threats
        content_threats = self._analyze_content_threats(posts)
        
        # Analyze behavioral indicators
        behavioral_risks = self._analyze_behavioral_risks(posts)
        
        # Analyze profile indicators
        profile_risks = self._analyze_profile_risks(profile)
        
        # Calculate overall threat score
        threat_score = self._calculate_threat_score(content_threats, behavioral_risks, profile_risks)
        
        # Generate recommendations
        recommendations = self._generate_threat_recommendations(threat_score, content_threats)
        
        return {
            'threat_level': self._get_threat_level(threat_score),
            'threat_score': threat_score,
            'content_threats': content_threats,
            'behavioral_risks': behavioral_risks,
            'profile_risks': profile_risks,
            'recommendations': recommendations,
            'requires_monitoring': threat_score > 60,
            'immediate_concern': threat_score > 80
        }
    
    def detect_radicalization_indicators(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect signs of radicalization in content"""
        if not posts:
            return {}
        
        # Sort posts by date to track progression
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
        
        # Analyze content evolution
        radicalization_indicators = []
        
        # Language escalation
        escalation_score = self._detect_language_escalation(dated_posts)
        if escalation_score > 0.6:
            radicalization_indicators.append('language_escalation')
        
        # Ideology adoption
        ideology_markers = self._detect_ideology_markers(dated_posts)
        if ideology_markers['score'] > 0.5:
            radicalization_indicators.append('ideology_adoption')
        
        # Social isolation
        isolation_score = self._detect_social_isolation(dated_posts)
        if isolation_score > 0.7:
            radicalization_indicators.append('social_isolation')
        
        # Echo chamber behavior
        echo_chamber_score = self._detect_echo_chamber(dated_posts)
        if echo_chamber_score > 0.6:
            radicalization_indicators.append('echo_chamber')
        
        return {
            'radicalization_risk': len(radicalization_indicators) / 4,
            'indicators': radicalization_indicators,
            'escalation_score': escalation_score,
            'ideology_markers': ideology_markers,
            'isolation_score': isolation_score,
            'echo_chamber_score': echo_chamber_score
        }
    
    def analyze_cybersecurity_risks(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cybersecurity and privacy risks"""
        profile = profile_data.get('profile', {})
        posts = profile_data.get('posts', [])
        
        privacy_risks = []
        security_risks = []
        
        # Personal information exposure
        pii_exposure = self._detect_pii_exposure(posts, profile)
        if pii_exposure['risk_level'] > 0.5:
            privacy_risks.append('personal_info_exposure')
        
        # Location disclosure
        location_risks = self._analyze_location_disclosure(posts)
        if location_risks['risk_score'] > 0.6:
            privacy_risks.append('location_disclosure')
        
        # Social engineering vulnerabilities
        social_eng_risks = self._assess_social_engineering_risks(profile, posts)
        if social_eng_risks['vulnerability_score'] > 0.7:
            security_risks.append('social_engineering_vulnerable')
        
        # Suspicious links and attachments
        malware_risks = self._detect_malware_indicators(posts)
        if malware_risks['risk_score'] > 0.5:
            security_risks.append('malware_distribution')
        
        return {
            'privacy_risks': privacy_risks,
            'security_risks': security_risks,
            'pii_exposure': pii_exposure,
            'location_risks': location_risks,
            'social_engineering_risks': social_eng_risks,
            'malware_risks': malware_risks,
            'overall_cyber_risk': (len(privacy_risks) + len(security_risks)) / 4
        }
    
    def detect_coordinated_behavior(self, profiles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect coordinated inauthentic behavior across profiles"""
        if len(profiles_data) < 2:
            return {}
        
        coordination_indicators = []
        
        # Synchronized posting
        sync_score = self._detect_synchronized_posting(profiles_data)
        if sync_score > 0.7:
            coordination_indicators.append('synchronized_posting')
        
        # Content similarity
        content_similarity = self._analyze_content_similarity(profiles_data)
        if content_similarity > 0.8:
            coordination_indicators.append('similar_content')
        
        # Network overlap
        network_overlap = self._analyze_network_overlap(profiles_data)
        if network_overlap > 0.6:
            coordination_indicators.append('network_overlap')
        
        # Behavioral patterns
        behavior_similarity = self._analyze_behavior_similarity(profiles_data)
        if behavior_similarity > 0.7:
            coordination_indicators.append('similar_behavior')
        
        return {
            'coordination_score': len(coordination_indicators) / 4,
            'indicators': coordination_indicators,
            'sync_score': sync_score,
            'content_similarity': content_similarity,
            'network_overlap': network_overlap,
            'behavior_similarity': behavior_similarity,
            'likely_coordinated': len(coordination_indicators) >= 2
        }
    
    def _analyze_content_threats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posts for threatening content"""
        threat_counts = defaultdict(int)
        threatening_posts = []
        
        for i, post in enumerate(posts):
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            post_threats = []
            for threat_type, keywords in self.threat_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        threat_counts[threat_type] += 1
                        post_threats.append(threat_type)
            
            if post_threats:
                threatening_posts.append({
                    'post_index': i,
                    'threats': post_threats,
                    'content_preview': content[:100]
                })
        
        return {
            'threat_categories': dict(threat_counts),
            'threatening_posts': threatening_posts,
            'total_threats': sum(threat_counts.values()),
            'threat_density': sum(threat_counts.values()) / max(1, len(posts))
        }
    
    def _analyze_behavioral_risks(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavioral risk indicators"""
        risk_indicators = defaultdict(int)
        
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            for risk_type, keywords in self.risk_indicators.items():
                for keyword in keywords:
                    if keyword in content:
                        risk_indicators[risk_type] += 1
        
        # Analyze posting patterns for erratic behavior
        erratic_score = self._detect_erratic_posting(posts)
        
        return {
            'psychological_indicators': dict(risk_indicators),
            'erratic_posting_score': erratic_score,
            'total_risk_indicators': sum(risk_indicators.values())
        }
    
    def _analyze_profile_risks(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile-level risk indicators"""
        risks = []
        
        # Anonymous/fake profile indicators
        if not profile.get('biography') or len(profile.get('biography', '')) < 10:
            risks.append('minimal_profile_info')
        
        # Suspicious follower patterns
        followers = profile.get('followers', 0)
        following = profile.get('following', 0)
        
        if following > 0:
            ratio = followers / following
            if ratio < 0.1:  # Very low follower ratio
                risks.append('suspicious_follower_ratio')
        
        # Recent account creation (if available)
        # This would need creation date from profile data
        
        return {
            'profile_risks': risks,
            'risk_count': len(risks)
        }
    
    def _calculate_threat_score(self, content_threats: Dict, behavioral_risks: Dict, profile_risks: Dict) -> float:
        """Calculate overall threat score (0-100)"""
        score = 0
        
        # Content threat scoring
        threat_weight = {
            'violence': 25,
            'harassment': 20,
            'extremism': 30,
            'self_harm': 15,
            'hate_speech': 20,
            'cybercrime': 15
        }
        
        for threat_type, count in content_threats.get('threat_categories', {}).items():
            score += min(threat_weight.get(threat_type, 10) * count, 40)
        
        # Behavioral risk scoring
        risk_weight = {
            'isolation': 10,
            'anger': 15,
            'depression': 10,
            'paranoia': 15
        }
        
        for risk_type, count in behavioral_risks.get('psychological_indicators', {}).items():
            score += min(risk_weight.get(risk_type, 5) * count, 20)
        
        # Profile risk scoring
        score += profile_risks.get('risk_count', 0) * 5
        
        # Erratic behavior bonus
        score += behavioral_risks.get('erratic_posting_score', 0) * 10
        
        return min(100, score)
    
    def _get_threat_level(self, threat_score: float) -> str:
        """Convert threat score to threat level"""
        if threat_score >= 80:
            return 'CRITICAL'
        elif threat_score >= 60:
            return 'HIGH'
        elif threat_score >= 40:
            return 'MEDIUM'
        elif threat_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _generate_threat_recommendations(self, threat_score: float, content_threats: Dict) -> List[str]:
        """Generate threat mitigation recommendations"""
        recommendations = []
        
        if threat_score >= 80:
            recommendations.append('Immediate law enforcement notification recommended')
            recommendations.append('Continuous monitoring required')
        elif threat_score >= 60:
            recommendations.append('Enhanced monitoring recommended')
            recommendations.append('Consider professional threat assessment')
        elif threat_score >= 40:
            recommendations.append('Regular monitoring advised')
        
        # Specific threat recommendations
        threats = content_threats.get('threat_categories', {})
        if 'violence' in threats:
            recommendations.append('Violence indicators detected - assess immediate risk')
        if 'self_harm' in threats:
            recommendations.append('Self-harm indicators - consider mental health intervention')
        if 'cybercrime' in threats:
            recommendations.append('Cybercrime indicators - monitor for malicious activity')
        
        return recommendations
    
    def _detect_language_escalation(self, dated_posts: List[Tuple]) -> float:
        """Detect escalation in language intensity over time"""
        if len(dated_posts) < 3:
            return 0
        
        # Divide posts into early and recent
        mid_point = len(dated_posts) // 2
        early_posts = dated_posts[:mid_point]
        recent_posts = dated_posts[mid_point:]
        
        # Calculate threat density for each period
        early_threats = self._count_threats_in_posts([post for _, post in early_posts])
        recent_threats = self._count_threats_in_posts([post for _, post in recent_posts])
        
        early_density = early_threats / len(early_posts)
        recent_density = recent_threats / len(recent_posts)
        
        # Calculate escalation
        if early_density == 0:
            return 1.0 if recent_density > 0 else 0.0
        
        escalation = (recent_density - early_density) / early_density
        return max(0, min(1, escalation))
    
    def _detect_ideology_markers(self, dated_posts: List[Tuple]) -> Dict[str, Any]:
        """Detect adoption of extremist ideology markers"""
        ideology_keywords = [
            'pure', 'superior', 'chosen', 'awakened', 'enlightened',
            'enemy', 'traitor', 'corrupt', 'degenerate', 'invasion'
        ]
        
        ideology_count = 0
        total_words = 0
        
        for _, post in dated_posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            words = content.split()
            total_words += len(words)
            
            for keyword in ideology_keywords:
                ideology_count += content.count(keyword)
        
        score = ideology_count / max(1, total_words / 100)  # Per 100 words
        
        return {
            'score': min(1, score),
            'keyword_count': ideology_count,
            'density': score
        }
    
    def _detect_social_isolation(self, dated_posts: List[Tuple]) -> float:
        """Detect increasing social isolation"""
        isolation_indicators = ['alone', 'nobody understands', 'no one cares', 'isolated', 'abandoned']
        
        isolation_count = 0
        for _, post in dated_posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            for indicator in isolation_indicators:
                if indicator in content:
                    isolation_count += 1
        
        return min(1, isolation_count / max(1, len(dated_posts)))
    
    def _detect_echo_chamber(self, dated_posts: List[Tuple]) -> float:
        """Detect echo chamber behavior"""
        # Look for repetitive themes and lack of diverse viewpoints
        all_content = []
        for _, post in dated_posts:
            content = post.get('caption', '') or post.get('content', '')
            all_content.append(content.lower())
        
        if len(all_content) < 2:
            return 0
        
        # Calculate content similarity (simple approach)
        unique_words = set()
        total_words = 0
        
        for content in all_content:
            words = set(content.split())
            unique_words.update(words)
            total_words += len(content.split())
        
        # High repetition = low diversity = echo chamber
        diversity = len(unique_words) / max(1, total_words)
        echo_chamber_score = 1 - min(1, diversity * 2)  # Invert and normalize
        
        return echo_chamber_score
    
    def _detect_pii_exposure(self, posts: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Detect personally identifiable information exposure"""
        pii_types = {
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b'
        }
        
        exposed_pii = defaultdict(list)
        
        # Check posts
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            for pii_type, pattern in pii_types.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                exposed_pii[pii_type].extend(matches)
        
        # Check profile
        bio = profile.get('biography', '') or profile.get('description', '')
        for pii_type, pattern in pii_types.items():
            matches = re.findall(pattern, bio, re.IGNORECASE)
            exposed_pii[pii_type].extend(matches)
        
        risk_level = len(exposed_pii) / len(pii_types)
        
        return {
            'exposed_pii': dict(exposed_pii),
            'risk_level': risk_level,
            'pii_count': sum(len(matches) for matches in exposed_pii.values())
        }
    
    def _analyze_location_disclosure(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze location disclosure risks"""
        location_indicators = 0
        
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            # Check for location keywords
            location_keywords = ['home', 'work', 'school', 'gym', 'restaurant', 'mall', 'park']
            for keyword in location_keywords:
                if keyword in content:
                    location_indicators += 1
            
            # Check for specific location patterns
            if re.search(r'\bat\s+[A-Z][a-z]+', content):  # "at Location"
                location_indicators += 1
        
        risk_score = min(1, location_indicators / max(1, len(posts)))
        
        return {
            'location_mentions': location_indicators,
            'risk_score': risk_score
        }
    
    def _assess_social_engineering_risks(self, profile: Dict[str, Any], posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess vulnerability to social engineering attacks"""
        vulnerability_score = 0
        
        # Over-sharing personal information
        bio = profile.get('biography', '') or profile.get('description', '')
        personal_info_count = len(re.findall(r'\b(?:born|birthday|anniversary|pet|mother|father|school|work)\b', bio.lower()))
        vulnerability_score += min(0.3, personal_info_count * 0.1)
        
        # Trusting behavior indicators
        trust_indicators = ['dm me', 'message me', 'contact me', 'click link', 'check out']
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            for indicator in trust_indicators:
                if indicator in content:
                    vulnerability_score += 0.1
        
        vulnerability_score = min(1, vulnerability_score)
        
        return {
            'vulnerability_score': vulnerability_score,
            'personal_info_exposure': personal_info_count
        }
    
    def _detect_malware_indicators(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential malware distribution"""
        suspicious_patterns = [
            r'bit\.ly/\w+',
            r'tinyurl\.com/\w+',
            r'click.*here.*download',
            r'free.*software.*download',
            r'urgent.*update.*required'
        ]
        
        suspicious_count = 0
        for post in posts:
            content = post.get('caption', '') or post.get('content', '')
            for pattern in suspicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    suspicious_count += 1
        
        risk_score = min(1, suspicious_count / max(1, len(posts)))
        
        return {
            'suspicious_links': suspicious_count,
            'risk_score': risk_score
        }
    
    def _detect_synchronized_posting(self, profiles_data: List[Dict[str, Any]]) -> float:
        """Detect synchronized posting patterns"""
        all_post_times = []
        
        for profile_data in profiles_data:
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
            
            all_post_times.append(post_times)
        
        # Calculate synchronization score
        sync_count = 0
        total_comparisons = 0
        
        for i in range(len(all_post_times)):
            for j in range(i + 1, len(all_post_times)):
                times1, times2 = all_post_times[i], all_post_times[j]
                
                for t1 in times1:
                    for t2 in times2:
                        total_comparisons += 1
                        if abs(t1 - t2) <= timedelta(minutes=30):  # 30-minute window
                            sync_count += 1
        
        return sync_count / max(1, total_comparisons) if total_comparisons > 0 else 0
    
    def _analyze_content_similarity(self, profiles_data: List[Dict[str, Any]]) -> float:
        """Analyze content similarity across profiles"""
        all_content = []
        
        for profile_data in profiles_data:
            posts = profile_data.get('posts', [])
            content = ' '.join([p.get('caption', '') or p.get('content', '') for p in posts])
            all_content.append(content.lower())
        
        if len(all_content) < 2:
            return 0
        
        # Simple similarity calculation
        similarities = []
        for i in range(len(all_content)):
            for j in range(i + 1, len(all_content)):
                # Calculate word overlap
                words1 = set(all_content[i].split())
                words2 = set(all_content[j].split())
                
                if len(words1) == 0 or len(words2) == 0:
                    continue
                
                overlap = len(words1 & words2)
                union = len(words1 | words2)
                similarity = overlap / union if union > 0 else 0
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0
    
    def _analyze_network_overlap(self, profiles_data: List[Dict[str, Any]]) -> float:
        """Analyze network overlap between profiles"""
        all_mentions = []
        
        for profile_data in profiles_data:
            posts = profile_data.get('posts', [])
            mentions = []
            
            for post in posts:
                post_mentions = post.get('mentions', [])
                mentions.extend(post_mentions)
            
            all_mentions.append(set(mentions))
        
        if len(all_mentions) < 2:
            return 0
        
        # Calculate overlap
        overlaps = []
        for i in range(len(all_mentions)):
            for j in range(i + 1, len(all_mentions)):
                mentions1, mentions2 = all_mentions[i], all_mentions[j]
                
                if len(mentions1) == 0 or len(mentions2) == 0:
                    continue
                
                overlap = len(mentions1 & mentions2)
                union = len(mentions1 | mentions2)
                overlap_ratio = overlap / union if union > 0 else 0
                overlaps.append(overlap_ratio)
        
        return np.mean(overlaps) if overlaps else 0
    
    def _analyze_behavior_similarity(self, profiles_data: List[Dict[str, Any]]) -> float:
        """Analyze behavioral similarity between profiles"""
        # This would compare posting patterns, engagement patterns, etc.
        # Simplified implementation
        return 0.5  # Placeholder
    
    def _count_threats_in_posts(self, posts: List[Dict[str, Any]]) -> int:
        """Count threat keywords in posts"""
        threat_count = 0
        
        for post in posts:
            content = (post.get('caption', '') or post.get('content', '')).lower()
            
            for threat_type, keywords in self.threat_keywords.items():
                for keyword in keywords:
                    threat_count += content.count(keyword)
        
        return threat_count
    
    def _detect_erratic_posting(self, posts: List[Dict[str, Any]]) -> float:
        """Detect erratic posting behavior"""
        if len(posts) < 3:
            return 0
        
        # Calculate posting intervals
        post_times = []
        for post in posts:
            date_str = post.get('date')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    post_times.append(dt)
                except:
                    continue
        
        if len(post_times) < 3:
            return 0
        
        post_times.sort()
        intervals = []
        
        for i in range(1, len(post_times)):
            interval = (post_times[i] - post_times[i-1]).total_seconds() / 3600  # Hours
            intervals.append(interval)
        
        # Calculate coefficient of variation (std/mean)
        if len(intervals) > 1:
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            if mean_interval > 0:
                cv = std_interval / mean_interval
                return min(1, cv / 2)  # Normalize to 0-1
        
        return 0