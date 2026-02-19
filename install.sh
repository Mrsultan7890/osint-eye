#!/bin/bash

# OSINT Eye - Advanced Installation Script
# Supports Ubuntu/Debian, CentOS/RHEL, macOS, and Kali Linux

set -e

echo "🔍 OSINT Eye - Advanced Installation Script"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    
    echo -e "${BLUE}Detected OS: $OS${NC}"
}

# Install system dependencies
install_system_deps() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    
    case $OS in
        "debian")
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl wget
            sudo apt install -y build-essential cmake libopenblas-dev liblapack-dev
            sudo apt install -y libgtk-3-dev libboost-python-dev
            sudo apt install -y chromium-browser chromium-chromedriver
            # Optional: Tor for proxy support
            sudo apt install -y tor
            ;;
        "redhat")
            sudo yum update -y
            sudo yum install -y python3 python3-pip git curl wget
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y cmake openblas-devel lapack-devel
            sudo yum install -y chromium chromedriver
            ;;
        "arch")
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm python python-pip git curl wget
            sudo pacman -S --noconfirm base-devel cmake openblas lapack
            sudo pacman -S --noconfirm chromium chromedriver
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                echo "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install python3 git curl wget cmake
            brew install chromium chromedriver
            # Optional: Tor
            brew install tor
            ;;
        *)
            echo -e "${RED}Unsupported OS. Please install dependencies manually.${NC}"
            exit 1
            ;;
    esac
}

# Create virtual environment
setup_venv() {
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
}

# Install Python dependencies
install_python_deps() {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    # Install spaCy language model
    python -m spacy download en_core_web_sm
    
    echo -e "${GREEN}Python dependencies installed successfully!${NC}"
}

# Setup configuration files
setup_config() {
    echo -e "${YELLOW}Setting up configuration files...${NC}"
    
    # Create config directory
    mkdir -p config
    
    # Copy example configurations
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env configuration file${NC}"
    fi
    
    # Create directories
    mkdir -p data logs reports cache images
    
    echo -e "${GREEN}Configuration setup complete!${NC}"
}

# Test installation
test_installation() {
    echo -e "${YELLOW}Testing installation...${NC}"
    
    source venv/bin/activate
    
    # Test basic imports
    python3 -c "
import sys
sys.path.insert(0, 'src')

try:
    from main import app
    from fetchers.instagram_fetcher import InstagramFetcher
    from analysis.analyzer import Analyzer
    from database.sqlite_manager import SQLiteManager
    print('✅ All core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    # Test CLI
    python src/main.py --help > /dev/null
    
    echo -e "${GREEN}Installation test passed!${NC}"
}

# Setup Tor (optional)
setup_tor() {
    echo -e "${YELLOW}Setting up Tor proxy (optional)...${NC}"
    
    case $OS in
        "debian")
            if command -v tor &> /dev/null; then
                sudo systemctl enable tor
                sudo systemctl start tor
                echo -e "${GREEN}Tor service started${NC}"
            fi
            ;;
        "macos")
            if command -v tor &> /dev/null; then
                brew services start tor
                echo -e "${GREEN}Tor service started${NC}"
            fi
            ;;
    esac
}

# Create desktop shortcut (Linux only)
create_shortcut() {
    if [[ "$OS" == "debian" ]] && command -v desktop-file-install &> /dev/null; then
        echo -e "${YELLOW}Creating desktop shortcut...${NC}"
        
        cat > osint-eye.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OSINT Eye
Comment=Advanced Social Media Intelligence Tool
Exec=$(pwd)/venv/bin/python $(pwd)/src/main.py
Icon=$(pwd)/icon.png
Terminal=true
Categories=Development;Security;
EOF
        
        desktop-file-install --dir=$HOME/.local/share/applications osint-eye.desktop
        rm osint-eye.desktop
        
        echo -e "${GREEN}Desktop shortcut created${NC}"
    fi
}

# Main installation function
main() {
    echo -e "${BLUE}Starting OSINT Eye installation...${NC}"
    
    detect_os
    install_system_deps
    setup_venv
    install_python_deps
    setup_config
    test_installation
    setup_tor
    create_shortcut
    
    echo -e "${GREEN}"
    echo "🎉 OSINT Eye installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Edit configuration: nano .env"
    echo "3. Run the tool: python src/main.py --help"
    echo "4. Start web server: python src/main.py server"
    echo ""
    echo "📖 Documentation: README.md"
    echo "🌐 Web Dashboard: http://localhost:5000 (after starting server)"
    echo -e "${NC}"
}

# Run installation
main "$@"