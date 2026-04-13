from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

STROMPREIS = 0.30
IDLE_WATT = 3.0
MAX_WATT = 8.0

def get_power():
    load = float(subprocess.check_output(["cat", "/proc/loadavg"]).decode().split()[0])
    watt = IDLE_WATT + (min(load, 4.0) / 4.0) * (MAX_WATT - IDLE_WATT)
    return round(watt, 2)

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
                with open("/proc/uptime") as f:
                    seconds = int(float(f.read().split()[0]))
                days = seconds // 86400
                hours = (seconds % 86400) // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                uptime = f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"uptime": uptime}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path == "/api/power":
            try:
                watt = get_power()
                kwh_per_day = (watt * 24) / 1000
                kwh_per_month = kwh_per_day * 30
                cost_per_day = round(kwh_per_day * STROMPREIS, 4)
                cost_per_month = round(kwh_per_month * STROMPREIS, 2)
                co2_per_day = round(kwh_per_day * 0.4, 4)
                data = {
                    "watt": watt,
                    "cost_per_day": cost_per_day,
                    "cost_per_month": cost_per_month,
                    "co2_per_day": co2_per_day
                }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
