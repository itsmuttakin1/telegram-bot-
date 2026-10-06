import os
import re
import json
import logging
import google.generativeai as genai
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatMemberHandler,
    CallbackQueryHandler, ContextTypes, filters, ApplicationHandlerStop
)
from telegram.constants import MessageEntityType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5140546628"))

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "welcome": "ওয়েলকাম {name}! গ্রুপে স্বাগতম 🎉",
        "goodbye": "{name} গ্রুপ থেকে চলে গেলেন। বিদায় 👋",
        "warnings": {},   # user_id(str) -> count
        "banned": {},      # user_id(str) -> reason
        "ai_enabled": True,
        "antilink_enabled": True,
        "whitelist_links": []   # domains allowed, e.g. "t.me/yourchannel"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------- Helper ----------
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

# ---------- Welcome / Goodbye ----------
async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if str(member.id) in data["banned"]:
            try:
                await context.bot.ban_chat_member(update.effective_chat.id, member.id)
            except Exception:
                pass
            continue
        text = data["welcome"].format(name=member.mention_html(), group=update.effective_chat.title)
        await update.message.reply_html(text)

async def farewell_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.message.left_chat_member
    if member:
        text = data["goodbye"].format(name=member.full_name, group=update.effective_chat.title)
        await update.message.reply_text(text)

# ---------- Warning / Ban ----------
async def issue_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, target, reason: str):
    """Core warn logic — used by /warn command and by auto-mod. Bans at 3."""
    chat = update.effective_chat
    uid = str(target.id)
    data["warnings"][uid] = data["warnings"].get(uid, 0) + 1
    count = data["warnings"][uid]
    save_data(data)

    if count >= 3:
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            data["banned"][uid] = reason
            data["warnings"][uid] = 0
            save_data(data)
            await update.effective_chat.send_message(
                f"⛔ {target.mention_html()} কে ৩টি ওয়ার্নিং এর কারনে ব্যান করা হলো।\nকারণ: {reason}",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.effective_chat.send_message(f"ব্যান করতে সমস্যা হয়েছে: {e}")
    else:
        await update.effective_chat.send_message(
            f"⚠️ {target.mention_html()} কে ওয়ার্নিং দেওয়া হলো। ({count}/3)\nকারণ: {reason}",
            parse_mode="HTML"
        )

async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin(update, context, update.effective_user.id):
        await update.message.reply_text("শুধু গ্রুপ এডমিনরা এই কমান্ড ব্যবহার করতে পারবে।")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("যাকে ওয়ার্নিং দিতে চান তার মেসেজে রিপ্লাই দিয়ে /warn লিখুন।")
        return
    target = update.message.reply_to_message.from_user
    await issue_warning(update, context, target, "এডমিন কর্তৃক ম্যানুয়াল ওয়ার্নিং")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not await is_group_admin(update, context, update.effective_user.id):
        await update.message.reply_text("শুধু গ্রুপ এডমিনরা এই কমান্ড ব্যবহার করতে পারবে।")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("যাকে ব্যান দিতে চান তার মেসেজে রিপ্লাই দিয়ে /ban লিখুন।")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        data["banned"][str(target.id)] = "manual ban"
        save_data(data)
        await update.message.reply_html(f"⛔ {target.mention_html()} কে ব্যান করা হলো।")
    except Exception as e:
        await update.message.reply_text(f"সমস্যা: {e}")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("ব্যবহার: /unban <user_id>")
        return
    uid = context.args[0]
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, int(uid))
        data["banned"].pop(uid, None)
        save_data(data)
        await update.message.reply_text(f"✅ {uid} কে আনব্যান করা হলো।")
    except Exception as e:
        await update.message.reply_text(f"সমস্যা: {e}")

