from flask import Flask, render_template, request, jsonify, send_file
import requests
import bencodepy
import struct
import socket
import json
import csv
from datetime import datetime
import os
from urllib.parse import urlencode, urlparse
import hashlib
import random
import string

app = Flask(__name__)

class TorrentTracker:
    def __init__(self):
        self.tracking_data = []
        
    def generate_peer_id(self):
        """Generate a proper 20-byte peer ID"""
        client_id = "-PY0001-"  # Fake Python client
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        return (client_id + random_part).encode()[:20]
    
    def parse_tracker_response(self, response_data):
        """Parse bencoded tracker response"""
        try:
            decoded = bencodepy.decode(response_data)
            peers_data = []
            
            if b'peers' in decoded:
                peers = decoded[b'peers']
                if isinstance(peers, bytes):
                    # Compact format: 6 bytes per peer (4 for IP, 2 for port)
                    for i in range(0, len(peers), 6):
                        if i + 6 <= len(peers):
                            ip_bytes = peers[i:i+4]
                            port_bytes = peers[i+4:i+6]
                            ip = socket.inet_ntoa(ip_bytes)
                            port = struct.unpack('!H', port_bytes)[0]
                            peers_data.append({'ip': ip, 'port': port})
                elif isinstance(peers, list):
                    # Dictionary format
                    for peer in peers:
                        if b'ip' in peer and b'port' in peer:
                            peers_data.append({
                                'ip': peer[b'ip'].decode(),
                                'port': peer[b'port']
                            })
            
            return {
                'peers': peers_data,
                'interval': decoded.get(b'interval', 1800),
                'complete': decoded.get(b'complete', 0),
                'incomplete': decoded.get(b'incomplete', 0),
                'downloaded': decoded.get(b'downloaded', 0)
            }
        except Exception as e:
            return {'error': f'Failed to parse response: {str(e)}'}
    
    def get_peers(self, info_hash, tracker_url, port=6881):
        """Get peers from tracker"""
        try:
            # Convert hex info_hash to bytes if needed
            if isinstance(info_hash, str):
                if len(info_hash) == 40:  # Hex string
                    info_hash = bytes.fromhex(info_hash)
                else:
                    info_hash = info_hash.encode()
            
            peer_id = self.generate_peer_id()
            
            params = {
                'info_hash': info_hash,
                'peer_id': peer_id,
                'port': port,
                'uploaded': 0,
                'downloaded': 0,
                'left': 0,
                'compact': 1,
                'event': 'started'
            }
            
            # Make request
            response = requests.get(tracker_url, params=params, timeout=10)
            
            if response.status_code == 200:
                parsed_data = self.parse_tracker_response(response.content)
                
                # Store tracking data
                tracking_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'info_hash': info_hash.hex() if isinstance(info_hash, bytes) else info_hash,
                    'tracker_url': tracker_url,
                    'response': parsed_data
                }
                self.tracking_data.append(tracking_entry)
                
                return parsed_data
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'error': f'Request failed: {str(e)}'}
    
    def get_report_data(self):
        """Get all tracking data for reports"""
        return self.tracking_data
    
    def export_csv(self, filename='tracker_report.csv'):
        """Export tracking data to CSV"""
        if not self.tracking_data:
            return None
            
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'info_hash', 'tracker_url', 'peer_count', 
                         'seeders', 'leechers', 'peers_list']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in self.tracking_data:
                response = entry['response']
                peers_list = []
                if 'peers' in response:
                    peers_list = [f"{p['ip']}:{p['port']}" for p in response['peers']]
                
                writer.writerow({
                    'timestamp': entry['timestamp'],
                    'info_hash': entry['info_hash'],
                    'tracker_url': entry['tracker_url'],
                    'peer_count': len(response.get('peers', [])),
                    'seeders': response.get('complete', 0),
                    'leechers': response.get('incomplete', 0),
                    'peers_list': '; '.join(peers_list)
                })
        
        return filename

# Global tracker instance
tracker = TorrentTracker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_peers():
    data = request.get_json()
    info_hash = data.get('info_hash', '').strip()
    tracker_url = data.get('tracker_url', '').strip()
    port = int(data.get('port', 6881))
    
    if not info_hash or not tracker_url:
        return jsonify({'error': 'Info hash and tracker URL are required'})
    
    result = tracker.get_peers(info_hash, tracker_url, port)
    return jsonify(result)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/api/reports')
def api_reports():
    return jsonify(tracker.get_report_data())

@app.route('/export/csv')
def export_csv():
    filename = tracker.export_csv()
    if filename and os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({'error': 'No data to export'})

