# Raspberry Pi Home Server Dashboard

Persönliches Heimserver-Projekt auf Basis eines Raspberry Pi 4 unter Linux (Raspberry Pi OS).
Öffentlich erreichbar unter: https://aymanel-pi.duckdns.org

---

## Projektübersicht

Dieses Projekt dokumentiert den Aufbau und Betrieb eines vollständigen Heimservers - von der Netzwerkkonfiguration über die API-Entwicklung bis hin zur KI-Integration.

---

## Projekte

### Projekt 1 - Raspberry Pi Heimserver
- nginx als Webserver und Reverse Proxy konfiguriert
- Python REST-API entwickelt (CPU, RAM, Temperatur, Uptime)
- DuckDNS für dynamisches DNS eingerichtet (Cronjob alle 5 Min.)
- Portweiterleitung über Fritz!Box 7560
- SSL-Zertifikat mit Let's Encrypt (HTTPS)
- Firewall mit UFW konfiguriert
- Fail2ban für SSH-Schutz eingerichtet
- Alle Dienste als systemd-Services (Autostart)

### Projekt 2 - Energie-Monitoring
- Stromverbrauch-Schätzung basierend auf CPU Last
- Kostenberechnung (0,30 Euro/kWh)
- CO2-Emissionen basierend auf deutschem Strommix
- Gesamtstatistik persistent in energy_log.json gespeichert
- REST API Endpunkt /api/energy_total

### Projekt 3 - IT-Helpdesk Bot
- KI-Chatbot mit Groq API (LLaMA 3)
- Beantwortet IT-Fragen automatisch auf Deutsch
- Python Backend + REST API (/api/chat)
- Chat-Interface direkt auf der Website

---

## Technologien

| Bereich | Tools |
|---|---|
| Hardware | Raspberry Pi 4 (2GB RAM) |
| Betriebssystem | Raspberry Pi OS (Debian Trixie) |
| Webserver | nginx |
| Backend | Python 3 |
| DNS | DuckDNS |
| Security | UFW, Fail2ban, Let's Encrypt |
| Remote Access | Tailscale VPN |
| KI | Groq API, LLaMA 3 |
| Versionskontrolle | Git, GitHub |
| Prozessmanagement | systemd |

---

## Architektur

Internet --> DuckDNS (aymanel-pi.duckdns.org) --> Fritz!Box 7560 (Port 80/443) --> Raspberry Pi 4

Raspberry Pi 4:
- nginx (Reverse Proxy)
  - / --> index.html
  - /api/status --> Python API (Port 5000)
  - /api/uptime --> Python API (Port 5000)
  - /api/power --> Python API (Port 5000)
  - /api/energy_total --> Python API (Port 5000)
  - /api/chat --> Helpdesk Bot (Port 5001)
- Tailscale VPN (Remote SSH Zugriff von überall)
- DuckDNS Cronjob (IP-Update alle 5 Minuten)

---

## Projektstruktur

pi-dashboard/
- api.py              (REST API: Status, Uptime, Power, Energy)
- helpdesk.py         (IT-Helpdesk Bot via Groq API)
- energy_log.json     (Persistente Energiedaten)
- duckdns/update.sh   (DuckDNS IP-Update Script)
- web/index.html      (Frontend Dashboard)

---

## Autor

Ayman El-Toufaili
Umschüler zum IT-Systemelektroniker | COMCAVE.COLLEGE Essen
Praktikum ab September 2026 - Helpdesk, Netzwerktechnik, Systemadministration

Gehostet auf eigenem Raspberry Pi - Marl, NRW
