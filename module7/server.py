#!/usr/bin/env python3
"""
Simple HTTP server for container lifecycle demonstration.
Logs every request to stdout so they appear in docker logs.
"""

import http.server
import signal
import sys

class LoggingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests and respond with a simple message."""
        print(f"[REQUEST] {self.command} {self.path} from {self.client_address[0]}", flush=True)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello from container!\n")

    def log_message(self, format, *args):
        """Override default logger to write to stdout (captured by docker logs)."""
        print(f"[HTTP] {self.address_string()} - {format % args}", flush=True)

def handle_sigterm(signum, frame):
    """
    Graceful shutdown on SIGTERM.
    Docker sends SIGTERM on 'docker stop'; we catch it and exit cleanly.
    """
    print("[SIGNAL] Received SIGTERM — shutting down gracefully", flush=True)
    sys.exit(0)

# Register SIGTERM handler
signal.signal(signal.SIGTERM, handle_sigterm)

PORT = 8080
print(f"[START] Server listening on port {PORT}", flush=True)

with http.server.HTTPServer(("", PORT), LoggingHandler) as httpd:
    httpd.serve_forever()
