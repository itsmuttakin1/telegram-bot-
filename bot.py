import os
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatJoinRequestHandler,
    CallbackQueryHandler, ContextTypes, filters, ApplicationHandlerStop
)
from telegram.constants import ChatMemberStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# 3 jon admin access pabe
ADMIN_IDS = {5140546628, 7728010216,}

DATA_FILE = "data.json"

# Shudhumatro ei 1-ti channel-e post hobe
TARGET_CHANNEL_ID = -1003999213768

# Shob post-e default bhabe Backup Channel button thakbe
BACKUP_CHANNEL_BUTTON = {
    "text": "Backup Channel",
    "url": "https://t.me/+67b2i8j0t7phOTdl"
}

def get_channel_button_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BACKUP_CHANNEL_BUTTON["text"], url=BACKUP_CHANNEL_BUTTON["url"])]
    ])

MEMBER_NOTICE_CAPTION = (
    "📢 <b>সম্মানিত মেম্বারদের দৃষ্টি আকর্ষণ করছি!</b> 📢\n\n"
    "👋 আপনারা অনেকেই হয়তো নতুন যুক্ত হয়েছেন এবং আমাদের চ্যানেলের নিয়ম সম্পর্কে জানেন না:\n\n"
    "⏳ <b>পোস্ট স্থায়িত্ব:</b>\n"
    "আমাদের চ্যানেলে প্রতিটি ভিডিও সর্বোচ্চ <b>২ দিন (৪৮ ঘণ্টা)</b> পর্যন্ত রাখা হয়। এরপর পুরাতন ভিডিও অটোমেটিক ডিলিট করে নতুন এক্সক্লুসিভ ভিডিও যোগ করা হয়।\n\n"
    "⏰ <b>ভিডিও আপলোডের সময়সূচী:</b>\n"
    "প্রতিদিন <b>রাত ৮:০০ টা থেকে ৯:০০ টা</b> এবং <b>রাত ১২:০০ টায়</b> চ্যানেলে নতুন ভিডিও আপলোড করা হয়।\n\n"
    "⚠️ <b>সতর্কবার্তা:</b>\n"
    "চ্যানেল থেকে লিভ নেওয়ার আগে একবার ভেবে দেখবেন—এখানে কিন্তু সব <b>প্রিমিয়াম ও পেইড ভিডিও সম্পূর্ণ ফ্রিতে</b> দেওয়া হয়! 🔥\n\n"
    "❤️ একটিভ থাকুন এবং বন্ধুদের শেয়ার করুন। ধন্যবাদ সবাইকে! ✨"
)

DEFAULT_DATA = {
    "auto_approve_enabled": True,
    "channel_clean_enabled": True,
    "clean_channel_posts": [],     # [{"message_id": int, "timestamp": float, "date_str": str}, ...]
    "saved_caption": "Full Video 👇\nhttps://breedsmuteexams.com/ja1gp1y0?key=5ad4cd88923c063b5b21a813a4822ed8",
}

def load_data():
    merged = dict(DEFAULT_DATA)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged.update(saved)
            if not isinstance(merged.get("clean_channel_posts"), list):
                merged["clean_channel_posts"] = []
        except Exception as e:
            logger.error(f"Error loading data.json: {e}")
    return merged

def save_data(data_obj):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_obj, f, ensure_ascii=False, indent=2)

data = load_data()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ---------- Auto Approve Join Request (Channel) ----------
async def auto_approve_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data.get("auto_approve_enabled", True):
        return
    request = update.chat_join_request
    if not request:
        return
    try:
        await request.approve()
        logger.info(f"Auto approved user {request.from_user.id} in chat {request.chat.id}")
    except Exception as e:
        logger.error(f"Failed to auto-approve: {e}")

# ---------- 2 Days Channel Auto-Clean Service ----------
async def channel_post_cleaner_job(context: ContextTypes.DEFAULT_TYPE):
    """2 din (48 ghonta) por TARGET_CHANNEL_ID theke post auto delete korbe"""
    if not data.get("channel_clean_enabled", True):
        return

    posts = data.get("clean_channel_posts", [])
    if not posts:
        return

    now = time.time()
    two_days_seconds = 2 * 24 * 3600  # 48 hours

    expired_posts = [p for p in posts if now - p.get("timestamp", now) >= two_days_seconds]
    if not expired_posts:
        return

    remaining_posts = []

    for p in posts:
        if p in expired_posts:
            mid = p.get("message_id")
            try:
                await context.bot.delete_message(chat_id=TARGET_CHANNEL_ID, message_id=mid)
                logger.info(f"Deleted old post {mid} from {TARGET_CHANNEL_ID}")
            except Exception as e:
                logger.debug(f"Could not delete old post {mid}: {e}")
        else:
            remaining_posts.append(p)

    data["clean_channel_posts"] = remaining_posts
    save_data(data)

