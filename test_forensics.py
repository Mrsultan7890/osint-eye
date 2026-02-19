#!/usr/bin/env python3
"""
Test script for Digital Forensics features
"""
import os
import sys
import tempfile
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_metadata_extraction():
    """Test metadata extraction"""
    print("🔍 Testing Metadata Extraction...")
    
    from forensics.metadata_extractor import MetadataExtractor
    extractor = MetadataExtractor()
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test file for forensic analysis\nCreated for OSINT Eye testing")
        test_file = f.name
    
    try:
        # Extract metadata
        metadata = extractor.extract_file_metadata(test_file)
        
        print(f"✅ File analyzed: {os.path.basename(test_file)}")
        print(f"   Size: {metadata['file_info']['size']} bytes")
        print(f"   SHA256: {metadata['hashes']['sha256'][:16]}...")
        print(f"   Created: {metadata['timestamps']['created']}")
        
        return True
    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")
        return False
    finally:
        os.unlink(test_file)

def test_timeline_analysis():
    """Test timeline analysis"""
    print("\n⏰ Testing Timeline Analysis...")
    
    from forensics.timeline_analyzer import TimelineAnalyzer
    analyzer = TimelineAnalyzer()
    
    try:
        # Analyze current directory
        timeline = analyzer.create_timeline(".", "test_timeline.json")
        
        print(f"✅ Timeline created with {len(timeline)} events")
        
        # Analyze patterns
        patterns = analyzer.analyze_activity_patterns(timeline)
        
        print(f"   File types found: {len(patterns['file_types'])}")
        print(f"   Hourly activity points: {len(patterns['hourly_activity'])}")
        
        # Cleanup
        if os.path.exists("test_timeline.json"):
            os.unlink("test_timeline.json")
        
        return True
    except Exception as e:
        print(f"❌ Timeline analysis failed: {e}")
        return False

def test_network_forensics():
    """Test network forensics"""
    print("\n🌐 Testing Network Forensics...")
    
    from forensics.network_forensics import NetworkForensics
    forensics = NetworkForensics()
    
    try:
        # Get active connections
        connections = forensics.get_active_connections()
        print(f"✅ Found {len([c for c in connections if 'error' not in c])} active connections")
        
        # Analyze connections
        analysis = forensics.analyze_network_connections()
        print(f"   Listening ports: {len(analysis['listening_ports'])}")
        print(f"   External connections: {len(analysis['external_connections'])}")
        
        # Scan localhost ports (limited range for testing)
        open_ports = forensics.scan_open_ports("127.0.0.1", (80, 100))
        print(f"   Open ports (80-100): {len(open_ports)}")
        
        return True
    except Exception as e:
        print(f"❌ Network forensics failed: {e}")
        return False

def test_memory_forensics():
    """Test memory forensics"""
    print("\n🧠 Testing Memory Forensics...")
    
    from forensics.memory_analyzer import MemoryAnalyzer
    analyzer = MemoryAnalyzer()
    
    try:
        # Get running processes
        processes = analyzer.get_running_processes()
        print(f"✅ Found {len(processes)} running processes")
        
        # Analyze suspicious processes
        analysis = analyzer.analyze_suspicious_processes(processes)
        print(f"   Suspicious processes: {len(analysis['suspicious_processes'])}")
        print(f"   High memory processes: {len(analysis['high_memory_processes'])}")
        print(f"   Network active processes: {len(analysis['network_active_processes'])}")
        
        # Get system memory info
        memory_info = analyzer.get_system_memory_info()
        print(f"   Memory usage: {memory_info['memory_percent']:.1f}%")
        print(f"   Available memory: {memory_info['available_memory_gb']:.1f} GB")
        
        return True
    except Exception as e:
        print(f"❌ Memory forensics failed: {e}")
        return False

def test_comprehensive_forensics():
    """Test comprehensive forensic scan"""
    print("\n🔬 Testing Comprehensive Forensic Scan...")
    
    try:
        from forensics.metadata_extractor import MetadataExtractor
        from forensics.timeline_analyzer import TimelineAnalyzer
        from forensics.network_forensics import NetworkForensics
        from forensics.memory_analyzer import MemoryAnalyzer
        
        # Create test directory
        test_dir = "test_forensic_target"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create some test files
        for i in range(3):
            with open(f"{test_dir}/test_file_{i}.txt", 'w') as f:
                f.write(f"Test file {i} content\nTimestamp: {datetime.now()}")
        
        print("✅ Created test environment")
        
        # Run all forensic modules
        extractor = MetadataExtractor()
        results = extractor.analyze_directory(test_dir)
        print(f"   Metadata: {len(results)} files analyzed")
        
        timeline_analyzer = TimelineAnalyzer()
        timeline = timeline_analyzer.create_timeline(test_dir)
        print(f"   Timeline: {len(timeline)} events")
        
        network_forensics = NetworkForensics()
        network_analysis = network_forensics.analyze_network_connections()
        print(f"   Network: {network_analysis['total_connections']} connections")
        
        memory_analyzer = MemoryAnalyzer()
        memory_info = memory_analyzer.get_system_memory_info()
        print(f"   Memory: {memory_info['memory_percent']:.1f}% used")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ Comprehensive forensics failed: {e}")
        return False

def main():
    """Run all forensic tests"""
    print("🔬 OSINT Eye - Digital Forensics Test Suite")
    print("=" * 50)
    
    tests = [
        test_metadata_extraction,
        test_timeline_analysis,
        test_network_forensics,
        test_memory_forensics,
        test_comprehensive_forensics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All forensic modules working perfectly!")
        print("\n🚀 Ready for cybersecurity investigations!")
        print("\nAvailable forensic commands:")
        print("  • osint-eye extract-metadata <file/dir>")
        print("  • osint-eye timeline-analysis <directory>")
        print("  • osint-eye network-forensics")
        print("  • osint-eye memory-forensics")
        print("  • osint-eye forensic-scan <target>")
    else:
        print("⚠️ Some tests failed - check dependencies")

if __name__ == "__main__":
    main()