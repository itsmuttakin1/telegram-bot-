import os
import re
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatMemberHandler,
    ChatJoinRequestHandler, CallbackQueryHandler, ContextTypes, filters, ApplicationHandlerStop
)
from telegram.constants import MessageEntityType, ChatMemberStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# 3 jon admin access pabe
ADMIN_IDS = {5140546628, 7728010216, 8967715315}

DATA_FILE = "data.json"

PERMANENT_RULES = (
    "📜 Group Rules:\n"
    "❌ কোনো ধরনের Link দেওয়া যাবে না\n"
    "❌ অন্য Group/Channel-এর Link বা Promo নিষেধ\n"
    "❌ @Username বা চ্যানেলের Mention করা সম্পূর্ণ নিষেধ (শুধু Admin পারবে)\n"
    "❌ Spam করা যাবে না\n"
    "❌ Promotion করা যাবে না\n"
    "❌ অপ্রয়োজনীয় Message দেওয়া যাবে না\n\n"
    "⚠️ Rules ভাঙলে Message Delete + Restrict/Ban করা হতে পারে।\n\n"
    "🔥 New Viral Videos পেতে Group-এ Active থাকুন!\n\n"
    "❤️ Respect Everyone & Enjoy the Group!"
)

PERMANENT_WELCOME = (
    "✨ <b>স্বাগতম আমাদের গ্রুপে {name}</b> ✨\n\n"
    "🎬 নতুন সব ভাইরাল ও প্রিমিয়াম ভিডিও সবার আগে পেতে নিচের <b>Official Video Group</b> এ যুক্ত থাকুন!\n\n"
    "👇 নিচে ক্লিক করে এখনই জয়েন করুন:"
)

PERMANENT_GOODBYE = (
    "👋 <b>{name}</b>\n\n"
    "💰 <i>সে টাকা দিয়ে গ্রুপ কিনছে,</i>\n"
    "🔥 তাই তাকে এই গ্রুপ থেকে বের করে <b>প্রিমিয়াম গ্রুপে যুক্ত করা হয়েছে!</b> 👑"
)

MEMBER_NOTICE_CAPTION = (
    "📢 <b>সম্মানিত মেম্বারদের দৃষ্টি আকর্ষণ করছি!</b> 📢\n\n"
    "👋 আপনারা অনেকেই হয়তো নতুন যুক্ত হয়েছেন এবং আমাদের চ্যানেলের নিয়ম সম্পর্কে জানেন না:\n\n"
    "⏳ <b>পোস্ট স্থায়িত্ব:</b>\n"
    "আমাদের চ্যানেলে প্রতিটি ভিডিও সর্বোচ্চ <b>২ দিন (৪৮ ঘণ্টা)</b> পর্যন্ত রাখা হয়। এরপর পুরাতন ভিডিও অটোমেটিক ডিলিট করে নতুন এক্সক্লুসিভ ভিডিও যোগ করা হয়।\n\n"
    "⏰ <b>ভিডিও আপলোডের সময়সূচী:</b>\n"
    "প্রতিদিন <b>রাত ৮:০০ টা থেকে ৯:০০ টা</b> এবং <b>রাত ১২:০০ টায়</b> চ্যানেলে নতুন ভিডিও আপলোড করা হয়।\n\n"
    "⚠️ <b>সতর্কবার্তা:</b>\n"
    "চ্যানেল থেকে লিভ নেওয়ার আগে একবার ভেবে দেখবেন—এখানে কিন্তু সব <b>প্রিমিয়াম ও পেইড ভিডিও সম্পূর্ণ ফ্রিতে</b> দেওয়া হয়! 🔥\n\n"
    "❤️ একটিভ থাকুন এবং বন্ধুদের ইনভাইট করুন। ধন্যবাদ সবাইকে! ✨"
)

DEFAULT_PERMANENT_BUTTON = {
    "text": "পাবলিক গ্রুপ",
    "url": "https://t.me/+f0vawMiFO75mNDM1"
}

CLEAN_CHANNEL_ID = -1004422557441
NOTIFY_GROUP_ID = -1004427297260

PERMANENT_CHANNELS = {
    -1004427297260: "Full Video 👇\nhttps://breedsmuteexams.com/ja1gp1y0?key=5ad4cd88923c063b5b21a813a4822ed8",
    CLEAN_CHANNEL_ID: "Full Video 👇\nhttps://breedsmuteexams.com/ja1gp1y0?key=5ad4cd88923c063b5b21a813a4822ed8",
    -1003529904183: "Full Video 👇\nhttps://auctionr.org/4/f7aef1875c5940fd01991dfe705874c7"
}

