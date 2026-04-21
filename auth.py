from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import jwt
import datetime
import os

SECRET_KEY = "LcyJcNSTfX(46a=6Ad@Y0.!U!O<i0L@t"

USERS = {
    "admin": "admin2026",
    "demo": "demo2026"
}

def create_token(username):
    payload = {
        "user": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user"]
    except:
        return None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path == "/auth/login":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            username = body.get("username", "")
            password = body.get("password", "")
            if USERS.get(username) == password:
                token = create_token(username)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "token": token,
                    "user": username
                }).encode())
            else:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Ungültige Zugangsdaten"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/auth/verify":
            token = self.headers.get("Authorization", "").replace("Bearer ", "")
            user = verify_token(token)
            if user:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"user": user}).encode())
            else:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Ungültiger Token"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

HTTPServer(("127.0.0.1", 5002), Handler).serve_forever()
