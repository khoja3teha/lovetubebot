import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
import yt_dlp

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا ویدیو رو برات دانلود کنم.")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("✅ لینک دریافت شد! در حال پردازش و دانلود...")

    ydl_opts = {
        'format': 'best[filesize<50M]/best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        with open(file_name, 'rb') as f:
            await update.message.reply_video(f, caption=info.get("title", "ویدیو"))

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا هنگام دانلود: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("🚀 ربات آماده است و داره اجرا میشه...")
    app.run_polling()

if __name__ == '__main__':
    main()
