import os
import uuid
import yt_dlp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# گرفتن توکن از محیط
TOKEN = os.environ["BOT_TOKEN"]

# نگهداری وضعیت کاربران
user_data = {}

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋\nلینک ویدیوی یوتیوب رو برام بفرست تا دانلودش کنم 📥")

# وقتی لینک فرستاده میشه
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("⚠️ لطفاً یک لینک معتبر یوتیوب بفرست.")
        return

    await update.message.reply_text("🔍 در حال بررسی لینک...")

    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title")
        duration = info.get("duration")
        thumbnail = info.get("thumbnail")
        formats = info.get("formats")

        # فیلتر فرمت‌های mp4 و دارای ویدیو
        video_formats = [
            f for f in formats
            if f.get("ext") == "mp4" and f.get("vcodec") != "none"
        ]
        video_formats.sort(key=lambda x: int(x.get("height", 0)), reverse=True)

        # ذخیره اطلاعات
        user_data[update.effective_chat.id] = {
            "formats": video_formats,
            "url": url,
            "info": info
        }

        # دکمه‌های کیفیت
        buttons = [
            [InlineKeyboardButton(f"{f['height']}p", callback_data=str(i))]
            for i, f in enumerate(video_formats[:5])
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        caption = f"""🎬 <b>{title}</b>
🕒 مدت: {duration // 60} دقیقه
👇 لطفاً کیفیت موردنظر رو انتخاب کن:"""

        await update.message.reply_photo(
            photo=thumbnail,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در پردازش لینک: {e}")

# وقتی کیفیت انتخاب میشه
async def handle_quality_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    user = user_data.get(chat_id)
    if not user:
        await query.edit_message_text("⚠️ لطفاً اول لینک یوتیوب بفرست.")
        return

    index = int(query.data)
    selected_format = user["formats"][index]
    download_url = selected_format.get("url")
    height = selected_format.get("height")
    filesize = selected_format.get("filesize") or 0

    MB = filesize / (1024 * 1024)

    if MB > 50:
        await query.edit_message_text(
            f"⚠️ این فایل بزرگه (حدوداً {MB:.1f}MB)\n📎 لینک مستقیم دانلود:\n{download_url}"
        )
        return

    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'quiet': True,
        'outtmpl': filename,
        'format': selected_format["format_id"]
    }

    try:
        await query.edit_message_text("⏬ در حال دانلود فایل...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([user["url"]])

        await context.bot.send_video(chat_id=chat_id, video=open(filename, 'rb'))
        os.remove(filename)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ خطا در دانلود فایل: {e}")

# راه‌اندازی بات
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_quality_choice))

    print("✅ ربات اجرا شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
