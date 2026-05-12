# Raspberry Pi Home Server Dashboard

Persönliches Heimserver-Projekt auf Basis eines Raspberry Pi 4 unter Linux (Raspberry Pi OS).

Live erreichbar unter:

https://ayman-eltoufaili.de/

Demo-Zugang:
- Benutzer: demo
- Passwort: demo2026

---

## Projektübersicht

Dieses Projekt dokumentiert den Aufbau und Betrieb eines vollständigen Heimservers – von Netzwerkkonfiguration, API-Entwicklung, Security-Setup, Monitoring, KI-Integration bis hin zu Containerisierung und Visualisierung.

Der Fokus liegt auf einer realistischen Home-Lab Infrastruktur mit IT-typischen Komponenten wie Reverse Proxy, DNS-Filtering, Auth-Systemen, Monitoring und Automatisierung.

---

## Projekte

### Projekt 1 - Raspberry Pi Heimserver

- Aufbau eines vollständigen Linux-Servers auf Raspberry Pi 4
- nginx als Webserver und Reverse Proxy konfiguriert
- Python REST-API entwickelt (CPU, RAM, Temperatur, Uptime)
- Eigene Domain (ayman-eltoufaili.de) über Netcup angebunden
- Dynamische DNS / IP Aktualisierung automatisiert
- SSL-Zertifikate mit Let's Encrypt (HTTPS aktiv)
- Firewall mit UFW konfiguriert
- Fail2ban Schutz gegen Brute-Force Angriffe
- Alle Dienste als systemd Services mit Autostart

---

### Projekt 2 - Energie-Monitoring (Green IT)

- Live-Überwachung des Stromverbrauchs des Raspberry Pi Servers
- Realistische Verbrauchsschätzung mit Idle- und Max-Werten des Geräts
- Berechnung von Kosten basierend auf deutschem Strompreis (0,30 €/kWh)
- CO₂-Emissionen basierend auf deutschem Strommix (~0,4 kg/kWh)
- Persistente Speicherung der Verbrauchsdaten in energy_log.json
- REST API Endpunkt /api/energy_total für Gesamtstatistiken

---

### Projekt 3 - IT-Helpdesk Bot (KI Integration)

- KI-basierter Chatbot für IT-Support
- Nutzung der Groq API mit LLaMA 3 Modell
- Beantwortet IT-Fragen automatisch auf Deutsch
- Gesprächsgedächtnis für Kontext-Verständnis
- Python Backend mit REST API (/api/chat)
- Floating Chat Widget in Dashboard integriert

---

### Projekt 4 - JWT Authentifizierungssystem

- Eigenes Login-System mit JWT Tokens
- Python Auth-Service (nur localhost Zugriff)
- Zwei Benutzerrollen: Admin und Demo
- Token-basierte Session Verwaltung im Browser
- Schutz des gesamten Dashboards
- Logout durch Token Invalidierung

---

### Projekt 5 - Pi-hole Netzwerk-Werbeblocker

- Netzwerkweiter DNS-basierter Adblocker
- Pi-hole auf Raspberry Pi installiert und konfiguriert
- Filterung von Werbung und Tracking für alle Geräte im Heimnetz
- Fritz!Box DNS Umstellung auf Pi-hole
- Port-Konflikt mit nginx gelöst (Port 8080)
- Über 242.000 blockierte Domains
- Pi-hole API über nginx Reverse Proxy integriert
- Live Statistik im Dashboard

---

### Projekt 6 - Uptime Monitoring mit Docker

- Erstes Docker Projekt auf Raspberry Pi (ARM64)
- Uptime Kuma als Container deployed
- Persistente Datenhaltung via Docker Volumes
- Monitoring von Website, DNS, API und Internet
- nginx Reverse Proxy für Zugriff integriert
- Automatischer Restart bei Systemstart
- Live Status Anzeige im Dashboard

---

### Projekt 7 - Interaktive Netzwerk-Topologie (D3.js)

- Entwicklung einer Live Netzwerk Visualisierung mit D3.js
- Darstellung aller Home-Lab Komponenten als Graph
- Echtzeit Netzwerk-Topologie mit Force Simulation
- Integration von Live Daten aus /api/network
- Visualisierung von Clients, Servern, DNS und Cloud Services
- Tooltip-System mit dynamischen Gerätedaten
- Animationen für Netzwerkaktivität und Heartbeat
- Pi-hole DNS Events live dargestellt (geblockte Anfragen als rote Animation)

