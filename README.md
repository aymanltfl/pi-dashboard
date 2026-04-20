# Raspberry Pi Home Server Dashboard

Persönliches Heimserver-Projekt auf Basis eines Raspberry Pi 4 unter Linux (Raspberry Pi OS).
Öffentlich erreichbar unter: https://aymanel-pi.duckdns.org

---

## Projektübersicht

Dieses Projekt dokumentiert den Aufbau und Betrieb eines vollständigen Heimservers - von der Netzwerkkonfiguration über die API-Entwicklung bis hin zur KI-Integration und Service-Monitoring.

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
- Gesprächsgedächtnis implementiert
- Python Backend + REST API (/api/chat)
- Floating Chat-Widget auf der Website

### Projekt 4 - Service Monitor
- Automatische Überwachung von Services alle 30 Sekunden
- HTTP-Check für externe Dienste (Website, Internet)
- DNS-Erreichbarkeit prüfen
- systemd-Services live überwachen
- SSL-Zertifikat Gültigkeit prüfen
- Antwortzeiten in Millisekunden messen

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

Internet --> DuckDNS (aymanel-pi.duckdns.org) --> Fritz!Box 7560 (Port 443/80) --> Raspberry Pi 4

Raspberry Pi 4:
- nginx (einziger oeffentlicher Entry Point, Port 443/80)
  - / --> index.html
  - /api/status --> Python API (nur localhost)
  - /api/uptime --> Python API (nur localhost)
  - /api/power --> Python API (nur localhost)
  - /api/energy_total --> Python API (nur localhost)
  - /api/monitor --> Python API (nur localhost)
  - /api/chat --> Helpdesk Bot (nur localhost)
- APIs binden nur auf 127.0.0.1 - nicht direkt aus dem Internet erreichbar
- Tailscale VPN (Remote SSH Zugriff von überall ohne Portfreigabe)
- DuckDNS Cronjob (IP-Update alle 5 Minuten)

---

## Sicherheit

- nginx als einziger oeffentlicher Entry Point
- APIs nur auf localhost gebunden (127.0.0.1) - kein direkter Internetzugriff
- UFW Firewall - nur Port 80, 443 und 22 offen
- Fail2ban - automatische IP-Sperrung bei Brute-Force
- SSL/TLS mit Let's Encrypt - automatische Erneuerung
- Tailscale VPN fuer sicheren Remote-Zugriff ohne offenen SSH-Port im Router

---

## Projektstruktur

pi-dashboard/
- api.py              (REST API: Status, Uptime, Power, Energy, Monitor)
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
