import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import json
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class TaskScheduler:
    def __init__(self, config_path: str = "config/scheduler.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.scheduler_thread = None
        self.tasks = {}
        self.load_config()
    
    def load_config(self):
        """Load scheduler configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.tasks = config.get('tasks', {})
            except Exception as e:
                logger.error(f"Config load error: {e}")
                self.tasks = {}
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default scheduler configuration"""
        default_config = {
            "tasks": {
                "daily_monitoring": {
                    "enabled": False,
                    "schedule": "daily",
                    "time": "09:00",
                    "targets": [],
                    "platforms": ["instagram", "twitter"],
                    "max_items": 10
                },
                "weekly_analysis": {
                    "enabled": False,
                    "schedule": "weekly",
                    "day": "monday",
                    "time": "10:00",
                    "targets": [],
                    "generate_reports": True
                },
                "hourly_alerts": {
                    "enabled": False,
                    "schedule": "hourly",
                    "targets": [],
                    "keywords": [],
                    "sentiment_threshold": -0.5
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.tasks = default_config['tasks']
    
    def add_monitoring_task(self, task_name: str, targets: List[str], platforms: List[str], 
                          schedule_type: str = "daily", schedule_time: str = "09:00"):
        """Add a new monitoring task"""
        self.tasks[task_name] = {
            "enabled": True,
            "schedule": schedule_type,
            "time": schedule_time,
            "targets": targets,
            "platforms": platforms,
            "max_items": 20,
            "last_run": None
        }
        self.save_config()
        logger.info(f"Added monitoring task: {task_name}")
    
    def add_analysis_task(self, task_name: str, targets: List[str], 
                         schedule_type: str = "weekly", schedule_time: str = "10:00"):
        """Add a new analysis task"""
        self.tasks[task_name] = {
            "enabled": True,
            "schedule": schedule_type,
            "time": schedule_time,
            "targets": targets,
            "generate_reports": True,
            "last_run": None
        }
        self.save_config()
        logger.info(f"Added analysis task: {task_name}")
    
    def setup_schedules(self):
        """Setup all scheduled tasks"""
        schedule.clear()
        
        for task_name, task_config in self.tasks.items():
            if not task_config.get('enabled', False):
                continue
            
            schedule_type = task_config.get('schedule', 'daily')
            schedule_time = task_config.get('time', '09:00')
            
            if schedule_type == 'daily':
                schedule.every().day.at(schedule_time).do(self._run_task, task_name, task_config)
            elif schedule_type == 'weekly':
                day = task_config.get('day', 'monday')
                getattr(schedule.every(), day).at(schedule_time).do(self._run_task, task_name, task_config)
            elif schedule_type == 'hourly':
                schedule.every().hour.do(self._run_task, task_name, task_config)
            elif schedule_type.startswith('every_'):
                # Custom intervals like 'every_30_minutes'
                parts = schedule_type.split('_')
                if len(parts) == 3:
                    interval = int(parts[1])
                    unit = parts[2]
                    if unit == 'minutes':
                        schedule.every(interval).minutes.do(self._run_task, task_name, task_config)
                    elif unit == 'hours':
                        schedule.every(interval).hours.do(self._run_task, task_name, task_config)
        
        logger.info(f"Setup {len(schedule.jobs)} scheduled tasks")
    
    def _run_task(self, task_name: str, task_config: Dict[str, Any]):
        """Execute a scheduled task"""
        try:
            logger.info(f"Running scheduled task: {task_name}")
            
            # Update last run time
            task_config['last_run'] = datetime.now().isoformat()
            self.save_config()
            
            # Import here to avoid circular imports
            from fetchers.instagram_fetcher import InstagramFetcher
            from fetchers.twitter_fetcher import TwitterFetcher
            from analysis.analyzer import Analyzer
            from storage.data_manager import DataManager
            
            dm = DataManager()
            analyzer = Analyzer()
            
            targets = task_config.get('targets', [])
            platforms = task_config.get('platforms', ['instagram', 'twitter'])
            max_items = task_config.get('max_items', 10)
            
            # Fetch data for each target
            for target in targets:
                for platform in platforms:
                    try:
                        # Get appropriate fetcher
                        if platform == 'instagram':
                            fetcher = InstagramFetcher()
                        elif platform == 'twitter':
                            fetcher = TwitterFetcher()
                        else:
                            continue
                        
                        # Fetch data
                        data = fetcher.fetch_user_data(target, max_items)
                        dm.save_data(platform, target, data)
                        
                        # Run analysis if configured
                        if task_config.get('generate_reports', False):
                            analysis = analyzer.analyze_profile(data)
                            dm.save_analysis(platform, target, analysis)
                        
                        logger.info(f"Completed scheduled fetch: {platform}/{target}")
                        
                    except Exception as e:
                        logger.error(f"Task execution error for {platform}/{target}: {e}")
            
            # Check for alerts if configured
            if 'keywords' in task_config or 'sentiment_threshold' in task_config:
                self._check_alerts(task_name, task_config, targets)
            
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
    
    def _check_alerts(self, task_name: str, task_config: Dict[str, Any], targets: List[str]):
        """Check for alert conditions"""
        try:
            keywords = task_config.get('keywords', [])
            sentiment_threshold = task_config.get('sentiment_threshold', -0.5)
            
            from storage.data_manager import DataManager
            dm = DataManager()
            
            alerts = []
            
            for target in targets:
                # Check recent data for keywords and sentiment
                for platform in ['instagram', 'twitter']:
                    try:
                        data = dm.load_data(platform, target)
                        if not data:
                            continue
                        
                        posts = data.get('posts', [])
                        for post in posts[-5:]:  # Check last 5 posts
                            content = post.get('caption', '') or post.get('content', '')
                            
                            # Keyword alerts
                            for keyword in keywords:
                                if keyword.lower() in content.lower():
                                    alerts.append({
                                        'type': 'keyword',
                                        'platform': platform,
                                        'target': target,
                                        'keyword': keyword,
                                        'content': content[:200],
                                        'timestamp': datetime.now().isoformat()
                                    })
                            
                            # Sentiment alerts
                            from textblob import TextBlob
                            if content:
                                sentiment = TextBlob(content).sentiment.polarity
                                if sentiment < sentiment_threshold:
                                    alerts.append({
                                        'type': 'negative_sentiment',
                                        'platform': platform,
                                        'target': target,
                                        'sentiment_score': sentiment,
                                        'content': content[:200],
                                        'timestamp': datetime.now().isoformat()
                                    })
                    
                    except Exception as e:
                        logger.error(f"Alert check error for {platform}/{target}: {e}")
            
            # Save alerts
            if alerts:
                self._save_alerts(alerts)
                logger.warning(f"Generated {len(alerts)} alerts for task {task_name}")
        
        except Exception as e:
            logger.error(f"Alert checking error: {e}")
    
    def _save_alerts(self, alerts: List[Dict[str, Any]]):
        """Save alerts to file"""
        alerts_file = Path("data/alerts.json")
        
        existing_alerts = []
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    existing_alerts = json.load(f)
            except:
                pass
        
        existing_alerts.extend(alerts)
        
        # Keep only last 1000 alerts
        if len(existing_alerts) > 1000:
            existing_alerts = existing_alerts[-1000:]
        
        with open(alerts_file, 'w') as f:
            json.dump(existing_alerts, f, indent=2, ensure_ascii=False)
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.setup_schedules()
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def save_config(self):
        """Save current configuration"""
        config = {"tasks": self.tasks}
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all tasks"""
        status = {
            'running': self.running,
            'total_tasks': len(self.tasks),
            'enabled_tasks': len([t for t in self.tasks.values() if t.get('enabled', False)]),
            'next_runs': []
        }
        
        for job in schedule.jobs:
            status['next_runs'].append({
                'job': str(job.job_func),
                'next_run': job.next_run.isoformat() if job.next_run else None
            })
        
        return status