---

### Projekt 8 - Lerntagebuch & Telegram Notes Bot

- Persönlicher Telegram Bot als mobiles CMS für Lernnotizen
- Notizen und Fotos werden direkt per Telegram erfasst
- Groq API (LLaMA 3) verbessert Texte automatisch vor der Speicherung
- Persistente Speicherung aller Einträge in einer lokalen JSON-Datenbank
- Bildnotizen werden serverseitig gespeichert und in der Notes-Seite angezeigt
- Bot läuft als systemd Service mit Autostart
- Notes-Seite zeigt alle Einträge chronologisch als Karten-Layout
- Interne Zugriffspunkte, Bot-Tokens und Pfade werden bewusst nicht öffentlich dokumentiert

> **Sicherheitshinweis:** Bot-Token, interne Routen und Zugangsdaten sind nicht Teil dieser Dokumentation und werden nicht im Repository hinterlegt. Sensible Konfiguration erfolgt ausschließlich über Umgebungsvariablen (.env).

---

## Technologien

| Bereich | Tools |
|---|---|
| Hardware | Raspberry Pi 4 (2GB RAM) |
| Betriebssystem | Raspberry Pi OS (Debian) |
| Webserver | nginx |
| Backend | Python 3 |
| API | REST Architektur |
| DNS | Pi-hole, Netcup DNS |
| Security | UFW, Fail2ban, JWT, Let's Encrypt |
| Remote Access | Tailscale VPN |
| KI | Groq API, LLaMA 3 |
| Container | Docker, Uptime Kuma |
| Visualisierung | D3.js |
| Messaging | Telegram Bot API |
| Versionskontrolle | Git, GitHub |
| Automatisierung | systemd, Cronjobs |

---

## Architektur

Internet → Domain (ayman-eltoufaili.de) → Fritz!Box 7560 → Raspberry Pi 4 → nginx Reverse Proxy → interne Services

---

## Entry Point

- https://ayman-eltoufaili.de
- nginx als einziger öffentlicher Zugang (Port 80/443)

---

## Backend APIs (lokal gebunden)

- /api/status → Systemdaten (CPU, RAM, Temperatur)
- /api/uptime → Laufzeit & Service Status
- /api/power → Energieverbrauch Schätzung
- /api/energy_total → Gesamtenergie Statistik
- /api/chat → KI Helpdesk Bot
- /api/network → Netzwerk Topologie Daten

> Interne Datenpfade und Notes-Endpunkte werden bewusst nicht öffentlich dokumentiert.

---

## Sicherheit

- Alle Backend APIs nur auf 127.0.0.1 erreichbar
- nginx als einzig öffentlicher Entry Point
- JWT Auth schützt komplettes Dashboard
- UFW Firewall (nur 80/443 extern)
- SSH Zugriff nur über Tailscale VPN
- Fail2ban schützt vor Brute Force Angriffen
- HTTPS via Let's Encrypt
- Pi-hole filtert DNS Traffic im Heimnetz
- Sensible Zugangsdaten ausschließlich in .env (nicht im Repository)
- Interne Routen und Bot-Konfiguration nicht öffentlich dokumentiert

---

## Dashboard Features

- Dark Mode / Light Mode
- Deutsch / Englisch Sprachumschaltung
- Live System Monitoring (CPU, RAM, Temperatur)
- Energieverbrauch & Kosten Tracking
- Pi-hole Live Statistik
- Uptime Monitoring Dashboard
- Interaktive Netzwerk-Topologie (D3.js)
- KI Helpdesk Chatbot
- Lerntagebuch (Notes-Seite)
- Mobile optimiertes UI

---

## Infrastruktur

- Raspberry Pi 4 Home Server
- nginx Reverse Proxy Architektur
- Docker Container für Monitoring
- systemd für Service Management (inkl. Telegram Bot Service)
- Cronjobs für Automatisierung
- Tailscale VPN für sicheren Remote Zugriff

---

## Autor

Ayman El-Toufaili  
Umschüler zum IT-Systemelektroniker  

Fokus: Netzwerktechnik, Systemadministration, IT-Security, Home-Lab Infrastruktur

Gehostet auf eigenem Raspberry Pi 4 (NRW, Deutschland)
