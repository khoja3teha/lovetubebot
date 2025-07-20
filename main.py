import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.environ['BOT_TOKEN']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک ویدیوی یوتیوب رو بفرست تا دانلودش کنم 😉")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("دارم لینک رو پردازش می‌کنم...")

    ydl_opts = {
        'format': 'best[filesize<50M]/best',
        'outtmpl': 'video.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        with open(file_name, 'rb') as f:
            await update.message.reply_video(video=f)

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"خطا در دانلود: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
