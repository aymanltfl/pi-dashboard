from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Du bist ein freundlicher IT-Helpdesk Assistent.
Du hilfst Benutzern bei IT-Problemen wie WLAN, Drucker, Passwörter,
Windows, Software Installation und allgemeinen Computer-Problemen.
Antworte immer auf Deutsch, kurz und verständlich.
Wenn du etwas nicht weißt, sage es ehrlich."""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            history = body.get("messages", [])
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                reply = response.choices[0].message.content
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

HTTPServer(("0.0.0.0", 5001), Handler).serve_forever()
