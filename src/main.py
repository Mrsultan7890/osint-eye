#!/usr/bin/env python3

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import json
import os
from datetime import datetime
from pathlib import Path

app = typer.Typer(help="🔍 OSINT Eye - Advanced Social Media Intelligence Tool")
console = Console()

@app.callback()
def main():
    """🔍 OSINT Eye - Advanced Social Media Intelligence Tool"""
    console.print("🔍 OSINT Eye - Advanced Social Media Intelligence Tool", style="bold blue")

@app.command()
def fetch(
    platform: str = typer.Option(..., "--platform", help="Platform (instagram, twitter, youtube, tiktok, linkedin)"),
    username: str = typer.Option(..., "--username", help="Target username"),
    max: int = typer.Option(20, "--max", help="Maximum items to fetch"),
    download_media: bool = typer.Option(False, "--download-media", help="Download photos/videos"),
    max_downloads: int = typer.Option(4, "--max-downloads", help="Maximum media files to download")
):
    """🔍 Fetch data from social media platforms with optional media download"""
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_desc = f"Fetching {platform} data for {username}..."
        if download_media:
            task_desc += f" (downloading up to {max_downloads} media files)"
        task = progress.add_task(task_desc, total=None)
        
        try:
            # Select appropriate fetcher
            if platform == 'instagram':
                from fetchers.instagram_fetcher import InstagramFetcher
                fetcher = InstagramFetcher()
                data = fetcher.fetch_user_data(username, max_posts=max, download_media=download_media, max_downloads=max_downloads)
            elif platform == 'twitter':
                from fetchers.twitter_fetcher import TwitterFetcher
                fetcher = TwitterFetcher()
                data = fetcher.fetch_user_data(username, max_tweets=max)
            elif platform == 'youtube':
                from fetchers.youtube_fetcher import YouTubeFetcher
                fetcher = YouTubeFetcher()
                data = fetcher.fetch_user_data(username, max_videos=max)
            elif platform == 'tiktok':
                from fetchers.tiktok_fetcher import TikTokFetcher
                fetcher = TikTokFetcher()
                data = fetcher.fetch_user_data(username, max_videos=max)
            elif platform == 'linkedin':
                from fetchers.linkedin_fetcher import LinkedInFetcher
                fetcher = LinkedInFetcher()
                data = fetcher.fetch_user_data(username, max_posts=max)
            else:
                console.print(f"❌ Unsupported platform: {platform}", style="red")
                return
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path("data") / platform / username
            output_path.mkdir(parents=True, exist_ok=True)
            
            filename = output_path / f"data_{timestamp}.json"
            
            data['metadata'] = {
                'platform': platform,
                'username': username,
                'timestamp': timestamp,
                'fetched_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Success animation
            console.print("\n   ✨    Operation Successful!    ✨   ")
            console.print("  ✨✨   Operation Successful!   ✨✨  ")
            console.print(" ✨✨✨  Operation Successful!  ✨✨✨ ")
            console.print("✨✨✨✨ Operation Successful! ✨✨✨✨")
            console.print(" ✨✨✨  Operation Successful!  ✨✨✨ ")
            console.print("  ✨✨   Operation Successful!   ✨✨  ")
            console.print("   ✨    Operation Successful!    ✨   ")
            
            # Display results
            profile = data.get('profile', {})
            
            results_table = Table(title=f"✅ Fetch Complete - {username}")
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Value", style="green")
            
            results_table.add_row("Platform", platform.title())
            results_table.add_row("Posts Fetched", str(data.get('total_fetched', 0)))
            
            display_name = (profile.get('full_name') or 
                          profile.get('display_name') or 
                          profile.get('channel_name') or 
                          "N/A")
            results_table.add_row("Display Name", display_name)
            
            followers = profile.get('followers', 0)
            results_table.add_row("Followers", f"{followers:,}" if followers else "0")
            
            results_table.add_row("JSON File", str(filename))
            
            # Show downloaded media info
            if download_media:
                downloaded_count = sum(1 for post in data.get('posts', []) if 'local_media_path' in post)
                results_table.add_row("Downloaded Media", str(downloaded_count))
                
                if downloaded_count > 0:
                    console.print(f"\n📸 Media files saved in: /home/kali/Desktop/tools/osint-eye/images/{username}/", style="bold cyan")
            
            console.print(results_table)
            
        except Exception as e:
            console.print(f"❌ Error fetching data: {e}", style="red")

@app.command()
def analyze(
    platform: str = typer.Option(..., "--platform", help="Platform to analyze"),
    username: str = typer.Option(..., "--username", help="Username to analyze")
):
    """🧠 Analyze collected data with advanced features"""
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("AI Analysis...", total=None)
        
        try:
            # Load latest data file
            data_path = Path("data") / platform / username
            if not data_path.exists():
                console.print(f"❌ No data found for {username} on {platform}", style="red")
                return
            
            # Find latest data file
            data_files = list(data_path.glob("data_*.json"))
            if not data_files:
                console.print(f"❌ No data files found for {username}", style="red")
                return
            
            latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Basic analysis
            from analysis.analyzer import Analyzer
            analyzer = Analyzer()
            analysis = analyzer.analyze_profile(data)
            
            progress.update(task, description="✅ AI Analysis complete!")
            time.sleep(1)
            
            # Success animation
            console.print("\n   ✨    Operation Successful!    ✨   ")
            console.print("  ✨✨   Operation Successful!   ✨✨  ")
            console.print(" ✨✨✨  Operation Successful!  ✨✨✨ ")
            console.print("✨✨✨✨ Operation Successful! ✨✨✨✨")
            console.print(" ✨✨✨  Operation Successful!  ✨✨✨ ")
            console.print("  ✨✨   Operation Successful!   ✨✨  ")
            console.print("   ✨    Operation Successful!    ✨   ")
            
            # Display results
            console.print(Panel(f"🧠 Analysis Complete for {username}", style="bold blue"))
            
            # Key metrics table
            metrics_table = Table(title="📊 Key Metrics")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")
            
            metrics_table.add_row("Posts Analyzed", str(analysis.get('post_count', 0)))
            metrics_table.add_row("Sentiment Score", f"{analysis.get('sentiment_score', 0):.2f}")
            metrics_table.add_row("Activity Peak", analysis.get('activity_peak', 'Unknown'))
            
            engagement = analysis.get('engagement_analysis', {})
            metrics_table.add_row("Avg Likes", f"{engagement.get('avg_likes', 0):,.0f}")
            metrics_table.add_row("Avg Comments", f"{engagement.get('avg_comments', 0):,.0f}")
            metrics_table.add_row("Engagement Rate", f"{engagement.get('engagement_rate', 0):,.2f}")
            
            console.print(metrics_table)
            
            # Top keywords
            keywords = analysis.get('top_keywords', [])
            if keywords:
                console.print(f"\n🔑 Top Keywords: {', '.join(keywords[:5])}")
            
            # Top hashtags
            hashtag_analysis = analysis.get('hashtag_analysis', {})
            top_hashtags = hashtag_analysis.get('top_hashtags', [])
            if top_hashtags:
                hashtag_list = [f"#{tag}" for tag, count in top_hashtags[:3]]
                console.print(f"#️⃣ Top Hashtags: {', '.join(hashtag_list)}")
            
        except Exception as e:
            console.print(f"❌ Error in analysis: {e}", style="red")

@app.command()
def fake_detect(
    platform: str = typer.Option(..., "--platform", help="Platform to analyze"),
    username: str = typer.Option(..., "--username", help="Username to analyze")
):
    """🤖 Detect fake/bot accounts"""
    try:
        # Load data
        data_path = Path("data") / platform / username
        data_files = list(data_path.glob("data_*.json"))
        if not data_files:
            console.print(f"❌ No data found for {username} on {platform}", style="red")
            return
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        from analysis.fake_detector import FakeDetector
        detector = FakeDetector()
        result = detector.detect_fake_account(data.get('profile', {}), data.get('posts', []))
        
        console.print(f"\n🤖 Fake Account Analysis - {username}", style="bold blue")
        
        results_table = Table()
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Authenticity Score", f"{result['authenticity_score']}/100")
        results_table.add_row("Authenticity Level", result['authenticity_level'])
        results_table.add_row("Likely Fake", "Yes" if result['is_likely_fake'] else "No")
        
        console.print(results_table)
        
        if result['red_flags']:
            console.print("\n🚩 Red Flags:", style="bold red")
            for flag in result['red_flags']:
                console.print(f"  • {flag}", style="red")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def correlate(
    username: str = typer.Option(..., "--username", help="Username to correlate")
):
    """🔗 Cross-platform correlation analysis"""
    try:
        from analysis.cross_platform_correlator import CrossPlatformCorrelator
        
        correlator = CrossPlatformCorrelator()
        result = correlator.correlate_accounts(username)
        
        console.print(f"\n🔗 Cross-Platform Analysis - {username}", style="bold blue")
        
        presence_table = Table()
        presence_table.add_column("Platform", style="cyan")
        presence_table.add_column("Found", style="green")
        
        for platform, data in result['platform_presence'].items():
            found = "✅" if data['found'] else "❌"
            presence_table.add_row(platform.title(), found)
        
        console.print(presence_table)
        console.print(f"\n📊 Total Platforms: {result['total_platforms']}", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def bulk(
    usernames: str = typer.Option(..., "--usernames", help="Comma-separated usernames"),
    platform: str = typer.Option(..., "--platform", help="Platform to analyze")
):
    """📊 Bulk analysis of multiple accounts"""
    username_list = [u.strip() for u in usernames.split(',')]
    
    try:
        from search.bulk_analyzer import BulkAnalyzer
        
        analyzer = BulkAnalyzer()
        result = analyzer.analyze_multiple_accounts(username_list, platform)
        
        console.print(f"\n📊 Bulk Analysis Results", style="bold blue")
        console.print(f"Total Analyzed: {result['total_analyzed']}", style="green")
        
        results_table = Table()
        results_table.add_column("Username", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Followers", style="yellow")
        
        for username, data in result['results'].items():
            if 'error' in data:
                status = "❌ Error"
                followers = "N/A"
            else:
                status = "✅ Success"
                followers = f"{data.get('profile', {}).get('followers', 0):,}"
            
            results_table.add_row(username, status, followers)
        
        console.print(results_table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def report(
    platform: str = typer.Option(..., "--platform", help="Platform"),
    username: str = typer.Option(..., "--username", help="Username"),
    format: str = typer.Option("pdf", "--format", help="Report format (pdf/json)")
):
    """📄 Generate comprehensive reports"""
    try:
        # Load data
        data_path = Path("data") / platform / username
        data_files = list(data_path.glob("data_*.json"))
        if not data_files:
            console.print(f"❌ No data found for {username} on {platform}", style="red")
            return
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if format.lower() == 'pdf':
            from reports.pdf_generator import PDFGenerator
            generator = PDFGenerator()
            filename = generator.generate_profile_report(username, platform, data)
            console.print(f"\n📄 PDF Report Generated: {filename}", style="bold green")
        elif format.lower() == 'json':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/{platform}_{username}_report_{timestamp}.json"
            Path("reports").mkdir(exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            console.print(f"\n📄 JSON Report Generated: {filename}", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

# NEW ADVANCED COMMANDS

@app.command()
def threat_intel(
    platform: str = typer.Option(..., "--platform", help="Platform to analyze"),
    username: str = typer.Option(..., "--username", help="Username to analyze")
):
    """🚨 Advanced threat intelligence analysis"""
    try:
        from analysis.threat_intelligence import ThreatIntelligence
        
        # Load data
        data_path = Path("data") / platform / username
        data_files = list(data_path.glob("data_*.json"))
        if not data_files:
            console.print(f"❌ No data found for {username} on {platform}", style="red")
            return
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        threat_analyzer = ThreatIntelligence()
        result = threat_analyzer.analyze_threat_profile(data.get('profile', {}))
        
        console.print(f"\n🚨 Threat Intelligence - {username}", style="bold red")
        
        threat_table = Table()
        threat_table.add_column("Metric", style="cyan")
        threat_table.add_column("Value", style="red")
        
        threat_table.add_row("Threat Score", f"{result['overall_threat_score']:.1f}/100")
        threat_table.add_row("Severity Level", result['severity_level'].upper())
        threat_table.add_row("Detected Threats", str(len(result['threat_categories'])))
        
        console.print(threat_table)
        
        if result['threat_categories']:
            console.print("\n⚠️ Detected Threats:", style="bold yellow")
            for threat in result['threat_categories']:
                console.print(f"  • {threat['type'].title()}: {threat['confidence']:.1f}% confidence", style="red")
        
        if result['recommendations']:
            console.print("\n💡 Recommendations:", style="bold blue")
            for rec in result['recommendations'][:3]:
                console.print(f"  • {rec}", style="blue")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def discover(
    username: str = typer.Option(..., "--username", help="Username to discover"),
    variations: bool = typer.Option(True, "--variations", help="Generate username variations")
):
    """🔍 Advanced username discovery across platforms"""
    try:
        from search.advanced_discovery import AdvancedDiscovery
        
        discovery = AdvancedDiscovery()
        result = discovery.discover_social_profiles(username, check_variations=variations)
        
        console.print(f"\n🔍 Discovery Results - {username}", style="bold blue")
        
        summary_table = Table()
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Platforms Checked", str(len(result['checked_platforms'])))
        summary_table.add_row("Profiles Found", str(len(result['found_profiles'])))
        summary_table.add_row("Possible Matches", str(len(result['possible_profiles'])))
        summary_table.add_row("Variations Tested", str(len(result['username_variations'])))
        
        console.print(summary_table)
        
        if result['found_profiles']:
            console.print("\n✅ Found Profiles:", style="bold green")
            for profile in result['found_profiles']:
                console.print(f"  • {profile['platform'].title()}: {profile['url']}", style="green")
        
        if result['possible_profiles']:
            console.print("\n🤔 Possible Matches:", style="bold yellow")
            for profile in result['possible_profiles'][:5]:
                console.print(f"  • {profile['platform'].title()}: {profile['url']}", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def image_analyze(
    platform: str = typer.Option(..., "--platform", help="Platform"),
    username: str = typer.Option(..., "--username", help="Username")
):
    """🖼️ Advanced image analysis of profile pictures"""
    try:
        from ai.advanced_image_analyzer import AdvancedImageAnalyzer
        
        # Load data
        data_path = Path("data") / platform / username
        data_files = list(data_path.glob("data_*.json"))
        if not data_files:
            console.print(f"❌ No data found for {username} on {platform}", style="red")
            return
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        profile = data.get('profile', {})
        image_url = profile.get('profile_pic_url')
        
        if not image_url:
            console.print("❌ No profile image found", style="red")
            return
        
        analyzer = AdvancedImageAnalyzer()
        result = analyzer.analyze_profile_image(image_url, username)
        
        console.print(f"\n🖼️ Image Analysis - {username}", style="bold blue")
        
        if 'error' in result:
            console.print(f"❌ {result['error']}", style="red")
            return
        
        image_table = Table()
        image_table.add_column("Metric", style="cyan")
        image_table.add_column("Value", style="green")
        
        basic_info = result.get('basic_info', {})
        image_table.add_row("Image Format", basic_info.get('format', 'Unknown'))
        image_table.add_row("Image Size", f"{basic_info.get('size', [0, 0])[0]}x{basic_info.get('size', [0, 0])[1]}")
        image_table.add_row("File Size", f"{basic_info.get('file_size', 0):,} bytes")
        image_table.add_row("Authenticity Score", f"{result.get('authenticity_score', 0)}/100")
        
        console.print(image_table)
        
        similarity = result.get('similarity_check', {})
        red_flags = similarity.get('red_flags', [])
        if red_flags:
            console.print("\n🚩 Image Red Flags:", style="bold red")
            for flag in red_flags:
                console.print(f"  • {flag}", style="red")
        
        console.print("\n🔍 Reverse Search URLs:", style="bold blue")
        for url in result.get('reverse_search_urls', [])[:2]:
            console.print(f"  • {url}", style="blue")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def network_map(
    usernames: str = typer.Option(..., "--usernames", help="Comma-separated usernames"),
    output: str = typer.Option("interactive", "--output", help="Output type (interactive/static)")
):
    """🕸️ Generate network visualization"""
    try:
        from visualization.advanced_network_mapper import AdvancedNetworkMapper
        
        username_list = [u.strip() for u in usernames.split(',')]
        mapper = AdvancedNetworkMapper()
        
        # Add profiles to network (simplified - in real use, load actual data)
        for username in username_list:
            mapper.add_profile(username, "instagram", {
                "followers": 1000,
                "following": 500,
                "posts": 100,
                "verified": False
            })
        
        # Generate visualization
        if output == "interactive":
            viz_path = mapper.generate_interactive_visualization()
            console.print(f"\n🕸️ Interactive Network Map: {viz_path}", style="bold green")
        else:
            viz_path = mapper.generate_static_visualization()
            console.print(f"\n🕸️ Static Network Map: {viz_path}", style="bold green")
        
        # Show metrics
        metrics = mapper.analyze_network_metrics()
        
        network_table = Table()
        network_table.add_column("Metric", style="cyan")
        network_table.add_column("Value", style="green")
        
        basic_stats = metrics.get('basic_stats', {})
        network_table.add_row("Total Nodes", str(basic_stats.get('total_nodes', 0)))
        network_table.add_row("Total Connections", str(basic_stats.get('total_edges', 0)))
        network_table.add_row("Network Density", f"{basic_stats.get('density', 0):.3f}")
        
        console.print(network_table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@app.command()
def export_data(
    platform: str = typer.Option(..., "--platform", help="Platform"),
    username: str = typer.Option(..., "--username", help="Username"),
    format: str = typer.Option("json", "--format", help="Export format (json/csv/xml/xlsx/yaml/sqlite/html/markdown/txt)")
):
    """📤 Export data in multiple formats"""
    try:
        from export.advanced_exporter import AdvancedExporter
        
        # Load data
        data_path = Path("data") / platform / username
        data_files = list(data_path.glob("data_*.json"))
        if not data_files:
            console.print(f"❌ No data found for {username} on {platform}", style="red")
            return
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        exporter = AdvancedExporter()
        output_path = exporter.export_data(data, format)
        
        console.print(f"\n📤 Data Exported: {output_path}", style="bold green")
        
        export_table = Table()
        export_table.add_column("Property", style="cyan")
        export_table.add_column("Value", style="green")
        
        export_table.add_row("Format", format.upper())
        export_table.add_row("File Path", output_path)
        export_table.add_row("Username", username)
        export_table.add_row("Platform", platform.title())
        
        console.print(export_table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

# 🔬 DIGITAL FORENSICS COMMANDS
@app.command()
def extract_metadata(
    file_path: str = typer.Argument(..., help="Path to file or directory"),
    output: str = typer.Option("metadata_report.json", help="Output report file")
):
    """🔍 Extract metadata from files for forensic analysis"""
    try:
        from forensics.metadata_extractor import MetadataExtractor
        extractor = MetadataExtractor()
        
        if os.path.isfile(file_path):
            console.print(f"🔍 Extracting metadata from file: {file_path}")
            metadata = extractor.extract_file_metadata(file_path)
            
            with open(output, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            console.print(f"✅ Metadata extracted: {output}")
            
            # Show key findings
            if "hashes" in metadata:
                console.print(f"📋 File Hash (SHA256): {metadata['hashes'].get('sha256', 'N/A')}")
            if "forensic_data" in metadata and metadata["forensic_data"]:
                console.print(f"🔬 Forensic data found: {len(metadata['forensic_data'])} items")
                
        elif os.path.isdir(file_path):
            console.print(f"🔍 Analyzing directory: {file_path}")
            results = extractor.analyze_directory(file_path)
            hidden_files = extractor.find_hidden_files(file_path)
            
            report = {
                "analysis_timestamp": datetime.now().isoformat(),
                "target_path": file_path,
                "total_files_analyzed": len(results),
                "file_metadata": results,
                "hidden_files": hidden_files
            }
            
            with open(output, 'w') as f:
                json.dump(report, f, indent=2)
            
            console.print(f"✅ Directory analysis complete: {output}")
            console.print(f"📊 Files analyzed: {len(results)}")
            console.print(f"🕵️ Hidden files found: {len(hidden_files)}")
        else:
            console.print(f"❌ Path not found: {file_path}")
            
    except Exception as e:
        console.print(f"❌ Metadata extraction error: {str(e)}")

@app.command()
def timeline_analysis(
    directory: str = typer.Argument(..., help="Directory to analyze"),
    output: str = typer.Option("timeline_report.json", help="Output report file")
):
    """⏰ Create forensic timeline analysis"""
    try:
        from forensics.timeline_analyzer import TimelineAnalyzer
        analyzer = TimelineAnalyzer()
        report = analyzer.create_forensic_report(directory, output)
        
        # Show summary
        console.print(f"📊 Timeline Analysis Summary:")
        console.print(f"   Total events: {report['total_events']}")
        
        if report['forensic_summary']['most_active_hour'] is not None:
            console.print(f"   Most active hour: {report['forensic_summary']['most_active_hour']}:00")
        
        if report['forensic_summary']['suspicious_indicators'] > 0:
            console.print(f"   ⚠️ Suspicious indicators: {report['forensic_summary']['suspicious_indicators']}")
        
        if report['bulk_operations']:
            console.print(f"   📦 Bulk operations detected: {len(report['bulk_operations'])}")
            
    except Exception as e:
        console.print(f"❌ Timeline analysis error: {str(e)}")

@app.command()
def network_forensics(
    output: str = typer.Option("network_forensics.json", help="Output report file")
):
    """🌐 Analyze network connections and activities"""
    try:
        from forensics.network_forensics import NetworkForensics
        forensics = NetworkForensics()
        report = forensics.create_network_forensic_report(output)
        
        # Show summary
        console.print(f"🌐 Network Forensics Summary:")
        console.print(f"   Active connections: {report['network_connections']['total_connections']}")
        console.print(f"   Open ports: {len(report['open_ports_localhost'])}")
        console.print(f"   Risk level: {report['security_assessment']['risk_level']}")
        
        if report['security_assessment']['findings']:
            console.print(f"   ⚠️ Security findings:")
            for finding in report['security_assessment']['findings']:
                console.print(f"     • {finding}")
                
    except Exception as e:
        console.print(f"❌ Network forensics error: {str(e)}")

@app.command()
def memory_forensics(
    output: str = typer.Option("memory_forensics.json", help="Output report file")
):
    """🧠 Analyze system memory and running processes"""
    try:
        from forensics.memory_analyzer import MemoryAnalyzer
        analyzer = MemoryAnalyzer()
        report = analyzer.create_memory_forensic_report(output)
        
        # Show summary
        console.print(f"🧠 Memory Forensics Summary:")
        console.print(f"   Total processes: {report['total_processes']}")
        console.print(f"   Memory usage: {report['system_memory']['memory_percent']}%")
        console.print(f"   Risk level: {report['security_assessment']['risk_level']}")
        
        if report['process_analysis']['suspicious_processes']:
            console.print(f"   ⚠️ Suspicious processes: {len(report['process_analysis']['suspicious_processes'])}")
        
        if report['injection_indicators']:
            console.print(f"   🚨 Code injection indicators: {len(report['injection_indicators'])}")
        
        # Show top memory consumers
        console.print(f"   📊 Top memory consumers:")
        for proc in report['top_memory_consumers'][:3]:
            console.print(f"     • {proc['name']} (PID: {proc['pid']}) - {proc['memory_mb']} MB")
            
    except Exception as e:
        console.print(f"❌ Memory forensics error: {str(e)}")

@app.command()
def forensic_scan(
    target: str = typer.Argument(..., help="Target file or directory"),
    output_dir: str = typer.Option("forensic_reports", help="Output directory for reports")
):
    """🔬 Complete forensic analysis (metadata + timeline + network + memory)"""
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        console.print(f"🔬 Starting comprehensive forensic analysis...")
        console.print(f"📁 Target: {target}")
        console.print(f"📂 Reports will be saved to: {output_dir}")
        
        # 1. Metadata extraction
        console.print(f"\n1️⃣ Extracting metadata...")
        from forensics.metadata_extractor import MetadataExtractor
        extractor = MetadataExtractor()
        if os.path.exists(target):
            if os.path.isfile(target):
                metadata = extractor.extract_file_metadata(target)
            else:
                metadata = {
                    "directory_analysis": extractor.analyze_directory(target),
                    "hidden_files": extractor.find_hidden_files(target)
                }
            
            with open(f"{output_dir}/metadata_analysis.json", 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # 2. Timeline analysis (if directory)
        if os.path.isdir(target):
            console.print(f"2️⃣ Creating timeline analysis...")
            from forensics.timeline_analyzer import TimelineAnalyzer
            timeline_analyzer = TimelineAnalyzer()
            timeline_analyzer.create_forensic_report(target, f"{output_dir}/timeline_analysis.json")
        
        # 3. Network forensics
        console.print(f"3️⃣ Analyzing network activities...")
        from forensics.network_forensics import NetworkForensics
        network_forensics = NetworkForensics()
        network_forensics.create_network_forensic_report(f"{output_dir}/network_analysis.json")
        
        # 4. Memory forensics
        console.print(f"4️⃣ Analyzing system memory...")
        from forensics.memory_analyzer import MemoryAnalyzer
        memory_analyzer = MemoryAnalyzer()
        memory_analyzer.create_memory_forensic_report(f"{output_dir}/memory_analysis.json")
        
        console.print(f"\n✅ Comprehensive forensic analysis complete!")
        console.print(f"📋 Reports saved in: {output_dir}/")
        console.print(f"   • metadata_analysis.json")
        if os.path.isdir(target):
            console.print(f"   • timeline_analysis.json")
        console.print(f"   • network_analysis.json")
        console.print(f"   • memory_analysis.json")
        
    except Exception as e:
        console.print(f"❌ Forensic scan error: {str(e)}")

# 📡 REAL-TIME MONITORING COMMANDS
@app.command()
def start_monitoring(
    username: str = typer.Argument(..., help="Username to monitor"),
    interval: int = typer.Option(30, help="Check interval in minutes"),
    duration: int = typer.Option(24, help="Monitoring duration in hours")
):
    """📵 Start real-time monitoring of Instagram profile"""
    try:
        from monitoring.real_time_monitor import RealTimeMonitor
        
        monitor = RealTimeMonitor()
        console.print(f"📵 Starting real-time monitoring for @{username}")
        console.print(f"⏰ Interval: {interval} minutes | Duration: {duration} hours")
        console.print("Press Ctrl+C to stop monitoring\n")
        
        report_file = monitor.start_monitoring(username, interval, duration)
        
        console.print(f"✅ Monitoring complete! Report saved: {report_file}")
        
    except KeyboardInterrupt:
        console.print("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        console.print(f"❌ Monitoring error: {str(e)}")

@app.command()
def monitoring_status(
    username: str = typer.Argument(..., help="Username to check")
):
    """📊 Check monitoring status for a username"""
    try:
        from monitoring.real_time_monitor import RealTimeMonitor
        
        monitor = RealTimeMonitor()
        status = monitor.get_monitoring_status(username)
        
        console.print(f"📊 Monitoring Status for @{username}:")
        console.print(f"   Monitored: {'Yes' if status['is_monitored'] else 'No'}")
        console.print(f"   Total changes: {status['total_changes']}")
        
        if status['recent_changes']:
            console.print("   Recent changes:")
            for change in status['recent_changes'][-3:]:
                console.print(f"     • {change['timestamp']}: {len(change['changes'])} changes")
                
    except Exception as e:
        console.print(f"❌ Status check error: {str(e)}")

# 🖼️ ADVANCED IMAGE ANALYSIS COMMANDS
@app.command()
def analyze_image(
    image_path: str = typer.Argument(..., help="Path to image file"),
    output: str = typer.Option("image_analysis.json", help="Output report file")
):
    """🖼️ Advanced image analysis with tampering detection"""
    try:
        from image_analysis.advanced_analyzer import AdvancedImageAnalyzer
        
        analyzer = AdvancedImageAnalyzer()
        console.print(f"🖼️ Analyzing image: {os.path.basename(image_path)}")
        
        analysis = analyzer.analyze_image_comprehensive(image_path)
        
        # Save analysis
        with open(output, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Show results
        console.print(f"✅ Image analysis complete: {output}")
        console.print(f"🎯 Authenticity Score: {analysis.get('authenticity_score', 0)}/100")
        
        tampering = analysis.get('tampering_detection', {})
        console.print(f"⚠️ Tampering Risk: {tampering.get('risk_level', 'UNKNOWN')}")
        
        if analysis.get('similarity_analysis', {}).get('is_likely_stock'):
            console.print("📷 Likely stock photo detected")
        
        forensic_markers = analysis.get('forensic_markers', {})
        if forensic_markers.get('authenticity_indicators'):
            console.print("🔍 Authenticity indicators:")
            for indicator in forensic_markers['authenticity_indicators']:
                console.print(f"     • {indicator}")
                
    except Exception as e:
        console.print(f"❌ Image analysis error: {str(e)}")

@app.command()
def batch_image_analysis(
    directory: str = typer.Argument(..., help="Directory containing images"),
    output: str = typer.Option("batch_analysis.json", help="Output report file")
):
    """🖼️ Batch analysis of all images in directory"""
    try:
        from image_analysis.advanced_analyzer import AdvancedImageAnalyzer
        
        analyzer = AdvancedImageAnalyzer()
        console.print(f"🖼️ Starting batch analysis: {directory}")
        
        results = analyzer.batch_analyze_directory(directory)
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Show summary
        console.print(f"✅ Batch analysis complete: {output}")
        console.print(f"📊 Summary:")
        console.print(f"   Total images: {results['total_images']}")
        console.print(f"   Analyzed: {results['analyzed_images']}")
        console.print(f"   High authenticity: {results['summary']['high_authenticity']}")
        console.print(f"   Likely tampered: {results['summary']['likely_tampered']}")
        console.print(f"   Likely stock: {results['summary']['likely_stock']}")
        
    except Exception as e:
        console.print(f"❌ Batch analysis error: {str(e)}")

@app.command()
def compare_images(
    image1: str = typer.Argument(..., help="First image path"),
    image2: str = typer.Argument(..., help="Second image path")
):
    """🔄 Compare two images for similarity"""
    try:
        from image_analysis.advanced_analyzer import AdvancedImageAnalyzer
        
        analyzer = AdvancedImageAnalyzer()
        console.print(f"🔄 Comparing images...")
        
        comparison = analyzer.compare_images(image1, image2)
        
        console.print(f"✅ Comparison complete:")
        console.print(f"   Similarity: {comparison.get('similarity_percentage', 0):.1f}%")
        console.print(f"   Same image: {'Yes' if comparison.get('likely_same_image') else 'No'}")
        console.print(f"   Similar: {'Yes' if comparison.get('likely_similar') else 'No'}")
        console.print(f"   Hash difference: {comparison.get('hash_difference', 0)}")
        
    except Exception as e:
        console.print(f"❌ Image comparison error: {str(e)}")

# 📊 ADVANCED REPORTING COMMANDS
@app.command()
def generate_html_report(
    data_file: str = typer.Argument(..., help="JSON data file to create report from"),
    report_type: str = typer.Option("profile", help="Report type (profile/forensic/monitoring)")
):
    """📊 Generate interactive HTML report"""
    try:
        from reporting.advanced_reporter import AdvancedReporter
        
        # Load data
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        reporter = AdvancedReporter()
        html_file = reporter.generate_interactive_html_report(data, report_type)
        
        console.print(f"✅ Interactive HTML report generated: {html_file}")
        console.print(f"🌐 Open in browser to view interactive features")
        
    except Exception as e:
        console.print(f"❌ Report generation error: {str(e)}")

@app.command()
def generate_dashboard(
    output: str = typer.Option("dashboard.html", help="Output dashboard file")
):
    """📊 Generate comprehensive analysis dashboard"""
    try:
        from reporting.advanced_reporter import AdvancedReporter
        
        # Collect data from recent analyses
        dashboard_data = {
            "summary": "Comprehensive OSINT Analysis Dashboard",
            "generated_at": datetime.now().isoformat()
        }
        
        reporter = AdvancedReporter()
        dashboard_file = reporter.generate_dashboard_report(dashboard_data)
        
        console.print(f"✅ Dashboard generated: {dashboard_file}")
        console.print(f"📊 Open in browser for interactive dashboard")
        
    except Exception as e:
        console.print(f"❌ Dashboard generation error: {str(e)}")

@app.command()
def export_report(
    data_file: str = typer.Argument(..., help="Data file to export"),
    format: str = typer.Option("json", help="Export format (json)")
):
    """📤 Export analysis data in various formats"""
    try:
        from reporting.advanced_reporter import AdvancedReporter
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        reporter = AdvancedReporter()
        
        if format == "json":
            export_file = reporter.export_to_json(data)
            console.print(f"✅ JSON export saved: {export_file}")
        else:
            console.print(f"❌ Unsupported format: {format}")
            
    except Exception as e:
        console.print(f"❌ Export error: {str(e)}")

if __name__ == "__main__":
    app()