import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا ویدیو رو برات دانلود کنم.")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("در حال دانلود... لطفاً صبر کن.")

    ydl_opts = {
        'format': 'best[filesize<50M]/best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        with open(file_name, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=info.get("title", "ویدیو"))

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد:\n{e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
