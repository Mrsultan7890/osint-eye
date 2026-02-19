from flask import Flask, request, jsonify, render_template_string, send_file
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import threading
from utils.logger import setup_logger

logger = setup_logger()

class OSINTWebServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard"""
            return render_template_string(self.get_dashboard_template())
        
        @self.app.route('/api/profiles', methods=['GET'])
        def get_profiles():
            """Get all profiles"""
            try:
                from database.sqlite_manager import SQLiteManager
                db = SQLiteManager()
                
                platform = request.args.get('platform')
                search = request.args.get('search', '')
                
                if search:
                    profiles = db.search_profiles(search, platform)
                else:
                    # Get recent profiles (implement this method in SQLiteManager)
                    profiles = []
                
                return jsonify({
                    'success': True,
                    'profiles': profiles,
                    'total': len(profiles)
                })
                
            except Exception as e:
                logger.error(f"API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/fetch', methods=['POST'])
        def fetch_data():
            """Fetch data for a profile"""
            try:
                data = request.get_json()
                platform = data.get('platform')
                username = data.get('username')
                max_items = data.get('max_items', 20)
                
                if not platform or not username:
                    return jsonify({'success': False, 'error': 'Platform and username required'}), 400
                
                # Import fetchers
                from fetchers.instagram_fetcher import InstagramFetcher
                from fetchers.twitter_fetcher import TwitterFetcher
                from fetchers.tiktok_fetcher import TikTokFetcher
                from storage.data_manager import DataManager
                
                fetchers = {
                    'instagram': InstagramFetcher(),
                    'twitter': TwitterFetcher(),
                    'tiktok': TikTokFetcher()
                }
                
                if platform not in fetchers:
                    return jsonify({'success': False, 'error': f'Unsupported platform: {platform}'}), 400
                
                # Fetch data
                fetcher = fetchers[platform]
                profile_data = fetcher.fetch_user_data(username, max_items)
                
                # Save data
                dm = DataManager()
                dm.save_data(platform, username, profile_data)
                
                return jsonify({
                    'success': True,
                    'message': f'Fetched {len(profile_data.get("posts", []))} items',
                    'data': profile_data
                })
                
            except Exception as e:
                logger.error(f"Fetch API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_profile():
            """Analyze a profile"""
            try:
                data = request.get_json()
                platform = data.get('platform')
                username = data.get('username')
                
                if not platform or not username:
                    return jsonify({'success': False, 'error': 'Platform and username required'}), 400
                
                from storage.data_manager import DataManager
                from analysis.analyzer import Analyzer
                
                dm = DataManager()
                profile_data = dm.load_data(platform, username)
                
                if not profile_data:
                    return jsonify({'success': False, 'error': 'No data found for profile'}), 404
                
                analyzer = Analyzer()
                analysis = analyzer.analyze_profile(profile_data)
                
                # Save analysis
                dm.save_analysis(platform, username, analysis)
                
                return jsonify({
                    'success': True,
                    'analysis': analysis
                })
                
            except Exception as e:
                logger.error(f"Analysis API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/network', methods=['GET'])
        def get_network_data():
            """Get network visualization data"""
            try:
                from visualization.network_mapper import NetworkMapper
                from database.sqlite_manager import SQLiteManager
                
                db = SQLiteManager()
                # Get profiles for network (implement this method)
                profiles = []  # db.get_profiles_for_network()
                
                mapper = NetworkMapper()
                graph = mapper.build_network_from_data(profiles)
                
                # Export network data
                network_file = mapper.export_network_data()
                
                return jsonify({
                    'success': True,
                    'network_file': str(network_file),
                    'nodes': len(graph.nodes()),
                    'edges': len(graph.edges())
                })
                
            except Exception as e:
                logger.error(f"Network API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scheduler/status', methods=['GET'])
        def get_scheduler_status():
            """Get scheduler status"""
            try:
                from automation.scheduler import TaskScheduler
                scheduler = TaskScheduler()
                status = scheduler.get_task_status()
                
                return jsonify({
                    'success': True,
                    'status': status
                })
                
            except Exception as e:
                logger.error(f"Scheduler API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/scheduler/add_task', methods=['POST'])
        def add_scheduled_task():
            """Add a new scheduled task"""
            try:
                data = request.get_json()
                task_name = data.get('task_name')
                targets = data.get('targets', [])
                platforms = data.get('platforms', [])
                schedule_type = data.get('schedule_type', 'daily')
                schedule_time = data.get('schedule_time', '09:00')
                
                from automation.scheduler import TaskScheduler
                scheduler = TaskScheduler()
                scheduler.add_monitoring_task(task_name, targets, platforms, schedule_type, schedule_time)
                
                return jsonify({
                    'success': True,
                    'message': f'Task {task_name} added successfully'
                })
                
            except Exception as e:
                logger.error(f"Add task API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_statistics():
            """Get database statistics"""
            try:
                from database.sqlite_manager import SQLiteManager
                db = SQLiteManager()
                stats = db.get_statistics()
                
                return jsonify({
                    'success': True,
                    'statistics': stats
                })
                
            except Exception as e:
                logger.error(f"Stats API error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_dashboard_template(self) -> str:
        """Get HTML template for dashboard"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>OSINT Eye Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .status { padding: 10px; border-radius: 3px; margin: 10px 0; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        #results { margin-top: 20px; }
        .result-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 3px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 OSINT Eye Dashboard</h1>
            <p>Social Media Intelligence & Analysis Platform</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Data Collection</h3>
                <form id="fetchForm">
                    <div class="form-group">
                        <label>Platform:</label>
                        <select id="platform" required>
                            <option value="">Select Platform</option>
                            <option value="instagram">Instagram</option>
                            <option value="twitter">Twitter</option>
                            <option value="tiktok">TikTok</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="username" placeholder="Enter username" required>
                    </div>
                    <div class="form-group">
                        <label>Max Items:</label>
                        <input type="number" id="maxItems" value="20" min="1" max="100">
                    </div>
                    <button type="submit" class="btn">🔍 Fetch Data</button>
                </form>
            </div>
            
            <div class="card">
                <h3>🧠 Analysis</h3>
                <form id="analyzeForm">
                    <div class="form-group">
                        <label>Platform:</label>
                        <select id="analyzePlatform" required>
                            <option value="">Select Platform</option>
                            <option value="instagram">Instagram</option>
                            <option value="twitter">Twitter</option>
                            <option value="tiktok">TikTok</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="analyzeUsername" placeholder="Enter username" required>
                    </div>
                    <button type="submit" class="btn btn-success">📈 Analyze Profile</button>
                </form>
            </div>
        </div>
        
        <div class="card">
            <h3>⏰ Scheduled Tasks</h3>
            <form id="scheduleForm">
                <div class="grid">
                    <div class="form-group">
                        <label>Task Name:</label>
                        <input type="text" id="taskName" placeholder="Enter task name" required>
                    </div>
                    <div class="form-group">
                        <label>Schedule:</label>
                        <select id="scheduleType">
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="hourly">Hourly</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Targets (comma-separated):</label>
                    <input type="text" id="targets" placeholder="username1, username2, username3">
                </div>
                <button type="submit" class="btn">⏰ Add Scheduled Task</button>
            </form>
        </div>
        
        <div id="results"></div>
    </div>

    <script>
        // Fetch Data Form
        document.getElementById('fetchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const platform = document.getElementById('platform').value;
            const username = document.getElementById('username').value;
            const maxItems = document.getElementById('maxItems').value;
            
            showStatus('Fetching data...', 'info');
            
            try {
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ platform, username, max_items: parseInt(maxItems) })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(result.message, 'success');
                    displayResult('Fetch Result', result.data);
                } else {
                    showStatus('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        });
        
        // Analyze Form
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const platform = document.getElementById('analyzePlatform').value;
            const username = document.getElementById('analyzeUsername').value;
            
            showStatus('Analyzing profile...', 'info');
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ platform, username })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('Analysis completed', 'success');
                    displayResult('Analysis Result', result.analysis);
                } else {
                    showStatus('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        });
        
        // Schedule Form
        document.getElementById('scheduleForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const taskName = document.getElementById('taskName').value;
            const scheduleType = document.getElementById('scheduleType').value;
            const targets = document.getElementById('targets').value.split(',').map(t => t.trim());
            
            try {
                const response = await fetch('/api/scheduler/add_task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        task_name: taskName, 
                        targets, 
                        platforms: ['instagram', 'twitter'],
                        schedule_type: scheduleType 
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(result.message, 'success');
                } else {
                    showStatus('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        });
        
        function showStatus(message, type) {
            const results = document.getElementById('results');
            const status = document.createElement('div');
            status.className = `status ${type}`;
            status.textContent = message;
            results.appendChild(status);
            
            // Auto-remove after 5 seconds
            setTimeout(() => status.remove(), 5000);
        }
        
        function displayResult(title, data) {
            const results = document.getElementById('results');
            const resultDiv = document.createElement('div');
            resultDiv.className = 'result-item';
            resultDiv.innerHTML = `
                <h4>${title}</h4>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
            results.appendChild(resultDiv);
        }
        
        // Load initial stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const result = await response.json();
                
                if (result.success) {
                    displayResult('Database Statistics', result.statistics);
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        // Load stats on page load
        loadStats();
    </script>
</body>
</html>
        '''
    
    def start_server(self, debug=False):
        """Start the web server"""
        logger.info(f"Starting OSINT Eye web server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
    
    def start_server_threaded(self, debug=False):
        """Start the web server in a separate thread"""
        server_thread = threading.Thread(
            target=self.start_server, 
            args=(debug,), 
            daemon=True
        )
        server_thread.start()
        logger.info(f"Web server started in background thread")
        return server_thread