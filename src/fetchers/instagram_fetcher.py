import requests
from bs4 import BeautifulSoup
import re
import random
import os
from typing import Dict, List, Any
from utils.rate_limiter import rate_limit
from utils.logger import setup_logger
from urllib.parse import urlparse

logger = setup_logger()

class InstagramFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @rate_limit(delay=3)
    def fetch_user_data(self, username: str, max_posts: int = 20, download_media: bool = False, max_downloads: int = 4) -> Dict[str, Any]:
        """Fetch Instagram data with video support"""
        try:
            logger.info(f"Fetching Instagram data for @{username}")
            
            url = f"https://www.instagram.com/{username}/"
            response = self.session.get(url, timeout=10)
            
            profile_data = {
                'username': username,
                'full_name': '',
                'biography': '',
                'followers': 0,
                'followees': 0,
                'posts_count': 0,
                'is_verified': False,
                'is_private': False,
                'external_url': '',
                'profile_pic_url': ''
            }
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract real name from title
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.text
                    if '(@' in title_text:
                        profile_data['full_name'] = title_text.split('(@')[0].strip()
                    elif '•' in title_text:
                        profile_data['full_name'] = title_text.split('•')[0].strip()
                
                # Get profile pic URL
                og_image = soup.find('meta', {'property': 'og:image'})
                if og_image:
                    profile_data['profile_pic_url'] = og_image.get('content', '')
                
                # Extract data from meta description
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc:
                    desc = meta_desc.get('content', '')
                    
                    # Extract followers
                    follower_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Followers', desc)
                    if follower_match:
                        profile_data['followers'] = self._parse_count(follower_match.group(1))
                    
                    # Extract following
                    following_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Following', desc)
                    if following_match:
                        profile_data['followees'] = self._parse_count(following_match.group(1))
                    
                    # Extract posts count
                    posts_match = re.search(r'([0-9,]+(?:\.[0-9]+)?[KMB]?)\s*Posts', desc)
                    if posts_match:
                        profile_data['posts_count'] = self._parse_count(posts_match.group(1))
                    
                    # Extract bio
                    bio_patterns = [
                        r'on Instagram:\s*"([^"]+)"',
                        r'"([^"]{10,})"'
                    ]
                    
                    for pattern in bio_patterns:
                        bio_match = re.search(pattern, desc)
                        if bio_match and not profile_data['biography']:
                            profile_data['biography'] = bio_match.group(1).strip()
                            break
                    
                    logger.info(f"Real data: {profile_data['followers']} followers, bio: '{profile_data['biography'][:50]}'")
            
            # Instagram Reality Check - Post Data Limitation
            posts = []
            stories = []
            
            logger.info("🔍 INSTAGRAM DATA EXTRACTION REPORT:")
            logger.info("✅ REAL DATA EXTRACTED:")
            logger.info(f"   • Followers: {profile_data['followers']:,}")
            logger.info(f"   • Bio: '{profile_data['biography'][:50]}'")
            logger.info(f"   • Posts Count: {profile_data['posts_count']:,}")
            logger.info(f"   • Profile Picture: Available")
            
            logger.info("❌ INSTAGRAM LIMITATIONS (Login Required):")
            logger.info("   • Individual post likes/comments")
            logger.info("   • Real post captions")
            logger.info("   • Actual hashtags used")
            logger.info("   • Post images/videos")
            logger.info("   • Stories content")
            
            # Only extract profile picture for download
            media_urls = []
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                profile_pic = og_image.get('content', '')
                if profile_pic and 'scontent' in profile_pic:
                    media_urls = [profile_pic]
                    logger.info("✅ Profile picture available for download")
            
            # Generate demonstration posts (clearly marked as generated)
            if profile_data['posts_count'] > 0:
                logger.info("\n📝 GENERATING SAMPLE POST DATA (For Analysis Demo):")
                logger.info("⚠️  Note: Post engagement data is ESTIMATED, not real Instagram data")
                
                sample_posts = min(max_posts, 5)  # Limit to 5 to be clear it's demo
                for i in range(sample_posts):
                    post_data = {
                        'id': f'demo_post_{username}_{i}',
                        'caption': f'[DEMO] Sample post {i+1} for analysis demonstration',
                        'likes': 0,  # Set to 0 to indicate no real data
                        'comments': 0,  # Set to 0 to indicate no real data
                        'timestamp': '2024-01-01T12:00:00Z',
                        'media_type': 'unknown',
                        'hashtags': [],  # Empty since we don't have real hashtags
                        'mentions': [],  # Empty since we don't have real mentions
                        'data_source': 'generated_demo',  # Mark as demo data
                        'note': 'This is demonstration data - real post metrics require Instagram login'
                    }
                    
                    posts.append(post_data)
                
                # Download media if requested
                if download_media and media_urls:
                    downloaded_files = self._download_media(media_urls[:max_downloads], username)
                    logger.info(f"Downloaded {len(downloaded_files)} media files")
                    
                    # Update posts with local file paths
                    for i, file_path in enumerate(downloaded_files):
                        if i < len(posts):
                            posts[i]['local_media_path'] = file_path
                
                logger.info(f"Generated {len(posts)} demo posts for analysis framework testing")
            else:
                logger.info("No posts to analyze (account has 0 posts)")
            
            # Add data source information to return data
            data_limitations = {
                'real_data': ['followers', 'biography', 'posts_count', 'profile_picture'],
                'unavailable_data': ['post_likes', 'post_comments', 'post_captions', 'hashtags', 'post_media'],
                'reason': 'Instagram requires login for detailed post data',
                'demo_data_generated': len(posts) > 0
            }
            
            return {
                'profile': profile_data,
                'posts': posts,
                'stories': stories,
                'total_fetched': len(posts),
                'data_limitations': data_limitations
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                'profile': profile_data,
                'posts': [],
                'stories': [],
                'total_fetched': 0,
                'data_limitations': {
                    'real_data': ['basic_profile_info'],
                    'unavailable_data': ['all_post_data'],
                    'reason': f'Error occurred: {str(e)}',
                    'demo_data_generated': False
                }
            }
    
    def _parse_count(self, count_str: str) -> int:
        """Parse count strings"""
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
    
    def _extract_media_urls(self, soup: BeautifulSoup, username: str) -> List[str]:
        """Extract REAL media URLs from Instagram profile"""
        media_urls = []
        
        try:
            # Method 1: Extract from JSON-LD structured data
            json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if 'mainEntity' in data and 'image' in data['mainEntity']:
                        images = data['mainEntity']['image']
                        if isinstance(images, list):
                            for img in images[:5]:
                                if isinstance(img, str) and 'scontent' in img:
                                    media_urls.append(img)
                                    logger.info(f"Found JSON-LD image: {img[:80]}...")
                except:
                    continue
            
            # Method 2: Extract from window._sharedData
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        import json
                        content = script.string
                        start = content.find('window._sharedData = ') + len('window._sharedData = ')
                        end = content.find(';</script>')
                        if start > 20 and end > start:
                            shared_data = json.loads(content[start:end])
                            
                            # Navigate through the data structure
                            entry_data = shared_data.get('entry_data', {})
                            profile_page = entry_data.get('ProfilePage', [{}])
                            if profile_page:
                                graphql = profile_page[0].get('graphql', {})
                                user = graphql.get('user', {})
                                timeline = user.get('edge_owner_to_timeline_media', {})
                                edges = timeline.get('edges', [])
                                
                                for edge in edges[:10]:
                                    node = edge.get('node', {})
                                    # Get display URL (thumbnail)
                                    if 'display_url' in node:
                                        media_urls.append(node['display_url'])
                                        logger.info(f"Found post image: {node['display_url'][:80]}...")
                                    
                                    # Get video URL if it's a video post
                                    if node.get('is_video') and 'video_url' in node:
                                        media_urls.append(node['video_url'])
                                        logger.info(f"Found post VIDEO: {node['video_url'][:80]}...")
                                    
                                    # Get additional resources
                                    if 'edge_sidecar_to_children' in node:
                                        children = node['edge_sidecar_to_children'].get('edges', [])
                                        for child in children:
                                            child_node = child.get('node', {})
                                            if 'display_url' in child_node:
                                                media_urls.append(child_node['display_url'])
                                            if child_node.get('is_video') and 'video_url' in child_node:
                                                media_urls.append(child_node['video_url'])
                                                logger.info(f"Found carousel VIDEO: {child_node['video_url'][:80]}...")
                            break
                    except Exception as e:
                        logger.error(f"Error parsing shared data: {e}")
                        continue
            
            # Method 3: Extract from regular script tags with different patterns
            for script in scripts:
                if script.string and ('display_url' in script.string or 'video_url' in script.string):
                    content = script.string
                    
                    # More specific patterns for Instagram media
                    patterns = [
                        r'"display_url":"(https://scontent[^"]+)"',
                        r'"video_url":"(https://scontent[^"]+)"',
                        r'"thumbnail_src":"(https://scontent[^"]+)"',
                        r'"src":"(https://scontent[^"]+\.(?:jpg|jpeg|png|mp4|webp))"'
                    ]
                    
                    for pattern in patterns:
                        urls = re.findall(pattern, content)
                        for url in urls:
                            clean_url = url.replace('\\u0026', '&').replace('\\/', '/')
                            if clean_url not in media_urls and len(clean_url) > 50:
                                media_urls.append(clean_url)
                                if any(vid_ext in clean_url.lower() for vid_ext in ['.mp4', 'video']):
                                    logger.info(f"Found script VIDEO: {clean_url[:80]}...")
                                else:
                                    logger.info(f"Found script IMAGE: {clean_url[:80]}...")
            
            # Method 4: Extract from img and video tags (fallback)
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if 'scontent' in src and 'instagram' in src and len(src) > 50:
                    if src not in media_urls:
                        media_urls.append(src)
            
            video_tags = soup.find_all('video')
            for video in video_tags:
                src = video.get('src', '')
                if src and 'scontent' in src and src not in media_urls:
                    media_urls.append(src)
                    logger.info(f"Found HTML5 video: {src[:80]}...")
            
            # Remove duplicates and categorize
            unique_urls = list(dict.fromkeys(media_urls))  # Preserve order, remove duplicates
            
            video_urls = []
            image_urls = []
            
            for url in unique_urls:
                if any(vid_indicator in url.lower() for vid_indicator in ['.mp4', 'video', '/v/', '/videos/']):
                    video_urls.append(url)
                elif any(img_indicator in url.lower() for img_indicator in ['.jpg', '.jpeg', '.png', '.webp', '/s/', '/images/']):
                    image_urls.append(url)
            
            # Prioritize videos, then images
            final_urls = video_urls + image_urls
            logger.info(f"Extracted {len(video_urls)} REAL videos and {len(image_urls)} REAL images from {username}'s profile")
            
            return final_urls[:10]
            
        except Exception as e:
            logger.error(f"Error extracting real media URLs: {e}")
            return []
    
    def _try_sample_videos(self) -> List[str]:
        """Try to get sample video URLs for testing"""
        sample_videos = [
            "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        ]
        
        working_urls = []
        for url in sample_videos:
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    working_urls.append(url)
                    logger.info(f"Added sample video: {url}")
            except:
                continue
        
        return working_urls
    
    def _download_media(self, media_urls: List[str], username: str) -> List[str]:
        """Download media files"""
        downloaded_files = []
        
        # Create download directory
        download_dir = f"/home/kali/Desktop/tools/osint-eye/images/{username}"
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"Created download directory: {download_dir}")
        
        for i, url in enumerate(media_urls):
            try:
                logger.info(f"Downloading media {i+1}/{len(media_urls)}: {url[:100]}...")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
                }
                
                response = requests.get(url, headers=headers, timeout=30, stream=True)
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    # Determine file extension
                    ext = '.jpg'  # Default
                    if 'mp4' in url.lower():
                        ext = '.mp4'
                    elif 'png' in url.lower():
                        ext = '.png'
                    elif 'webp' in url.lower():
                        ext = '.webp'
                    
                    # Check content-type
                    content_type = response.headers.get('content-type', '')
                    if 'video' in content_type:
                        ext = '.mp4'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    
                    filename = f"{username}_media_{i+1}{ext}"
                    filepath = os.path.join(download_dir, filename)
                    abs_filepath = os.path.abspath(filepath)
                    
                    # Download with streaming
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(filepath)
                    downloaded_files.append(abs_filepath)
                    media_type = "VIDEO" if ext in ['.mp4', '.mov', '.webm'] else "IMAGE"
                    logger.info(f"✅ Downloaded {media_type}: {filepath} ({file_size:,} bytes)")
                else:
                    logger.warning(f"❌ Failed to download {url[:100]}: HTTP {response.status_code}")
                
                # Rate limiting
                import time
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error downloading {url[:100]}: {e}")
                continue
        
        logger.info(f"Download complete: {len(downloaded_files)} files saved in {download_dir}")
        return downloaded_files
    
    def _generate_realistic_caption(self, username: str, post_num: int) -> str:
        """Generate realistic captions"""
        captions = {
            'virat.kohli': [
                'Training hard for the next match! 💪 #cricket #training #nevergiveup',
                'Grateful for all the love and support! ❤️ #blessed #teamwork #cricket',
                'Another day, another opportunity to improve! 🏏 #cricket #motivation #hardwork',
                'With my team, we are unstoppable! 🔥 #teamvirat #cricket #champions'
            ],
            'cristiano': [
                'Always working to be better! 💪 #cr7 #football #training #siuuu',
                'Grateful for this amazing journey! ⚽ #blessed #football #champions',
                'Hard work pays off! 🏆 #dedication #football #nevergiveup #cr7',
                'With my family, everything is possible! ❤️ #family #blessed #football'
            ]
        }
        
        user_captions = captions.get(username, [
            'Living my best life! 💫 #blessed #life #motivation',
            'Another amazing day! ✨ #grateful #inspiration #success',
            'Working hard, dreaming big! 🚀 #goals #hustle #success',
            'Thankful for all the support! ❤️ #blessed #grateful #love'
        ])
        
        return user_captions[post_num % len(user_captions)]
    
    def _get_realistic_hashtags(self, username: str) -> List[str]:
        """Get realistic hashtags based on username"""
        hashtag_sets = {
            'cristiano': ['#cr7', '#football', '#siuuu', '#manchesterunited', '#portugal', '#training', '#champions'],
            'virat.kohli': ['#cricket', '#teamindia', '#rcb', '#kingkohli', '#batting', '#champions', '#nevergiveup'],
            'leomessi': ['#messi', '#football', '#psg', '#argentina', '#goat', '#barcelona', '#champions'],
            'selenagomez': ['#music', '#acting', '#love', '#blessed', '#grateful', '#inspiration', '#selena'],
            'kyliejenner': ['#kylie', '#makeup', '#fashion', '#family', '#blessed', '#entrepreneur', '#beauty']
        }
        
        default_tags = ['#life', '#blessed', '#motivation', '#inspiration', '#success', '#grateful', '#love']
        return hashtag_sets.get(username, default_tags)
    
    def _get_realistic_mentions(self, username: str) -> List[str]:
        """Get realistic mentions based on username"""
        mention_sets = {
            'cristiano': ['@nike', '@cr7', '@manchesterunited', '@portugal', '@championsleague'],
            'virat.kohli': ['@bcci', '@royalchallengersbangalore', '@puma', '@teamindia', '@ipl'],
            'leomessi': ['@psg', '@adidas', '@fcbarcelona', '@argentina', '@championsleague'],
            'selenagomez': ['@rarebeauty', '@netflix', '@disney', '@unicef', '@coach'],
            'kyliejenner': ['@kyliecosmetics', '@kyliebaby', '@kendalljenner', '@krisjenner', '@stormiwebster']
        }
        
        default_mentions = ['@friends', '@family', '@team', '@brand', '@sponsor']
        return mention_sets.get(username, default_mentions)