@app.route('/export/json')
def export_json():
    data = tracker.get_report_data()
    filename = 'tracker_report.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    # Create templates directory and files
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html template
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Torrent Peer Tracker - Educational Research Tool</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .results { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .error { color: #e74c3c; }
        .success { color: #27ae60; }
        .peer-list { margin-top: 10px; }
        .peer-item { background: white; padding: 8px; margin: 5px 0; border-radius: 4px; border-left: 4px solid #3498db; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #3498db; text-decoration: none; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-box { background: #ecf0f1; padding: 15px; border-radius: 4px; flex: 1; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Torrent Peer Tracker</h1>
        <p>Educational Research Tool for Legal Torrents</p>
    </div>
    
    <div class="nav">
        <a href="/">🏠 Tracker</a>
        <a href="/reports">📊 Reports</a>
    </div>
    
    <div class="form-container">
        <h2>Track Torrent Peers</h2>
        <form id="trackForm">
            <div class="form-group">
                <label for="info_hash">Info Hash (40-character hex string):</label>
                <input type="text" id="info_hash" placeholder="e.g., 1234567890abcdef1234567890abcdef12345678" maxlength="40">
            </div>
            
            <div class="form-group">
                <label for="tracker_url">Tracker URL:</label>
                <input type="text" id="tracker_url" placeholder="e.g., http://tracker.example.com:8080/announce">
            </div>
            
            <div class="form-group">
                <label for="port">Port (optional):</label>
                <input type="number" id="port" value="6881" min="1" max="65535">
            </div>
            
            <button type="submit">🔍 Track Peers</button>
        </form>
    </div>
    
    <div id="results" class="results" style="display: none;"></div>
    
    <script>
        document.getElementById('trackForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<p>🔄 Tracking peers...</p>';
            
            const data = {
                info_hash: document.getElementById('info_hash').value,
                tracker_url: document.getElementById('tracker_url').value,
                port: document.getElementById('port').value
            };
            
            try {
                const response = await fetch('/track', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    resultsDiv.innerHTML = `<p class="error">❌ Error: ${result.error}</p>`;
                } else {
                    let html = '<h3>✅ Tracking Results</h3>';
                    
                    if (result.peers && result.peers.length > 0) {
                        html += `
                            <div class="stats">
                                <div class="stat-box">
                                    <h4>👥 Total Peers</h4>
                                    <strong>${result.peers.length}</strong>
                                </div>
                                <div class="stat-box">
                                    <h4>🌱 Seeders</h4>
                                    <strong>${result.complete || 0}</strong>
                                </div>
                                <div class="stat-box">
                                    <h4>⬇️ Leechers</h4>
                                    <strong>${result.incomplete || 0}</strong>
                                </div>
                            </div>
                            <div class="peer-list">
                                <h4>Peer List:</h4>
                        `;
                        
                        result.peers.forEach(peer => {
                            html += `<div class="peer-item">📡 ${peer.ip}:${peer.port}</div>`;
                        });
                        
                        html += '</div>';
                    } else {
                        html += '<p>No peers found for this torrent.</p>';
                    }
                    
                    if (result.interval) {
                        html += `<p><strong>⏱️ Update Interval:</strong> ${result.interval} seconds</p>`;
                    }
                    
                    resultsDiv.innerHTML = html;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<p class="error">❌ Network error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>'''
    
    # Create reports.html template
    reports_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracking Reports - Torrent Peer Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #3498db; text-decoration: none; }
        .export-buttons { margin-bottom: 20px; }
        .export-buttons button { background: #27ae60; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .export-buttons button:hover { background: #229954; }
        .report-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #3498db; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .peers-summary { margin-top: 10px; padding: 10px; background: white; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Tracking Reports</h1>
        <p>Historical data from torrent peer tracking sessions</p>
    </div>
    
    <div class="nav">
        <a href="/">🏠 Tracker</a>
        <a href="/reports">📊 Reports</a>
    </div>
    
    <div class="export-buttons">
        <button onclick="exportCSV()">📄 Export CSV</button>
        <button onclick="exportJSON()">📋 Export JSON</button>
        <button onclick="loadReports()">🔄 Refresh</button>
    </div>
    
    <div id="reports-container">
        <p>Loading reports...</p>
    </div>
    
    <script>
        async function loadReports() {
            const container = document.getElementById('reports-container');
            container.innerHTML = '<p>🔄 Loading reports...</p>';
            
            try {
                const response = await fetch('/api/reports');
                const reports = await response.json();
                
                if (reports.length === 0) {
                    container.innerHTML = '<p>No tracking data available yet. Use the tracker to generate some data!</p>';
                    return;
                }
                
                let html = `<h3>📈 Total Sessions: ${reports.length}</h3>`;
                
                reports.reverse().forEach((report, index) => {
                    const response = report.response;
                    const peerCount = response.peers ? response.peers.length : 0;
                    
                    html += `
                        <div class="report-item">
                            <h4>Session ${reports.length - index}</h4>
                            <div class="timestamp">🕐 ${new Date(report.timestamp).toLocaleString()}</div>
                            <p><strong>Info Hash:</strong> ${report.info_hash}</p>
                            <p><strong>Tracker:</strong> ${report.tracker_url}</p>
                            
                            <div class="peers-summary">
                                <strong>📊 Summary:</strong>
                                Peers: ${peerCount} | 
                                Seeders: ${response.complete || 0} | 
                                Leechers: ${response.incomplete || 0}
                                
                                ${peerCount > 0 ? `
                                    <table>
                                        <thead>
                                            <tr><th>IP Address</th><th>Port</th></tr>
                                        </thead>
                                        <tbody>
                                            ${response.peers.map(peer => 
                                                `<tr><td>${peer.ip}</td><td>${peer.port}</td></tr>`
                                            ).join('')}
                                        </tbody>
                                    </table>
                                ` : '<p>No peers found in this session.</p>'}
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = `<p class="error">❌ Error loading reports: ${error.message}</p>`;
            }
        }
        
        function exportCSV() {
            window.location.href = '/export/csv';
        }
        
        function exportJSON() {
            window.location.href = '/export/json';
        }
        
        // Load reports on page load
        loadReports();
    </script>
</body>
</html>'''
    
    # Write template files
    with open('templates/index.html', 'w') as f:
        f.write(index_html)
    
    with open('templates/reports.html', 'w') as f:
        f.write(reports_html)
    
    print("🚀 Starting Torrent Peer Tracker Web Application...")
    print("📋 Educational Research Tool for Legal Torrents")
    print("🌐 Access at: http://localhost:5000")
    print("📊 Reports at: http://localhost:5000/reports")
    
    app.run(debug=True, host='0.0.0.0', port=5000)