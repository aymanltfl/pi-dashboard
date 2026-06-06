import os
import json
import logging
import urllib.request
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv("/home/raspberrypi/Desktop/pi-dashboard/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = 8535941521
NOTES_FILE = "/home/raspberrypi/Desktop/pi-dashboard/notes/notes.json"
IMAGES_DIR = "/home/raspberrypi/Desktop/pi-dashboard/notes/images"
DEVICES_FILE = "/home/raspberrypi/Desktop/pi-dashboard/notes/known_devices.json"
API_BASE = "http://127.0.0.1:5000"

CPU_THRESHOLD  = 2.5
TEMP_THRESHOLD = 70.0
RAM_THRESHOLD  = 90.0

# Handys für /whoishome — MAC Adressen
PEOPLE = {
    "Ayman":  "92:20:41:34:8f:5a",
    "Mama":   "72:7e:11:b3:20:b2",
    "Wael":   "86:cc:13:d1:df:c7"
}

os.makedirs(IMAGES_DIR, exist_ok=True)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
logging.basicConfig(level=logging.INFO)

def load_devices():
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE) as f:
            data = json.load(f)
        return {k.lower(): v for k, v in data.items()}
    return {}

def save_devices(data):
    clean = {k.lower(): v for k, v in data.items()}
    with open(DEVICES_FILE, "w") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)

def load_notes():
    with open(NOTES_FILE) as f:
        return json.load(f)

def save_notes(data):
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def improve_text(text):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Du bist mein persönlicher Notiz-Assistent.

Deine Aufgabe:
1. Schreibe den Text leicht verbessert aber KURZ — erfinde nichts dazu
2. Behalte den originalen Inhalt bei — kein Roman, keine Ausschmückungen

