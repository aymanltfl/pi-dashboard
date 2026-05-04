# Raspberry Pi Home Server Dashboard

Persönliches Heimserver-Projekt auf Basis eines Raspberry Pi 4 unter Linux (Raspberry Pi OS).

Live erreichbar unter:
https://ayman-eltoufaili.de/

Demo-Zugang:
- Benutzer: demo
- Passwort: demo2026

---

## Projektübersicht

Dieses Projekt dokumentiert den Aufbau und Betrieb eines vollständigen Heimservers - von der Netzwerkkonfiguration über die API-Entwicklung bis hin zur KI-Integration, Authentifizierung, netzwerkweitem Werbeblocker und Container-basiertem Monitoring.

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

### Projekt 4 - JWT Authentifizierung
- Eigenes JWT-basiertes Authentifizierungssystem
- Python Auth-Service (nur localhost)
- Zwei Benutzerrollen: Admin und Demo
- Login-Seite im Dashboard-Design
- Token-Verifizierung bei jedem Seitenaufruf
- Logout-Funktion mit Token-Löschung

### Projekt 5 - Pi-hole Netzwerk-Werbeblocker
- Pi-hole auf Raspberry Pi installiert und konfiguriert
- DNS-Filter für das gesamte Heimnetz (Laptops, Smartphones, Smart-TVs)
- Port-Konflikt mit nginx gelöst - Pi-hole FTL auf Port 8080
- UFW Firewall für Port 53 und 8080 im Heimnetz konfiguriert
- Fritz!Box DNS auf Pi-hole umgestellt mit automatischem Fallback
- DNS-Rebind-Schutz für eigene Domain eingetragen
- Über 242.000 Domains auf der Blockliste
- Pi-hole API über nginx Reverse Proxy erreichbar
- Live-Stats Card im Dashboard integriert

### Projekt 6 - Uptime Monitoring mit Docker
- Erstes Docker-Projekt auf Raspberry Pi 4 (ARM64)
- Uptime Kuma als Docker Container deployed
- Persistentes Volume für Datenspeicherung eingerichtet
- 4 Monitore konfiguriert: Website, Internet, Pi-hole DNS, pi-api
- nginx Reverse Proxy für Uptime Kuma API konfiguriert
- Live Status Card im Dashboard integriert
- Container startet automatisch nach Neustart (--restart always)

---

## Technologien

| Bereich | Tools |
|---|---|
| Hardware | Raspberry Pi 4 (2GB RAM) |
| Betriebssystem | Raspberry Pi OS (Debian Trixie) |
| Webserver | nginx |
| Backend | Python 3 |
| DNS | DuckDNS, Pi-hole |
| Security | UFW, Fail2ban, Let's Encrypt, JWT, Tailscale |
| Remote Access | Tailscale VPN |
| KI | Groq API, LLaMA 3 |
| Container | Docker, Uptime Kuma |
| Versionskontrolle | Git, GitHub |
| Prozessmanagement | systemd |

---

## Architektur

Internet --> DuckDNS (aymanel-pi.duckdns.org) --> Fritz!Box 7560 (Port 443/80) --> Raspberry Pi 4

Raspberry Pi 4:
- nginx (einziger oeffentlicher Entry Point, Port 443/80)
  - / --> index.html (Login-geschuetzt)
  - /login.html --> Login-Seite
  - /auth/ --> Auth Service (nur localhost, Port 5002)
  - /api/status --> Python API (nur localhost, Port 5000)
  - /api/uptime --> Python API (nur localhost, Port 5000)
  - /api/power --> Python API (nur localhost, Port 5000)
  - /api/energy_total --> Python API (nur localhost, Port 5000)
  - /api/chat --> Helpdesk Bot (nur localhost, Port 5001)
  - /pihole-api/ --> Pi-hole API (Port 8080)
  - /uptime-api/ --> Uptime Kuma API (Docker, Port 3001)
- Pi-hole FTL (DNS-Filter, Port 53 + 8080, nur Heimnetz)
- Docker Container: Uptime Kuma (Port 3001, nur localhost)
- Alle APIs binden nur auf 127.0.0.1 - kein direkter Internetzugriff
- Tailscale VPN fuer sicheren SSH-Zugriff (Port 22 nur ueber Tailscale)
- DuckDNS Cronjob (IP-Update alle 5 Minuten)

---

## Sicherheit

- nginx als einziger oeffentlicher Entry Point
- Alle APIs nur auf localhost gebunden (127.0.0.1)
- JWT-Authentifizierung schuetzt das komplette Dashboard
- UFW Firewall - nur Port 80/443 oeffentlich
- Port 53/8080 nur Heimnetz, Port 3001 nur Docker-intern
- SSH nur ueber Tailscale VPN erreichbar
- Fail2ban - automatische IP-Sperrung bei Brute-Force
- SSL/TLS mit Let's Encrypt - automatische Erneuerung
- Pi-hole - DNS-basierter Schutz vor Tracking und Werbung

---

## Dashboard Features

- Dark Mode + Light Mode Toggle
- Deutsch / Englisch Sprachumschaltung
- Live System-Daten (CPU, RAM, Temperatur, Uptime)
- Energie-Gesamtstatistik seit Inbetriebnahme
- Pi-hole Live-Stats (Anfragen, Blockrate, Clients)
- Uptime Monitoring Status Card (Uptime Kuma)
- Projekt-Portfolio mit Beschreibungen
- IT-Helpdesk Bot (Floating Chat Widget)
- Lebenslauf Download
- Mobile-optimiert

---

## Autor

Ayman El-Toufaili
Umschüler zum IT-Systemelektroniker
Praktikum ab September 2026 - Helpdesk, Netzwerktechnik, Systemadministration

Gehostet auf eigenem Raspberry Pi 4 - Marl, NRW
