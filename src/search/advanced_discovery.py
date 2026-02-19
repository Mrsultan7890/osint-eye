#!/usr/bin/env python3

import re
import itertools
import requests
from typing import Dict, List, Set, Optional, Tuple
import json
from datetime import datetime
import hashlib
from urllib.parse import urlparse, parse_qs
import time
import random

class AdvancedDiscovery:
    def __init__(self):
        self.common_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
            "protonmail.com", "icloud.com", "aol.com"
        ]
        
        self.social_platforms = {
            "instagram.com": "instagram",
            "twitter.com": "twitter", 
            "x.com": "twitter",
            "youtube.com": "youtube",
            "tiktok.com": "tiktok",
            "linkedin.com": "linkedin",
            "facebook.com": "facebook",
            "snapchat.com": "snapchat",
            "pinterest.com": "pinterest",
            "reddit.com": "reddit",
            "github.com": "github",
            "twitch.tv": "twitch"
        }
        
        self.username_patterns = [
            "{base}",
            "{base}_{year}",
            "{base}{year}",
            "{base}_{random}",
            "{base}{random}",
            "_{base}",
            "{base}_",
            "{base}.{random}",
            "{base}-{random}",
            "{first}.{last}",
            "{first}_{last}",
            "{first}{last}",
            "{last}.{first}",
            "{last}_{first}",
            "{last}{first}"
        ]
    
    def generate_username_variations(self, base_username: str, 
                                   first_name: str = None, 
                                   last_name: str = None) -> List[str]:
        """Generate possible username variations"""
        variations = set()
        
        # Basic variations
        variations.add(base_username)
        variations.add(base_username.lower())
        variations.add(base_username.upper())
        variations.add(base_username.capitalize())
        
        # Number variations
        for i in range(1, 100):
            variations.add(f"{base_username}{i}")
            variations.add(f"{base_username}_{i}")
            variations.add(f"{base_username}.{i}")
            variations.add(f"{base_username}-{i}")
        
        # Year variations
        current_year = datetime.now().year
        for year in range(1990, current_year + 1):
            variations.add(f"{base_username}{year}")
            variations.add(f"{base_username}_{year}")
            variations.add(f"{year}{base_username}")
            variations.add(f"{year}_{base_username}")
        
        # Character substitutions
        char_subs = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 
            'o': ['0'], 's': ['5', '$'], 't': ['7']
        }
        
        for char, subs in char_subs.items():
            for sub in subs:
                if char in base_username.lower():
                    variations.add(base_username.lower().replace(char, sub))
        
        # Name-based variations if provided
        if first_name and last_name:
            name_variations = self._generate_name_variations(first_name, last_name)
            variations.update(name_variations)
        
        # Remove duplicates and sort
        return sorted(list(variations))[:100]  # Limit to 100 variations
    
    def _generate_name_variations(self, first_name: str, last_name: str) -> Set[str]:
        """Generate variations based on first and last name"""
        variations = set()
        
        first = first_name.lower()
        last = last_name.lower()
        
        # Basic combinations
        variations.update([
            f"{first}.{last}",
            f"{first}_{last}",
            f"{first}{last}",
            f"{last}.{first}",
            f"{last}_{first}",
            f"{last}{first}",
            f"{first[0]}.{last}",
            f"{first}.{last[0]}",
            f"{first[0]}{last}",
            f"{first}{last[0]}"
        ])
        
        # With numbers
        for i in range(1, 20):
            variations.update([
                f"{first}.{last}{i}",
                f"{first}_{last}{i}",
                f"{first}{last}{i}",
                f"{first}.{last}_{i}",
                f"{first}_{last}_{i}"
            ])
        
        return variations
    
    def find_email_patterns(self, username: str, domain: str = None) -> List[str]:
        """Generate possible email patterns"""
        emails = []
        
        domains_to_check = [domain] if domain else self.common_domains
        
        for domain in domains_to_check:
            # Basic patterns
            emails.extend([
                f"{username}@{domain}",
                f"{username.lower()}@{domain}",
                f"{username.upper()}@{domain}"
            ])
            
            # With dots and underscores
            if len(username) > 3:
                emails.extend([
                    f"{username[:3]}.{username[3:]}@{domain}",
                    f"{username[:2]}_{username[2:]}@{domain}",
                    f"{username[0]}.{username[1:]}@{domain}"
                ])
            
            # With numbers
            for i in range(1, 10):
                emails.extend([
                    f"{username}{i}@{domain}",
                    f"{username}.{i}@{domain}",
                    f"{username}_{i}@{domain}"
                ])
        
        return list(set(emails))  # Remove duplicates
    
    def discover_social_profiles(self, username: str, 
                               check_variations: bool = True) -> Dict[str, List[Dict]]:
        """Discover social media profiles across platforms"""
        results = {
            "found_profiles": [],
            "possible_profiles": [],
            "checked_platforms": [],
            "username_variations": []
        }
        
        usernames_to_check = [username]
        if check_variations:
            variations = self.generate_username_variations(username)
            usernames_to_check.extend(variations[:20])  # Limit to avoid rate limiting
            results["username_variations"] = variations
        
        for platform_domain, platform_name in self.social_platforms.items():
            results["checked_platforms"].append(platform_name)
            
            for user in usernames_to_check:
                profile_url = self._construct_profile_url(platform_domain, user)
                
                if profile_url:
                    status = self._check_profile_exists(profile_url)
                    
                    profile_info = {
                        "platform": platform_name,
                        "username": user,
                        "url": profile_url,
                        "status": status,
                        "checked_at": datetime.now().isoformat()
                    }
                    
                    if status == "exists":
                        results["found_profiles"].append(profile_info)
                    elif status == "possible":
                        results["possible_profiles"].append(profile_info)
                
                # Rate limiting
                time.sleep(random.uniform(1, 3))
        
        return results
    
    def _construct_profile_url(self, domain: str, username: str) -> Optional[str]:
        """Construct profile URL for different platforms"""
        url_patterns = {
            "instagram.com": f"https://www.instagram.com/{username}/",
            "twitter.com": f"https://twitter.com/{username}",
            "x.com": f"https://x.com/{username}",
            "youtube.com": f"https://www.youtube.com/@{username}",
            "tiktok.com": f"https://www.tiktok.com/@{username}",
            "linkedin.com": f"https://www.linkedin.com/in/{username}/",
            "facebook.com": f"https://www.facebook.com/{username}",
            "github.com": f"https://github.com/{username}",
            "reddit.com": f"https://www.reddit.com/user/{username}",
            "pinterest.com": f"https://www.pinterest.com/{username}/",
            "snapchat.com": f"https://www.snapchat.com/add/{username}",
            "twitch.tv": f"https://www.twitch.tv/{username}"
        }
        
        return url_patterns.get(domain)
    
    def _check_profile_exists(self, url: str) -> str:
        """Check if a profile URL exists"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Check status code
            if response.status_code == 200:
                # Additional checks for content
                content = response.text.lower()
                
                # Check for common "not found" indicators
                not_found_indicators = [
                    "page not found", "user not found", "profile not found",
                    "doesn't exist", "not available", "suspended",
                    "404", "this account doesn't exist"
                ]
                
                if any(indicator in content for indicator in not_found_indicators):
                    return "not_found"
                
                # Check for profile indicators
                profile_indicators = [
                    "followers", "following", "posts", "tweets",
                    "profile", "bio", "about"
                ]
                
                if any(indicator in content for indicator in profile_indicators):
                    return "exists"
                
                return "possible"
            
            elif response.status_code == 404:
                return "not_found"
            elif response.status_code == 403:
                return "private_or_blocked"
            else:
                return "unknown"
                
        except requests.RequestException:
            return "error"
    
    def analyze_username_patterns(self, usernames: List[str]) -> Dict:
        """Analyze patterns in a list of usernames"""
        analysis = {
            "total_usernames": len(usernames),
            "length_distribution": {},
            "character_patterns": {},
            "common_prefixes": [],
            "common_suffixes": [],
            "number_patterns": {},
            "special_chars": {},
            "similarity_clusters": []
        }
        
        # Length distribution
        lengths = [len(u) for u in usernames]
        for length in set(lengths):
            analysis["length_distribution"][length] = lengths.count(length)
        
        # Character patterns
        for username in usernames:
            # Count digits
            digit_count = sum(c.isdigit() for c in username)
            if digit_count not in analysis["number_patterns"]:
                analysis["number_patterns"][digit_count] = 0
            analysis["number_patterns"][digit_count] += 1
            
            # Count special characters
            special_chars = set(c for c in username if not c.isalnum())
            for char in special_chars:
                if char not in analysis["special_chars"]:
                    analysis["special_chars"][char] = 0
                analysis["special_chars"][char] += 1
        
        # Common prefixes and suffixes
        prefixes = [u[:3] for u in usernames if len(u) >= 3]
        suffixes = [u[-3:] for u in usernames if len(u) >= 3]
        
        prefix_counts = {}
        suffix_counts = {}
        
        for prefix in prefixes:
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        for suffix in suffixes:
            suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
        
        # Get most common
        analysis["common_prefixes"] = sorted(prefix_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
        analysis["common_suffixes"] = sorted(suffix_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
        
        return analysis
    
    def find_domain_correlations(self, email_or_username: str) -> Dict:
        """Find potential domain correlations"""
        correlations = {
            "potential_domains": [],
            "social_handles": [],
            "professional_profiles": [],
            "personal_domains": []
        }
        
        base_name = email_or_username.split('@')[0] if '@' in email_or_username else email_or_username
        
        # Generate potential domains
        domain_patterns = [
            f"{base_name}.com",
            f"{base_name}.net", 
            f"{base_name}.org",
            f"{base_name}.io",
            f"{base_name}.me",
            f"www.{base_name}.com"
        ]
        
        for domain in domain_patterns:
            status = self._check_domain_exists(domain)
            correlations["potential_domains"].append({
                "domain": domain,
                "status": status,
                "checked_at": datetime.now().isoformat()
            })
        
        # Check for social media handles
        for platform_domain, platform_name in self.social_platforms.items():
            profile_url = self._construct_profile_url(platform_domain, base_name)
            if profile_url:
                correlations["social_handles"].append({
                    "platform": platform_name,
                    "url": profile_url,
                    "username": base_name
                })
        
        return correlations
    
    def _check_domain_exists(self, domain: str) -> str:
        """Check if a domain exists"""
        try:
            response = requests.get(f"http://{domain}", timeout=5)
            if response.status_code == 200:
                return "active"
            else:
                return "inactive"
        except:
            try:
                response = requests.get(f"https://{domain}", timeout=5)
                if response.status_code == 200:
                    return "active_https"
                else:
                    return "inactive"
            except:
                return "not_found"
    
    def search_data_breaches(self, email: str) -> Dict:
        """Search for email in known data breach patterns (educational purposes)"""
        # This is a simplified version - in real implementation, 
        # you would check against known breach databases
        
        breach_indicators = {
            "common_patterns": [],
            "risk_assessment": "unknown",
            "recommendations": []
        }
        
        # Check email pattern against common breach patterns
        domain = email.split('@')[1] if '@' in email else ""
        
        # High-risk domains (commonly targeted)
        high_risk_domains = [
            "yahoo.com", "hotmail.com", "gmail.com", 
            "aol.com", "live.com"
        ]
        
        if domain in high_risk_domains:
            breach_indicators["risk_assessment"] = "medium"
            breach_indicators["recommendations"].append(
                "Email domain commonly found in data breaches"
            )
        
        # Check for common password patterns in username
        username = email.split('@')[0]
        weak_patterns = ['123', 'password', 'admin', 'user']
        
        if any(pattern in username.lower() for pattern in weak_patterns):
            breach_indicators["common_patterns"].append("Weak username pattern")
            breach_indicators["recommendations"].append(
                "Username contains common weak patterns"
            )
        
        return breach_indicators
    
    def bulk_username_search(self, usernames: List[str], 
                           platforms: List[str] = None) -> Dict:
        """Perform bulk username search across platforms"""
        if platforms is None:
            platforms = list(self.social_platforms.values())
        
        results = {
            "search_summary": {
                "total_usernames": len(usernames),
                "platforms_checked": len(platforms),
                "started_at": datetime.now().isoformat()
            },
            "results": {},
            "statistics": {
                "found_profiles": 0,
                "possible_profiles": 0,
                "not_found": 0
            }
        }
        
        for username in usernames:
            print(f"Searching for: {username}")
            user_results = []
            
            for platform_domain, platform_name in self.social_platforms.items():
                if platform_name in platforms:
                    profile_url = self._construct_profile_url(platform_domain, username)
                    
                    if profile_url:
                        status = self._check_profile_exists(profile_url)
                        
                        result = {
                            "platform": platform_name,
                            "url": profile_url,
                            "status": status
                        }
                        
                        user_results.append(result)
                        
                        # Update statistics
                        if status == "exists":
                            results["statistics"]["found_profiles"] += 1
                        elif status == "possible":
                            results["statistics"]["possible_profiles"] += 1
                        else:
                            results["statistics"]["not_found"] += 1
                    
                    # Rate limiting
                    time.sleep(random.uniform(0.5, 2))
            
            results["results"][username] = user_results
        
        results["search_summary"]["completed_at"] = datetime.now().isoformat()
        return results
    
    def generate_search_report(self, search_results: Dict, output_path: str = None) -> str:
        """Generate a comprehensive search report"""
        if output_path is None:
            output_path = f"/home/kali/Desktop/tools/osint-eye/reports/search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "Advanced Discovery Report",
                "version": "1.0"
            },
            "search_results": search_results,
            "analysis": self._analyze_search_results(search_results),
            "recommendations": self._generate_search_recommendations(search_results)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path
    
    def _analyze_search_results(self, results: Dict) -> Dict:
        """Analyze search results for patterns"""
        analysis = {
            "platform_success_rates": {},
            "username_patterns": {},
            "discovery_insights": []
        }
        
        if "results" in results:
            total_searches = len(results["results"])
            platform_stats = {}
            
            for username, user_results in results["results"].items():
                for result in user_results:
                    platform = result["platform"]
                    status = result["status"]
                    
                    if platform not in platform_stats:
                        platform_stats[platform] = {"total": 0, "found": 0}
                    
                    platform_stats[platform]["total"] += 1
                    if status == "exists":
                        platform_stats[platform]["found"] += 1
            
            # Calculate success rates
            for platform, stats in platform_stats.items():
                success_rate = (stats["found"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                analysis["platform_success_rates"][platform] = round(success_rate, 2)
        
        return analysis
    
    def _generate_search_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on search results"""
        recommendations = []
        
        if "statistics" in results:
            stats = results["statistics"]
            total = stats.get("found_profiles", 0) + stats.get("possible_profiles", 0) + stats.get("not_found", 0)
            
            if total > 0:
                found_rate = (stats.get("found_profiles", 0) / total) * 100
                
                if found_rate > 70:
                    recommendations.append("High profile discovery rate - target appears to have strong online presence")
                elif found_rate > 30:
                    recommendations.append("Moderate profile discovery rate - consider checking username variations")
                else:
                    recommendations.append("Low profile discovery rate - target may use different usernames or have limited online presence")
        
        recommendations.extend([
            "Verify found profiles manually for accuracy",
            "Check profile creation dates for timeline analysis",
            "Look for cross-platform content correlation",
            "Monitor profiles for activity patterns"
        ])
        
        return recommendations