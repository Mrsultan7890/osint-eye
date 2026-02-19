import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class Reporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_json_report(self, platform: str, username: str, analysis: Dict[str, Any]) -> str:
        """Generate JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{username}_report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        report = {
            'report_metadata': {
                'platform': platform,
                'username': username,
                'generated_at': datetime.now().isoformat(),
                'report_type': 'json'
            },
            'analysis': analysis
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return str(filepath)
    
    def generate_html_report(self, platform: str, username: str, analysis: Dict[str, Any]) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{username}_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        html_content = self._create_html_template(platform, username, analysis)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_markdown_report(self, platform: str, username: str, analysis: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{username}_report_{timestamp}.md"
        filepath = self.output_dir / filename
        
        md_content = self._create_markdown_template(platform, username, analysis)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(filepath)
    
    def _create_html_template(self, platform: str, username: str, analysis: Dict[str, Any]) -> str:
        """Create HTML report template"""
        profile_analysis = analysis.get('profile_analysis', {})
        content_analysis = analysis.get('content_analysis', {})
        engagement_analysis = analysis.get('engagement_analysis', {})
        hashtag_analysis = analysis.get('hashtag_analysis', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OSINT Report - {username} ({platform})</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
        .top-hashtags {{ color: #1da1f2; }}
        .sentiment-positive {{ color: #28a745; }}
        .sentiment-negative {{ color: #dc3545; }}
        .sentiment-neutral {{ color: #6c757d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OSINT Analysis Report</h1>
        <h2>{username} on {platform.title()}</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h3>Profile Overview</h3>
        <div class="metric">Posts Analyzed: {analysis.get('post_count', 0)}</div>
        <div class="metric">Verified: {'Yes' if profile_analysis.get('is_verified') else 'No'}</div>
        <div class="metric">Follower Ratio: {profile_analysis.get('follower_ratio', 0):.2f}</div>
        <div class="metric">Has External URL: {'Yes' if profile_analysis.get('has_external_url') else 'No'}</div>
    </div>
    
    <div class="section">
        <h3>Content Analysis</h3>
        <div class="metric">Avg Post Length: {content_analysis.get('avg_post_length', 0):.0f} chars</div>
        <div class="metric">Readability Score: {content_analysis.get('readability_score', 0):.2f}</div>
        <div class="metric">Total Characters: {content_analysis.get('total_characters', 0):,}</div>
    </div>
    
    <div class="section">
        <h3>Engagement Metrics</h3>
        <div class="metric">Avg Likes: {engagement_analysis.get('avg_likes', 0):.0f}</div>
        <div class="metric">Avg Comments: {engagement_analysis.get('avg_comments', 0):.0f}</div>
        <div class="metric">Engagement Rate: {engagement_analysis.get('engagement_rate', 0):.2f}</div>
    </div>
    
    <div class="section">
        <h3>Sentiment Analysis</h3>
        <div class="metric sentiment-{self._get_sentiment_class(analysis.get('sentiment_score', 0))}">
            Overall Sentiment: {analysis.get('sentiment_score', 0):.2f}
        </div>
    </div>
    
    <div class="section">
        <h3>Hashtag Analysis</h3>
        <div class="metric">Total Hashtags: {hashtag_analysis.get('total_hashtags', 0)}</div>
        <div class="metric">Unique Hashtags: {hashtag_analysis.get('unique_hashtags', 0)}</div>
        <div class="top-hashtags">
            Top Hashtags: {', '.join([f"#{tag}" for tag, count in hashtag_analysis.get('top_hashtags', [])[:5]])}
        </div>
    </div>
    
    <div class="section">
        <h3>Activity Pattern</h3>
        <div class="metric">Peak Activity: {analysis.get('activity_peak', 'Unknown')}</div>
    </div>
    
    <div class="section">
        <h3>Top Keywords</h3>
        <p>{', '.join(analysis.get('top_keywords', [])[:10])}</p>
    </div>
</body>
</html>
        """
        return html
    
    def _create_markdown_template(self, platform: str, username: str, analysis: Dict[str, Any]) -> str:
        """Create Markdown report template"""
        profile_analysis = analysis.get('profile_analysis', {})
        content_analysis = analysis.get('content_analysis', {})
        engagement_analysis = analysis.get('engagement_analysis', {})
        hashtag_analysis = analysis.get('hashtag_analysis', {})
        
        md = f"""# OSINT Analysis Report

## {username} on {platform.title()}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Profile Overview

- **Posts Analyzed:** {analysis.get('post_count', 0)}
- **Verified:** {'Yes' if profile_analysis.get('is_verified') else 'No'}
- **Follower Ratio:** {profile_analysis.get('follower_ratio', 0):.2f}
- **Has External URL:** {'Yes' if profile_analysis.get('has_external_url') else 'No'}

## Content Analysis

- **Average Post Length:** {content_analysis.get('avg_post_length', 0):.0f} characters
- **Readability Score:** {content_analysis.get('readability_score', 0):.2f}
- **Total Characters:** {content_analysis.get('total_characters', 0):,}

## Engagement Metrics

- **Average Likes:** {engagement_analysis.get('avg_likes', 0):.0f}
- **Average Comments:** {engagement_analysis.get('avg_comments', 0):.0f}
- **Engagement Rate:** {engagement_analysis.get('engagement_rate', 0):.2f}

## Sentiment Analysis

- **Overall Sentiment Score:** {analysis.get('sentiment_score', 0):.2f}
- **Sentiment:** {self._get_sentiment_label(analysis.get('sentiment_score', 0))}

## Hashtag Analysis

- **Total Hashtags:** {hashtag_analysis.get('total_hashtags', 0)}
- **Unique Hashtags:** {hashtag_analysis.get('unique_hashtags', 0)}
- **Top Hashtags:** {', '.join([f"#{tag}" for tag, count in hashtag_analysis.get('top_hashtags', [])[:5]])}

## Activity Pattern

- **Peak Activity Time:** {analysis.get('activity_peak', 'Unknown')}

## Top Keywords

{', '.join(analysis.get('top_keywords', [])[:10])}

---

*Report generated by OSINT Eye*
"""
        return md
    
    def _get_sentiment_class(self, score: float) -> str:
        """Get CSS class for sentiment"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label"""
        if score > 0.1:
            return 'Positive'
        elif score < -0.1:
            return 'Negative'
        else:
            return 'Neutral'