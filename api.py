from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/status":
            try:
                temp = subprocess.check_output(
                    ["vcgencmd", "measure_temp"]
                ).decode().strip().replace("temp=", "").replace("'C", "")
                load = subprocess.check_output(
                    ["cat", "/proc/loadavg"]
                ).decode().split()[0]
                mem = subprocess.check_output(
                    ["free", "-m"]
                ).decode().split("\n")[1].split()
                data = {
                    "temp": float(temp),
                    "cpu_load": float(load),
                    "ram_used": int(mem[2]),
                    "ram_total": int(mem[1])
                }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path == "/api/uptime":
            try:
                uptime = subprocess.check_output(
                    ["uptime", "-p"]
                ).decode().strip().replace("up ", "")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"uptime": uptime}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
