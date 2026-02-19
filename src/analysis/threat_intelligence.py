#!/usr/bin/env python3

import re
import json
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
from collections import defaultdict, Counter
import math

class ThreatIntelligence:
    def __init__(self):
        self.scam_indicators = {
            "bio_keywords": [
                "investment", "crypto", "bitcoin", "trading", "forex", "profit",
                "guaranteed", "money", "rich", "millionaire", "entrepreneur",
                "dm for business", "link in bio", "make money", "passive income",
                "financial freedom", "work from home", "easy money"
            ],
            "suspicious_patterns": [
                r"\b\d+%\s*(profit|return|gain)",
                r"\$\d+.*day",
                r"dm.*business",
                r"link.*bio.*money",
                r"guaranteed.*profit",
                r"risk.*free",
                r"double.*money"
            ],
            "fake_verification": [
                "✓", "☑", "✔", "verified", "official", "real"
            ]
        }
        
        self.bot_indicators = {
            "username_patterns": [
                r"^[a-z]+\d{4,}$",  # letters followed by many numbers
                r"^[a-z]+_[a-z]+\d+$",  # word_word123 pattern
                r"^user\d+$",  # user123 pattern
                r"^[a-z]{1,3}\d{6,}$"  # few letters, many numbers
            ],
            "bio_patterns": [
                r"^$",  # empty bio
                r"^\w+\s*$",  # single word bio
                r"^.{1,10}$"  # very short bio
            ],
            "activity_patterns": {
                "high_following_low_followers": True,
                "no_profile_picture": True,
                "recent_creation": True,
                "repetitive_content": True
            }
        }
        
        self.malicious_domains = [
            "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
            "short.link", "tiny.cc", "is.gd", "buff.ly"
        ]
        
        self.threat_categories = {
            "scammer": {"weight": 0.8, "severity": "high"},
            "bot": {"weight": 0.6, "severity": "medium"},
            "fake_account": {"weight": 0.7, "severity": "high"},
            "spam_account": {"weight": 0.5, "severity": "medium"},
            "phishing": {"weight": 0.9, "severity": "critical"},
            "impersonator": {"weight": 0.8, "severity": "high"},
            "suspicious": {"weight": 0.4, "severity": "low"}
        }
    
    def analyze_threat_profile(self, profile_data: Dict) -> Dict:
        """Comprehensive threat analysis of a profile"""
        threat_analysis = {
            "overall_threat_score": 0,
            "threat_categories": [],
            "risk_indicators": [],
            "severity_level": "low",
            "confidence_score": 0,
            "detailed_analysis": {},
            "recommendations": []
        }
        
        # Analyze different threat vectors
        scam_analysis = self._analyze_scam_indicators(profile_data)
        bot_analysis = self._analyze_bot_indicators(profile_data)
        fake_analysis = self._analyze_fake_indicators(profile_data)
        phishing_analysis = self._analyze_phishing_indicators(profile_data)
        
        # Combine analyses
        all_analyses = {
            "scam": scam_analysis,
            "bot": bot_analysis,
            "fake": fake_analysis,
            "phishing": phishing_analysis
        }
        
        threat_analysis["detailed_analysis"] = all_analyses
        
        # Calculate overall threat score
        total_score = 0
        detected_threats = []
        
        for threat_type, analysis in all_analyses.items():
            if analysis["is_threat"]:
                category_info = self.threat_categories.get(threat_type, {"weight": 0.5, "severity": "medium"})
                weighted_score = analysis["confidence"] * category_info["weight"]
                total_score += weighted_score
                detected_threats.append({
                    "type": threat_type,
                    "confidence": analysis["confidence"],
                    "severity": category_info["severity"],
                    "indicators": analysis["indicators"]
                })
        
        threat_analysis["overall_threat_score"] = min(100, total_score)
        threat_analysis["threat_categories"] = detected_threats
        
        # Determine severity level
        if threat_analysis["overall_threat_score"] >= 80:
            threat_analysis["severity_level"] = "critical"
        elif threat_analysis["overall_threat_score"] >= 60:
            threat_analysis["severity_level"] = "high"
        elif threat_analysis["overall_threat_score"] >= 40:
            threat_analysis["severity_level"] = "medium"
        else:
            threat_analysis["severity_level"] = "low"
        
        # Generate recommendations
        threat_analysis["recommendations"] = self._generate_threat_recommendations(threat_analysis)
        
        return threat_analysis
    
    def _analyze_scam_indicators(self, profile_data: Dict) -> Dict:
        """Analyze profile for scam indicators"""
        analysis = {
            "is_threat": False,
            "confidence": 0,
            "indicators": [],
            "score_breakdown": {}
        }
        
        bio = profile_data.get("bio", "").lower()
        username = profile_data.get("username", "").lower()
        
        # Check bio for scam keywords
        keyword_matches = 0
        for keyword in self.scam_indicators["bio_keywords"]:
            if keyword in bio:
                keyword_matches += 1
                analysis["indicators"].append(f"Scam keyword found: {keyword}")
        
        if keyword_matches > 0:
            analysis["score_breakdown"]["keyword_matches"] = min(50, keyword_matches * 10)
        
        # Check for suspicious patterns
        pattern_matches = 0
        for pattern in self.scam_indicators["suspicious_patterns"]:
            if re.search(pattern, bio, re.IGNORECASE):
                pattern_matches += 1
                analysis["indicators"].append(f"Suspicious pattern detected: {pattern}")
        
        if pattern_matches > 0:
            analysis["score_breakdown"]["pattern_matches"] = min(40, pattern_matches * 15)
        
        # Check for fake verification symbols
        fake_verification = 0
        for symbol in self.scam_indicators["fake_verification"]:
            if symbol in bio and not profile_data.get("verified", False):
                fake_verification += 1
                analysis["indicators"].append(f"Fake verification symbol: {symbol}")
        
        if fake_verification > 0:
            analysis["score_breakdown"]["fake_verification"] = min(30, fake_verification * 15)
        
        # Check follower/following ratio (scammers often have suspicious ratios)
        followers = profile_data.get("followers", 0)
        following = profile_data.get("following", 0)
        
        if following > 0 and followers > 0:
            ratio = followers / following
            if ratio > 100 or ratio < 0.01:  # Very high or very low ratio
                analysis["indicators"].append(f"Suspicious follower ratio: {ratio:.2f}")
                analysis["score_breakdown"]["suspicious_ratio"] = 20
        
        # Calculate total confidence
        total_score = sum(analysis["score_breakdown"].values())
        analysis["confidence"] = min(100, total_score)
        analysis["is_threat"] = analysis["confidence"] > 30
        
        return analysis
    
    def _analyze_bot_indicators(self, profile_data: Dict) -> Dict:
        """Analyze profile for bot indicators"""
        analysis = {
            "is_threat": False,
            "confidence": 0,
            "indicators": [],
            "score_breakdown": {}
        }
        
        username = profile_data.get("username", "")
        bio = profile_data.get("bio", "")
        
        # Check username patterns
        username_score = 0
        for pattern in self.bot_indicators["username_patterns"]:
            if re.match(pattern, username.lower()):
                username_score += 25
                analysis["indicators"].append(f"Bot-like username pattern: {pattern}")
        
        if username_score > 0:
            analysis["score_breakdown"]["username_patterns"] = min(50, username_score)
        
        # Check bio patterns
        bio_score = 0
        for pattern in self.bot_indicators["bio_patterns"]:
            if re.match(pattern, bio):
                bio_score += 20
                analysis["indicators"].append(f"Bot-like bio pattern")
        
        if bio_score > 0:
            analysis["score_breakdown"]["bio_patterns"] = min(40, bio_score)
        
        # Check activity patterns
        followers = profile_data.get("followers", 0)
        following = profile_data.get("following", 0)
        posts = profile_data.get("posts", 0)
        
        # High following, low followers (typical bot behavior)
        if following > 1000 and followers < 100:
            analysis["indicators"].append("High following, low followers (bot pattern)")
            analysis["score_breakdown"]["following_pattern"] = 30
        
        # No posts but high activity
        if posts == 0 and following > 500:
            analysis["indicators"].append("No posts but high following activity")
            analysis["score_breakdown"]["no_content"] = 25
        
        # Very recent account with high activity
        created_date = profile_data.get("created_date")
        if created_date:
            # Simplified check - in real implementation, parse the date
            analysis["indicators"].append("Account creation date analysis needed")
        
        # Calculate total confidence
        total_score = sum(analysis["score_breakdown"].values())
        analysis["confidence"] = min(100, total_score)
        analysis["is_threat"] = analysis["confidence"] > 40
        
        return analysis
    
    def _analyze_fake_indicators(self, profile_data: Dict) -> Dict:
        """Analyze profile for fake account indicators"""
        analysis = {
            "is_threat": False,
            "confidence": 0,
            "indicators": [],
            "score_breakdown": {}
        }
        
        # Check for stock photo indicators (simplified)
        profile_pic_url = profile_data.get("profile_pic_url", "")
        if "default" in profile_pic_url or not profile_pic_url:
            analysis["indicators"].append("Default or missing profile picture")
            analysis["score_breakdown"]["no_profile_pic"] = 20
        
        # Check for inconsistent information
        bio = profile_data.get("bio", "")
        username = profile_data.get("username", "")
        
        # Bio-username mismatch (different languages, styles)
        if bio and username:
            bio_words = set(re.findall(r'\w+', bio.lower()))
            username_words = set(re.findall(r'\w+', username.lower()))
            
            if not bio_words.intersection(username_words) and len(bio) > 20:
                analysis["indicators"].append("Bio and username seem unrelated")
                analysis["score_breakdown"]["inconsistent_info"] = 15
        
        # Check for minimal engagement relative to followers
        followers = profile_data.get("followers", 0)
        posts = profile_data.get("posts", 0)
        
        if followers > 1000 and posts < 5:
            analysis["indicators"].append("High followers but very few posts")
            analysis["score_breakdown"]["low_engagement"] = 25
        
        # Check for suspicious verification claims
        if not profile_data.get("verified", False):
            verification_claims = ["verified", "official", "real", "authentic"]
            for claim in verification_claims:
                if claim in bio.lower():
                    analysis["indicators"].append(f"Claims to be {claim} but not verified")
                    analysis["score_breakdown"]["false_verification"] = 30
                    break
        
        # Calculate total confidence
        total_score = sum(analysis["score_breakdown"].values())
        analysis["confidence"] = min(100, total_score)
        analysis["is_threat"] = analysis["confidence"] > 35
        
        return analysis
    
    def _analyze_phishing_indicators(self, profile_data: Dict) -> Dict:
        """Analyze profile for phishing indicators"""
        analysis = {
            "is_threat": False,
            "confidence": 0,
            "indicators": [],
            "score_breakdown": {}
        }
        
        bio = profile_data.get("bio", "")
        
        # Check for suspicious links
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', bio)
        
        suspicious_links = 0
        for url in urls:
            for domain in self.malicious_domains:
                if domain in url:
                    suspicious_links += 1
                    analysis["indicators"].append(f"Suspicious shortened URL: {url}")
        
        if suspicious_links > 0:
            analysis["score_breakdown"]["suspicious_links"] = min(60, suspicious_links * 30)
        
        # Check for urgency keywords
        urgency_keywords = ["urgent", "limited time", "act now", "expires", "hurry", "last chance"]
        urgency_count = 0
        for keyword in urgency_keywords:
            if keyword in bio.lower():
                urgency_count += 1
                analysis["indicators"].append(f"Urgency keyword: {keyword}")
        
        if urgency_count > 0:
            analysis["score_breakdown"]["urgency_tactics"] = min(40, urgency_count * 20)
        
        # Check for credential harvesting indicators
        credential_keywords = ["login", "password", "verify account", "confirm identity", "update info"]
        credential_count = 0
        for keyword in credential_keywords:
            if keyword in bio.lower():
                credential_count += 1
                analysis["indicators"].append(f"Credential harvesting keyword: {keyword}")
        
        if credential_count > 0:
            analysis["score_breakdown"]["credential_harvesting"] = min(50, credential_count * 25)
        
        # Calculate total confidence
        total_score = sum(analysis["score_breakdown"].values())
        analysis["confidence"] = min(100, total_score)
        analysis["is_threat"] = analysis["confidence"] > 25
        
        return analysis
    
    def _generate_threat_recommendations(self, threat_analysis: Dict) -> List[str]:
        """Generate recommendations based on threat analysis"""
        recommendations = []
        
        severity = threat_analysis["severity_level"]
        threat_score = threat_analysis["overall_threat_score"]
        
        if severity == "critical":
            recommendations.extend([
                "🚨 CRITICAL THREAT: Avoid all interaction with this profile",
                "Report this profile to platform administrators immediately",
                "Do not click any links or provide personal information",
                "Warn others about this potential threat"
            ])
        elif severity == "high":
            recommendations.extend([
                "⚠️ HIGH RISK: Exercise extreme caution",
                "Verify identity through alternative means before interaction",
                "Do not engage in financial transactions",
                "Consider reporting suspicious activity"
            ])
        elif severity == "medium":
            recommendations.extend([
                "⚡ MODERATE RISK: Proceed with caution",
                "Verify profile authenticity before trusting",
                "Be skeptical of unsolicited offers or requests",
                "Monitor for suspicious behavior patterns"
            ])
        else:
            recommendations.extend([
                "✅ LOW RISK: Profile appears relatively safe",
                "Continue normal security practices",
                "Stay alert for any changes in behavior"
            ])
        
        # Add specific recommendations based on detected threats
        for threat in threat_analysis["threat_categories"]:
            threat_type = threat["type"]
            
            if threat_type == "scam":
                recommendations.append("🔍 Scam indicators detected - verify any financial claims independently")
            elif threat_type == "bot":
                recommendations.append("🤖 Bot-like behavior detected - may be automated account")
            elif threat_type == "fake":
                recommendations.append("👤 Fake account indicators - verify identity through other channels")
            elif threat_type == "phishing":
                recommendations.append("🎣 Phishing indicators detected - do not click suspicious links")
        
        return recommendations
    
    def batch_threat_analysis(self, profiles: List[Dict]) -> Dict:
        """Perform threat analysis on multiple profiles"""
        results = {
            "analysis_summary": {
                "total_profiles": len(profiles),
                "analyzed_at": datetime.now().isoformat(),
                "threat_distribution": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
            },
            "individual_analyses": {},
            "network_threats": {},
            "recommendations": []
        }
        
        threat_profiles = []
        
        for profile in profiles:
            username = profile.get("username", "unknown")
            platform = profile.get("platform", "unknown")
            profile_key = f"{platform}:{username}"
            
            analysis = self.analyze_threat_profile(profile)
            results["individual_analyses"][profile_key] = analysis
            
            # Update threat distribution
            severity = analysis["severity_level"]
            results["analysis_summary"]["threat_distribution"][severity] += 1
            
            if analysis["overall_threat_score"] > 40:
                threat_profiles.append({
                    "profile": profile_key,
                    "score": analysis["overall_threat_score"],
                    "threats": analysis["threat_categories"]
                })
        
        # Analyze network-level threats
        results["network_threats"] = self._analyze_network_threats(threat_profiles)
        
        # Generate batch recommendations
        results["recommendations"] = self._generate_batch_recommendations(results)
        
        return results
    
    def _analyze_network_threats(self, threat_profiles: List[Dict]) -> Dict:
        """Analyze threats at network level"""
        network_analysis = {
            "coordinated_threats": [],
            "threat_clusters": {},
            "risk_propagation": {},
            "network_risk_score": 0
        }
        
        if len(threat_profiles) < 2:
            return network_analysis
        
        # Look for coordinated threats (similar threat patterns)
        threat_patterns = defaultdict(list)
        
        for profile in threat_profiles:
            for threat in profile["threats"]:
                threat_type = threat["type"]
                threat_patterns[threat_type].append(profile["profile"])
        
        # Identify potential coordinated attacks
        for threat_type, profiles in threat_patterns.items():
            if len(profiles) > 1:
                network_analysis["coordinated_threats"].append({
                    "threat_type": threat_type,
                    "affected_profiles": profiles,
                    "coordination_likelihood": min(100, len(profiles) * 20)
                })
        
        # Calculate network risk score
        if threat_profiles:
            avg_threat_score = sum(p["score"] for p in threat_profiles) / len(threat_profiles)
            coordination_bonus = len(network_analysis["coordinated_threats"]) * 10
            network_analysis["network_risk_score"] = min(100, avg_threat_score + coordination_bonus)
        
        return network_analysis
    
    def _generate_batch_recommendations(self, batch_results: Dict) -> List[str]:
        """Generate recommendations for batch analysis"""
        recommendations = []
        
        threat_dist = batch_results["analysis_summary"]["threat_distribution"]
        total_profiles = batch_results["analysis_summary"]["total_profiles"]
        
        critical_ratio = threat_dist["critical"] / total_profiles if total_profiles > 0 else 0
        high_ratio = threat_dist["high"] / total_profiles if total_profiles > 0 else 0
        
        if critical_ratio > 0.2:
            recommendations.append("🚨 HIGH ALERT: Over 20% of profiles show critical threat indicators")
        elif high_ratio > 0.3:
            recommendations.append("⚠️ WARNING: Over 30% of profiles show high-risk indicators")
        
        # Network-specific recommendations
        network_threats = batch_results.get("network_threats", {})
        coordinated_threats = network_threats.get("coordinated_threats", [])
        
        if coordinated_threats:
            recommendations.append("🕸️ COORDINATED THREAT: Multiple profiles show similar threat patterns")
            recommendations.append("Consider investigating potential bot networks or coordinated campaigns")
        
        recommendations.extend([
            "Monitor high-risk profiles for behavioral changes",
            "Implement additional verification for suspicious accounts",
            "Consider automated blocking of critical threat profiles",
            "Regular re-analysis recommended for threat evolution tracking"
        ])
        
        return recommendations
    
    def export_threat_intelligence(self, analysis_results: Dict, output_path: str = None) -> str:
        """Export threat intelligence report"""
        if output_path is None:
            output_path = f"/home/kali/Desktop/tools/osint-eye/reports/threat_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        threat_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "Threat Intelligence Analysis",
                "version": "1.0",
                "analysis_engine": "OSINT-Eye Threat Intelligence"
            },
            "executive_summary": self._generate_executive_summary(analysis_results),
            "detailed_analysis": analysis_results,
            "threat_indicators": self._extract_threat_indicators(analysis_results),
            "mitigation_strategies": self._generate_mitigation_strategies(analysis_results)
        }
        
        with open(output_path, 'w') as f:
            json.dump(threat_report, f, indent=2)
        
        return output_path
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """Generate executive summary of threat analysis"""
        if "analysis_summary" in results:
            # Batch analysis
            threat_dist = results["analysis_summary"]["threat_distribution"]
            total = results["analysis_summary"]["total_profiles"]
            
            return {
                "total_profiles_analyzed": total,
                "threat_breakdown": threat_dist,
                "high_priority_threats": threat_dist["critical"] + threat_dist["high"],
                "overall_risk_assessment": self._calculate_overall_risk(threat_dist, total),
                "key_findings": self._extract_key_findings(results)
            }
        else:
            # Single profile analysis
            return {
                "profile_threat_score": results.get("overall_threat_score", 0),
                "severity_level": results.get("severity_level", "unknown"),
                "threat_categories": len(results.get("threat_categories", [])),
                "confidence_level": results.get("confidence_score", 0)
            }
    
    def _calculate_overall_risk(self, threat_dist: Dict, total: int) -> str:
        """Calculate overall risk assessment"""
        if total == 0:
            return "unknown"
        
        high_risk_ratio = (threat_dist["critical"] + threat_dist["high"]) / total
        
        if high_risk_ratio > 0.3:
            return "critical"
        elif high_risk_ratio > 0.15:
            return "high"
        elif high_risk_ratio > 0.05:
            return "medium"
        else:
            return "low"
    
    def _extract_key_findings(self, results: Dict) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        if "network_threats" in results:
            coordinated = results["network_threats"].get("coordinated_threats", [])
            if coordinated:
                findings.append(f"Detected {len(coordinated)} potential coordinated threat campaigns")
        
        if "individual_analyses" in results:
            high_confidence_threats = 0
            for analysis in results["individual_analyses"].values():
                if analysis.get("overall_threat_score", 0) > 80:
                    high_confidence_threats += 1
            
            if high_confidence_threats > 0:
                findings.append(f"Identified {high_confidence_threats} high-confidence threat profiles")
        
        return findings
    
    def _extract_threat_indicators(self, results: Dict) -> Dict:
        """Extract threat indicators for future reference"""
        indicators = {
            "suspicious_keywords": set(),
            "malicious_patterns": set(),
            "threat_signatures": []
        }
        
        if "individual_analyses" in results:
            for analysis in results["individual_analyses"].values():
                detailed = analysis.get("detailed_analysis", {})
                
                for threat_type, threat_data in detailed.items():
                    for indicator in threat_data.get("indicators", []):
                        if "keyword" in indicator.lower():
                            indicators["suspicious_keywords"].add(indicator)
                        elif "pattern" in indicator.lower():
                            indicators["malicious_patterns"].add(indicator)
        
        # Convert sets to lists for JSON serialization
        indicators["suspicious_keywords"] = list(indicators["suspicious_keywords"])
        indicators["malicious_patterns"] = list(indicators["malicious_patterns"])
        
        return indicators
    
    def _generate_mitigation_strategies(self, results: Dict) -> List[Dict]:
        """Generate mitigation strategies based on analysis"""
        strategies = []
        
        # Generic strategies
        strategies.extend([
            {
                "strategy": "Automated Monitoring",
                "description": "Implement automated monitoring for high-risk profiles",
                "priority": "high",
                "implementation": "Set up alerts for profile changes and suspicious activity"
            },
            {
                "strategy": "User Education",
                "description": "Educate users about identified threat patterns",
                "priority": "medium",
                "implementation": "Create awareness campaigns about scam indicators"
            },
            {
                "strategy": "Platform Reporting",
                "description": "Report confirmed threats to platform administrators",
                "priority": "high",
                "implementation": "Submit detailed reports with evidence"
            }
        ])
        
        # Specific strategies based on detected threats
        if "network_threats" in results:
            coordinated = results["network_threats"].get("coordinated_threats", [])
            if coordinated:
                strategies.append({
                    "strategy": "Coordinated Threat Response",
                    "description": "Address coordinated threat campaigns",
                    "priority": "critical",
                    "implementation": "Block entire threat networks, not just individual accounts"
                })
        
        return strategies