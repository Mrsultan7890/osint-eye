import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from utils.logger import setup_logger

logger = setup_logger()

class BulkAnalyzer:
    def __init__(self):
        self.max_workers = 3
        
    def analyze_multiple_accounts(self, usernames: List[str], platform: str) -> Dict[str, Any]:
        """Analyze multiple accounts"""
        results = {}
        
        for username in usernames:
            try:
                result = self._analyze_single_account(username, platform)
                results[username] = result
                logger.info(f"Analyzed {username}")
                time.sleep(3)  # Rate limiting
            except Exception as e:
                results[username] = {'error': str(e)}
        
        return {
            'total_analyzed': len(results),
            'results': results
        }
    
    def search_similar_usernames(self, base_username: str, platform: str) -> List[Dict[str, Any]]:
        """Search for similar usernames"""
        variations = self._generate_variations(base_username)
        found_accounts = []
        
        for variation in variations[:10]:
            try:
                result = self._analyze_single_account(variation, platform)
                if result and result.get('profile', {}).get('followers', 0) > 0:
                    found_accounts.append({
                        'username': variation,
                        'profile': result['profile']
                    })
                time.sleep(2)
            except:
                continue
        
        return found_accounts
    
    def _analyze_single_account(self, username: str, platform: str) -> Dict[str, Any]:
        """Analyze single account"""
        if platform == 'instagram':
            from fetchers.instagram_fetcher import InstagramFetcher
            fetcher = InstagramFetcher()
            return fetcher.fetch_user_data(username, max_posts=1)
        return {}
    
    def _generate_variations(self, username: str) -> List[str]:
        """Generate username variations"""
        variations = []
        
        for i in range(1, 5):
            variations.extend([
                f"{username}{i}",
                f"{username}_{i}"
            ])
        
        variations.extend([
            f"{username}_official",
            f"{username}_real",
            f"_{username}",
            f"{username}_"
        ])
        
        return variations