import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class DataManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def save_data(self, platform: str, username: str, data: Dict[str, Any]):
        """Save fetched data to JSON file"""
        user_dir = self.base_dir / platform / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.json"
        filepath = user_dir / filename
        
        # Add metadata
        data['metadata'] = {
            'platform': platform,
            'username': username,
            'timestamp': timestamp,
            'fetched_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Create/update latest symlink
        latest_path = user_dir / "latest.json"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(filename)
        
        return filepath
    
    def load_data(self, platform: str, username: str, timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load data from JSON file"""
        user_dir = self.base_dir / platform / username
        
        if not user_dir.exists():
            return None
        
        if timestamp:
            filepath = user_dir / f"data_{timestamp}.json"
        else:
            filepath = user_dir / "latest.json"
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def save_analysis(self, platform: str, username: str, analysis: Dict[str, Any]):
        """Save analysis results"""
        user_dir = self.base_dir / platform / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.json"
        filepath = user_dir / filename
        
        analysis['metadata'] = {
            'platform': platform,
            'username': username,
            'analyzed_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        # Create/update latest analysis symlink
        latest_path = user_dir / "latest_analysis.json"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(filename)
        
        return filepath
    
    def load_analysis(self, platform: str, username: str) -> Optional[Dict[str, Any]]:
        """Load latest analysis results"""
        user_dir = self.base_dir / platform / username
        filepath = user_dir / "latest_analysis.json"
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None