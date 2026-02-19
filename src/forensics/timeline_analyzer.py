"""
Digital Forensics - Timeline Analyzer
Creates forensic timelines and analyzes file access patterns
"""
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

class TimelineAnalyzer:
    def __init__(self):
        self.timeline_events = []
    
    def create_timeline(self, directory_path, output_file=None):
        """Create forensic timeline from directory"""
        timeline = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    
                    # Add creation event
                    timeline.append({
                        "timestamp": datetime.fromtimestamp(stat.st_ctime),
                        "event_type": "FILE_CREATED",
                        "file_path": file_path,
                        "file_name": file,
                        "file_size": stat.st_size
                    })
                    
                    # Add modification event
                    timeline.append({
                        "timestamp": datetime.fromtimestamp(stat.st_mtime),
                        "event_type": "FILE_MODIFIED",
                        "file_path": file_path,
                        "file_name": file,
                        "file_size": stat.st_size
                    })
                    
                    # Add access event
                    timeline.append({
                        "timestamp": datetime.fromtimestamp(stat.st_atime),
                        "event_type": "FILE_ACCESSED",
                        "file_path": file_path,
                        "file_name": file,
                        "file_size": stat.st_size
                    })
                except Exception as e:
                    continue
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        # Convert timestamps to strings for JSON serialization
        for event in timeline:
            event["timestamp"] = event["timestamp"].isoformat()
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(timeline, f, indent=2)
        
        return timeline
    
    def analyze_activity_patterns(self, timeline):
        """Analyze file activity patterns"""
        if isinstance(timeline, str):
            with open(timeline, 'r') as f:
                timeline = json.load(f)
        
        patterns = {
            "hourly_activity": defaultdict(int),
            "daily_activity": defaultdict(int),
            "file_types": defaultdict(int),
            "suspicious_activity": [],
            "bulk_operations": []
        }
        
        events_by_minute = defaultdict(list)
        
        for event in timeline:
            timestamp = datetime.fromisoformat(event["timestamp"])
            
            # Hourly patterns
            patterns["hourly_activity"][timestamp.hour] += 1
            
            # Daily patterns
            patterns["daily_activity"][timestamp.strftime("%Y-%m-%d")] += 1
            
            # File type patterns
            file_ext = os.path.splitext(event["file_name"])[1].lower()
            patterns["file_types"][file_ext] += 1
            
            # Group events by minute for bulk operation detection
            minute_key = timestamp.strftime("%Y-%m-%d %H:%M")
            events_by_minute[minute_key].append(event)
        
        # Detect bulk operations (>10 files in same minute)
        for minute, events in events_by_minute.items():
            if len(events) > 10:
                patterns["bulk_operations"].append({
                    "timestamp": minute,
                    "event_count": len(events),
                    "event_types": list(set(e["event_type"] for e in events))
                })
        
        # Detect suspicious activity (activity at unusual hours)
        for hour, count in patterns["hourly_activity"].items():
            if hour in [0, 1, 2, 3, 4, 5] and count > 50:  # Late night activity
                patterns["suspicious_activity"].append({
                    "type": "late_night_activity",
                    "hour": hour,
                    "event_count": count
                })
        
        return patterns
    
    def find_deleted_file_traces(self, directory_path):
        """Find traces of deleted files"""
        traces = []
        
        # Look for temporary files that might indicate deleted originals
        temp_patterns = ['.tmp', '.bak', '~', '.swp']
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check for temp file patterns
                for pattern in temp_patterns:
                    if pattern in file:
                        original_name = file.replace(pattern, '')
                        original_path = os.path.join(root, original_name)
                        
                        if not os.path.exists(original_path):
                            traces.append({
                                "type": "temp_file_orphan",
                                "temp_file": file_path,
                                "suspected_original": original_path,
                                "pattern": pattern
                            })
        
        return traces
    
    def analyze_file_gaps(self, timeline):
        """Analyze gaps in file creation timeline"""
        if isinstance(timeline, str):
            with open(timeline, 'r') as f:
                timeline = json.load(f)
        
        creation_events = [e for e in timeline if e["event_type"] == "FILE_CREATED"]
        creation_events.sort(key=lambda x: x["timestamp"])
        
        gaps = []
        
        for i in range(1, len(creation_events)):
            prev_time = datetime.fromisoformat(creation_events[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(creation_events[i]["timestamp"])
            
            gap_duration = curr_time - prev_time
            
            # Flag gaps longer than 1 hour during normal activity
            if gap_duration > timedelta(hours=1):
                gaps.append({
                    "start_time": creation_events[i-1]["timestamp"],
                    "end_time": creation_events[i]["timestamp"],
                    "gap_duration_hours": gap_duration.total_seconds() / 3600,
                    "files_before_gap": creation_events[i-1]["file_name"],
                    "files_after_gap": creation_events[i]["file_name"]
                })
        
        return gaps
    
    def create_forensic_report(self, directory_path, output_file):
        """Create comprehensive forensic timeline report"""
        print(f"🔍 Creating forensic timeline for: {directory_path}")
        
        # Create timeline
        timeline = self.create_timeline(directory_path)
        
        # Analyze patterns
        patterns = self.analyze_activity_patterns(timeline)
        
        # Find deleted file traces
        deleted_traces = self.find_deleted_file_traces(directory_path)
        
        # Analyze gaps
        gaps = self.analyze_file_gaps(timeline)
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "target_directory": directory_path,
            "total_events": len(timeline),
            "timeline": timeline[-50:],  # Last 50 events
            "activity_patterns": dict(patterns["hourly_activity"]),
            "daily_activity": dict(patterns["daily_activity"]),
            "file_types": dict(patterns["file_types"]),
            "bulk_operations": patterns["bulk_operations"],
            "suspicious_activity": patterns["suspicious_activity"],
            "deleted_file_traces": deleted_traces,
            "timeline_gaps": gaps,
            "forensic_summary": {
                "most_active_hour": max(patterns["hourly_activity"], key=patterns["hourly_activity"].get) if patterns["hourly_activity"] else None,
                "most_active_day": max(patterns["daily_activity"], key=patterns["daily_activity"].get) if patterns["daily_activity"] else None,
                "dominant_file_type": max(patterns["file_types"], key=patterns["file_types"].get) if patterns["file_types"] else None,
                "suspicious_indicators": len(patterns["suspicious_activity"]) + len(deleted_traces),
                "bulk_operations_count": len(patterns["bulk_operations"])
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Forensic report saved: {output_file}")
        return report