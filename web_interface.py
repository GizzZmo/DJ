#!/usr/bin/env python3
"""
Web Interface for DJ Mixer
Provides web-based control and monitoring using Flask
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from typing import Optional
import json
import threading
import time
from pathlib import Path


class DJMixerWebServer:
    """Web server for DJ Mixer with REST API and WebSocket support"""
    
    def __init__(self, mixer, host: str = '127.0.0.1', port: int = 5000):
        self.mixer = mixer
        self.host = host
        self.port = port
        
        # Create Flask app
        self.app = Flask(__name__, 
                        template_folder='web/templates',
                        static_folder='web/static')
        # Use environment variable for secret key in production
        import os
        self.app.config['SECRET_KEY'] = os.environ.get('DJ_MIXER_SECRET_KEY', 
                                                       'dj-mixer-dev-key-change-in-production')
        
        # Enable CORS
        CORS(self.app)
        
        # Setup SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # State
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main web interface"""
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            """Get mixer status"""
            try:
                status = {
                    'initialized': self.mixer.is_initialized,
                    'master_volume': self.mixer.get_master_volume(),
                    'crossfader': self.mixer.get_crossfader(),
                    'loaded_tracks': self.mixer.get_loaded_tracks(),
                    'tracks': {}
                }
                
                for track_name in self.mixer.get_loaded_tracks():
                    status['tracks'][track_name] = {
                        'volume': self.mixer.get_track_volume(track_name),
                        'playing': self.mixer.is_track_playing(track_name)
                    }
                
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/initialize', methods=['POST'])
        def initialize():
            """Initialize mixer"""
            try:
                success = self.mixer.initialize()
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/load', methods=['POST'])
        def load_track():
            """Load a track"""
            try:
                data = request.json
                deck = data.get('deck')
                file_path = data.get('file_path')
                
                if not deck or not file_path:
                    return jsonify({'error': 'Missing deck or file_path'}), 400
                
                success = self.mixer.load_track(deck, file_path)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/play/<deck>', methods=['POST'])
        def play_track(deck):
            """Play a track"""
            try:
                success = self.mixer.play_track(deck)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/pause/<deck>', methods=['POST'])
        def pause_track(deck):
            """Pause a track"""
            try:
                success = self.mixer.pause_track(deck)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stop/<deck>', methods=['POST'])
        def stop_track(deck):
            """Stop a track"""
            try:
                success = self.mixer.stop_track(deck)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/volume/<deck>', methods=['POST'])
        def set_volume(deck):
            """Set track volume"""
            try:
                data = request.json
                volume = float(data.get('volume', 1.0))
                success = self.mixer.set_track_volume(deck, volume)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/crossfader', methods=['POST'])
        def set_crossfader():
            """Set crossfader position"""
            try:
                data = request.json
                position = float(data.get('position', 0.5))
                success = self.mixer.set_crossfader(position)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/crossfader/apply', methods=['POST'])
        def apply_crossfader():
            """Apply crossfader between deck1 and deck2"""
            try:
                success = self.mixer.apply_crossfader('deck1', 'deck2')
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/master-volume', methods=['POST'])
        def set_master_volume():
            """Set master volume"""
            try:
                data = request.json
                volume = float(data.get('volume', 1.0))
                success = self.mixer.set_master_volume(volume)
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_socketio(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print('Client connected')
            emit('connected', {'data': 'Connected to DJ Mixer'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print('Client disconnected')
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status request from client"""
            self._broadcast_status()
    
    def _broadcast_status(self):
        """Broadcast current status to all connected clients"""
        try:
            status = {
                'initialized': self.mixer.is_initialized,
                'master_volume': self.mixer.get_master_volume(),
                'crossfader': self.mixer.get_crossfader(),
                'loaded_tracks': self.mixer.get_loaded_tracks(),
                'tracks': {}
            }
            
            for track_name in self.mixer.get_loaded_tracks():
                status['tracks'][track_name] = {
                    'volume': self.mixer.get_track_volume(track_name),
                    'playing': self.mixer.is_track_playing(track_name)
                }
            
            self.socketio.emit('status_update', status)
        except Exception as e:
            print(f"Error broadcasting status: {e}")
    
    def _status_update_loop(self):
        """Background loop to broadcast status updates"""
        while self.running:
            self._broadcast_status()
            time.sleep(1)  # Update every second
    
    def start(self, debug: bool = False):
        """Start the web server"""
        self.running = True
        
        # Start status update thread
        self.update_thread = threading.Thread(target=self._status_update_loop, daemon=True)
        self.update_thread.start()
        
        print(f"Starting DJ Mixer Web Interface on http://{self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=debug)
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)


def create_web_templates():
    """Create web interface HTML templates"""
    
    # Create directories
    web_dir = Path('web')
    templates_dir = web_dir / 'templates'
    static_dir = web_dir / 'static'
    
    templates_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DJ Mixer Web Interface</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }
        .mixer-panel {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
        }
        .decks {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .deck {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
        }
        .deck h2 {
            margin-bottom: 15px;
            color: #00ffff;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        button {
            background: linear-gradient(145deg, #00ccff, #0099cc);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            flex: 1;
        }
        button:hover {
            background: linear-gradient(145deg, #00ffff, #00cccc);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
        }
        button:active {
            transform: translateY(0);
        }
        .slider-container {
            margin: 15px 0;
        }
        .slider-container label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            outline: none;
            -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #00ffff;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        .crossfader-section {
            text-align: center;
            padding: 20px;
        }
        .crossfader-section h2 {
            margin-bottom: 20px;
            color: #00ffff;
        }
        .status {
            font-size: 0.9em;
            color: #aaa;
            margin-top: 10px;
        }
        .status.playing {
            color: #00ff00;
            font-weight: bold;
        }
        .master-controls {
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        .init-button {
            background: linear-gradient(145deg, #ff6b6b, #cc5555);
            font-size: 1.2em;
            padding: 15px 40px;
        }
        .init-button:hover {
            background: linear-gradient(145deg, #ff8888, #ff6b6b);
        }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: rgba(0, 255, 0, 0.2);
            border-radius: 5px;
            border: 1px solid #00ff00;
        }
        .connection-status.disconnected {
            background: rgba(255, 0, 0, 0.2);
            border-color: #ff0000;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connected</div>
    
    <div class="container">
        <h1>🎧 DJ MIXER WEB INTERFACE 🎧</h1>
        
        <div class="mixer-panel">
            <div class="master-controls">
                <button class="init-button" onclick="initializeMixer()">Initialize Mixer</button>
                <div class="slider-container" style="flex: 1; margin-left: 30px;">
                    <label>Master Volume: <span id="masterVolumeValue">1.0</span></label>
                    <input type="range" id="masterVolume" min="0" max="1" step="0.01" value="1.0" 
                           oninput="setMasterVolume(this.value)">
                </div>
            </div>
        </div>
        
        <div class="mixer-panel">
            <div class="decks">
                <!-- Deck 1 -->
                <div class="deck">
                    <h2>DECK 1</h2>
                    <div class="controls">
                        <button onclick="playTrack('deck1')">▶ Play</button>
                        <button onclick="pauseTrack('deck1')">⏸ Pause</button>
                        <button onclick="stopTrack('deck1')">⏹ Stop</button>
                    </div>
                    <div class="slider-container">
                        <label>Volume: <span id="deck1VolumeValue">1.0</span></label>
                        <input type="range" id="deck1Volume" min="0" max="1" step="0.01" value="1.0"
                               oninput="setVolume('deck1', this.value)">
                    </div>
                    <div class="status" id="deck1Status">Status: Stopped</div>
                </div>
                
                <!-- Crossfader -->
                <div class="crossfader-section">
                    <h2>CROSSFADER</h2>
                    <div class="slider-container">
                        <label>Position: <span id="crossfaderValue">0.50</span></label>
                        <input type="range" id="crossfader" min="0" max="1" step="0.01" value="0.5"
                               oninput="setCrossfader(this.value)" style="transform: rotate(90deg); width: 150px;">
                    </div>
                    <button onclick="applyCrossfader()">Apply Crossfader</button>
                </div>
                
                <!-- Deck 2 -->
                <div class="deck">
                    <h2>DECK 2</h2>
                    <div class="controls">
                        <button onclick="playTrack('deck2')">▶ Play</button>
                        <button onclick="pauseTrack('deck2')">⏸ Pause</button>
                        <button onclick="stopTrack('deck2')">⏹ Stop</button>
                    </div>
                    <div class="slider-container">
                        <label>Volume: <span id="deck2VolumeValue">1.0</span></label>
                        <input type="range" id="deck2Volume" min="0" max="1" step="0.01" value="1.0"
                               oninput="setVolume('deck2', this.value)">
                    </div>
                    <div class="status" id="deck2Status">Status: Stopped</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('connect', () => {
            console.log('Connected to server');
            document.getElementById('connectionStatus').textContent = 'Connected';
            document.getElementById('connectionStatus').classList.remove('disconnected');
        });
        
        socket.on('disconnect', () => {
            console.log('Disconnected from server');
            document.getElementById('connectionStatus').textContent = 'Disconnected';
            document.getElementById('connectionStatus').classList.add('disconnected');
        });
        
        socket.on('status_update', (status) => {
            updateUI(status);
        });
        
        function updateUI(status) {
            // Update master volume
            document.getElementById('masterVolume').value = status.master_volume;
            document.getElementById('masterVolumeValue').textContent = status.master_volume.toFixed(2);
            
            // Update crossfader
            document.getElementById('crossfader').value = status.crossfader;
            document.getElementById('crossfaderValue').textContent = status.crossfader.toFixed(2);
            
            // Update deck statuses
            ['deck1', 'deck2'].forEach(deck => {
                if (status.tracks[deck]) {
                    const volume = status.tracks[deck].volume;
                    const playing = status.tracks[deck].playing;
                    
                    document.getElementById(deck + 'Volume').value = volume;
                    document.getElementById(deck + 'VolumeValue').textContent = volume.toFixed(2);
                    
                    const statusEl = document.getElementById(deck + 'Status');
                    statusEl.textContent = 'Status: ' + (playing ? 'Playing' : 'Stopped');
                    statusEl.className = 'status ' + (playing ? 'playing' : '');
                }
            });
        }
        
        async function initializeMixer() {
            const response = await fetch('/api/initialize', { method: 'POST' });
            const data = await response.json();
            console.log('Initialize:', data);
        }
        
        async function playTrack(deck) {
            const response = await fetch(`/api/play/${deck}`, { method: 'POST' });
            const data = await response.json();
            console.log('Play:', data);
        }
        
        async function pauseTrack(deck) {
            const response = await fetch(`/api/pause/${deck}`, { method: 'POST' });
            const data = await response.json();
            console.log('Pause:', data);
        }
        
        async function stopTrack(deck) {
            const response = await fetch(`/api/stop/${deck}`, { method: 'POST' });
            const data = await response.json();
            console.log('Stop:', data);
        }
        
        async function setVolume(deck, volume) {
            document.getElementById(deck + 'VolumeValue').textContent = parseFloat(volume).toFixed(2);
            const response = await fetch(`/api/volume/${deck}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ volume: parseFloat(volume) })
            });
        }
        
        async function setCrossfader(position) {
            document.getElementById('crossfaderValue').textContent = parseFloat(position).toFixed(2);
            const response = await fetch('/api/crossfader', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position: parseFloat(position) })
            });
        }
        
        async function applyCrossfader() {
            const response = await fetch('/api/crossfader/apply', { method: 'POST' });
            const data = await response.json();
            console.log('Apply crossfader:', data);
        }
        
        async function setMasterVolume(volume) {
            document.getElementById('masterVolumeValue').textContent = parseFloat(volume).toFixed(2);
            const response = await fetch('/api/master-volume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ volume: parseFloat(volume) })
            });
        }
        
        // Request status updates
        setInterval(() => {
            socket.emit('request_status');
        }, 1000);
    </script>
</body>
</html>"""
    
    with open(templates_dir / 'index.html', 'w') as f:
        f.write(index_html)
    
    print("Web templates created successfully!")
    return True


if __name__ == "__main__":
    # Create web templates
    create_web_templates()
    
    print("\nWeb templates created!")
    print("To start the web server, use:")
    print("  from web_interface import DJMixerWebServer")
    print("  from test_mixer import MockDJMixer")
    print("  mixer = MockDJMixer()")
    print("  server = DJMixerWebServer(mixer)")
    print("  server.start()")