def get_welcome_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Official Video Group", url="https://t.me/+9f4oDOMukMhmNjU1")],
        [InlineKeyboardButton("পাবলিক গ্রুপ", url="https://t.me/+f0vawMiFO75mNDM1")],
        [InlineKeyboardButton("Invite Friend", url="https://t.me/+N4Qum_s5qFQ3NWI1")]
    ])

def get_group_action_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("পাবলিক গ্রুপ", url="https://t.me/+f0vawMiFO75mNDM1")],
        [InlineKeyboardButton("Invite Friend", url="https://t.me/+N4Qum_s5qFQ3NWI1")]
    ])

DEFAULT_DATA = {
    "warnings": {},          
    "banned": {},            
    "active_groups": [],     
    "antilink_enabled": True,
    "auto_approve_enabled": True,
    "channel_clean_enabled": True,
    "post_to_clean_channel": True, # -1004422557441 channel-e post on/off
    "clean_channel_posts": [],     
    "whitelist_links": [],
    "saved_caption": "",     
}

def load_data():
    merged = dict(DEFAULT_DATA)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged.update(saved)
            if not isinstance(merged.get("active_groups"), list):
                merged["active_groups"] = []
            if not isinstance(merged.get("clean_channel_posts"), list):
                merged["clean_channel_posts"] = []
        except Exception as e:
            logger.error(f"Error loading data.json: {e}")
    return merged

def save_data(data_obj):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_obj, f, ensure_ascii=False, indent=2)

data = load_data()

recent_greets = {}

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False

async def delete_message_after_delay(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE, delay_seconds: int = 60):
    try:
        await asyncio.sleep(delay_seconds)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.debug(f"Auto delete message failed: {e}")

def register_group(chat_id: int):
    groups = data.setdefault("active_groups", [])
    if chat_id not in groups:
        groups.append(chat_id)
        save_data(data)

# ---------- Auto Approve Join Request ----------
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

# ---------- Welcome / Goodbye ----------
async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return

    register_group(chat.id)

    result = update.chat_member
    if not result:
        return

    user = result.new_chat_member.user
    if user.is_bot:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    now = time.time()

    if old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED) and new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
        key = (chat.id, user.id, "welcome")
        if now - recent_greets.get(key, 0) < 10:
            return
        recent_greets[key] = now

        if str(user.id) in data["banned"]:
            try:
                await context.bot.ban_chat_member(chat.id, user.id)
            except Exception:
                pass
            return
        
        text = PERMANENT_WELCOME.format(name=user.mention_html())
        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_welcome_markup()
            )
            asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))
        except Exception as e:
            logger.error(f"Welcome message error in {chat.id}: {e}")

    elif old_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.RESTRICTED) and new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        key = (chat.id, user.id, "goodbye")
        if now - recent_greets.get(key, 0) < 10:
            return
        recent_greets[key] = now

        text = PERMANENT_GOODBYE.format(name=user.full_name or "মেম্বার")
        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_group_action_markup()
            )
            asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))
        except Exception as e:
            logger.error(f"Goodbye message error in {chat.id}: {e}")

# ---------- Periodic Reminders ----------
async def periodic_channel_reminder(context: ContextTypes.DEFAULT_TYPE):
    groups = data.get("active_groups", [])
    text = (
        "🔥 <b>আমাদের Official Video চ্যানেলে জয়েন করুন!</b> 🔥\n\n"
        "সব আনকাট, স্পেশাল ও ভাইরাল প্রিমিয়াম ভিডিও ফ্রিতে পেতে আমাদের অফিশিয়াল চ্যানেলে যুক্ত থাকুন।\n"
        "নিচের বাটনে ক্লিক করে এখনই চ্যানেলে জয়েন করে নিন 👇"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Join Official Video Channel", url="https://t.me/+9f4oDOMukMhmNjU1")],
        [InlineKeyboardButton("পাবলিক গ্রুপ", url="https://t.me/+f0vawMiFO75mNDM1")]
    ])

    for chat_id in list(groups):
        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup
            )
            asyncio.create_task(delete_message_after_delay(chat_id, sent_msg.message_id, context, 300))
        except Exception as e:
            logger.debug(f"Failed to send channel reminder in {chat_id}: {e}")

async def periodic_invite_reminder(context: ContextTypes.DEFAULT_TYPE):
    groups = data.get("active_groups", [])
    text = (
        "📢 <b>বন্ধুদের ইনভাইট করুন!</b> 🔥\n\n"
        "আমাদের গ্রুপের নতুন সব ভাইরাল ও প্রিমিয়াম আপডেট পেতে আপনার বন্ধুদেরও যুক্ত করুন।\n"
        "নিচের বাটনে ক্লিক করে বন্ধুদের সাথে লিঙ্ক শেয়ার করুন 👇"
    )
    markup = get_group_action_markup()

    for chat_id in list(groups):
        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup
            )
            asyncio.create_task(delete_message_after_delay(chat_id, sent_msg.message_id, context, 300))
        except Exception as e:
            logger.debug(f"Failed to send invite reminder in {chat_id}: {e}")

