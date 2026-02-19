import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import setup_logger

logger = setup_logger()

class SQLiteManager:
    def __init__(self, db_path: str = "data/osint_eye.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    display_name TEXT,
                    bio TEXT,
                    followers INTEGER,
                    following INTEGER,
                    verified BOOLEAN,
                    profile_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, username)
                )
            ''')
            
            # Posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    post_id TEXT,
                    content TEXT,
                    post_date TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    hashtags JSON,
                    mentions JSON,
                    post_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            ''')
            
            # Analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    analysis_type TEXT,
                    sentiment_score REAL,
                    entity_data JSON,
                    activity_data JSON,
                    analysis_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            ''')
            
            # Relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_profile_id INTEGER,
                    target_profile_id INTEGER,
                    relationship_type TEXT,
                    strength REAL,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_profile_id) REFERENCES profiles (id),
                    FOREIGN KEY (target_profile_id) REFERENCES profiles (id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_platform_username ON profiles(platform, username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_profile_id ON posts(profile_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_platform_username ON posts(platform, username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_profile_id ON analysis(profile_id)')
            
            conn.commit()
    
    def save_profile(self, platform: str, username: str, profile_data: Dict[str, Any]) -> int:
        """Save or update profile data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Extract common fields
            display_name = profile_data.get('display_name') or profile_data.get('full_name') or profile_data.get('name', '')
            bio = profile_data.get('bio') or profile_data.get('biography') or profile_data.get('description', '')
            followers = profile_data.get('followers') or profile_data.get('followers_count', 0)
            following = profile_data.get('following') or profile_data.get('followees') or profile_data.get('friends_count', 0)
            verified = profile_data.get('verified') or profile_data.get('is_verified', False)
            
            # Insert or update profile
            cursor.execute('''
                INSERT OR REPLACE INTO profiles 
                (platform, username, display_name, bio, followers, following, verified, profile_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (platform, username, display_name, bio, followers, following, verified, json.dumps(profile_data)))
            
            profile_id = cursor.lastrowid
            
            # Get existing profile_id if this was an update
            if not profile_id:
                cursor.execute('SELECT id FROM profiles WHERE platform = ? AND username = ?', (platform, username))
                result = cursor.fetchone()
                if result:
                    profile_id = result[0]
            
            conn.commit()
            return profile_id
    
    def save_posts(self, platform: str, username: str, posts: List[Dict[str, Any]]) -> List[int]:
        """Save posts data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get profile_id
            cursor.execute('SELECT id FROM profiles WHERE platform = ? AND username = ?', (platform, username))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Profile not found: {platform}/{username}")
            
            profile_id = result[0]
            post_ids = []
            
            for post in posts:
                post_id = post.get('shortcode') or post.get('id') or post.get('video_id', '')
                content = post.get('caption') or post.get('content') or post.get('title', '')
                
                # Parse date
                post_date = None
                if post.get('date'):
                    try:
                        post_date = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
                    except:
                        pass
                
                likes = post.get('likes') or post.get('like_count', 0)
                comments = post.get('comments') or post.get('reply_count', 0)
                shares = post.get('shares') or post.get('retweet_count', 0)
                
                hashtags = json.dumps(post.get('hashtags', []))
                mentions = json.dumps(post.get('mentions', []))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO posts 
                    (profile_id, platform, username, post_id, content, post_date, likes, comments, shares, hashtags, mentions, post_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (profile_id, platform, username, post_id, content, post_date, likes, comments, shares, hashtags, mentions, json.dumps(post)))
                
                post_ids.append(cursor.lastrowid)
            
            conn.commit()
            return post_ids
    
    def save_analysis(self, platform: str, username: str, analysis_data: Dict[str, Any]) -> int:
        """Save analysis results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get profile_id
            cursor.execute('SELECT id FROM profiles WHERE platform = ? AND username = ?', (platform, username))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Profile not found: {platform}/{username}")
            
            profile_id = result[0]
            
            sentiment_score = analysis_data.get('sentiment_score', 0.0)
            entity_data = json.dumps(analysis_data.get('entity_extraction', {}))
            activity_data = json.dumps(analysis_data.get('activity_analysis', {}))
            
            cursor.execute('''
                INSERT INTO analysis 
                (profile_id, platform, username, analysis_type, sentiment_score, entity_data, activity_data, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (profile_id, platform, username, 'comprehensive', sentiment_score, entity_data, activity_data, json.dumps(analysis_data)))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id
    
    def get_profile(self, platform: str, username: str) -> Optional[Dict[str, Any]]:
        """Get profile data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM profiles WHERE platform = ? AND username = ?
            ''', (platform, username))
            
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                profile = dict(zip(columns, result))
                profile['profile_data'] = json.loads(profile['profile_data']) if profile['profile_data'] else {}
                return profile
            return None
    
    def get_posts(self, platform: str, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts for a profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = cursor.cursor()
            cursor.execute('''
                SELECT * FROM posts WHERE platform = ? AND username = ? 
                ORDER BY post_date DESC LIMIT ?
            ''', (platform, username, limit))
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            posts = []
            for result in results:
                post = dict(zip(columns, result))
                post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []
                post['mentions'] = json.loads(post['mentions']) if post['mentions'] else []
                post['post_data'] = json.loads(post['post_data']) if post['post_data'] else {}
                posts.append(post)
            
            return posts
    
    def search_profiles(self, query: str, platform: str = None) -> List[Dict[str, Any]]:
        """Search profiles by username or display name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if platform:
                cursor.execute('''
                    SELECT * FROM profiles 
                    WHERE platform = ? AND (username LIKE ? OR display_name LIKE ?)
                    ORDER BY followers DESC
                ''', (platform, f'%{query}%', f'%{query}%'))
            else:
                cursor.execute('''
                    SELECT * FROM profiles 
                    WHERE username LIKE ? OR display_name LIKE ?
                    ORDER BY followers DESC
                ''', (f'%{query}%', f'%{query}%'))
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            profiles = []
            for result in results:
                profile = dict(zip(columns, result))
                profile['profile_data'] = json.loads(profile['profile_data']) if profile['profile_data'] else {}
                profiles.append(profile)
            
            return profiles
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Profile counts by platform
            cursor.execute('SELECT platform, COUNT(*) FROM profiles GROUP BY platform')
            stats['profiles_by_platform'] = dict(cursor.fetchall())
            
            # Total posts
            cursor.execute('SELECT COUNT(*) FROM posts')
            stats['total_posts'] = cursor.fetchone()[0]
            
            # Total analysis
            cursor.execute('SELECT COUNT(*) FROM analysis')
            stats['total_analysis'] = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) 
                FROM profiles 
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            ''')
            stats['recent_profiles'] = dict(cursor.fetchall())
            
            return stats