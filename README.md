# Raspberry Pi Home Server Dashboard

Persönliches Home-Lab Projekt auf Basis eines Raspberry Pi 4 (Raspberry Pi OS).

Live erreichbar unter:  
https://aymanel-pi.duckdns.org

Demo-Zugang (optional):  
Benutzer: demo  
Passwort: demo2026  

---

## 📌 Projektübersicht

Dieses Projekt ist ein vollständig selbst gehostetes Home-Server-System, das verschiedene IT- und Systemadministrations-Konzepte kombiniert:

- Webserver & Reverse Proxy
- REST APIs für Systemdaten
- Netzwerk-Monitoring
- Authentifizierungssystem
- KI-gestützter Helpdesk Bot
- DNS-basierter Werbeblocker
- Remote-Zugriff via VPN

Ziel des Projekts ist es, eine realistische IT-Infrastruktur im Heimnetz nachzubauen und zu betreiben.

---

## 🚀 Features / Projekte

### 🖥️ Raspberry Pi Home Server
- Webserver mit Reverse Proxy (nginx)
- Eigene REST API für Systemdaten (CPU, RAM, Temperatur, Uptime)
- Dynamisches DNS über DuckDNS
- Automatischer IP-Update Mechanismus
- HTTPS mit Let's Encrypt
- Systemdienste via systemd
- Firewall-Schutz mit UFW
- Schutz vor Brute-Force Angriffen (Fail2ban)

---

### ⚡ Energie- & Systemmonitoring
- Echtzeit Schätzung des Stromverbrauchs
- Kostenberechnung basierend auf Strompreis
- CO₂-Emissionen basierend auf Energieverbrauch
- Speicherung historischer Systemdaten

---

### 🤖 IT Helpdesk Bot
- KI-basierter Chatbot für IT-Support
- Integration eines Large Language Models (Groq / LLaMA 3)
- Kontextspeicher für Gesprächsverlauf
- Webbasierte Chat-Oberfläche im Dashboard

---

### 🌐 Netzwerk-Werbeblocker (Pi-hole)
- Netzwerkweiter DNS-Werbeblocker
- Filterung von Werbung und Trackern für alle Geräte im Heimnetz
- Zentrale Verwaltung über Webinterface
- Anpassbare Blocklisten

---

### 🔐 Authentifizierungssystem
- JWT-basiertes Login-System
- Geschütztes Dashboard
- Zwei Benutzerrollen (Admin / Demo)
- Session-Handling im Browser

---

## 🧰 Technologien

| Bereich | Technologie |
|--------|------------|
| Hardware | Raspberry Pi 4 |
| OS | Raspberry Pi OS (Debian-based) |
| Webserver | nginx |
| Backend | Python 3 |
| Frontend | HTML, CSS, JavaScript |
| DNS | DuckDNS, Pi-hole |
| Security | UFW, Fail2ban, Let's Encrypt |
| Auth | JWT |
| Remote Access | Tailscale VPN |
| AI | Groq API / LLaMA 3 |
| Deployment | systemd |

---

## 🏗️ Architektur (vereinfacht)

Internet → Domain (DuckDNS) → nginx Reverse Proxy → interne Services

Interne Services:
- Web Dashboard
- Authentication Service
- System API
- Helpdesk Bot
- Pi-hole DNS Filter

Alle Backend-Services laufen lokal auf dem Raspberry Pi und sind nicht direkt öffentlich erreichbar.

---

## 🔐 Sicherheit

- nginx als einziger öffentlicher Entry Point
- interne APIs nur lokal erreichbar
- JWT Authentifizierung für Dashboard Zugriff
- Firewall (UFW) schützt Netzwerkzugänge
- Fail2ban schützt gegen Brute-Force Angriffe
- HTTPS Verschlüsselung für alle externen Verbindungen
- Remote Zugriff ausschließlich über VPN (Tailscale)

---

## 📁 Projektstruktur

pi-dashboard/
├── backend (Python APIs & Services)
├── frontend (Dashboard UI)
├── auth service (Login / JWT)
├── helpdesk bot (KI Chat)
├── energy monitoring
├── pi-hole integration
├── system config (nginx, systemd, scripts)

---

## 👤 Autor

Ayman El-Toufaili  
Umschüler zum IT-System-Elektroniker  
Praktikum ab September 2026  

---

## ⚙️ Hosting

Gehostet auf einem eigenen Raspberry Pi 4 im Heimnetzwerk
```

---
