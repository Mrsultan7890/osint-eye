import time
import random
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

console = Console()

def animated_eye():
    """Animated eye opening effect"""
    frames = [
        "     ___     ",
        "    /   \\    ",
        "   |  ●  |   ",
        "    \\___/    ",
        "             "
    ]
    
    # Eye opening animation
    for i in range(3):
        console.clear()
        eye_frame = "\n".join([
            "             ",
            "     ___     ",
            "    /   \\    ",
            "   |     |   ",
            "    \\___/    ",
            "             "
        ])
        print(eye_frame)
        time.sleep(0.3)
        
        console.clear()
        eye_frame = "\n".join([
            "             ",
            "     ___     ",
            "    /   \\    ",
            "   |  ●  |   ",
            "    \\___/    ",
            "             "
        ])
        print(eye_frame)
        time.sleep(0.3)

def matrix_effect():
    """Matrix-style falling characters"""
    chars = "01OSINT"
    for _ in range(20):
        line = ""
        for _ in range(50):
            if random.random() > 0.7:
                line += random.choice(chars)
            else:
                line += " "
        console.print(line, style="green")
        time.sleep(0.05)

def display_banner():
    """Display animated OSINT Eye banner"""
    console.clear()
    
    # ASCII Art Eye
    eye_art = """
    ██████╗ ███████╗██╗███╗   ██╗████████╗    ███████╗██╗   ██╗███████╗
    ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝    ██╔════╝╚██╗ ██╔╝██╔════╝
    ██║   ██║███████╗██║██╔██╗ ██║   ██║       █████╗   ╚████╔╝ █████╗  
    ██║   ██║╚════██║██║██║╚██╗██║   ██║       ██╔══╝    ╚██╔╝  ██╔══╝  
    ╚██████╔╝███████║██║██║ ╚████║   ██║       ███████╗   ██║   ███████╗
     ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝       ╚══════╝   ╚═╝   ╚══════╝
    """
    
    # Animated typing effect
    for line in eye_art.split('\n'):
        if line.strip():
            for char in line:
                console.print(char, end='', style="bold cyan")
                time.sleep(0.01)
            console.print()
        else:
            console.print()
    
    # Eye symbol with animation
    eye_symbol = """
                            ╭─────────────────╮
                            │    👁️  OSINT    │
                            │   INTELLIGENCE  │
                            │     SYSTEM      │
                            ╰─────────────────╯
    """
    
    console.print(eye_symbol, style="bold yellow", justify="center")
    
    # Blinking effect
    for _ in range(3):
        time.sleep(0.5)
        console.print("                            ╭─────────────────╮", style="bold yellow", justify="center")
        console.print("                            │    ●   OSINT    │", style="bold yellow", justify="center")
        console.print("                            │   INTELLIGENCE  │", style="bold yellow", justify="center")
        console.print("                            │     SYSTEM      │", style="bold yellow", justify="center")
        console.print("                            ╰─────────────────╯", style="bold yellow", justify="center")
        time.sleep(0.3)
        console.clear()
        console.print(eye_art, style="bold cyan")
        console.print(eye_symbol, style="bold yellow", justify="center")

def display_startup_banner():
    """Complete startup banner with animations"""
    console.clear()
    
    # Matrix effect background
    console.print("🔍 Initializing OSINT Eye...", style="bold green")
    time.sleep(1)
    
    # Main banner
    display_banner()
    
    # System info
    info_panel = Panel.fit(
        """
🔍 Advanced Social Media Intelligence Tool
🤖 AI-Powered Analysis & Network Mapping
🕸️  Multi-Platform OSINT Collection
🔒 Secure & Anonymous Operations
⚡ Real-time Monitoring & Alerts

[bold green]Status:[/bold green] [green]READY[/green]
[bold cyan]Version:[/bold cyan] [cyan]2.0 Advanced[/cyan]
[bold yellow]Mode:[/bold yellow] [yellow]CLI Interface[/yellow]
        """,
        title="🎯 System Status",
        border_style="blue"
    )
    
    console.print(info_panel, justify="center")
    
    # Loading animation
    console.print("\n🚀 Loading modules...", style="bold white")
    modules = [
        "AI Analysis Engine",
        "Network Mapper", 
        "Database Manager",
        "Security Layer",
        "Automation System",
        "Web Interface"
    ]
    
    for module in modules:
        console.print(f"   ✅ {module}", style="green")
        time.sleep(0.2)
    
    console.print("\n🎉 OSINT Eye is ready for operation!", style="bold green")
    time.sleep(1)

def display_help_banner():
    """Help command banner"""
    help_art = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🔍 OSINT EYE COMMANDS                     ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📊 fetch    - Collect data from social platforms           ║
    ║  🧠 analyze  - AI-powered profile analysis                  ║
    ║  🕸️  network  - Generate relationship visualizations        ║
    ║  ⏰ schedule - Automated monitoring tasks                   ║
    ║  🌐 server   - Start web dashboard                         ║
    ║  🔒 proxy    - Manage security & anonymity                 ║
    ║  📈 stats    - Database statistics                         ║
    ║  📊 report   - Generate comprehensive reports              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(help_art, style="bold cyan")

def loading_spinner(text="Processing"):
    """Animated loading spinner"""
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for _ in range(20):
        for spinner in spinners:
            console.print(f"\r{spinner} {text}...", end="", style="bold yellow")
            time.sleep(0.1)
    console.print(f"\r✅ {text} complete!", style="bold green")

def success_animation():
    """Success completion animation"""
    success_frames = [
        "   ✨   ",
        "  ✨✨  ",
        " ✨✨✨ ",
        "✨✨✨✨",
        " ✨✨✨ ",
        "  ✨✨  ",
        "   ✨   "
    ]
    
    for frame in success_frames:
        console.print(f"\r{frame} Operation Successful! {frame}", end="", style="bold green")
        time.sleep(0.2)
    console.print()

def error_animation():
    """Error animation"""
    console.print("❌ ERROR DETECTED ❌", style="bold red blink")
    time.sleep(0.5)
    console.print("🔧 Attempting recovery...", style="bold yellow")

def display_credits():
    """Display credits with animation"""
    credits = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        🏆 CREDITS                            ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🔬 Developed by: Advanced OSINT Research Team              ║
    ║  🎯 Purpose: Educational & Security Research                ║
    ║  ⚖️  License: MIT Open Source                               ║
    ║  🌟 Version: 2.0 Advanced Edition                          ║
    ║  📧 Support: github.com/osint-eye                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    for line in credits.split('\n'):
        console.print(line, style="bold magenta")
        time.sleep(0.1)