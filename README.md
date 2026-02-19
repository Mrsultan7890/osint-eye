# 🔍 OSINT Eye - Advanced Social Media Intelligence Tool

A comprehensive, production-ready CLI-based OSINT tool for analyzing social media profiles across multiple platforms with advanced AI capabilities, network analysis, and automated monitoring - all without external paid APIs.

## 🚀 **Advanced Features**

### **🎯 Multi-Platform Support**
- **Instagram**: Profile analysis, post scraping, engagement metrics
- **Twitter/X**: Tweet analysis, user profiling, sentiment tracking  
- **YouTube**: Channel metadata, video analysis
- **TikTok**: Profile scraping, video metadata (Selenium-based)
- **LinkedIn**: Public profile analysis, professional network mapping

### **🤖 AI-Powered Analysis**
- **Face Recognition**: Profile image analysis and comparison
- **Image Analysis**: EXIF metadata extraction, reverse image search hashes
- **Advanced NLP**: Entity extraction, sentiment analysis, language detection
- **Behavioral Analysis**: Activity pattern recognition, anomaly detection

### **🕸️ Network Visualization**
- **Interactive Graphs**: Plotly-based relationship mapping
- **Static Visualizations**: High-quality matplotlib network graphs
- **Community Detection**: Automated cluster identification
- **Centrality Analysis**: Influence and importance metrics

### **💾 Advanced Storage**
- **SQLite Database**: Structured data storage with relationships
- **JSON Archives**: Timestamped data versioning
- **Full-Text Search**: Elasticsearch-ready data structure
- **Data Export**: CSV, Excel, JSON formats

### **⏰ Automation & Monitoring**
- **Task Scheduler**: Cron-like automated data collection
- **Real-time Alerts**: Keyword and sentiment monitoring
- **Batch Processing**: Multi-target simultaneous analysis
- **Background Tasks**: Non-blocking scheduled operations

### **🔒 Security & Privacy**
- **Proxy Support**: Tor integration, HTTP/SOCKS5 proxies
- **User Agent Rotation**: Anti-detection mechanisms
- **Rate Limiting**: Intelligent request throttling
- **Local Storage**: No external data transmission

### **🌐 Web Interface**
- **REST API**: Programmatic access to all features
- **Interactive Dashboard**: Web-based control panel
- **Real-time Updates**: Live monitoring interface
- **Mobile Responsive**: Cross-device compatibility

## 📁 **Project Structure**

```
osint-eye/
├── src/
│   ├── main.py                 # Enhanced CLI with all features
│   ├── fetchers/              # Platform-specific collectors
│   │   ├── instagram_fetcher.py
│   │   ├── twitter_fetcher.py
│   │   ├── youtube_fetcher.py
│   │   ├── tiktok_fetcher.py   # NEW: Selenium-based
│   │   └── linkedin_fetcher.py # NEW: Professional networks
│   ├── analysis/              # Advanced analytics
│   │   ├── analyzer.py        # Enhanced NLP analysis
│   │   └── reporter.py        # Multi-format reporting
│   ├── ai/                    # NEW: AI capabilities
│   │   ├── face_analyzer.py   # Face detection & recognition
│   │   └── image_analyzer.py  # EXIF & image forensics
│   ├── database/              # NEW: Database layer
│   │   └── sqlite_manager.py  # Structured data storage
│   ├── visualization/         # NEW: Advanced visualizations
│   │   └── network_mapper.py  # Network analysis & graphs
│   ├── automation/            # NEW: Scheduling & monitoring
│   │   └── scheduler.py       # Task automation
│   ├── security/              # NEW: Security features
│   │   └── proxy_manager.py   # Proxy & anonymization
│   ├── api/                   # NEW: Web interface
│   │   └── web_server.py      # Flask API & dashboard
│   ├── storage/               # Data management
│   │   └── data_manager.py    # Enhanced JSON storage
│   └── utils/                 # Utilities
│       ├── logger.py
│       └── rate_limiter.py
├── config/                    # NEW: Configuration management
│   ├── config.yaml           # Main configuration
│   ├── proxies.json          # Proxy settings
│   └── scheduler.json        # Task schedules
├── data/                     # Local data storage
├── reports/                  # Generated reports
├── cache/                    # NEW: Caching layer
├── images/                   # NEW: Downloaded images
└── logs/                     # Application logs
```

