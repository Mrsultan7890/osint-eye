"""
Digital Forensics - Memory Analyzer
Analyzes running processes, memory usage, and suspicious activities
"""
import psutil
import os
import json
from datetime import datetime
from collections import defaultdict
import hashlib

class MemoryAnalyzer:
    def __init__(self):
        self.suspicious_processes = [
            'nc', 'netcat', 'ncat', 'socat', 'telnet',
            'wget', 'curl', 'python', 'perl', 'ruby',
            'powershell', 'cmd', 'bash', 'sh'
        ]
        self.system_processes = [
            'systemd', 'kthreadd', 'ksoftirqd', 'migration',
            'rcu_', 'watchdog', 'sshd', 'NetworkManager'
        ]
    
    def get_running_processes(self):
        """Get detailed information about running processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 
                                       'create_time', 'memory_info', 'cpu_percent']):
            try:
                pinfo = proc.info
                
                # Get process details
                process_info = {
                    "pid": pinfo['pid'],
                    "name": pinfo['name'] or "Unknown",
                    "username": pinfo['username'] or "Unknown",
                    "cmdline": ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else '',
                    "created": datetime.fromtimestamp(pinfo['create_time']).isoformat() if pinfo['create_time'] else "Unknown",
                    "memory_mb": round(pinfo['memory_info'].rss / 1024 / 1024, 2) if pinfo['memory_info'] else 0,
                    "cpu_percent": pinfo['cpu_percent'] or 0
                }
                
                # Get executable path and hash
                try:
                    exe_path = proc.exe()
                    process_info["executable_path"] = exe_path
                    process_info["executable_hash"] = self._get_file_hash(exe_path)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_info["executable_path"] = "Access Denied"
                
                # Get network connections for this process
                try:
                    connections = proc.connections()
                    process_info["network_connections"] = len(connections)
                    process_info["listening_ports"] = [
                        conn.laddr.port for conn in connections 
                        if conn.status == 'LISTEN'
                    ]
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_info["network_connections"] = 0
                    process_info["listening_ports"] = []
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    def _get_file_hash(self, file_path):
        """Calculate SHA256 hash of executable"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return "Unable to calculate"
    
    def analyze_suspicious_processes(self, processes=None):
        """Analyze processes for suspicious activities"""
        if processes is None:
            processes = self.get_running_processes()
        
        analysis = {
            "suspicious_processes": [],
            "high_memory_processes": [],
            "network_active_processes": [],
            "recently_started": [],
            "unsigned_executables": [],
            "process_anomalies": []
        }
        
        current_time = datetime.now()
        
        for proc in processes:
            # Check for suspicious process names
            proc_name = proc["name"].lower()
            if any(susp in proc_name for susp in self.suspicious_processes):
                if not any(sys_proc in proc_name for sys_proc in self.system_processes):
                    analysis["suspicious_processes"].append({
                        "pid": proc["pid"],
                        "name": proc["name"],
                        "cmdline": proc["cmdline"],
                        "reason": "Suspicious process name",
                        "risk_level": "MEDIUM"
                    })
            
            # High memory usage (>500MB)
            if proc["memory_mb"] > 500:
                analysis["high_memory_processes"].append({
                    "pid": proc["pid"],
                    "name": proc["name"],
                    "memory_mb": proc["memory_mb"],
                    "cmdline": proc["cmdline"][:100]  # Truncate long command lines
                })
            
            # Network active processes
            if proc["network_connections"] > 0:
                analysis["network_active_processes"].append({
                    "pid": proc["pid"],
                    "name": proc["name"],
                    "connections": proc["network_connections"],
                    "listening_ports": proc["listening_ports"]
                })
            
            # Recently started processes (last 1 hour)
            try:
                created_time = datetime.fromisoformat(proc["created"])
                if (current_time - created_time).total_seconds() < 3600:
                    analysis["recently_started"].append({
                        "pid": proc["pid"],
                        "name": proc["name"],
                        "created": proc["created"],
                        "cmdline": proc["cmdline"]
                    })
            except:
                pass
            
            # Check for processes with suspicious command lines
            cmdline = proc["cmdline"].lower()
            suspicious_keywords = ['download', 'wget', 'curl', 'base64', 'powershell', 
                                 'cmd.exe', '/c ', 'nc ', 'netcat', 'reverse', 'shell']
            
            if any(keyword in cmdline for keyword in suspicious_keywords):
                analysis["process_anomalies"].append({
                    "pid": proc["pid"],
                    "name": proc["name"],
                    "cmdline": proc["cmdline"],
                    "reason": "Suspicious command line arguments",
                    "risk_level": "HIGH"
                })
        
        return analysis
    
    def get_system_memory_info(self):
        """Get system memory information"""
        memory = psutil.virtual_memory()
        
        result = {
            "total_memory_gb": round(memory.total / 1024**3, 2),
            "available_memory_gb": round(memory.available / 1024**3, 2),
            "used_memory_gb": round(memory.used / 1024**3, 2),
            "memory_percent": memory.percent
        }
        
        # Try to get swap info, handle permission errors
        try:
            swap = psutil.swap_memory()
            result.update({
                "swap_total_gb": round(swap.total / 1024**3, 2),
                "swap_used_gb": round(swap.used / 1024**3, 2),
                "swap_percent": swap.percent
            })
        except (PermissionError, OSError):
            result.update({
                "swap_total_gb": 0,
                "swap_used_gb": 0,
                "swap_percent": 0
            })
        
        return result
    
    def analyze_process_tree(self):
        """Analyze process parent-child relationships"""
        process_tree = {}
        
        for proc in psutil.process_iter(['pid', 'ppid', 'name']):
            try:
                pinfo = proc.info
                pid = pinfo['pid']
                ppid = pinfo['ppid']
                name = pinfo['name']
                
                if ppid not in process_tree:
                    process_tree[ppid] = []
                
                process_tree[ppid].append({
                    "pid": pid,
                    "name": name
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Find processes with many children (potential process spawning)
        suspicious_parents = []
        for ppid, children in process_tree.items():
            if len(children) > 10:  # More than 10 child processes
                try:
                    parent = psutil.Process(ppid)
                    suspicious_parents.append({
                        "parent_pid": ppid,
                        "parent_name": parent.name(),
                        "child_count": len(children),
                        "children": [child["name"] for child in children[:5]]  # First 5 children
                    })
                except:
                    continue
        
        return {
            "process_tree": process_tree,
            "suspicious_parents": suspicious_parents
        }
    
    def detect_code_injection(self):
        """Detect potential code injection indicators"""
        injection_indicators = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_maps']):
            try:
                # Check for processes with unusual memory mappings
                maps = proc.memory_maps()
                
                executable_maps = [m for m in maps if 'x' in m.perms]
                writable_executable = [m for m in maps if 'w' in m.perms and 'x' in m.perms]
                
                if writable_executable:
                    injection_indicators.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "indicator": "writable_executable_memory",
                        "count": len(writable_executable),
                        "risk_level": "HIGH"
                    })
                
                # Check for anonymous memory regions
                anonymous_maps = [m for m in maps if m.path == '[anon]']
                if len(anonymous_maps) > 20:  # Unusual number of anonymous mappings
                    injection_indicators.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "indicator": "excessive_anonymous_memory",
                        "count": len(anonymous_maps),
                        "risk_level": "MEDIUM"
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return injection_indicators
    
    def create_memory_forensic_report(self, output_file):
        """Create comprehensive memory forensics report"""
        print("🔍 Analyzing system memory and processes...")
        
        processes = self.get_running_processes()
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "system_memory": self.get_system_memory_info(),
            "total_processes": len(processes),
            "process_analysis": self.analyze_suspicious_processes(processes),
            "process_tree": self.analyze_process_tree(),
            "injection_indicators": self.detect_code_injection(),
            "top_memory_consumers": sorted(
                [{"pid": p["pid"], "name": p["name"], "memory_mb": p["memory_mb"]} 
                 for p in processes], 
                key=lambda x: x["memory_mb"], reverse=True
            )[:10],
            "security_assessment": {
                "risk_level": "LOW",
                "findings": [],
                "recommendations": []
            }
        }
        
        # Security assessment
        findings = []
        risk_level = "LOW"
        
        if report["process_analysis"]["suspicious_processes"]:
            findings.append(f"Found {len(report['process_analysis']['suspicious_processes'])} suspicious processes")
            risk_level = "HIGH"
        
        if report["process_analysis"]["process_anomalies"]:
            findings.append(f"Found {len(report['process_analysis']['process_anomalies'])} process anomalies")
            risk_level = "HIGH"
        
        if report["injection_indicators"]:
            findings.append(f"Found {len(report['injection_indicators'])} code injection indicators")
            risk_level = "HIGH"
        
        if report["system_memory"]["memory_percent"] > 90:
            findings.append("High memory usage detected")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        
        report["security_assessment"]["risk_level"] = risk_level
        report["security_assessment"]["findings"] = findings
        
        # Recommendations
        recommendations = [
            "Monitor suspicious processes regularly",
            "Investigate processes with unusual memory patterns",
            "Check network connections of active processes",
            "Verify executable signatures and hashes"
        ]
        report["security_assessment"]["recommendations"] = recommendations
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Memory forensic report saved: {output_file}")
        return report