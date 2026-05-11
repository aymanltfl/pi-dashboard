import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv("/home/raspberrypi/Desktop/pi-dashboard/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = 8535941521  # Deine Telegram User ID
NOTES_FILE = "/home/raspberrypi/Desktop/pi-dashboard/notes/notes.json"
IMAGES_DIR = "/home/raspberrypi/Desktop/pi-dashboard/notes/images"

os.makedirs(IMAGES_DIR, exist_ok=True)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

logging.basicConfig(level=logging.INFO)

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
                "content": f"Formuliere diese IT-Lernnotiz professioneller und klarer, behalte den Inhalt bei, antworte nur mit dem verbesserten Text ohne Erklärungen:\n\n{text}"
            }]
        )
        return response.choices[0].message.content
    except:
        return text

async def check_user(update: Update) -> bool:
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Nicht autorisiert!")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    await update.message.reply_text(
        "Pi Notes Bot bereit!\n\n"
        "Schick mir einfach Text oder Fotos.\n\n"
        "Befehle:\n"
        "/list — alle Einträge anzeigen\n"
        "/delete <nr> — Eintrag löschen\n"
        "/deleteall — alle Einträge löschen"
    )

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
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot startet...")
app.run_polling()
