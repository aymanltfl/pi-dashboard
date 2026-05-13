import os
import json
import logging
import urllib.request
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv("/home/raspberrypi/Desktop/pi-dashboard/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = 8535941521
NOTES_FILE = "/home/raspberrypi/Desktop/pi-dashboard/notes/notes.json"
IMAGES_DIR = "/home/raspberrypi/Desktop/pi-dashboard/notes/images"
API_BASE = "http://127.0.0.1:5000"

# ─── ALERT SCHWELLWERTE ───────────────────────────────────────────────────────
CPU_THRESHOLD    = 2.5   # CPU Load (nicht %)
TEMP_THRESHOLD   = 70.0  # °C
RAM_THRESHOLD    = 90.0  # %

os.makedirs(IMAGES_DIR, exist_ok=True)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
logging.basicConfig(level=logging.INFO)

# ─── BEKANNTE GERÄTE ──────────────────────────────────────────────────────────
known_devices = set()

# ─── NOTES HELPERS ────────────────────────────────────────────────────────────
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

# ─── API HELPERS ──────────────────────────────────────────────────────────────
def fetch_api(path):
    try:
        res = urllib.request.urlopen(f"{API_BASE}{path}", timeout=5)
        return json.loads(res.read())
    except:
        return None

# ─── AUTH ─────────────────────────────────────────────────────────────────────
async def check_user(update: Update) -> bool:
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Nicht autorisiert!")
        return False
    return True

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    await update.message.reply_text(
        "Pi Notes Bot bereit!\n\n"
        "Schick mir einfach Text oder Fotos.\n\n"
        "Befehle:\n"
        "/list — alle Einträge anzeigen\n"
        "/delete <nr> — Eintrag löschen\n"
        "/deleteall — alle Einträge löschen\n"
        "/status — Pi Status abrufen"
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
            services += f"{icon} {svc}\n"

    energy = ""
    if e:
        energy = (
            f"\n⚡ Energie seit {e['start_date']}:\n"
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

# ─── ALERTS ───────────────────────────────────────────────────────────────────
async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    d = fetch_api("/api/status")
    n = fetch_api("/api/network")
    global known_devices

    if not d:
        await context.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text="❌ Pi API nicht erreichbar! Services möglicherweise ausgefallen."
        )
        return

    # CPU Alert
    if d["cpu_load"] >= CPU_THRESHOLD:
        await context.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text=f"⚠️ CPU Load hoch: {d['cpu_load']} (Schwelle: {CPU_THRESHOLD})"
        )

    # Temperatur Alert
    if d["temp"] >= TEMP_THRESHOLD:
        await context.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text=f"🌡️ Temperatur kritisch: {d['temp']} °C (Schwelle: {TEMP_THRESHOLD} °C)"
        )

    # RAM Alert
    ram_pct = round((d["ram_used"] / d["ram_total"]) * 100)
    if ram_pct >= RAM_THRESHOLD:
        await context.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text=f"💾 RAM fast voll: {ram_pct}% ({d['ram_used']}/{d['ram_total']} MB)"
        )

    # Services Alert
    if n and "services" in n:
        for svc, active in n["services"].items():
            if not active:
                await context.bot.send_message(
                    chat_id=ALLOWED_USER_ID,
                    text=f"❌ Service ausgefallen: {svc}"
                )

    # Neue Geräte im Netzwerk
    if n and "devices" in n:
        current_ips = set(dev["ip"] for dev in n["devices"])
        if known_devices:
            new_devices = current_ips - known_devices
            for ip in new_devices:
                await context.bot.send_message(
                    chat_id=ALLOWED_USER_ID,
                    text=f"👀 Neues Gerät im Netzwerk: {ip}"
                )
        known_devices = current_ips

# ─── TÄGLICHE ZUSAMMENFASSUNG ─────────────────────────────────────────────────
async def daily_summary(context: ContextTypes.DEFAULT_TYPE):
    d = fetch_api("/api/status")
    e = fetch_api("/api/energy_total")
    n = fetch_api("/api/network")

    if not d:
        await context.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text="❌ Tägliche Zusammenfassung fehlgeschlagen — Pi nicht erreichbar."
        )
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

# ─── NOTES HANDLERS ───────────────────────────────────────────────────────────
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

# ─── APP ──────────────────────────────────────────────────────────────────────
app = Application.builder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_notes))
app.add_handler(CommandHandler("delete", delete_note))
app.add_handler(CommandHandler("deleteall", delete_all))
app.add_handler(CommandHandler("status", status_command))

# Messages
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Jobs
job_queue = app.job_queue
job_queue.run_repeating(check_alerts, interval=300, first=10)       # Alerts alle 5 Min
job_queue.run_daily(daily_summary, time=datetime.strptime("08:00", "%H:%M").time())  # Täglich 8 Uhr

print("Bot startet...")
app.run_polling()
