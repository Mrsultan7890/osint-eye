import requests
import socks
import socket
from urllib.parse import urlparse
import random
import time
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class ProxyManager:
    def __init__(self, config_path: str = "config/proxies.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.proxies = []
        self.current_proxy_index = 0
        self.failed_proxies = set()
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxy configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.proxies = config.get('proxies', [])
            except Exception as e:
                logger.error(f"Proxy config load error: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default proxy configuration"""
        default_config = {
            "proxies": [
                {
                    "type": "http",
                    "host": "127.0.0.1",
                    "port": 8080,
                    "username": "",
                    "password": "",
                    "enabled": False
                },
                {
                    "type": "socks5",
                    "host": "127.0.0.1", 
                    "port": 9050,
                    "username": "",
                    "password": "",
                    "enabled": False,
                    "description": "Tor SOCKS5 proxy"
                }
            ],
            "rotation": {
                "enabled": True,
                "rotate_after_requests": 10,
                "rotate_after_failures": 3
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.proxies = default_config['proxies']
    
    def add_proxy(self, proxy_type: str, host: str, port: int, 
                  username: str = "", password: str = "", enabled: bool = True):
        """Add a new proxy"""
        proxy = {
            "type": proxy_type,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "enabled": enabled
        }
        
        self.proxies.append(proxy)
        self.save_config()
        logger.info(f"Added proxy: {proxy_type}://{host}:{port}")
    
    def get_active_proxies(self) -> List[Dict[str, Any]]:
        """Get list of active proxies"""
        return [p for p in self.proxies if p.get('enabled', False)]
    
    def get_next_proxy(self) -> Optional[Dict[str, Any]]:
        """Get next proxy in rotation"""
        active_proxies = self.get_active_proxies()
        if not active_proxies:
            return None
        
        # Filter out failed proxies
        available_proxies = [p for p in active_proxies 
                           if self._proxy_key(p) not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all are failed
            self.failed_proxies.clear()
            available_proxies = active_proxies
        
        if not available_proxies:
            return None
        
        # Rotate to next proxy
        self.current_proxy_index = (self.current_proxy_index + 1) % len(available_proxies)
        return available_proxies[self.current_proxy_index]
    
    def get_requests_session(self, proxy: Optional[Dict[str, Any]] = None) -> requests.Session:
        """Get requests session with proxy configuration"""
        session = requests.Session()
        
        if not proxy:
            proxy = self.get_next_proxy()
        
        if proxy:
            proxy_url = self._build_proxy_url(proxy)
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Add authentication if provided
            if proxy.get('username') and proxy.get('password'):
                session.auth = (proxy['username'], proxy['password'])
        
        # Add common headers
        session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def test_proxy(self, proxy: Dict[str, Any]) -> bool:
        """Test if a proxy is working"""
        try:
            session = self.get_requests_session(proxy)
            response = session.get('http://httpbin.org/ip', timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Proxy test successful: {result.get('origin')}")
                return True
            else:
                logger.warning(f"Proxy test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Proxy test error: {e}")
            return False
    
    def test_all_proxies(self) -> Dict[str, bool]:
        """Test all configured proxies"""
        results = {}
        
        for proxy in self.get_active_proxies():
            proxy_key = self._proxy_key(proxy)
            results[proxy_key] = self.test_proxy(proxy)
            
            if not results[proxy_key]:
                self.failed_proxies.add(proxy_key)
            else:
                self.failed_proxies.discard(proxy_key)
        
        return results
    
    def setup_tor_proxy(self):
        """Setup Tor SOCKS proxy"""
        try:
            # Check if Tor is running
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            
            if result == 0:
                # Tor is running, add/enable Tor proxy
                tor_proxy = {
                    "type": "socks5",
                    "host": "127.0.0.1",
                    "port": 9050,
                    "username": "",
                    "password": "",
                    "enabled": True,
                    "description": "Tor SOCKS5 proxy"
                }
                
                # Check if Tor proxy already exists
                tor_exists = False
                for i, proxy in enumerate(self.proxies):
                    if proxy.get('host') == '127.0.0.1' and proxy.get('port') == 9050:
                        self.proxies[i] = tor_proxy
                        tor_exists = True
                        break
                
                if not tor_exists:
                    self.proxies.append(tor_proxy)
                
                self.save_config()
                logger.info("Tor proxy configured and enabled")
                return True
            else:
                logger.warning("Tor is not running on port 9050")
                return False
                
        except Exception as e:
            logger.error(f"Tor setup error: {e}")
            return False
    
    def rotate_proxy(self):
        """Force proxy rotation"""
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.get_active_proxies())
    
    def mark_proxy_failed(self, proxy: Dict[str, Any]):
        """Mark a proxy as failed"""
        proxy_key = self._proxy_key(proxy)
        self.failed_proxies.add(proxy_key)
        logger.warning(f"Marked proxy as failed: {proxy_key}")
    
    def _build_proxy_url(self, proxy: Dict[str, Any]) -> str:
        """Build proxy URL from configuration"""
        proxy_type = proxy.get('type', 'http')
        host = proxy.get('host')
        port = proxy.get('port')
        username = proxy.get('username', '')
        password = proxy.get('password', '')
        
        if username and password:
            return f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            return f"{proxy_type}://{host}:{port}"
    
    def _proxy_key(self, proxy: Dict[str, Any]) -> str:
        """Generate unique key for proxy"""
        return f"{proxy.get('type')}://{proxy.get('host')}:{proxy.get('port')}"
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        return random.choice(user_agents)
    
    def save_config(self):
        """Save proxy configuration"""
        config = {
            "proxies": self.proxies,
            "rotation": {
                "enabled": True,
                "rotate_after_requests": 10,
                "rotate_after_failures": 3
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        """Get proxy manager status"""
        active_proxies = self.get_active_proxies()
        
        return {
            'total_proxies': len(self.proxies),
            'active_proxies': len(active_proxies),
            'failed_proxies': len(self.failed_proxies),
            'current_proxy_index': self.current_proxy_index,
            'tor_available': self._check_tor_availability()
        }
    
    def _check_tor_availability(self) -> bool:
        """Check if Tor is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            return result == 0
        except:
            return False