# ---------- 2 Days Channel Auto-Clean Service ----------
async def channel_post_cleaner_job(context: ContextTypes.DEFAULT_TYPE):
    if not data.get("channel_clean_enabled", True):
        return

    posts = data.get("clean_channel_posts", [])
    if not posts:
        return

    now = time.time()
    two_days_seconds = 2 * 24 * 3600

    expired_posts = [p for p in posts if now - p.get("timestamp", now) >= two_days_seconds]
    if not expired_posts:
        return

    dates_deleted = {}
    remaining_posts = []

    for p in posts:
        if p in expired_posts:
            mid = p.get("message_id")
            d_str = p.get("date_str", "পূর্বের")
            try:
                await context.bot.delete_message(chat_id=CLEAN_CHANNEL_ID, message_id=mid)
            except Exception as e:
                logger.debug(f"Could not delete old post {mid}: {e}")
            dates_deleted[d_str] = dates_deleted.get(d_str, 0) + 1
        else:
            remaining_posts.append(p)

    data["clean_channel_posts"] = remaining_posts
    save_data(data)

    for date_str, count in dates_deleted.items():
        try:
            msg_text = (
                f"🗑️ <b>ক্লিন সার্ভিস আপডেট:</b>\n\n"
                f"📅 <b>{date_str}</b> তারিখের সকল পোস্ট ({count} টি) সফলভাবে চ্যানেল থেকে ডিলিট করা হয়েছে।"
            )
            await context.bot.send_message(
                chat_id=NOTIFY_GROUP_ID,
                text=msg_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify group {NOTIFY_GROUP_ID}: {e}")

# ---------- Warning / Ban ----------
async def issue_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, target, reason: str):
    chat = update.effective_chat
    uid = str(target.id)
    warn_key = f"{chat.id}:{uid}"
    data["warnings"][warn_key] = data["warnings"].get(warn_key, 0) + 1
    count = data["warnings"][warn_key]
    save_data(data)

    if count >= 3:
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            data["banned"][uid] = {"reason": reason, "chat_id": chat.id}
            data["warnings"][warn_key] = 0
            save_data(data)
            await chat.send_message(
                f"⛔ {target.mention_html()} কে ৩টি ওয়ার্নিং এর কারনে ব্যান করা হলো।\nকারণ: {reason}",
                parse_mode="HTML"
            )
        except Exception as e:
            await chat.send_message(f"ব্যান করতে সমস্যা হয়েছে: {e}")
    else:
        warn_text = (
            f"⚠️ {target.mention_html()} কে ওয়ার্নিং দেওয়া হলো। ({count}/3)\n"
            f"কারণ: {reason}\n\n"
            f"{PERMANENT_RULES}"
        )
        try:
            await chat.send_message(warn_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to send warn text: {e}")

async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin(update, context, update.effective_user.id) and not is_admin(update.effective_user.id):
        await update.message.reply_text("শুধু গ্রুপ এডমিনরা এই কমান্ড ব্যবহার করতে পারবে।")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("যাকে ওয়ার্নিং দিতে চান তার মেসেজে রিপ্লাই দিয়ে /warn লিখুন।")
        return
    target = update.message.reply_to_message.from_user
    await issue_warning(update, context, target, "এডমিন কর্তৃক ম্যানুয়াল ওয়ার্নিং")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not await is_group_admin(update, context, update.effective_user.id) and not is_admin(update.effective_user.id):
        await update.message.reply_text("শুধু গ্রুপ এডমিনরা এই কমান্ড ব্যবহার করতে পারবে।")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("যাকে ব্যান দিতে চান তার মেসেজে রিপ্লাই দিয়ে /ban লিখুন।")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        data["banned"][str(target.id)] = {"reason": "manual ban", "chat_id": chat.id}
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
    ban_info = data["banned"].get(uid)
    chat_id = update.effective_chat.id
    if isinstance(ban_info, dict) and ban_info.get("chat_id"):
        chat_id = ban_info["chat_id"]
    try:
        await context.bot.unban_chat_member(chat_id, int(uid))
        data["banned"].pop(uid, None)
        save_data(data)
        await update.message.reply_text(f"✅ {uid} কে আনব্যান করা হলো।")
    except Exception as e:
        await update.message.reply_text(f"সমস্যা: {e}")

# ---------- Anti-link / Anti-mention / Inbox / Taka & Bad Words Filter ----------
LINK_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|\b[a-zA-Z0-9\-]+\.(com|net|org|io|xyz|info|co|gg|me|app|link|site|live|online|store|tech|top|pro|biz|tv)\b)",
    re.IGNORECASE
)
PROMO_KEYWORDS = [
    "join our channel", "join now", "earn money", "free followers",
    "subscribe", "promo code", "click here", "limited offer",
    "চ্যানেলে জয়েন", "জয়েন করুন", "ফ্রি টাকা", "ইনকাম করুন", "প্রমো কোড",
    "লিংকে ক্লিক", "সাবস্ক্রাইব",
]

