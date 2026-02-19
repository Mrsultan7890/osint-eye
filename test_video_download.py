#!/usr/bin/env python3

import requests
import os

def test_video_download():
    """Test video download functionality"""
    
    # Sample video URLs for testing
    test_videos = [
        "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
        "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4"
    ]
    
    # Create test directory
    download_dir = "images/test_videos"
    os.makedirs(download_dir, exist_ok=True)
    
    downloaded_files = []
    
    for i, url in enumerate(test_videos):
        try:
            print(f"Testing video download {i+1}: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                filename = f"test_video_{i+1}.mp4"
                filepath = os.path.join(download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(filepath)
                downloaded_files.append(filepath)
                print(f"✅ Downloaded VIDEO: {filepath} ({file_size:,} bytes)")
            else:
                print(f"❌ Failed to download: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
    
    print(f"\nDownload complete: {len(downloaded_files)} videos downloaded")
    return downloaded_files

if __name__ == "__main__":
    test_video_download()