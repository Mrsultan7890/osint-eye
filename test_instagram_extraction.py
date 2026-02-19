#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import json

def test_instagram_extraction(username):
    """Test what data we can actually extract from Instagram"""
    
    url = f"https://www.instagram.com/{username}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("\n=== AVAILABLE DATA ===")
            
            # Check meta tags
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                print(f"Meta Description: {meta_desc.get('content', '')[:200]}...")
            
            # Check for JSON-LD
            json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            print(f"JSON-LD Scripts Found: {len(json_scripts)}")
            
            # Check for window._sharedData
            scripts = soup.find_all('script')
            shared_data_found = False
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    shared_data_found = True
                    print("✅ window._sharedData found")
                    break
            
            if not shared_data_found:
                print("❌ window._sharedData not found")
            
            # Check what's actually in the page
            page_text = response.text
            
            # Look for media indicators
            media_indicators = [
                'display_url',
                'video_url', 
                'thumbnail_src',
                'edge_owner_to_timeline_media',
                'GraphImage',
                'GraphVideo'
            ]
            
            print("\n=== MEDIA INDICATORS ===")
            for indicator in media_indicators:
                count = page_text.count(indicator)
                print(f"{indicator}: {count} occurrences")
            
            # Look for actual scontent URLs
            scontent_urls = re.findall(r'https://scontent[^"\\s]+', page_text)
            print(f"\n=== SCONTENT URLS FOUND ===")
            print(f"Total scontent URLs: {len(scontent_urls)}")
            
            # Categorize URLs
            images = [url for url in scontent_urls if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
            videos = [url for url in scontent_urls if any(ext in url.lower() for ext in ['.mp4', '.mov'])]
            
            print(f"Image URLs: {len(images)}")
            print(f"Video URLs: {len(videos)}")
            
            # Show first few URLs
            if images:
                print("\nSample Image URLs:")
                for img in images[:3]:
                    print(f"  {img[:100]}...")
            
            if videos:
                print("\nSample Video URLs:")
                for vid in videos[:3]:
                    print(f"  {vid[:100]}...")
            
            return {
                'images': images,
                'videos': videos,
                'total_media': len(images) + len(videos)
            }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with different usernames
    usernames = ['cristiano', 'virat.kohli', 'leomessi']
    
    for username in usernames:
        print(f"\n{'='*50}")
        print(f"TESTING: {username}")
        print(f"{'='*50}")
        
        result = test_instagram_extraction(username)
        if result:
            print(f"\nSUMMARY for {username}:")
            print(f"  Images: {len(result['images'])}")
            print(f"  Videos: {len(result['videos'])}")
            print(f"  Total: {result['total_media']}")