INBOX_KEYWORDS_PATTERN = re.compile(
    r"\b(inbox|dm|ib|pm|ইনবক্স|ইনবক্সে|ইনবক্স করো|ইনবক্স করুন|dm me|inbox me)\b",
    re.IGNORECASE
)

MENTION_PATTERN = re.compile(r"@[a-zA-Z0-9_]{3,}", re.IGNORECASE)

BAD_WORDS_PATTERN = re.compile(
    r"(\b\d+\s*(tk|টাকা|taka|bdt)\b|"
    r"\b(tk|taka|bdt|টাকা|টাকায়|টাকায়|দাম কত|কত টাকা|বিক্রি|সেল)\b|"
    r"\b(dud|dudh|dudhe|দুধ|দুদ|ভোদা|ভুদা|খানকি|মাদারচোদ|চুদা|চুদি)\b)",
    re.IGNORECASE
)

def _is_whitelisted(text: str) -> bool:
    wl = data.get("whitelist_links", [])
    return any(domain.lower() in text.lower() for domain in wl)

def message_has_link(msg) -> bool:
    text = msg.text or msg.caption or ""
    if LINK_PATTERN.search(text):
        return True
    entities = (msg.entities or []) + (msg.caption_entities or [])
    for ent in entities:
        if ent.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK):
            return True
    return False

def message_has_mention(msg) -> bool:
    text = msg.text or msg.caption or ""
    if MENTION_PATTERN.search(text):
        return True
    entities = (msg.entities or []) + (msg.caption_entities or [])
    for ent in entities:
        if ent.type in (MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION):
            return True
    return False

def message_is_promo(msg) -> bool:
    text = (msg.text or msg.caption or "").lower()
    return any(kw in text for kw in PROMO_KEYWORDS)

def is_forwarded_message(msg) -> bool:
    if getattr(msg, "forward_origin", None) is not None:
        return True
    if getattr(msg, "forward_from", None) is not None:
        return True
    if getattr(msg, "forward_from_chat", None) is not None:
        return True
    if getattr(msg, "forward_sender_name", None) is not None:
        return True
    return False

async def anti_link_automod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data.get("antilink_enabled", True):
        return
    msg = update.message
    if not msg or update.effective_chat.type not in ("group", "supergroup"):
        return

    register_group(update.effective_chat.id)

    if msg.is_automatic_forward or getattr(msg, "sender_chat", None) is not None:
        return

    user = update.effective_user
    if not user or is_admin(user.id) or user.is_bot:
        return
    if await is_group_admin(update, context, user.id):
        return

    text = msg.text or msg.caption or ""

    if INBOX_KEYWORDS_PATTERN.search(text) or BAD_WORDS_PATTERN.search(text):
        try:
            await msg.delete()
        except Exception as e:
            logger.warning(f"Bad words / Inbox delete failed: {e}")
        raise ApplicationHandlerStop

    if message_has_mention(msg):
        try:
            await msg.delete()
        except Exception as e:
            logger.warning(f"Mention delete failed: {e}")
        raise ApplicationHandlerStop

    if _is_whitelisted(text):
        return

    is_fwd = is_forwarded_message(msg)
    has_lnk = message_has_link(msg)
    is_prm = message_is_promo(msg)

    if not (is_fwd or has_lnk or is_prm):
        return

    reason_parts = []
    if has_lnk:
        reason_parts.append("লিংক")
    if is_fwd:
        reason_parts.append("ফরোয়ার্ড মেসেজ")
    if is_prm:
        reason_parts.append("প্রোমোশনাল কনটেন্ট")
    reason = " + ".join(reason_parts)

    try:
        await msg.delete()
    except Exception as e:
        logger.warning(f"Auto-mod delete failed: {e}")

    await issue_warning(update, context, user, reason)
    raise ApplicationHandlerStop