Hier ist meine Notiz:
{text}"""
            }]
        )
        return response.choices[0].message.content
    except:
        return text

def fetch_api(path):
    try:
        res = urllib.request.urlopen(f"{API_BASE}{path}", timeout=5)
        return json.loads(res.read())
    except:
        return None

def format_last_seen(last_seen_str):
    if not last_seen_str:
        return "unbekannt"
    try:
        last = datetime.strptime(last_seen_str, "%d.%m.%Y %H:%M")
        diff = datetime.now() - last
        mins = int(diff.total_seconds() / 60)
        if mins < 2:
            return "gerade eben"
        elif mins < 60:
            return f"vor {mins} Min"
        elif mins < 1440:
            hours = mins // 60
            return f"vor {hours} Std"
        else:
            days = mins // 1440
            return f"vor {days} Tagen"
    except:
        return last_seen_str

async def check_user(update: Update) -> bool:
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Nicht autorisiert!")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    await update.message.reply_text(
        "Pi Notes Bot bereit!\n\n"
        "Notizen:\n"
        "/list — alle Einträge\n"
        "/delete <nr> — Eintrag löschen\n"
        "/deleteall — alle löschen\n\n"
        "Netzwerk:\n"
        "/status — Pi Status\n"
        "/devices — Geräte im Netz\n"
        "/whoishome — wer ist zuhause?\n"
        "/name <mac> <name> — Gerät benennen\n"
        "  Beispiel: /name aa:bb:cc:dd:ee:ff Mamas Handy"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    d = fetch_api("/api/status")
    e = fetch_api("/api/energy_total")
    n = fetch_api("/api/network")
    if not d:
        await update.message.reply_text("❌ Pi API nicht erreichbar!")
        return
    ram_pct = round((d["ram_used"] / d["ram_total"]) * 100)
    services = ""
    if n and "services" in n:
        for svc, active in n["services"].items():
            icon = "✅" if active else "❌"
            services += f"  {icon} {svc}\n"
    energy = ""
    if e:
        energy = (
            f"\n⚡ Energie seit {e['start_date']}:\n"
            f"  Laufzeit: {e['runtime']}\n"
            f"  {e['total_kwh']} kWh · {e['total_cost']} € · {round(e['total_co2']*1000,1)}g CO₂\n"
        )
    msg = (
        f"📊 Pi Status\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌡️ Temperatur: {d['temp']} °C\n"
        f"⚙️ CPU Load: {d['cpu_load']}\n"
        f"💾 RAM: {d['ram_used']}/{d['ram_total']} MB ({ram_pct}%)\n"
        f"{energy}"
        f"\n🔧 Services:\n{services}"
    )
    await update.message.reply_text(msg)

async def devices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    n = fetch_api("/api/network")
    if not n:
        await update.message.reply_text("❌ Netzwerk nicht erreichbar!")
        return
    known = load_devices()
    devices = n.get("devices", [])
    if not devices:
        await update.message.reply_text("Keine Geräte gefunden.")
        return
    msg = f"📱 Geräte im Netzwerk ({len(devices)} aktiv)\n━━━━━━━━━━━━━━━━\n"
    for dev in devices:
        mac = dev.get("mac", "").lower()
        ip = dev.get("ip", "")
        hostname = dev.get("hostname", "")
        if mac in known and known[mac].get("name"):
            name = known[mac]["name"]
        elif hostname and hostname != "?":
            name = hostname
        else:
            name = mac
        last_seen = known.get(mac, {}).get("last_seen", "")
        last_seen_str = format_last_seen(last_seen)
        msg += f"✅ {name}\n     {ip} · {last_seen_str}\n"
    msg += "\nTipp: /name <mac> <name> zum Benennen"
    await update.message.reply_text(msg)

async def whoishome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    known = load_devices()
    msg = "🏠 Wer ist zuhause?\n━━━━━━━━━━━━━━━━\n"
    for person, mac in PEOPLE.items():
        mac = mac.lower()
        entry = known.get(mac, {})
        last_seen = entry.get("last_seen", "")
        if last_seen:
            try:
                last = datetime.strptime(last_seen, "%d.%m.%Y %H:%M")
                diff = datetime.now() - last
                mins = int(diff.total_seconds() / 60)
                if mins <= 10:
                    status = "✅ zuhause"
                elif mins <= 60:
                    status = f"⚠️ vor {mins} Min gesehen"
                else:
                    status = f"❌ nicht zuhause (vor {mins//60} Std)"
            except:
                status = "❓ unbekannt"
        else:
            status = "❓ noch nie gesehen"
        msg += f"{person}: {status}\n"
    await update.message.reply_text(msg)

async def name_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    if len(context.args) < 2:
        await update.message.reply_text(
            "Verwendung: /name <mac> <name>\n"
            "Beispiel: /name aa:bb:cc:dd:ee:ff Mamas Handy"
        )
        return
    mac = context.args[0].lower()
    name = " ".join(context.args[1:])
    known = load_devices()
    known[mac] = {
        "name": name,
        "added": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "hostname": known.get(mac, {}).get("hostname", ""),
        "last_seen": known.get(mac, {}).get("last_seen", ""),
        "last_ip": known.get(mac, {}).get("last_ip", "")
    }
    save_devices(known)
    await update.message.reply_text(f"✅ Gerät gespeichert!\n{mac} → {name}")

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    d = fetch_api("/api/status")
    n = fetch_api("/api/network")
    if not d:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text="❌ Pi API nicht erreichbar!")
        return
    if d["cpu_load"] >= CPU_THRESHOLD:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"⚠️ CPU Load hoch: {d['cpu_load']}")
    if d["temp"] >= TEMP_THRESHOLD:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"🌡️ Temperatur kritisch: {d['temp']} °C")
    ram_pct = round((d["ram_used"] / d["ram_total"]) * 100)
    if ram_pct >= RAM_THRESHOLD:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"💾 RAM fast voll: {ram_pct}%")
    if n and "services" in n:
        for svc, active in n["services"].items():
            if not active:
                await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"❌ Service ausgefallen: {svc}")
    if n and "devices" in n:
        known = load_devices()
        for dev in n["devices"]:
            mac = dev.get("mac", "").lower()
            ip = dev.get("ip", "")
            hostname = dev.get("hostname", "")
            if not mac:
                continue
            if mac not in known:
                name = hostname if hostname and hostname != "?" else mac
                await context.bot.send_message(
                    chat_id=ALLOWED_USER_ID,
                    text=(
                        f"👀 Neues Gerät im Netzwerk!\n"
                        f"  Name: {name}\n"
                        f"  IP: {ip}\n"
                        f"  MAC: {mac}\n\n"
                        f"Benennen: /name {mac} Mein Gerät"
                    )
                )
                known[mac] = {
                    "name": "",
                    "hostname": hostname,
                    "first_seen": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "last_ip": ip,
                    "last_seen": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
            else:
                known[mac]["last_ip"] = ip
                known[mac]["last_seen"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        save_devices(known)

async def daily_summary(context: ContextTypes.DEFAULT_TYPE):
    d = fetch_api("/api/status")
    e = fetch_api("/api/energy_total")
    n = fetch_api("/api/network")
    if not d:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text="❌ Tägliche Zusammenfassung fehlgeschlagen.")
        return
    ram_pct = round((d["ram_used"] / d["ram_total"]) * 100)
    services = ""
    if n and "services" in n:
        for svc, active in n["services"].items():
            icon = "✅" if active else "❌"
            services += f"  {icon} {svc}\n"
    energy = ""
    if e:
        energy = (
            f"\n⚡ Energie seit {e['start_date']}:\n"
            f"  Laufzeit: {e['runtime']}\n"
            f"  {e['total_kwh']} kWh · {e['total_cost']} € · {round(e['total_co2']*1000,1)}g CO₂\n"
        )
    devices_count = len(n["devices"]) if n and "devices" in n else "?"
    msg = (
        f"☀️ Guten Morgen! Pi Tagesbericht\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌡️ Temperatur: {d['temp']} °C\n"
        f"⚙️ CPU Load: {d['cpu_load']}\n"
        f"💾 RAM: {d['ram_used']}/{d['ram_total']} MB ({ram_pct}%)\n"
        f"🏠 Geräte im Netz: {devices_count}\n"
        f"{energy}"
        f"\n🔧 Services:\n{services}"
    )
    await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    text = update.message.text
    await update.message.reply_text("Verarbeite...")
    improved = improve_text(text)
    notes = load_notes()
    entry = {
        "id": len(notes["entries"]) + 1,
        "date": datetime.now().strftime("%d.%m.%Y"),
        "time": datetime.now().strftime("%H:%M"),
        "content": improved,
        "original": text,
        "image": None,
        "tags": []
    }
    notes["entries"].append(entry)
    save_notes(notes)
    await update.message.reply_text(f"✅ Notiz #{entry['id']} gespeichert!\n\n{improved}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    await update.message.reply_text("Verarbeite...")
    file = await context.bot.get_file(photo.file_id)
    notes = load_notes()
    image_name = f"img_{len(notes['entries']) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image_path = os.path.join(IMAGES_DIR, image_name)
    await file.download_to_drive(image_path)
    improved = improve_text(caption) if caption else ""
    entry = {
        "id": len(notes["entries"]) + 1,
        "date": datetime.now().strftime("%d.%m.%Y"),
        "time": datetime.now().strftime("%H:%M"),
        "content": improved,
        "original": caption,
        "image": image_name,
        "tags": []
    }
    notes["entries"].append(entry)
    save_notes(notes)
    await update.message.reply_text(f"✅ Notiz #{entry['id']} mit Bild gespeichert!")

async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    notes = load_notes()
    if not notes["entries"]:
        await update.message.reply_text("Keine Notizen vorhanden.")
        return
    text = "📋 Deine Notizen:\n\n"
    for e in notes["entries"]:
        preview = e["content"][:50] + "..." if len(e["content"]) > 50 else e["content"]
        text += f"#{e['id']} — {e['date']} — {preview}\n"
    await update.message.reply_text(text)

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    if not context.args:
        await update.message.reply_text("Verwendung: /delete <nummer>")
        return
    try:
        note_id = int(context.args[0])
        notes = load_notes()
        before = len(notes["entries"])
        notes["entries"] = [e for e in notes["entries"] if e["id"] != note_id]
        if len(notes["entries"]) < before:
            save_notes(notes)
            await update.message.reply_text(f"✅ Notiz #{note_id} gelöscht!")
        else:
            await update.message.reply_text(f"Notiz #{note_id} nicht gefunden.")
    except ValueError:
        await update.message.reply_text("Bitte eine gültige Nummer angeben.")

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    notes = load_notes()
    notes["entries"] = []
    save_notes(notes)
    await update.message.reply_text("✅ Alle Notizen gelöscht!")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_notes))
app.add_handler(CommandHandler("delete", delete_note))
app.add_handler(CommandHandler("deleteall", delete_all))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(CommandHandler("devices", devices_command))
app.add_handler(CommandHandler("whoishome", whoishome_command))
app.add_handler(CommandHandler("name", name_device))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

job_queue = app.job_queue
job_queue.run_repeating(check_alerts, interval=300, first=10)
job_queue.run_daily(daily_summary, time=datetime.strptime("08:00", "%H:%M").time())

print("Bot startet...")
app.run_polling()