## 🛠 **Installation & Setup**

### **1. Clone & Install**
```bash
git clone <repository-url>
cd osint-eye
pip install -r requirements.txt
```

### **2. Install Additional Dependencies**
```bash
# spaCy language model
python -m spacy download en_core_web_sm

# Chrome WebDriver (for TikTok)
# Will be auto-downloaded by webdriver-manager

# Optional: Tor for proxy support
sudo apt install tor  # Ubuntu/Debian
brew install tor      # macOS
```

### **3. Configuration**
```bash
cp .env.example .env
cp config/config.yaml.example config/config.yaml
# Edit configuration files as needed
```

## 🎯 **Usage Examples**

### **Basic Data Collection**
```bash
# Fetch Instagram profile
python src/main.py fetch --platform instagram --username natgeo --max 30

# Fetch with proxy support
python src/main.py fetch --platform instagram --username target --proxy

# Fetch multiple platforms
python src/main.py fetch --platform twitter --username nasa --max 50
python src/main.py fetch --platform tiktok --username username --max 20
```

### **Advanced Analysis**
```bash
# Standard analysis
python src/main.py analyze --platform instagram --username natgeo

# AI-powered analysis (face detection, image analysis)
python src/main.py analyze --platform instagram --username target --ai

# Cross-platform analysis
python src/main.py analyze --platform twitter --username nasa --ai
```

### **Network Visualization**
```bash
# Generate interactive network graph
python src/main.py network --format interactive

# Static network visualization
python src/main.py network --format static

# Export network data
python src/main.py network --format json
```

### **Automated Monitoring**
```bash
# Add scheduled monitoring task
python src/main.py schedule --action add --task-name "daily_monitoring" \
  --targets "target1,target2,target3" --schedule-type daily

# Start scheduler
python src/main.py schedule --action start

# Check scheduler status
python src/main.py schedule --action status
```

### **Security & Proxy Management**
```bash
# Setup Tor proxy
python src/main.py proxy --action setup --proxy-type tor

# Test all proxies
python src/main.py proxy --action test

# Check proxy status
python src/main.py proxy --action status
```

### **Web Interface**
```bash
# Start web server and dashboard
python src/main.py server --host 0.0.0.0 --port 5000

# Access dashboard at: http://localhost:5000
# API endpoints at: http://localhost:5000/api/
```

### **Advanced Reporting**
```bash
# Generate HTML report with network analysis
python src/main.py report --platform instagram --username natgeo \
  --format html --include-network --include-ai

# Generate PDF report
python src/main.py report --platform twitter --username nasa --format pdf

# Generate comprehensive markdown report
python src/main.py report --platform instagram --username target --format markdown
```

## 🔧 **Configuration**

### **Main Configuration (config/config.yaml)**
```yaml
# Enable/disable features
analysis:
  ai_features:
    face_detection: true
    image_analysis: true
    
security:
  proxy_enabled: true
  tor_enabled: true
  
automation:
  scheduler_enabled: true
  alert_keywords: ["crisis", "emergency"]
```

### **Proxy Configuration**
```bash
# Add HTTP proxy
python src/main.py proxy --action setup --proxy-type http --host proxy.example.com --port 8080

# Setup Tor (automatic)
python src/main.py proxy --action setup --proxy-type tor
```

## 📊 **Advanced Features**

### **1. AI Analysis**
- **Face Detection**: Identify and compare faces across profiles
- **Image Forensics**: EXIF metadata extraction, compression analysis
- **Reverse Image Search**: Generate perceptual hashes for image matching
- **Behavioral Analysis**: ML-based pattern recognition

### **2. Network Analysis**
- **Relationship Mapping**: Visualize connections between profiles
- **Community Detection**: Identify clusters and groups
- **Influence Analysis**: Calculate centrality and importance metrics
- **Cross-Platform Linking**: Connect same users across platforms

