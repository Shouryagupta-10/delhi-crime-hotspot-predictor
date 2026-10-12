"""
Rakshak.ai Emergency SOS Alert Dedicated API Server
Provides high-availability endpoints for SOS distress telemetry, SMS gateway dispatch,
and mobile push notification routing on port 4021.
Runs standalone or as a background daemon thread alongside Streamlit.
"""

import os
import sys
import json
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Add base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
for p in [BASE_DIR, PROJECT_ROOT]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

try:
    from models.sos_dispatcher import EmergencySOSDispatcher
except ImportError:
    from backend.models.sos_dispatcher import EmergencySOSDispatcher


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class SOSRequestHandler(BaseHTTPRequestHandler):
    dispatcher = EmergencySOSDispatcher()

    def _set_cors_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path in ("/health", "/api/health"):
            self._set_cors_headers(200)
            resp = {
                "status": "ONLINE",
                "service": "Rakshak.ai SOS Dispatch Server",
                "active_gateways": {
                    "twilio": bool(self.dispatcher.twilio_sid and self.dispatcher.twilio_token),
                    "fast2sms": bool(self.dispatcher.fast2sms_key),
                    "msg91": bool(self.dispatcher.msg91_key),
                    "webhook": bool(self.dispatcher.webhook_url),
                    "ntfy_push": True
                }
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if path in ("/api/send-sos", "/api/v1/sos-alert"):
            # Handle query params if any
            params = urllib.parse.parse_qs(parsed.query)
            phone = params.get("phone", ["112"])[0]
            name = params.get("name", ["Emergency Contact"])[0]
            lat = float(params.get("lat", [28.6328])[0])
            lon = float(params.get("lon", [77.2197])[0])
            
            payload = self.dispatcher.build_sos_payload(
                lat=lat,
                lon=lon,
                recipient_name=name,
                recipient_phone=phone
            )
            result = self.dispatcher.dispatch_alert(payload)
            self._set_cors_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        self._set_cors_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path not in ("/api/send-sos", "/api/v1/sos-alert"):
            self._set_cors_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))
            return

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        
        try:
            data = json.loads(post_body.decode("utf-8"))
        except Exception:
            data = {}

        recipient = data.get("recipient", {})
        loc = data.get("location", {})
        
        rec_name = recipient.get("name", "Primary Emergency Contact")
        rec_phone = recipient.get("phone", "112")
        lat = float(loc.get("latitude", 28.6328))
        lon = float(loc.get("longitude", 77.2197))
        custom_msg = data.get("message")
        
        # Check if client passed temporary/saved gateway credentials
        gateway_config = data.get("gateway_config", {})
        if gateway_config.get("fast2sms_key"):
            self.dispatcher.fast2sms_key = gateway_config["fast2sms_key"]
        if gateway_config.get("twilio_sid"):
            self.dispatcher.twilio_sid = gateway_config["twilio_sid"]
            self.dispatcher.twilio_token = gateway_config.get("twilio_token", "")
            self.dispatcher.twilio_from = gateway_config.get("twilio_from", "")
        if gateway_config.get("webhook_url"):
            self.dispatcher.webhook_url = gateway_config["webhook_url"]

        payload = self.dispatcher.build_sos_payload(
            lat=lat,
            lon=lon,
            recipient_name=rec_name,
            recipient_phone=rec_phone,
            custom_message=custom_msg
        )

        result = self.dispatcher.dispatch_alert(payload)
        
        # Generate deep links for immediate mobile SMS and WhatsApp
        clean_phone = "".join(ch for ch in rec_phone if ch.isdigit())
        if len(clean_phone) > 10:
            clean_phone = clean_phone[-10:]
        
        urgent_text = payload["message"]
        encoded_msg = urllib.parse.quote(urgent_text)
        
        result["native_sms_url"] = f"sms:{rec_phone}?body={encoded_msg}"
        result["whatsapp_url"] = f"https://api.whatsapp.com/send?phone=91{clean_phone}&text={encoded_msg}"
        result["ntfy_topic_url"] = f"https://ntfy.sh/rakshak_sos_{clean_phone}"

        self._set_cors_headers(200)
        self.wfile.write(json.dumps(result, indent=2).encode("utf-8"))

    def log_message(self, format, *args):
        # Clean custom logger
        sys.stderr.write(f"[SOS-API-SERVER] {self.address_string()} - {format % args}\n")


_SERVER_INSTANCE = None
_SERVER_THREAD = None


def start_sos_api_server_background(port: int = 4021) -> bool:
    """
    Starts the SOS API server in a daemon thread if not already running.
    Returns True if started or already running, False if error.
    """
    global _SERVER_INSTANCE, _SERVER_THREAD
    if _SERVER_INSTANCE is not None:
        return True

    # Test if port is already open
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex(("127.0.0.1", port)) == 0:
            print(f"[SOS-API] Port {port} is already active.")
            return True

    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), SOSRequestHandler)
        _SERVER_INSTANCE = server
        thread = threading.Thread(target=server.serve_forever, daemon=True, name="SOS-API-Daemon")
        _SERVER_THREAD = thread
        thread.start()
        print(f"[SOS-API] Emergency SOS Server listening in background on http://127.0.0.1:{port}")
        return True
    except Exception as e:
        print(f"[SOS-API] Failed to start SOS server on port {port}: {e}")
        return False


if __name__ == "__main__":
    port = int(os.getenv("PORT", "4021"))
    print(f"Starting Rakshak.ai Emergency SOS Dispatch Server on port {port}...")
    server = ThreadingHTTPServer(("0.0.0.0", port), SOSRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SOS Server.")
        server.shutdown()
