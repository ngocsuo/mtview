"""YouTube helper functions."""

import re
from typing import Optional
import requests
from bs4 import BeautifulSoup


def get_latest_video_url(channel_url: str) -> Optional[str]:
    """Extract latest video URL from YouTube channel.
    
    Supports:
    - youtube.com/c/channelname
    - youtube.com/@username
    - youtube.com/channel/CHANNEL_ID
    """
    try:
        # Normalize URL
        if not channel_url.startswith("http"):
            channel_url = f"https://www.youtube.com/{channel_url}"
        
        # Add /videos to get videos page
        if not channel_url.endswith("/videos"):
            channel_url = channel_url.rstrip("/") + "/videos"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        resp = requests.get(channel_url, headers=headers, timeout=15)
        if not resp.ok:
            return None
        
        # Parse HTML
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find video IDs in various script tags
        video_id = None
        
        # Method 1: ytInitialData
        for script in soup.find_all('script'):
            if script.string and 'ytInitialData' in script.string:
                # Extract video ID from ytInitialData
                match = re.search(r'"videoId":"([^"]+)"', script.string)
                if match:
                    video_id = match.group(1)
                    break
        
        # Method 2: Direct link tags
        if not video_id:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/watch?v=' in href:
                    match = re.search(r'/watch\?v=([a-zA-Z0-9_-]{11})', href)
                    if match:
                        video_id = match.group(1)
                        break
        
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        
        return None
        
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None