### **3. Automated Monitoring**
- **Scheduled Collection**: Automated data gathering
- **Real-time Alerts**: Keyword and sentiment-based notifications
- **Batch Processing**: Multi-target simultaneous analysis
- **Historical Tracking**: Long-term trend analysis

### **4. Security Features**
- **Proxy Rotation**: Automatic proxy switching
- **Tor Integration**: Anonymous data collection
- **User Agent Rotation**: Anti-detection mechanisms
- **Rate Limiting**: Intelligent request throttling

## 🌐 **API Endpoints**

### **Data Collection**
```bash
POST /api/fetch
{
  "platform": "instagram",
  "username": "target",
  "max_items": 20
}
```

### **Analysis**
```bash
POST /api/analyze
{
  "platform": "instagram", 
  "username": "target"
}
```

### **Network Analysis**
```bash
GET /api/network
```

### **Scheduler Management**
```bash
POST /api/scheduler/add_task
{
  "task_name": "monitoring",
  "targets": ["user1", "user2"],
  "schedule_type": "daily"
}
```

## 📈 **Database Schema**

### **Profiles Table**
- Platform, username, display name
- Follower metrics, verification status
- Profile metadata (JSON)

### **Posts Table**
- Content, engagement metrics
- Hashtags, mentions (JSON arrays)
- Timestamps, post metadata

### **Analysis Table**
- Sentiment scores, entity data
- Activity patterns, analysis results
- AI analysis results (JSON)

### **Relationships Table**
- Source/target profile connections
- Relationship types and strength
- Network metadata

## 🔍 **Advanced Search & Analytics**

```bash
# Database statistics
python src/main.py stats

# Search profiles
# (Implement search functionality)

# Export data
# (Implement data export features)
```

## 🛡️ **Security & Compliance**

### **Privacy Protection**
- All data stored locally
- No external API dependencies
- Configurable data retention
- Optional data anonymization

### **Ethical Usage**
- Respects robots.txt
- Rate limiting enabled
- Public data only
- Terms of service compliance

### **Security Features**
- Proxy support (HTTP, SOCKS5, Tor)
- User agent rotation
- Request randomization
- Session management

## 🚨 **Legal & Ethical Notice**

This tool is designed for:
- ✅ Educational and research purposes
- ✅ Security research and analysis
- ✅ Public data investigation
- ✅ OSINT training and learning

**Important Guidelines:**
- Only collect publicly available data
- Respect platform terms of service
- Comply with local privacy laws (GDPR, etc.)
- Use responsibly and ethically
- Obtain proper permissions when required

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Chrome Driver Issues (TikTok)**
   ```bash
   # Update Chrome and webdriver-manager
   pip install --upgrade webdriver-manager
   ```

2. **Tor Connection Issues**
   ```bash
   # Start Tor service
   sudo systemctl start tor
   # Or manually: tor
   ```

3. **Face Recognition Dependencies**
   ```bash
   # Install system dependencies
   sudo apt install cmake libopenblas-dev liblapack-dev
   pip install dlib face-recognition
   ```

4. **Memory Issues**
   ```bash
   # Reduce max_items or enable caching
   python src/main.py fetch --platform instagram --username target --max 10
   ```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add new fetchers in `src/fetchers/`
4. Implement analysis modules in `src/analysis/`
5. Update documentation
6. Submit pull request

### **Adding New Platforms**
```python
# src/fetchers/new_platform_fetcher.py
class NewPlatformFetcher:
    def fetch_user_data(self, username: str, max_items: int) -> Dict[str, Any]:
        # Implement platform-specific logic
        pass
```

## 📄 **License**

MIT License - see LICENSE file for details.

## 🙏 **Acknowledgments**

- **instaloader**: Instagram data collection
- **snscrape**: Twitter data scraping  
- **Selenium**: Dynamic content scraping
- **spaCy**: Natural language processing
- **NetworkX**: Network analysis
- **Face Recognition**: AI-powered face detection
- **Flask**: Web interface framework

---

**⚠️ Disclaimer**: This tool is provided for educational and research purposes only. Users are responsible for ensuring compliance with applicable laws, platform terms of service, and ethical guidelines. The authors assume no liability for misuse or legal issues arising from the use of this software.# osint-eye