# ---------- Channel Post System ----------
def _post_draft(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    drafts = context.bot_data.setdefault("post_draft", {})
    return drafts.get(user_id)

def post_editor_markup(draft):
    rows = [
        [InlineKeyboardButton(f"🔒 {BACKUP_CHANNEL_BUTTON['text']} (স্থায়ী)", callback_data="perm_btn_info")],
        [InlineKeyboardButton("✏️ ক্যাপশন পরিবর্তন", callback_data="post_set_caption")],
        [InlineKeyboardButton("✅ চ্যানেলে পোস্ট করুন", callback_data="post_publish")],
        [InlineKeyboardButton("❌ বাতিল করুন", callback_data="post_cancel")]
    ]
    return InlineKeyboardMarkup(rows)

def post_preview_text(draft):
    lines = [
        "📋 <b>পোস্ট প্রিভিউ:</b>",
        f"🎯 <b>টার্গেট চ্যানেল:</b> <code>{TARGET_CHANNEL_ID}</code>\n",
        f"📝 <b>ক্যাপশন:</b>\n{draft.get('caption', '') or '(খালি)'}\n",
        f"🔘 <b>যুক্ত বাটন:</b> {BACKUP_CHANNEL_BUTTON['text']} ➔ {BACKUP_CHANNEL_BUTTON['url']}"
    ]
    return "\n".join(lines)

async def post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    await start_post_flow(update, context)

async def start_post_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.bot_data.setdefault("post_draft", {})[user_id] = None
    context.user_data["awaiting"] = "post_video"
    await update.effective_message.reply_text(
        f"ভিডিও অথবা ছবি পাঠান যেটা চ্যানেলে ({TARGET_CHANNEL_ID}) পোস্ট করতে চান।\n"
        "বাতিল করতে /cancel লিখুন।"
    )

async def post_video_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    if context.user_data.get("awaiting") != "post_video":
        return
    msg = update.message
    if msg.video:
        kind, file_id = "video", msg.video.file_id
    elif msg.photo:
        kind, file_id = "photo", msg.photo[-1].file_id
    else:
        return

    caption = msg.caption or data.get("saved_caption", "")
    draft = {
        "kind": kind,
        "file_id": file_id,
        "caption": caption
    }
    context.bot_data.setdefault("post_draft", {})[user_id] = draft
    context.user_data["awaiting"] = None
    await update.message.reply_html(post_preview_text(draft), reply_markup=post_editor_markup(draft))
    raise ApplicationHandlerStop

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    context.user_data["awaiting"] = None
    context.bot_data.setdefault("post_draft", {})[user_id] = None
    await update.message.reply_text("❌ বাতিল করা হয়েছে।")

# ---------- Admin Panel ----------
def admin_panel_markup():
    auto_appr = "ON ✅" if data.get("auto_approve_enabled", True) else "OFF ❌"
    clean_svc = "ON ✅" if data.get("channel_clean_enabled", True) else "OFF ❌"

    kb = [
        [InlineKeyboardButton("📢 চ্যানেলে নতুন পোস্ট বানান", callback_data="new_post")],
        [InlineKeyboardButton("✏️ ডিফল্ট ক্যাপশন পরিবর্তন", callback_data="manage_saved_caption")],
        [InlineKeyboardButton(f"⚡ অটো জয়েন এপ্রুভ: {auto_appr}", callback_data="toggle_auto_approve")],
        [InlineKeyboardButton(f"🧹 ২ দিনের ক্লিন সার্ভিস: {clean_svc}", callback_data="toggle_clean_service")],
        [InlineKeyboardButton("🖼 Message for Member (চ্যানেলে পাঠান)", callback_data="send_member_notice")],
        [InlineKeyboardButton("🎙 Voice Message (চ্যানেলে পাঠান)", callback_data="send_voice_notice")],
        [InlineKeyboardButton("🎯 চ্যানেল স্ট্যাটাস চেক", callback_data="view_channels_status")],
    ]
    return InlineKeyboardMarkup(kb)

async def ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু এডমিনদের জন্য।")
        return
    await update.message.reply_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data

    if not is_admin(user_id):
        await query.edit_message_text("অনুমতি নেই।")
        return

    # Post flow
    if action in ("new_post", "post_set_caption", "post_cancel", "post_publish") or action == "perm_btn_info":
        if action == "perm_btn_info":
            await query.answer("এই বাটনটি ডিফল্ট স্থায়ী বাটন (Backup Channel)।", show_alert=True)
            return

        if action == "new_post":
            await start_post_flow(update, context)
            return

        draft = _post_draft(context, user_id)
        if not draft and action != "post_cancel":
            await query.edit_message_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            return

        if action == "post_set_caption":
            context.user_data["awaiting"] = "post_caption"
            await query.edit_message_text(
                "এই পোস্টের জন্য ক্যাপশন লিখে পাঠান:\n"
                "(মুছে ফেলতে চাইলে <code>clear</code> লিখে পাঠান)",
                parse_mode="HTML"
            )
        elif action == "post_cancel":
            context.bot_data.setdefault("post_draft", {})[user_id] = None
            context.user_data["awaiting"] = None
            await query.edit_message_text("❌ পোস্ট বাতিল করা হয়েছে।")
        elif action == "post_publish":
            markup = get_channel_button_markup()
            caption_text = draft.get("caption", "").strip() or None

            bd_tz = timezone(timedelta(hours=6))
            today_date_str = datetime.now(bd_tz).strftime("%d-%m-%Y")

            try:
                if draft["kind"] == "video":
                    sent_msg = await context.bot.send_video(
                        chat_id=TARGET_CHANNEL_ID, video=draft["file_id"],
                        caption=caption_text, reply_markup=markup
                    )
                else:
                    sent_msg = await context.bot.send_photo(
                        chat_id=TARGET_CHANNEL_ID, photo=draft["file_id"],
                        caption=caption_text, reply_markup=markup
                    )

                if sent_msg:
                    clean_posts = data.setdefault("clean_channel_posts", [])
                    clean_posts.append({
                        "message_id": sent_msg.message_id,
                        "timestamp": time.time(),
                        "date_str": today_date_str
                    })
                    save_data(data)

                context.bot_data.setdefault("post_draft", {})[user_id] = None
                again_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 আরেকটি পোস্ট করুন", callback_data="new_post")],
                    [InlineKeyboardButton("🛠 অ্যাডমিন প্যানেল", callback_data="back_to_panel")]
                ])
                await query.edit_message_text(
                    f"✅ চ্যানেলে ({TARGET_CHANNEL_ID}) পোস্ট সফলভাবে প্রকাশিত হয়েছে!",
                    reply_markup=again_markup
                )
            except Exception as e:
                logger.error(f"Failed to post in {TARGET_CHANNEL_ID}: {e}")
                await query.edit_message_text(
                    f"❌ পোস্ট করতে সমস্যা হয়েছে: {e}\n\nবট চ্যানেলে Administrator এবং Post Messages পারমিশন আছে কিনা চেক করুন।"
                )
        return

    # Panel Navigation
    if action == "back_to_panel":
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "manage_saved_caption":
        context.user_data["awaiting"] = "saved_caption"
        cur = data.get("saved_caption", "") or "(কোনো ক্যাপশন সেট নেই)"
        await query.edit_message_text(
            f"📝 <b>বর্তমান ডিফল্ট ক্যাপশন:</b>\n{cur}\n\n"
            "নতুন ডিফল্ট ক্যাপশন লিখে পাঠান যা প্রতিটি পোস্টে অটো চলে আসবে:\n"
            "ক্যাপশন বন্ধ করতে লিখুন: <code>off</code>",
            parse_mode="HTML"
        )
    elif action == "view_channels_status":
        admin_status = "❌ Admin নেই / Error"
        try:
            me = await context.bot.get_chat_member(TARGET_CHANNEL_ID, context.bot.id)
            if me.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                admin_status = "✅ Admin সক্রিয়"
        except Exception:
            admin_status = "❌ Not Found / Admin নেই"

        text = (
            f"🎯 <b>টার্গেট চ্যানেল:</b> <code>{TARGET_CHANNEL_ID}</code> ➔ <b>{admin_status}</b>\n"
            f"🔘 <b>স্থায়ী বাটন:</b> {BACKUP_CHANNEL_BUTTON['text']} ({BACKUP_CHANNEL_BUTTON['url']})\n"
            f"🧹 <b>ক্লিন সার্ভিস:</b> ২ দিন পর পোস্ট অটো-ডিলিট"
        )
        kb = [[InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif action == "toggle_auto_approve":
        data["auto_approve_enabled"] = not data.get("auto_approve_enabled", True)
        save_data(data)
        status_txt = "চালু" if data["auto_approve_enabled"] else "বন্ধ"
        await query.answer(f"⚡ অটো এপ্রুভ {status_txt} করা হয়েছে!", show_alert=True)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "toggle_clean_service":
        data["channel_clean_enabled"] = not data.get("channel_clean_enabled", True)
        save_data(data)
        status_txt = "চালু" if data["channel_clean_enabled"] else "বন্ধ"
        await query.answer(f"🧹 ক্লিন সার্ভিস {status_txt} করা হয়েছে!", show_alert=True)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())

    # Send 1.jpg to Channel
    elif action == "send_member_notice":
        photo_path = "1.jpg"
        if not os.path.exists(photo_path):
            await query.answer("❌ 1.jpg ফাইলটি পাওয়া যায়নি!", show_alert=True)
            return

        markup = get_channel_button_markup()
        try:
            with open(photo_path, "rb") as pf:
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL_ID,
                    photo=pf,
                    caption=MEMBER_NOTICE_CAPTION,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            await query.answer("✅ চ্যানেলে ফটো নোটিশ পাঠানো হয়েছে!", show_alert=True)
        except Exception as e:
            logger.error(f"Failed to send 1.jpg to channel: {e}")
            await query.answer(f"❌ পাঠাতে সমস্যা হয়েছে: {e}", show_alert=True)

    # Send telegram.ogg to Channel
    elif action == "send_voice_notice":
        voice_path = "telegram.ogg"
        if not os.path.exists(voice_path):
            await query.answer("❌ telegram.ogg ফাইলটি পাওয়া যায়নি!", show_alert=True)
            return

        markup = get_channel_button_markup()
        try:
            with open(voice_path, "rb") as vf:
                voice_data = vf.read()

            try:
                await context.bot.send_voice(
                    chat_id=TARGET_CHANNEL_ID,
                    voice=voice_data,
                    caption="🎙 <b>চ্যানেলের সকল মেম্বার অবশ্যই ভয়েসটি শুনুন!</b> 👇",
                    parse_mode="HTML",
                    reply_markup=markup
                )
            except Exception:
                await context.bot.send_audio(
                    chat_id=TARGET_CHANNEL_ID,
                    audio=voice_data,
                    title="Voice Notice",
                    caption="🎙 <b>চ্যানেলের সকল মেম্বার অবশ্যই অডিওটি শুনুন!</b> 👇",
                    parse_mode="HTML",
                    reply_markup=markup
                )
            await query.answer("✅ চ্যানেলে ভয়েস পাঠানো হয়েছে!", show_alert=True)
        except Exception as e:
            logger.error(f"Failed to send voice to channel: {e}")
            await query.answer(f"❌ পাঠাতে সমস্যা হয়েছে: {e}", show_alert=True)

async def admin_text_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    user_id = update.effective_user.id
    if not awaiting or not is_admin(user_id):
        return

    if awaiting == "post_caption":
        draft = _post_draft(context, user_id)
        if not draft:
            await update.message.reply_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            context.user_data["awaiting"] = None
            raise ApplicationHandlerStop
        raw = update.message.text.strip()
        if raw.lower() == "clear":
            draft["caption"] = ""
            await update.message.reply_text("✅ ক্যাপশন মুছে ফেলা হয়েছে।")
        else:
            draft["caption"] = update.message.text
            await update.message.reply_text("✅ ক্যাপশন সেট করা হয়েছে।")
        await update.message.reply_html(post_preview_text(draft), reply_markup=post_editor_markup(draft))
        context.user_data["awaiting"] = None
        raise ApplicationHandlerStop

    elif awaiting == "saved_caption":
        raw = update.message.text.strip()
        if raw.lower() == "off":
            data["saved_caption"] = ""
            save_data(data)
            await update.message.reply_text("✅ ডিফল্ট ক্যাপশন বন্ধ করা হয়েছে।")
        else:
            data["saved_caption"] = update.message.text
            save_data(data)
            await update.message.reply_text("✅ ডিফল্ট ক্যাপশন সফলভাবে সেভ হয়েছে!")
        context.user_data["awaiting"] = None
        raise ApplicationHandlerStop

    context.user_data["awaiting"] = None
    raise ApplicationHandlerStop

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.reply_text("বট চালু আছে ✅ পোস্ট করতে /post অথবা প্যানেল দেখতে /ad লিখুন।")
    else:
        await update.message.reply_text("বট সক্রিয় আছে ✅")

# ---------- Tiny HTTP server (Keep-alive) ----------
class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info(f"Health server listening on port {port}")

def main():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    start_health_server()
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands (Private chat with bot)
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("ad", ad_cmd))
    app.add_handler(CommandHandler("post", post_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # Auto Approve Member Join Requests (Target Channel)
    app.add_handler(ChatJoinRequestHandler(auto_approve_request))

    # Admin Callback Queries
    app.add_handler(CallbackQueryHandler(admin_callback))

    # Admin private video/photo capture for post
    app.add_handler(MessageHandler(
        (filters.VIDEO | filters.PHOTO) & filters.ChatType.PRIVATE, post_video_capture
    ))

    # Private text inputs (Caption management)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # 2 Days Old Channel Posts Auto-Cleaner (Checks every 10 minutes)
    if app.job_queue:
        app.job_queue.run_repeating(channel_post_cleaner_job, interval=600, first=30)

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