# ---------- Anti-link / Anti-promo auto-mod ----------
LINK_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|\S+\.(com|net|org|io|xyz|info|co|gg|me|app)\b)",
    re.IGNORECASE
)
PROMO_KEYWORDS = [
    "join our channel", "join now", "earn money", "free followers",
    "subscribe", "promo code", "click here", "limited offer",
    "চ্যানেলে জয়েন", "জয়েন করুন", "ফ্রি টাকা", "ইনকাম করুন", "প্রমো কোড",
    "লিংকে ক্লিক", "সাবস্ক্রাইব",
]

def _is_whitelisted(text: str) -> bool:
    wl = data.get("whitelist_links", [])
    return any(domain.lower() in text.lower() for domain in wl)

def message_has_link(msg) -> bool:
    text = msg.text or msg.caption or ""
    if LINK_PATTERN.search(text):
        return True
    entities = (msg.entities or []) + (msg.caption_entities or [])
    for ent in entities:
        if ent.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK, MessageEntityType.MENTION):
            return True
    return False

def message_is_promo(msg) -> bool:
    text = (msg.text or msg.caption or "").lower()
    return any(kw in text for kw in PROMO_KEYWORDS)

async def anti_link_automod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data.get("antilink_enabled", True):
        return
    msg = update.message
    if not msg or update.effective_chat.type not in ("group", "supergroup"):
        return
    user = update.effective_user
    if user.id == ADMIN_ID or user.is_bot:
        return
    if await is_group_admin(update, context, user.id):
        return

    text = msg.text or msg.caption or ""
    if _is_whitelisted(text):
        return

    is_forward = bool(msg.forward_origin or getattr(msg, "forward_from_chat", None) or getattr(msg, "forward_from", None))
    has_link = message_has_link(msg)
    is_promo = message_is_promo(msg)

    if not (is_forward or has_link or is_promo):
        return

    reason_parts = []
    if has_link:
        reason_parts.append("লিংক")
    if is_forward:
        reason_parts.append("ফরোয়ার্ড মেসেজ")
    if is_promo:
        reason_parts.append("প্রোমোশনাল কনটেন্ট")
    reason = " + ".join(reason_parts)

    try:
        await msg.delete()
    except Exception as e:
        logger.warning(f"delete failed: {e}")

    await issue_warning(update, context, user, reason)
    raise ApplicationHandlerStop  # stop further handlers (e.g. AI auto-reply) for this update

# ---------- Gemini AI auto reply ----------
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data.get("ai_enabled", True):
        return
    msg = update.message
    if not msg or not msg.text:
        return
    bot_username = context.bot.username
    is_reply_to_bot = (
        msg.reply_to_message
        and msg.reply_to_message.from_user
        and msg.reply_to_message.from_user.id == context.bot.id
    )
    mentioned = f"@{bot_username}" in msg.text if bot_username else False
    if not (is_reply_to_bot or mentioned):
        return

    prompt = msg.text.replace(f"@{bot_username}", "").strip() if bot_username else msg.text
    if not prompt:
        return
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    try:
        resp = model.generate_content(
            f"তুমি একজন বন্ধুত্বপূর্ণ বাংলা ভাষী টেলিগ্রাম গ্রুপ সহায়ক বট। সংক্ষেপে ও স্বাভাবিক বাংলায় উত্তর দাও।\n\nব্যবহারকারীর প্রশ্ন: {prompt}"
        )
        text = resp.text.strip() if resp.text else "দুঃখিত, উত্তর তৈরি করতে পারিনি।"
    except Exception as e:
        text = f"দুঃখিত, এআই উত্তর দিতে সমস্যা হয়েছে।"
        logger.error(f"Gemini error: {e}")
    await msg.reply_text(text)