# ---------- Multi-Channel Post System ----------
def _post_draft(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    drafts = context.bot_data.setdefault("post_draft", {})
    return drafts.get(user_id)

def post_editor_markup(draft):
    rows = []
    for i, btn in enumerate(draft["buttons"]):
        if i == 0 and btn.get("url") == DEFAULT_PERMANENT_BUTTON["url"]:
            rows.append([InlineKeyboardButton(f"🔒 {btn['text']} (স্থায়ী)", callback_data="perm_btn_info")])
        else:
            rows.append([InlineKeyboardButton(f"❌ বাটন মুছুন: {btn['text']}", callback_data=f"post_rm_{i}")])
    
    rows.append([InlineKeyboardButton("✏️ এক্সট্রা টেক্সট যোগ/বদল", callback_data="post_set_caption")])
    if len(draft["buttons"]) < 5:
        rows.append([InlineKeyboardButton("➕ আরও বাটন যোগ করুন", callback_data="post_add_btn")])
    rows.append([InlineKeyboardButton("✅ চ্যানেলে পোস্ট করুন", callback_data="post_publish")])
    rows.append([InlineKeyboardButton("❌ বাতিল করুন", callback_data="post_cancel")])
    return InlineKeyboardMarkup(rows)

def post_preview_text(draft):
    extra = draft.get("caption", "").strip()
    extra_txt = f"\n📝 <b>অতিরিক্ত টেক্সট:</b> {extra}" if extra else ""

    ch2_status = "চালু ✅" if data.get("post_to_clean_channel", True) else "বন্ধ ❌"
    lines = [
        "📋 <b>পোস্ট প্রিভিউ:</b>\n",
        f"🎯 <b>চ্যানেল ১ (-1004427297260):</b>\n{PERMANENT_CHANNELS[-1004427297260]}\n",
        f"🎯 <b>চ্যানেল ২ ({CLEAN_CHANNEL_ID}):</b> [{ch2_status}]\n{PERMANENT_CHANNELS[CLEAN_CHANNEL_ID]}\n",
        f"🎯 <b>চ্যানেল ৩ (-1003529904183):</b>\n{PERMANENT_CHANNELS[-1003529904183]}",
        extra_txt,
        "\n🔘 <b>যুক্ত করা বাটন:</b>"
    ]
    for b in draft["buttons"]:
        lines.append(f"  • {b['text']} ➔ {b['url']}")
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
        "ভিডিও অথবা ছবি পাঠান যেটা চ্যানেলে পোস্ট করতে চান।\n"
        "প্রতিটি চ্যানেলে নিজস্ব লিঙ্ক সহ ক্যাপশন চলে যাবে।\n"
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

    extra_caption = msg.caption or data.get("saved_caption", "")
    
    draft = {
        "kind": kind,
        "file_id": file_id,
        "caption": extra_caption,
        "buttons": [dict(DEFAULT_PERMANENT_BUTTON)]
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

# ---------- Admin Panel & Menus ----------
def admin_panel_markup():
    auto_appr = "ON ✅" if data.get("auto_approve_enabled", True) else "OFF ❌"
    antilink = "ON ✅" if data.get("antilink_enabled", True) else "OFF ❌"
    clean_svc = "ON ✅" if data.get("channel_clean_enabled", True) else "OFF ❌"
    ch2_post = "ON ✅" if data.get("post_to_clean_channel", True) else "OFF ❌"

    kb = [
        [InlineKeyboardButton("🚫 ব্যান লিস্ট দেখুন", callback_data="view_banned")],
        [InlineKeyboardButton("⚠️ ওয়ার্নিং লিস্ট দেখুন", callback_data="view_warnings")],
        [InlineKeyboardButton(f"🔗 অটো-ওয়ার্ন (লিংক/স্প্যাম): {antilink}", callback_data="toggle_antilink")],
        [InlineKeyboardButton(f"⚡ অটো জয়েন এপ্রুভ: {auto_appr}", callback_data="toggle_auto_approve")],
        [InlineKeyboardButton(f"🧹 চ্যানেল ক্লিন সার্ভিস: {clean_svc}", callback_data="toggle_clean_service")],
        [InlineKeyboardButton(f"📢 চ্যানেল ২ পোস্ট ({CLEAN_CHANNEL_ID}): {ch2_post}", callback_data="toggle_ch2_post")],
        [InlineKeyboardButton("🖼 Message for Member (গ্রুপ+চ্যানেল)", callback_data="send_member_notice")],
        [InlineKeyboardButton("🎙 Voice Message (গ্রুপ+চ্যানেল)", callback_data="send_voice_notice")],
        [InlineKeyboardButton("🎯 স্থায়ী চ্যানেল ও ক্যাপশন দেখুন", callback_data="view_channels_status")],
        [InlineKeyboardButton("📢 চ্যানেলে নতুন পোস্ট বানান", callback_data="new_post")],
    ]
    return InlineKeyboardMarkup(kb)

async def get_channels_status_markup(context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")]]
    lines = ["🎯 <b>স্থায়ী টার্গেট চ্যানেল ও ক্যাপশন লিস্ট:</b>\n"]

    for ch_id, default_cap in PERMANENT_CHANNELS.items():
        admin_status = "❌ Admin নেই / Error"
        try:
            me = await context.bot.get_chat_member(ch_id, context.bot.id)
            if me.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                admin_status = "✅ Admin সক্রিয়"
        except Exception:
            admin_status = "❌ Not Found / Admin নেই"

        extra_note = ""
        if ch_id == CLEAN_CHANNEL_ID:
            is_on = "পোস্ট চালু ✅" if data.get("post_to_clean_channel", True) else "পোস্ট বন্ধ ❌"
            extra_note = f" (২ দিন পর ক্লিন | {is_on})"

        lines.append(
            f"📍 <code>{ch_id}</code>{extra_note} ➔ <b>{admin_status}</b>\n"
            f"📝 <i>ক্যাপশন:</i>\n{default_cap}\n"
        )

    return "\n".join(lines), InlineKeyboardMarkup(kb)

def get_banned_list_markup():
    banned_items = data.get("banned", {})
    if not banned_items:
        text = "🚫 <b>ব্যান লিস্ট:</b>\nকোনো ব্যান করা ইউজার নেই।"
        kb = [[InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")]]
        return text, InlineKeyboardMarkup(kb)

    lines = ["🚫 <b>ব্যান লিস্ট (আনব্যান করতে বাটনে চাপুন):</b>\n"]
    kb = []
    for uid, info in banned_items.items():
        reason = info.get("reason", "unknown") if isinstance(info, dict) else str(info)
        lines.append(f"• ID: <code>{uid}</code>\n  কারণ: {reason}")
        kb.append([InlineKeyboardButton(f"🔓 Unban {uid}", callback_data=f"unban_user_{uid}")])

    kb.append([InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")])
    return "\n".join(lines), InlineKeyboardMarkup(kb)

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
    if action in ("new_post", "post_add_btn", "post_set_caption", "post_cancel", "post_publish") or action.startswith("post_rm_") or action == "perm_btn_info":
        if action == "perm_btn_info":
            await query.answer("এই বাটনটি ডিফল্ট স্থায়ী বাটন, সরানো যাবে না।", show_alert=True)
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
                "ক্যাপশনের সাথে অতিরিক্ত কোনো টেক্সট যোগ করতে চাইলে লিখে পাঠান:\n"
                "(মুছে ফেলতে চাইলে <code>clear</code> লিখে পাঠান)",
                parse_mode="HTML"
            )
        elif action == "post_add_btn":
            if len(draft["buttons"]) >= 5:
                await query.answer("সর্বোচ্চ ৫টি বাটন যোগ করা যাবে।", show_alert=True)
                return
            context.user_data["awaiting"] = "post_button"
            await query.edit_message_text(
                post_preview_text(draft) + "\n\nনতুন বাটন এই ফরম্যাটে পাঠান:\nবাটন নাম | লিংক\n\nউদাহরণ:\nWatch Now | https://t.me/yourchannel",
                parse_mode="HTML"
            )
        elif action.startswith("post_rm_"):
            idx = int(action.replace("post_rm_", ""))
            if 0 < idx < len(draft["buttons"]):
                draft["buttons"].pop(idx)
            await query.edit_message_text(post_preview_text(draft), reply_markup=post_editor_markup(draft), parse_mode="HTML")
        elif action == "post_cancel":
            context.bot_data.setdefault("post_draft", {})[user_id] = None
            context.user_data["awaiting"] = None
            await query.edit_message_text("❌ পোস্ট বাতিল করা হয়েছে।")
        elif action == "post_publish":
            markup = None
            if draft["buttons"]:
                rows = [[InlineKeyboardButton(b["text"], url=b["url"])] for b in draft["buttons"]]
                markup = InlineKeyboardMarkup(rows)

            success_count, fail_count = 0, 0
            extra_caption = draft.get("caption", "").strip()

            bd_tz = timezone(timedelta(hours=6))
            today_date_str = datetime.now(bd_tz).strftime("%d-%m-%Y")

            # Check if CLEAN_CHANNEL_ID is allowed to receive post
            allow_clean_post = data.get("post_to_clean_channel", True)

            for ch_id, base_caption in PERMANENT_CHANNELS.items():
                # Jodi post_to_clean_channel OFF thake tahole CLEAN_CHANNEL_ID skip korbe
                if ch_id == CLEAN_CHANNEL_ID and not allow_clean_post:
                    continue

                final_caption = f"{extra_caption}\n\n{base_caption}" if extra_caption else base_caption
                try:
                    if draft["kind"] == "video":
                        sent_msg = await context.bot.send_video(
                            chat_id=ch_id, video=draft["file_id"],
                            caption=final_caption, reply_markup=markup
                        )
                    else:
                        sent_msg = await context.bot.send_photo(
                            chat_id=ch_id, photo=draft["file_id"],
                            caption=final_caption, reply_markup=markup
                        )
                    success_count += 1

                    if ch_id == CLEAN_CHANNEL_ID and sent_msg:
                        clean_posts = data.setdefault("clean_channel_posts", [])
                        clean_posts.append({
                            "message_id": sent_msg.message_id,
                            "timestamp": time.time(),
                            "date_str": today_date_str
                        })
                        save_data(data)

                except Exception as e:
                    logger.error(f"Failed to post in {ch_id}: {e}")
                    fail_count += 1

            context.bot_data.setdefault("post_draft", {})[user_id] = None
            
            again_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 আরেকটি পোস্ট করুন", callback_data="new_post")],
                [InlineKeyboardButton("🛠 অ্যাডমিন প্যানেল", callback_data="back_to_panel")]
            ])
            await query.edit_message_text(
                f"✅ পোস্ট প্রক্রিয়া সম্পন্ন!\n\n"
                f"সফল হয়েছে: {success_count} টি চ্যানেলে\n"
                f"ব্যর্থ হয়েছে: {fail_count} টি চ্যানেলে",
                reply_markup=again_markup
            )
        return

    # Panel Navigation
    if action == "back_to_panel":
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "view_channels_status":
        text, markup = await get_channels_status_markup(context)
        await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
    elif action == "view_banned":
        text, markup = get_banned_list_markup()
        await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
    elif action.startswith("unban_user_"):
        target_uid = action.replace("unban_user_", "")
        ban_info = data.get("banned", {}).get(target_uid)
        
        if isinstance(ban_info, dict) and ban_info.get("chat_id"):
            try:
                await context.bot.unban_chat_member(ban_info["chat_id"], int(target_uid))
            except Exception as e:
                logger.warning(f"Failed to unban {target_uid}: {e}")

        data.get("banned", {}).pop(target_uid, None)
        save_data(data)
        await query.answer(f"✅ ইউজার {target_uid} কে আনব্যান করা হয়েছে!", show_alert=True)
        text, markup = get_banned_list_markup()
        await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
    elif action == "view_warnings":
        if not data["warnings"]:
            txt = "কোনো ওয়ার্নিং নেই।"
        else:
            txt = "⚠️ ওয়ার্নিং লিস্ট:\n" + "\n".join(f"- {k}: {c}" for k, c in data["warnings"].items() if c > 0)
        await query.edit_message_text(txt, reply_markup=admin_panel_markup())
    elif action == "toggle_antilink":
        data["antilink_enabled"] = not data.get("antilink_enabled", True)
        save_data(data)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
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
    elif action == "toggle_ch2_post":
        data["post_to_clean_channel"] = not data.get("post_to_clean_channel", True)
        save_data(data)
        status_txt = "চালু" if data["post_to_clean_channel"] else "বন্ধ"
        await query.answer(f"📢 চ্যানেল ২ পোস্ট {status_txt} করা হয়েছে!", show_alert=True)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())

    # Send 1.jpg to groups and permanent channels
    elif action == "send_member_notice":
        photo_path = "1.jpg"
        if not os.path.exists(photo_path):
            await query.answer("❌ 1.jpg ফাইলটি পাওয়া যায়নি!", show_alert=True)
            return

        targets = []
        for g in data.get("active_groups", []):
            if g not in targets:
                targets.append(g)
        for c in PERMANENT_CHANNELS.keys():
            if c not in targets:
                targets.append(c)

        if not targets:
            await query.answer("❌ কোনো এক্টিভ গ্রুপ বা চ্যানেল পাওয়া যায়নি!", show_alert=True)
            return

        success, fail = 0, 0
        markup = get_welcome_markup()

        with open(photo_path, "rb") as pf:
            photo_bytes = pf.read()

        for cid in targets:
            try:
                await context.bot.send_photo(
                    chat_id=cid,
                    photo=photo_bytes,
                    caption=MEMBER_NOTICE_CAPTION,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to send 1.jpg to {cid}: {e}")
                fail += 1

        await query.answer(f"✅ ফটো নোটিশ পাঠানো সম্পন্ন!\nসফল: {success} টি, ব্যর্থ: {fail} টি", show_alert=True)

    # Send telegram.ogg ONCE per target
    elif action == "send_voice_notice":
        voice_path = "telegram.ogg"
        if not os.path.exists(voice_path):
            await query.answer("❌ telegram.ogg ফাইলটি পাওয়া যায়নি!", show_alert=True)
            return

        targets = []
        for g in data.get("active_groups", []):
            if g not in targets:
                targets.append(g)
        for c in PERMANENT_CHANNELS.keys():
            if c not in targets:
                targets.append(c)

        if not targets:
            await query.answer("❌ কোনো এক্টিভ গ্রুপ বা চ্যানেল পাওয়া যায়নি!", show_alert=True)
            return

        success, fail = 0, 0
        markup = get_welcome_markup()

        try:
            with open(voice_path, "rb") as vf:
                voice_data = vf.read()
        except Exception as e:
            await query.answer(f"❌ অডিও ফাইল পড়তে সমস্যা: {e}", show_alert=True)
            return

        for cid in targets:
            try:
                await context.bot.send_voice(
                    chat_id=cid,
                    voice=voice_data,
                    caption="🎙 <b>গ্রুপ ও চ্যানেলের সকল মেম্বার অবশ্যই ভয়েসটি শুনুন!</b> 👇",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                success += 1
            except Exception as e:
                logger.warning(f"send_voice failed for {cid}: {e}, trying send_audio once...")
                try:
                    await context.bot.send_audio(
                        chat_id=cid,
                        audio=voice_data,
                        title="Voice Notice",
                        caption="🎙 <b>গ্রুপ ও চ্যানেলের সকল মেম্বার অবশ্যই ভয়েসটি শুনুন!</b> 👇",
                        parse_mode="HTML",
                        reply_markup=markup
                    )
                    success += 1
                except Exception as e2:
                    logger.error(f"Failed to send voice/audio to {cid}: {e2}")
                    fail += 1

        await query.answer(f"✅ ভয়েস মেসেজ পাঠানো সম্পন্ন!\nসফল: {success} টি, ব্যর্থ: {fail} টি", show_alert=True)

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
            await update.message.reply_text("✅ অতিরিক্ত টেক্সট মুছে ফেলা হয়েছে।")
        else:
            draft["caption"] = update.message.text
            await update.message.reply_text("✅ অতিরিক্ত টেক্সট সেট করা হয়েছে।")
        await update.message.reply_html(post_preview_text(draft), reply_markup=post_editor_markup(draft))
        context.user_data["awaiting"] = None
        raise ApplicationHandlerStop

    elif awaiting == "post_button":
        draft = _post_draft(context, user_id)
        if not draft:
            await update.message.reply_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            context.user_data["awaiting"] = None
            raise ApplicationHandlerStop
        raw = update.message.text.strip()
        if "|" not in raw:
            await update.message.reply_text("❌ ফরম্যাট ভুল। এভাবে পাঠান: বাটন নাম | লিংক")
            context.user_data["awaiting"] = "post_button"
            return
        btn_text, btn_url = raw.split("|", 1)
        btn_text, btn_url = btn_text.strip(), btn_url.strip()
        if not (btn_url.startswith("http://") or btn_url.startswith("https://") or btn_url.startswith("t.me/") or btn_url.startswith("tg://")):
            await update.message.reply_text("❌ লিংক সঠিক ফরম্যাটে দিন (http:// বা https:// দিয়ে শুরু)।")
            context.user_data["awaiting"] = "post_button"
            return
        if btn_url.startswith("t.me/"):
            btn_url = "https://" + btn_url
        if len(draft["buttons"]) >= 5:
            await update.message.reply_text("সর্বোচ্চ ৫টি বাটন যোগ করা যাবে।")
        else:
            draft["buttons"].append({"text": btn_text or "Button", "url": btn_url})
        await update.message.reply_html(post_preview_text(draft), reply_markup=post_editor_markup(draft))
        context.user_data["awaiting"] = None
        raise ApplicationHandlerStop

    context.user_data["awaiting"] = None
    raise ApplicationHandlerStop

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

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("ad", ad_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("whitelist", whitelist_cmd))
    app.add_handler(CommandHandler("post", post_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    app.add_handler(ChatJoinRequestHandler(auto_approve_request))
    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER))

    app.add_handler(CallbackQueryHandler(admin_callback))

    app.add_handler(MessageHandler(
        (filters.VIDEO | filters.PHOTO) & filters.ChatType.PRIVATE, post_video_capture
    ))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # Groups automod
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & ~filters.COMMAND,
        anti_link_automod
    ))

    if app.job_queue:
        app.job_queue.run_repeating(periodic_invite_reminder, interval=1800, first=60)
        app.job_queue.run_repeating(periodic_channel_reminder, interval=3300, first=120)
        app.job_queue.run_repeating(channel_post_cleaner_job, interval=600, first=30)

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
