import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# دریافت توکن از Environment Variable
TOKEN = os.getenv("8013306076:AAFy5_WYSfpfH7RsZcdaFti3-dcXg5z09bw")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من روشنم 😊")

def main():
    # بررسی اینکه توکن درست گرفته شده یا نه
    if not TOKEN:
        print("❌ توکن پیدا نشد! لطفاً در بخش Environment Variables توکن را با کلید TOKEN تنظیم کن.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ ربات اجرا شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
