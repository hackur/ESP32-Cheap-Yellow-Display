"""
CYD Stopwatch - Web Monitor (Optional Feature)
==============================================

This optional module provides a simple web interface to monitor
the stopwatch remotely via WiFi. Include this file if you want
remote monitoring capabilities.

Note: This requires WiFi configuration and will use additional memory.
"""

try:
    import network
    import socket
    import json
    import time
    from machine import unique_id
    import ubinascii
except ImportError:
    # Stub for development
    pass

class WebMonitor:
    def __init__(self, stopwatch_app, ssid=None, password=None):
        self.app = stopwatch_app
        self.ssid = ssid
        self.password = password
        self.socket = None
        self.connected = False
        self.server_running = False

    def connect_wifi(self, ssid=None, password=None):
        """Connect to WiFi network"""
        if ssid:
            self.ssid = ssid
        if password:
            self.password = password

        if not self.ssid or not self.password:
            print("WiFi credentials not provided")
            return False

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if wlan.isconnected():
            print(f"Already connected to WiFi: {wlan.ifconfig()[0]}")
            self.connected = True
            return True

        print(f"Connecting to WiFi: {self.ssid}")
        wlan.connect(self.ssid, self.password)

        # Wait for connection
        timeout = 10
        while timeout > 0 and not wlan.isconnected():
            time.sleep(1)
            timeout -= 1
            print(".", end="")

        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f"\nConnected! IP: {ip}")
            self.connected = True
            return True
        else:
            print("\nFailed to connect to WiFi")
            return False

    def start_server(self, port=80):
        """Start web server"""
        if not self.connected:
            print("Not connected to WiFi")
            return False

        try:
            self.socket = socket.socket()
            self.socket.bind(('', port))
            self.socket.listen(1)
            self.server_running = True

            wlan = network.WLAN(network.STA_IF)
            ip = wlan.ifconfig()[0]
            print(f"Web server started at http://{ip}:{port}")
            return True

        except Exception as e:
            print(f"Failed to start server: {e}")
            return False

    def generate_html(self):
        """Generate HTML page for stopwatch status"""
        stats = self.app.stopwatch.get_session_stats()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CYD Stopwatch Monitor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .title {{
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .time-display {{
            font-size: 4em;
            text-align: center;
            font-family: 'Courier New', monospace;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
        .status {{
            text-align: center;
            font-size: 1.5em;
            margin: 20px 0;
        }}
        .status.running {{ color: #4CAF50; }}
        .status.stopped {{ color: #f44336; }}
        .status.ready {{ color: #2196F3; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-box {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .refresh {{
            text-align: center;
            margin: 20px 0;
        }}
        .refresh a {{
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
        }}
        .device-info {{
            text-align: center;
            font-size: 0.8em;
            opacity: 0.7;
            margin-top: 30px;
        }}
    </style>
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1 class="title">🎯 CYD Stopwatch Monitor</h1>

        <div class="time-display">{stats['formatted']}</div>

        <div class="status {'running' if stats['is_running'] else 'ready' if stats['total_ms'] == 0 else 'stopped'}">
            {'🟢 RUNNING' if stats['is_running'] else '🔵 READY' if stats['total_ms'] == 0 else '🔴 STOPPED'}
        </div>

        <div class="stats">
            <div class="stat-box">
                <div class="stat-label">Total Milliseconds</div>
                <div class="stat-value">{stats['total_ms']:,}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Hours</div>
                <div class="stat-value">{stats['hours']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Minutes</div>
                <div class="stat-value">{stats['minutes']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Seconds</div>
                <div class="stat-value">{stats['seconds']}</div>
            </div>
        </div>

        <div class="refresh">
            <a href="/">🔄 Refresh</a>
            <a href="/api">📊 JSON API</a>
        </div>

        <div class="device-info">
            CYD Stopwatch Device<br>
            Last updated: {time.time()}<br>
            Auto-refresh in 5 seconds
        </div>
    </div>
</body>
</html>
"""
        return html

    def handle_request(self, conn):
        """Handle incoming HTTP request"""
        try:
            request = conn.recv(1024).decode()

            # Parse request
            if 'GET /' in request:
                if '/api' in request:
                    # JSON API response
                    stats = self.app.stopwatch.get_session_stats()
                    response_data = json.dumps(stats)
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_data}"
                else:
                    # HTML response
                    html = self.generate_html()
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"

            conn.send(response.encode())

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            conn.close()

    def run_server(self):
        """Run the web server (blocking)"""
        if not self.server_running:
            print("Server not started")
            return

        print("Web server running... (Ctrl+C to stop)")
        try:
            while True:
                conn, addr = self.socket.accept()
                self.handle_request(conn)
        except KeyboardInterrupt:
            print("\nWeb server stopped")
        finally:
            self.stop_server()

    def stop_server(self):
        """Stop the web server"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.server_running = False
        print("Web server stopped")

# Example usage (add to main.py if desired):
"""
# In main.py, after creating StopwatchApp:
if config.WEB_MONITOR_ENABLED:
    web_monitor = WebMonitor(app, ssid="YourWiFi", password="YourPassword")
    if web_monitor.connect_wifi():
        web_monitor.start_server()
        # Run server in background or separate thread
"""
