"""
Digital Forensics - Network Forensics
Analyzes network connections, logs, and suspicious activities
"""
import subprocess
import json
import re
from datetime import datetime
from collections import defaultdict
import socket

class NetworkForensics:
    def __init__(self):
        self.suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389, 5900]
        self.known_malware_ips = []  # Can be populated with threat intel
    
    def get_active_connections(self):
        """Get current active network connections"""
        connections = []
        
        try:
            # Use netstat to get connections
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines[2:]:  # Skip headers
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        connections.append({
                            "protocol": parts[0],
                            "local_address": parts[3],
                            "state": parts[5] if len(parts) > 5 else "LISTENING",
                            "timestamp": datetime.now().isoformat()
                        })
        except Exception as e:
            connections.append({"error": f"Failed to get connections: {str(e)}"})
        
        return connections
    
    def analyze_network_connections(self):
        """Analyze network connections for suspicious activity"""
        connections = self.get_active_connections()
        analysis = {
            "total_connections": len([c for c in connections if "error" not in c]),
            "listening_ports": [],
            "external_connections": [],
            "suspicious_activity": [],
            "port_analysis": defaultdict(int)
        }
        
        for conn in connections:
            if "error" in conn:
                continue
            
            try:
                local_addr = conn["local_address"]
                if ':' in local_addr:
                    ip, port = local_addr.rsplit(':', 1)
                    port = int(port)
                    
                    analysis["port_analysis"][port] += 1
                    
                    # Check for listening ports
                    if conn["state"] == "LISTENING":
                        analysis["listening_ports"].append({
                            "port": port,
                            "protocol": conn["protocol"],
                            "address": ip
                        })
                        
                        # Flag suspicious ports
                        if port in self.suspicious_ports:
                            analysis["suspicious_activity"].append({
                                "type": "suspicious_port_listening",
                                "port": port,
                                "protocol": conn["protocol"],
                                "risk_level": "HIGH"
                            })
                    
                    # Check for external connections
                    if not ip.startswith(('127.', '0.0.0.0', '::')):
                        analysis["external_connections"].append({
                            "local_address": local_addr,
                            "protocol": conn["protocol"],
                            "state": conn["state"]
                        })
            except Exception:
                continue
        
        return analysis
    
    def scan_open_ports(self, target_ip="127.0.0.1", port_range=(1, 1000)):
        """Scan for open ports on target"""
        open_ports = []
        
        print(f"🔍 Scanning ports {port_range[0]}-{port_range[1]} on {target_ip}")
        
        for port in range(port_range[0], min(port_range[1] + 1, 1001)):  # Limit to 1000 ports
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # Very quick timeout
                result = sock.connect_ex((target_ip, port))
                
                if result == 0:
                    service = self._identify_service(port)
                    open_ports.append({
                        "port": port,
                        "service": service,
                        "risk_level": "HIGH" if port in self.suspicious_ports else "LOW"
                    })
                
                sock.close()
            except Exception:
                continue
        
        return open_ports
    
    def _identify_service(self, port):
        """Identify common services by port"""
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S",
            135: "RPC", 139: "NetBIOS", 445: "SMB",
            1433: "MSSQL", 3389: "RDP", 5900: "VNC"
        }
        return services.get(port, "Unknown")
    
    def analyze_dns_queries(self):
        """Analyze DNS queries from system logs"""
        dns_analysis = {
            "recent_queries": [],
            "suspicious_domains": [],
            "domain_frequency": defaultdict(int)
        }
        
        try:
            # Try to read DNS queries from system logs
            log_files = ['/var/log/syslog', '/var/log/messages']
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-1000:]  # Last 1000 lines
                        
                        for line in lines:
                            # Look for DNS query patterns
                            if 'query' in line.lower() or 'dns' in line.lower():
                                # Extract domain names using regex
                                domains = re.findall(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
                                for domain in domains:
                                    if self._is_valid_domain(domain):
                                        dns_analysis["domain_frequency"][domain] += 1
                                        
                                        # Check for suspicious domains
                                        if self._is_suspicious_domain(domain):
                                            dns_analysis["suspicious_domains"].append({
                                                "domain": domain,
                                                "reason": "Suspicious TLD or pattern",
                                                "timestamp": datetime.now().isoformat()
                                            })
                except FileNotFoundError:
                    continue
        except Exception as e:
            dns_analysis["error"] = str(e)
        
        # Get top queried domains
        top_domains = sorted(dns_analysis["domain_frequency"].items(), 
                           key=lambda x: x[1], reverse=True)[:20]
        dns_analysis["top_domains"] = [{"domain": d, "count": c} for d, c in top_domains]
        
        return dns_analysis
    
    def _is_valid_domain(self, domain):
        """Check if string is a valid domain"""
        if len(domain) < 4 or len(domain) > 253:
            return False
        if domain.count('.') < 1:
            return False
        if domain.startswith('.') or domain.endswith('.'):
            return False
        return True
    
    def _is_suspicious_domain(self, domain):
        """Check if domain is suspicious"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.bit']
        suspicious_patterns = ['temp', 'tmp', 'test', 'malware', 'virus']
        
        # Check TLD
        for tld in suspicious_tlds:
            if domain.endswith(tld):
                return True
        
        # Check patterns
        for pattern in suspicious_patterns:
            if pattern in domain.lower():
                return True
        
        # Check for excessive subdomains
        if domain.count('.') > 3:
            return True
        
        return False
    
    def get_network_interfaces(self):
        """Get network interface information"""
        interfaces = []
        
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if re.match(r'^\d+:', line):
                    # New interface
                    parts = line.split()
                    if_name = parts[1].rstrip(':')
                    current_interface = {
                        "name": if_name,
                        "addresses": [],
                        "status": "UP" if "UP" in line else "DOWN"
                    }
                    interfaces.append(current_interface)
                elif 'inet ' in line and current_interface:
                    # IPv4 address
                    addr = line.strip().split()[1]
                    current_interface["addresses"].append({
                        "type": "IPv4",
                        "address": addr
                    })
        except Exception as e:
            interfaces.append({"error": f"Failed to get interfaces: {str(e)}"})
        
        return interfaces
    
    def create_network_forensic_report(self, output_file):
        """Create comprehensive network forensics report"""
        print("🔍 Analyzing network forensics...")
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "network_connections": self.analyze_network_connections(),
            "open_ports_localhost": self.scan_open_ports(),
            "dns_analysis": self.analyze_dns_queries(),
            "network_interfaces": self.get_network_interfaces(),
            "security_assessment": {
                "risk_level": "LOW",
                "findings": [],
                "recommendations": []
            }
        }
        
        # Security assessment
        findings = []
        
        # Check for suspicious ports
        suspicious_ports = [p for p in report["open_ports_localhost"] 
                          if p.get("risk_level") == "HIGH"]
        if suspicious_ports:
            findings.append(f"Found {len(suspicious_ports)} high-risk open ports")
            report["security_assessment"]["risk_level"] = "HIGH"
        
        # Check for suspicious domains
        if report["dns_analysis"].get("suspicious_domains"):
            findings.append(f"Found {len(report['dns_analysis']['suspicious_domains'])} suspicious domains")
            report["security_assessment"]["risk_level"] = "MEDIUM"
        
        report["security_assessment"]["findings"] = findings
        
        # Recommendations
        recommendations = [
            "Close unnecessary open ports",
            "Monitor DNS queries for malicious domains",
            "Enable firewall logging",
            "Regular network security audits"
        ]
        report["security_assessment"]["recommendations"] = recommendations
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Network forensic report saved: {output_file}")
        return report