"""
Real-Time Instagram Monitoring System
Tracks profile changes, new posts, follower changes
"""
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger()

class RealTimeMonitor:
    def __init__(self):
        self.monitoring_data = {}
        self.data_dir = "monitoring_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def start_monitoring(self, username: str, interval_minutes: int = 30, duration_hours: int = 24):
        """Start real-time monitoring of Instagram profile"""
        logger.info(f"🔍 Starting real-time monitoring for @{username}")
        logger.info(f"⏰ Check interval: {interval_minutes} minutes")
        logger.info(f"⏳ Duration: {duration_hours} hours")
        
        end_time = datetime.now() + timedelta(hours=duration_hours)
        check_count = 0
        
        # Get baseline data
        baseline = self._get_profile_snapshot(username)
        self._save_snapshot(username, baseline, "baseline")
        
        logger.info(f"📊 Baseline established:")
        logger.info(f"   Followers: {baseline['followers']:,}")
        logger.info(f"   Posts: {baseline['posts_count']:,}")
        
        while datetime.now() < end_time:
            try:
                check_count += 1
                logger.info(f"🔄 Check #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Get current snapshot
                current = self._get_profile_snapshot(username)
                
                # Compare with baseline
                changes = self._detect_changes(baseline, current)
                
                if changes:
                    logger.info("🚨 CHANGES DETECTED!")
                    for change in changes:
                        logger.info(f"   • {change}")
                    
                    # Save change event
                    self._save_change_event(username, changes, current)
                    
                    # Update baseline
                    baseline = current
                
                # Save current snapshot
                self._save_snapshot(username, current, f"check_{check_count}")
                
                # Wait for next check
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute on error
        
        # Generate monitoring report
        report = self._generate_monitoring_report(username)
        logger.info(f"📋 Monitoring complete. Report saved: {report}")
        
        return report
    
    def _get_profile_snapshot(self, username: str) -> Dict[str, Any]:
        """Get current profile snapshot"""
        try:
            url = f"https://www.instagram.com/{username}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'username': username,
                'followers': 0,
                'following': 0,
                'posts_count': 0,
                'bio': '',
                'profile_pic_url': '',
                'is_verified': False,
                'is_private': False
            }
            
            # Extract data from meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '')
                
                # Extract followers
                import re
                follower_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Followers', desc)
                if follower_match:
                    snapshot['followers'] = self._parse_count(follower_match.group(1))
                
                # Extract following
                following_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Following', desc)
                if following_match:
                    snapshot['following'] = self._parse_count(following_match.group(1))
                
                # Extract posts
                posts_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Posts', desc)
                if posts_match:
                    snapshot['posts_count'] = self._parse_count(posts_match.group(1))
                
                # Extract bio
                bio_match = re.search(r'on Instagram:\s*"([^"]+)"', desc)
                if bio_match:
                    snapshot['bio'] = bio_match.group(1).strip()
            
            # Get profile pic
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                snapshot['profile_pic_url'] = og_image.get('content', '')
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error getting snapshot: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'username': username,
                'error': str(e)
            }
    
    def _parse_count(self, count_str: str) -> int:
        """Parse count strings like 1.2M, 500K"""
        try:
            count_str = count_str.strip().upper().replace(',', '')
            
            if 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            else:
                return int(count_str)
        except:
            return 0
    
    def _detect_changes(self, baseline: Dict, current: Dict) -> List[str]:
        """Detect changes between snapshots"""
        changes = []
        
        if 'error' in current:
            return changes
        
        # Follower changes
        if baseline['followers'] != current['followers']:
            diff = current['followers'] - baseline['followers']
            if diff > 0:
                changes.append(f"Followers increased by {diff:,} ({baseline['followers']:,} → {current['followers']:,})")
            else:
                changes.append(f"Followers decreased by {abs(diff):,} ({baseline['followers']:,} → {current['followers']:,})")
        
        # Following changes
        if baseline['following'] != current['following']:
            diff = current['following'] - baseline['following']
            if diff > 0:
                changes.append(f"Following increased by {diff:,}")
            else:
                changes.append(f"Following decreased by {abs(diff):,}")
        
        # Posts changes
        if baseline['posts_count'] != current['posts_count']:
            diff = current['posts_count'] - baseline['posts_count']
            if diff > 0:
                changes.append(f"New posts: +{diff}")
            else:
                changes.append(f"Posts removed: -{abs(diff)}")
        
        # Bio changes
        if baseline['bio'] != current['bio']:
            changes.append(f"Bio changed: '{baseline['bio']}' → '{current['bio']}'")
        
        # Profile picture changes
        if baseline['profile_pic_url'] != current['profile_pic_url']:
            changes.append("Profile picture changed")
        
        return changes
    
    def _save_snapshot(self, username: str, snapshot: Dict, label: str):
        """Save snapshot to file"""
        filename = f"{self.data_dir}/{username}_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(snapshot, f, indent=2)
    
    def _save_change_event(self, username: str, changes: List[str], snapshot: Dict):
        """Save change event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'changes': changes,
            'snapshot': snapshot
        }
        
        filename = f"{self.data_dir}/{username}_changes.json"
        
        # Load existing changes
        events = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                events = json.load(f)
        
        events.append(event)
        
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)
    
    def _generate_monitoring_report(self, username: str) -> str:
        """Generate comprehensive monitoring report"""
        report_file = f"{self.data_dir}/{username}_monitoring_report.json"
        
        # Load all change events
        changes_file = f"{self.data_dir}/{username}_changes.json"
        changes = []
        if os.path.exists(changes_file):
            with open(changes_file, 'r') as f:
                changes = json.load(f)
        
        # Load all snapshots
        snapshots = []
        for file in os.listdir(self.data_dir):
            if file.startswith(f"{username}_") and file.endswith('.json') and 'changes' not in file and 'report' not in file:
                with open(f"{self.data_dir}/{file}", 'r') as f:
                    snapshots.append(json.load(f))
        
        # Sort by timestamp
        snapshots.sort(key=lambda x: x.get('timestamp', ''))
        
        report = {
            'username': username,
            'monitoring_period': {
                'start': snapshots[0]['timestamp'] if snapshots else None,
                'end': snapshots[-1]['timestamp'] if snapshots else None,
                'total_checks': len(snapshots)
            },
            'summary': {
                'total_changes': len(changes),
                'follower_changes': len([c for c in changes if any('Followers' in change for change in c['changes'])]),
                'post_changes': len([c for c in changes if any('posts' in change.lower() for change in c['changes'])]),
                'bio_changes': len([c for c in changes if any('Bio' in change for change in c['changes'])])
            },
            'changes': changes,
            'snapshots': snapshots[-10:]  # Last 10 snapshots
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def get_monitoring_status(self, username: str) -> Dict:
        """Get current monitoring status"""
        changes_file = f"{self.data_dir}/{username}_changes.json"
        
        if os.path.exists(changes_file):
            with open(changes_file, 'r') as f:
                changes = json.load(f)
            
            return {
                'username': username,
                'is_monitored': True,
                'total_changes': len(changes),
                'last_change': changes[-1]['timestamp'] if changes else None,
                'recent_changes': changes[-5:] if changes else []
            }
        
        return {
            'username': username,
            'is_monitored': False,
            'total_changes': 0
        }