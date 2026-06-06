from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os
import threading
import time
import urllib.request
import socket
from datetime import datetime
import re
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv("/home/raspberrypi/Desktop/pi-dashboard/.env")

STROMPREIS = 0.30
IDLE_WATT = 3.0
MAX_WATT = 8.0
LOG_FILE = "/home/raspberrypi/Desktop/pi-dashboard/energy_log.json"

FRITZ_URL  = os.getenv("FRITZ_URL", "http://192.168.178.1:49000")
FRITZ_USER = os.getenv("FRITZ_USER")
FRITZ_PASS = os.getenv("FRITZ_PASS")

network_cache = {"devices": [], "device_count": 0, "services": {}}
network_cache_lock = threading.Lock()

def fritz_call(action, body):
    url = f"{FRITZ_URL}/upnp/control/hosts"
    headers = {
        "Content-Type": 'text/xml; charset="utf-8"',
        "SOAPACTION": action
    }
    try:
        r = requests.post(url, data=body, headers=headers,
                          auth=(FRITZ_USER, FRITZ_PASS), timeout=5)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("fritz_call error:", e)
        return None

def get_services():
    services = {}
    for svc in ["nginx", "pi-api", "pi-helpdesk", "pi-auth", "pihole-FTL"]:
        try:
            out = subprocess.check_output(
                ["systemctl", "is-active", svc],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            services[svc] = out == "active"
        except:
            services[svc] = False
    return services

def update_network_cache():
    while True:
        try:
            xml_count = fritz_call(
                "urn:dslforum-org:service:Hosts:1#GetHostNumberOfEntries",
                """<?xml version="1.0"?>
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                  <s:Body>
                    <u:GetHostNumberOfEntries xmlns:u="urn:dslforum-org:service:Hosts:1"/>
                  </s:Body>
                </s:Envelope>"""
            )
            if not xml_count:
                time.sleep(120)
                continue

            root = ET.fromstring(xml_count)
            node = root.find(".//NewHostNumberOfEntries")
            count = int(node.text) if node is not None and node.text else 0

            devices = []
            for i in range(count):
                xml = fritz_call(
                    "urn:dslforum-org:service:Hosts:1#GetGenericHostEntry",
                    f"""<?xml version="1.0"?>
                    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                      <s:Body>
                        <u:GetGenericHostEntry xmlns:u="urn:dslforum-org:service:Hosts:1">
                          <NewIndex>{i}</NewIndex>
                        </u:GetGenericHostEntry>
                      </s:Body>
                    </s:Envelope>"""
                )
                if not xml:
                    continue
                r = ET.fromstring(xml)
                active = r.findtext(".//NewActive")
                if active not in ("1", "true"):
                    continue
                devices.append({
                    "ip":       r.findtext(".//NewIPAddress") or "",
                    "mac":      (r.findtext(".//NewMACAddress") or "").lower(),
                    "hostname": r.findtext(".//NewHostName") or ""
                })

            services = get_services()

            with network_cache_lock:
                network_cache["devices"]      = devices
                network_cache["device_count"] = len(devices)
                network_cache["services"]     = services

        except Exception as e:
            print("network error:", e)

        time.sleep(120)

network_thread = threading.Thread(target=update_network_cache, daemon=True)
network_thread.start()

def get_power():
    try:
        load = float(subprocess.check_output(["cat", "/proc/loadavg"]).decode().split()[0])
        temp_str = subprocess.check_output(["vcgencmd", "measure_temp"]).decode().strip().replace("temp=", "").replace("'C", "")
        temp = float(temp_str)
        mem = subprocess.check_output(["free", "-m"]).decode().split("\n")[1].split()
        ram_used = int(mem[2])
        ram_total = int(mem[1])
        ram_usage = ram_used / ram_total
        cpu_factor = min(load / 4.0, 1.0)
        temp_factor = min((temp - 40) / 40, 1.0)
        ram_factor = ram_usage
        usage = (cpu_factor * 0.5) + (temp_factor * 0.3) + (ram_factor * 0.2)
        watt = IDLE_WATT + usage * (MAX_WATT - IDLE_WATT)
        return round(watt, 2)
    except:
        return IDLE_WATT

def get_uptime_seconds():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"total_wh": 0.0, "total_minutes": 0, "start_date": datetime.now().strftime("%d.%m.%Y")}

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

tracker = threading.Thread(target=energy_tracker, daemon=True)
tracker.start()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/status":
            try:
                temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode().strip().replace("temp=", "").replace("'C", "")
                load = subprocess.check_output(["cat", "/proc/loadavg"]).decode().split()[0]
                mem = subprocess.check_output(["free", "-m"]).decode().split("\n")[1].split()
                data = {"temp": float(temp), "cpu_load": float(load), "ram_used": int(mem[2]), "ram_total": int(mem[1])}
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
                data = {"watt": watt, "cost_per_day": cost_per_day, "cost_per_month": cost_per_month, "co2_per_day": co2_per_day}
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
                data = {"runtime": runtime, "total_kwh": total_kwh, "total_cost": total_cost, "total_co2": total_co2, "start_date": log["start_date"]}
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path == "/api/network":
            try:
                with network_cache_lock:
                    data = {
                        "devices":      list(network_cache["devices"]),
                        "device_count": network_cache["device_count"],
                        "services":     dict(network_cache["services"])
                    }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(("127.0.0.1", 5000), Handler).serve_forever()