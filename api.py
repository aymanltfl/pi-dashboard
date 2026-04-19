from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os
import threading
import time
import urllib.request
import socket
from datetime import datetime

STROMPREIS = 0.30
IDLE_WATT = 3.0
MAX_WATT = 8.0
LOG_FILE = "/home/raspberrypi/Desktop/pi-dashboard/energy_log.json"

def get_power():
    load = float(subprocess.check_output(["cat", "/proc/loadavg"]).decode().split()[0])
    watt = IDLE_WATT + (min(load, 4.0) / 4.0) * (MAX_WATT - IDLE_WATT)
    return round(watt, 2)

def get_uptime_seconds():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {
        "total_wh": 0.0,
        "total_minutes": 0,
        "start_date": datetime.now().strftime("%d.%m.%Y")
    }

def save_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f)

def energy_tracker():
    while True:
        time.sleep(60)
        try:
            watt = get_power()
            log = load_log()
            log["total_wh"] += watt / 60
            log["total_minutes"] += 1
            save_log(log)
        except:
            pass

def check_http(url):
    try:
        start = time.time()
        req = urllib.request.urlopen(url, timeout=5)
        ms = round((time.time() - start) * 1000)
        return {"status": "online", "ms": ms, "code": req.getcode()}
    except:
        return {"status": "offline", "ms": None, "code": None}

def check_ping(host):
    try:
        start = time.time()
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 53))
        ms = round((time.time() - start) * 1000)
        return {"status": "online", "ms": ms}
    except:
        return {"status": "offline", "ms": None}

def check_systemd(service):
    try:
        result = subprocess.check_output(
            ["systemctl", "is-active", service]
        ).decode().strip()
        return {"status": "online" if result == "active" else "offline"}
    except:
        return {"status": "offline"}

def check_ssl():
    try:
        result = subprocess.check_output(
            ["certbot", "certificates"],
            stderr=subprocess.STDOUT
        ).decode()
        if "2026" in result or "2027" in result:
            for line in result.split("\n"):
                if "Expiry Date" in line:
                    return {"status": "online", "info": line.strip().replace("Expiry Date: ", "")}
        return {"status": "online", "info": "gültig"}
    except:
        return {"status": "online", "info": "gültig"}

tracker = threading.Thread(target=energy_tracker, daemon=True)
tracker.start()

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
                seconds = int(get_uptime_seconds())
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

        elif self.path == "/api/energy_total":
            try:
                log = load_log()
                total_kwh = round(log["total_wh"] / 1000, 4)
                total_cost = round(total_kwh * STROMPREIS, 4)
                total_co2 = round(total_kwh * 0.4, 4)
                total_mins = log["total_minutes"]
                days = total_mins // 1440
                hours = (total_mins % 1440) // 60
                minutes = total_mins % 60
                runtime = f"{days:02d}:{hours:02d}:{minutes:02d}"
                data = {
                    "runtime": runtime,
                    "total_kwh": total_kwh,
                    "total_cost": total_cost,
                    "total_co2": total_co2,
                    "start_date": log["start_date"]
                }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path == "/api/monitor":
            try:
                services = [
                    {"name": "Website", "type": "http", "target": "https://aymanel-pi.duckdns.org"},
                    {"name": "Internet", "type": "http", "target": "https://google.com"},
                    {"name": "DNS (1.1.1.1)", "type": "ping", "target": "1.1.1.1"},
                    {"name": "nginx", "type": "systemd", "target": "nginx"},
                    {"name": "pi-api", "type": "systemd", "target": "pi-api"},
                    {"name": "pi-helpdesk", "type": "systemd", "target": "pi-helpdesk"},
                    {"name": "SSL Zertifikat", "type": "ssl", "target": "certbot"},
                ]
                results = []
                for s in services:
                    if s["type"] == "http":
                        result = check_http(s["target"])
                    elif s["type"] == "ping":
                        result = check_ping(s["target"])
                    elif s["type"] == "systemd":
                        result = check_systemd(s["target"])
                    elif s["type"] == "ssl":
                        result = check_ssl()
                    results.append({
                        "name": s["name"],
                        **result
                    })
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"services": results}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
