from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import json
from typing import Dict, Any, List
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def generate_profile_report(self, username: str, platform: str, data: Dict[str, Any], output_dir: str = 'reports') -> str:
        """Generate PDF report for profile"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{platform}_{username}_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Title
        title = f"OSINT Report: {username} ({platform.title()})"
        story.append(Paragraph(title, self.styles['Title']))
        story.append(Spacer(1, 20))
        
        # Profile Info
        profile = data.get('profile', {})
        profile_data = [
            ['Username:', profile.get('username', 'N/A')],
            ['Full Name:', profile.get('full_name', 'N/A')],
            ['Followers:', f"{profile.get('followers', 0):,}"],
            ['Following:', f"{profile.get('followees', 0):,}"],
            ['Posts:', f"{profile.get('posts_count', 0):,}"],
            ['Verified:', 'Yes' if profile.get('is_verified', False) else 'No']
        ]
        
        profile_table = Table(profile_data)
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(profile_table)
        story.append(Spacer(1, 20))
        
        # Posts summary
        posts = data.get('posts', [])
        if posts:
            story.append(Paragraph("Posts Analysis", self.styles['Heading2']))
            total_likes = sum(post.get('likes', 0) for post in posts)
            avg_likes = total_likes / len(posts) if posts else 0
            
            posts_info = f"Total Posts: {len(posts)}, Average Likes: {avg_likes:,.0f}"
            story.append(Paragraph(posts_info, self.styles['Normal']))
        
        doc.build(story)
        return filename