# ---------- Admin Panel ----------
def admin_panel_markup():
    kb = [
        [InlineKeyboardButton("✏️ Welcome মেসেজ সেট", callback_data="set_welcome")],
        [InlineKeyboardButton("✏️ Goodbye মেসেজ সেট", callback_data="set_goodbye")],
        [InlineKeyboardButton("🚫 ব্যান লিস্ট দেখুন", callback_data="view_banned")],
        [InlineKeyboardButton("⚠️ ওয়ার্নিং লিস্ট দেখুন", callback_data="view_warnings")],
        [InlineKeyboardButton(
            "🤖 AI অটো-রিপ্লাই: " + ("ON ✅" if data.get("ai_enabled", True) else "OFF ❌"),
            callback_data="toggle_ai"
        )],
        [InlineKeyboardButton(
            "🔗 লিংক/প্রোমো অটো-ওয়ার্ন: " + ("ON ✅" if data.get("antilink_enabled", True) else "OFF ❌"),
            callback_data="toggle_antilink"
        )],
    ]
    return InlineKeyboardMarkup(kb)

async def ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু মেইন এডমিনের জন্য।")
        return
    await update.message.reply_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.edit_message_text("অনুমতি নেই।")
        return

    action = query.data
    if action == "set_welcome":
        context.user_data["awaiting"] = "welcome"
        await query.edit_message_text(
            "নতুন Welcome মেসেজ পাঠান। {name} আর {group} ব্যবহার করতে পারবেন।\n\nবর্তমান:\n" + data["welcome"]
        )
    elif action == "set_goodbye":
        context.user_data["awaiting"] = "goodbye"
        await query.edit_message_text(
            "নতুন Goodbye মেসেজ পাঠান। {name} আর {group} ব্যবহার করতে পারবেন।\n\nবর্তমান:\n" + data["goodbye"]
        )
    elif action == "view_banned":
        if not data["banned"]:
            txt = "কোনো ব্যান করা ইউজার নেই।"
        else:
            txt = "🚫 ব্যান লিস্ট:\n" + "\n".join(f"- {uid} ({reason})" for uid, reason in data["banned"].items())
        await query.edit_message_text(txt, reply_markup=admin_panel_markup())
    elif action == "view_warnings":
        if not data["warnings"]:
            txt = "কোনো ওয়ার্নিং নেই।"
        else:
            txt = "⚠️ ওয়ার্নিং লিস্ট:\n" + "\n".join(f"- {uid}: {c}" for uid, c in data["warnings"].items())
        await query.edit_message_text(txt, reply_markup=admin_panel_markup())
    elif action == "toggle_ai":
        data["ai_enabled"] = not data.get("ai_enabled", True)
        save_data(data)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "toggle_antilink":
        data["antilink_enabled"] = not data.get("antilink_enabled", True)
        save_data(data)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())

async def admin_text_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    if not awaiting or not is_admin(update.effective_user.id):
        return
    if awaiting == "welcome":
        data["welcome"] = update.message.text
        save_data(data)
        await update.message.reply_text("✅ Welcome মেসেজ সেট হয়েছে।")
    elif awaiting == "goodbye":
        data["goodbye"] = update.message.text
        save_data(data)
        await update.message.reply_text("✅ Goodbye মেসেজ সেট হয়েছে।")
    context.user_data["awaiting"] = None

async def whitelist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        current = ", ".join(data.get("whitelist_links", [])) or "খালি"
        await update.message.reply_text(f"ব্যবহার: /whitelist <domain>\nবর্তমান হোয়াইটলিস্ট: {current}")
        return
    domain = context.args[0].lower()
    wl = data.setdefault("whitelist_links", [])
    if domain in wl:
        wl.remove(domain)
        msg = f"❌ {domain} হোয়াইটলিস্ট থেকে বাদ দেওয়া হলো।"
    else:
        wl.append(domain)
        msg = f"✅ {domain} হোয়াইটলিস্টে যোগ হলো — এই লিংক আর ওয়ার্নিং খাবে না।"
    save_data(data)
    await update.message.reply_text(msg)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("বট চালু আছে ✅ গ্রুপে যোগ করুন এবং এডমিন করুন।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("ad", ad_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("whitelist", whitelist_cmd))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, farewell_member))

    app.add_handler(CallbackQueryHandler(admin_callback))

    # admin private text capture must run before general ai_reply
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # anti-link/promo/forward automod must run before AI auto-reply (same group, runs first = added first)
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
        anti_link_automod
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
