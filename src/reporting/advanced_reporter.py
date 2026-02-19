"""
Advanced Reporting System
Interactive HTML reports, PDF generation, dashboards
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import base64
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class AdvancedReporter:
    def __init__(self):
        self.templates_dir = "src/reporting/templates"
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_interactive_html_report(self, data: Dict[str, Any], report_type: str = "profile") -> str:
        """Generate interactive HTML report"""
        logger.info(f"📊 Generating interactive HTML report: {report_type}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.reports_dir}/{report_type}_report_{timestamp}.html"
        
        if report_type == "profile":
            html_content = self._generate_profile_html(data)
        elif report_type == "forensic":
            html_content = self._generate_forensic_html(data)
        elif report_type == "monitoring":
            html_content = self._generate_monitoring_html(data)
        else:
            html_content = self._generate_generic_html(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Interactive report saved: {filename}")
        return filename
    
    def _generate_profile_html(self, data: Dict[str, Any]) -> str:
        """Generate profile analysis HTML report"""
        profile = data.get('profile', {})
        posts = data.get('posts', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Eye - Profile Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .profile-card {{ display: flex; align-items: center; background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
        .profile-pic {{ width: 100px; height: 100px; border-radius: 50%; margin-right: 20px; object-fit: cover; }}
        .profile-info h2 {{ margin: 0; color: #333; }}
        .profile-info p {{ margin: 5px 0; color: #666; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
        .posts-section {{ margin-top: 30px; }}
        .post-card {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 15px; }}
        .post-meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
        .limitations {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
        .limitations h3 {{ color: #856404; margin-top: 0; }}
        .tag {{ background: #667eea; color: white; padding: 4px 8px; border-radius: 15px; font-size: 0.8em; margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 OSINT Eye Report</h1>
            <p>Profile Analysis for @{profile.get('username', 'Unknown')}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="profile-card">
                <img src="data:image/svg+xml;base64,{self._generate_placeholder_avatar()}" alt="Profile" class="profile-pic">
                <div class="profile-info">
                    <h2>{profile.get('full_name', 'N/A')}</h2>
                    <p><strong>@{profile.get('username', 'Unknown')}</strong></p>
                    <p>{profile.get('biography', 'No bio available')}</p>
                </div>
            </div>
            
            <div class="limitations">
                <h3>⚠️ Data Limitations</h3>
                <p><strong>Real Data:</strong> Followers ({profile.get('followers', 0):,}), Bio, Posts Count ({profile.get('posts_count', 0):,})</p>
                <p><strong>Limited Data:</strong> Individual post likes/comments, real captions, hashtags (Instagram login required)</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{profile.get('followers', 0):,}</div>
                    <div class="stat-label">Followers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('followees', 0):,}</div>
                    <div class="stat-label">Following</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('posts_count', 0):,}</div>
                    <div class="stat-label">Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(posts)}</div>
                    <div class="stat-label">Demo Posts Generated</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>📊 Account Overview</h3>
                <canvas id="overviewChart" width="400" height="200"></canvas>
            </div>
            
            <div class="posts-section">
                <h3>📝 Generated Demo Posts (For Analysis Framework)</h3>
                {self._generate_posts_html(posts)}
            </div>
        </div>
    </div>
    
    <script>
        // Chart.js visualization
        const ctx = document.getElementById('overviewChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Followers', 'Following', 'Posts'],
                datasets: [{{
                    data: [{profile.get('followers', 0)}, {profile.get('followees', 0)}, {profile.get('posts_count', 0)}],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        return html
    
    def _generate_forensic_html(self, data: Dict[str, Any]) -> str:
        """Generate forensic analysis HTML report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Eye - Forensic Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; }}
        .forensic-section {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
        .risk-high {{ border-left: 5px solid #e74c3c; }}
        .risk-medium {{ border-left: 5px solid #f39c12; }}
        .risk-low {{ border-left: 5px solid #27ae60; }}
        .hash-display {{ font-family: monospace; background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Digital Forensics Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            {self._generate_forensic_sections_html(data)}
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _generate_monitoring_html(self, data: Dict[str, Any]) -> str:
        """Generate monitoring report HTML"""
        changes = data.get('changes', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Eye - Monitoring Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #00b894 0%, #00a085 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; }}
        .timeline {{ position: relative; }}
        .timeline-item {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #00b894; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .change-list {{ margin-top: 10px; }}
        .change-item {{ background: #e8f5e8; padding: 8px 12px; border-radius: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📡 Real-Time Monitoring Report</h1>
            <p>Username: @{data.get('username', 'Unknown')}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(changes)}</div>
                    <div class="stat-label">Total Changes Detected</div>
                </div>
            </div>
            
            <div class="timeline">
                <h3>📅 Change Timeline</h3>
                {self._generate_timeline_html(changes)}
            </div>
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _generate_posts_html(self, posts: List[Dict]) -> str:
        """Generate HTML for posts section"""
        if not posts:
            return "<p>No posts available for analysis.</p>"
        
        posts_html = ""
        for i, post in enumerate(posts[:5]):  # Show first 5 posts
            posts_html += f"""
            <div class="post-card">
                <div class="post-meta">
                    Post #{i+1} • {post.get('timestamp', 'Unknown time')} • {post.get('media_type', 'unknown').title()}
                </div>
                <p><strong>Caption:</strong> {post.get('caption', 'No caption')}</p>
                <p><strong>Note:</strong> {post.get('note', 'Demo data for analysis framework')}</p>
                <div>
                    <span class="tag">Likes: {post.get('likes', 0):,}</span>
                    <span class="tag">Comments: {post.get('comments', 0):,}</span>
                </div>
            </div>"""
        
        return posts_html
    
    def _generate_forensic_sections_html(self, data: Dict[str, Any]) -> str:
        """Generate forensic sections HTML"""
        sections_html = ""
        
        # Metadata section
        if 'metadata_analysis' in data:
            sections_html += f"""
            <div class="forensic-section risk-low">
                <h3>📋 Metadata Analysis</h3>
                <p>Files analyzed: {data['metadata_analysis'].get('total_files_analyzed', 0)}</p>
                <p>Hidden files found: {len(data['metadata_analysis'].get('hidden_files', []))}</p>
            </div>"""
        
        # Network section
        if 'network_analysis' in data:
            risk_class = f"risk-{data['network_analysis']['security_assessment']['risk_level'].lower()}"
            sections_html += f"""
            <div class="forensic-section {risk_class}">
                <h3>🌐 Network Analysis</h3>
                <p>Risk Level: {data['network_analysis']['security_assessment']['risk_level']}</p>
                <p>Active Connections: {data['network_analysis']['network_connections']['total_connections']}</p>
                <p>Open Ports: {len(data['network_analysis']['open_ports_localhost'])}</p>
            </div>"""
        
        # Memory section
        if 'memory_analysis' in data:
            risk_class = f"risk-{data['memory_analysis']['security_assessment']['risk_level'].lower()}"
            sections_html += f"""
            <div class="forensic-section {risk_class}">
                <h3>🧠 Memory Analysis</h3>
                <p>Risk Level: {data['memory_analysis']['security_assessment']['risk_level']}</p>
                <p>Total Processes: {data['memory_analysis']['total_processes']}</p>
                <p>Memory Usage: {data['memory_analysis']['system_memory']['memory_percent']}%</p>
                <p>Suspicious Processes: {len(data['memory_analysis']['process_analysis']['suspicious_processes'])}</p>
            </div>"""
        
        return sections_html
    
    def _generate_timeline_html(self, changes: List[Dict]) -> str:
        """Generate timeline HTML for monitoring changes"""
        if not changes:
            return "<p>No changes detected during monitoring period.</p>"
        
        timeline_html = ""
        for change in changes[-10:]:  # Show last 10 changes
            timestamp = change.get('timestamp', 'Unknown')
            change_list = change.get('changes', [])
            
            timeline_html += f"""
            <div class="timeline-item">
                <div class="timestamp">{timestamp}</div>
                <div class="change-list">
                    {''.join([f'<div class="change-item">{c}</div>' for c in change_list])}
                </div>
            </div>"""
        
        return timeline_html
    
    def _generate_placeholder_avatar(self) -> str:
        """Generate base64 placeholder avatar"""
        svg = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="50" fill="#667eea"/>
            <circle cx="50" cy="35" r="15" fill="white"/>
            <ellipse cx="50" cy="75" rx="20" ry="15" fill="white"/>
        </svg>"""
        return base64.b64encode(svg.encode()).decode()
    
    def generate_dashboard_report(self, multiple_data: Dict[str, Any]) -> str:
        """Generate comprehensive dashboard with multiple accounts"""
        logger.info("📊 Generating comprehensive dashboard")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.reports_dir}/dashboard_{timestamp}.html"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Eye - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .widget {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ grid-column: 1 / -1; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="widget header">
            <h1>🔍 OSINT Eye Dashboard</h1>
            <p>Comprehensive Analysis Overview</p>
        </div>
        
        {self._generate_dashboard_widgets(multiple_data)}
    </div>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"✅ Dashboard saved: {filename}")
        return filename
    
    def _generate_dashboard_widgets(self, data: Dict[str, Any]) -> str:
        """Generate dashboard widgets"""
        widgets_html = ""
        
        # Summary widget
        widgets_html += """
        <div class="widget">
            <h3>📊 Analysis Summary</h3>
            <p>Total accounts analyzed: 1</p>
            <p>Reports generated: Multiple</p>
            <p>Last update: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>"""
        
        # Quick stats widget
        widgets_html += """
        <div class="widget">
            <h3>⚡ Quick Stats</h3>
            <p>Forensic scans: Active</p>
            <p>Monitoring: Available</p>
            <p>Image analysis: Ready</p>
        </div>"""
        
        return widgets_html
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to JSON format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.reports_dir}/export_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON export saved: {filename}")
        return filename
    
    def generate_summary_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary report"""
        summary = {
            "report_type": "Executive Summary",
            "generated_at": datetime.now().isoformat(),
            "key_findings": [],
            "risk_assessment": "LOW",
            "recommendations": [],
            "data_sources": []
        }
        
        # Analyze data and generate findings
        if 'profile' in analysis_data:
            profile = analysis_data['profile']
            summary["key_findings"].append(f"Profile analyzed: @{profile.get('username', 'Unknown')}")
            summary["key_findings"].append(f"Followers: {profile.get('followers', 0):,}")
            summary["data_sources"].append("Instagram Profile Data")
        
        if 'forensic_data' in analysis_data:
            summary["key_findings"].append("Digital forensics analysis completed")
            summary["data_sources"].append("Digital Forensics")
        
        # Default recommendations
        summary["recommendations"] = [
            "Continue monitoring for profile changes",
            "Verify authenticity of downloaded media",
            "Cross-reference with other platforms",
            "Maintain forensic evidence chain"
        ]
        
        return summary