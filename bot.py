import os
import re
import json
import time
import asyncio
import logging
import threading
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

# Sudhu ei 2 jon admin access pabe
ADMIN_IDS = {5140546628, 7728010216}

DATA_FILE = "data.json"

PERMANENT_RULES = (
    "📜 Group Rules:\n"
    "❌ কোনো ধরনের Link দেওয়া যাবে না\n"
    "❌ অন্য Group/Channel-এর Link নিষেধ\n"
    "❌ Spam করা যাবে না\n"
    "❌ Promotion করা যাবে না\n"
    "❌ অপ্রয়োজনীয় Message দেওয়া যাবে না\n\n"
    "⚠️ Rules ভাঙলে Message Delete + Restrict/Ban করা হতে পারে।\n\n"
    "🔥 New Viral Videos পেতে Group-এ Active থাকুন!\n\n"
    "❤️ Respect Everyone & Enjoy the Group!"
)

PERMANENT_WELCOME = (
    "✨ <b>স্বাগতম আমাদের গ্রুপে {name}</b> ✨\n\n"
    "⚠️ <i>চ্যানেল থেকে বের হওয়ার আগে ভেবে বের হবেন!</i>\n"
    "💎 কারণ <b>প্রিমিয়াম ভিডিও ফ্রিতে</b> দেয়া হয় এই চ্যানেলে।\n\n"
    "👉 তাই যাদের ফ্রিতে দরকার নাই তারা বের হয়ে যান, এটা সম্পূর্ণ আপনার ইচ্ছা! 🚀"
)

PERMANENT_GOODBYE = (
    "👋 <b>{name}</b>\n\n"
    "💰 <i>সে টাকা দিয়ে গ্রুপ কিনছে,</i>\n"
    "🔥 তাই তাকে এই গ্রুপ থেকে বের করে <b>প্রিমিয়াম গ্রুপে যুক্ত করা হয়েছে!</b> 👑"
)

# Shob post-e default bhabe ei button thakbe
DEFAULT_PERMANENT_BUTTON = {
    "text": "পাবলিক গ্রুপ",
    "url": "https://t.me/+f0vawMiFO75mNDM1"
}

# Shudhu ei 2-ti permanent channel-e post jabe
PERMANENT_CHANNELS = {
    -1004427297260: "Full Video   https://breedsmuteexams.com/ja1gp1y0?key=5ad4cd88923c063b5b21a813a4822ed8",
    -1004422557441: "Full Video   https://breedsmuteexams.com/ja1gp1y0?key=5ad4cd88923c063b5b21a813a4822ed8"
}

# Welcome, Goodbye ar periodic message-er permanent buttons
def get_group_action_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("পাবলিক গ্রুপ", url="https://t.me/+f0vawMiFO75mNDM1")],
        [InlineKeyboardButton("Invite Friend", url="https://t.me/+N4Qum_s5qFQ3NWI1")]
    ])

DEFAULT_DATA = {
    "warnings": {},          # "chat_id:user_id" -> count
    "banned": {},            # user_id(str) -> {"reason": str, "chat_id": int/str}
    "active_groups": [],     # active group ids for periodic invite reminders
    "antilink_enabled": True,
    "auto_approve_enabled": True,
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

# Track active groups
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

# ---------- Welcome / Goodbye (Duplicate Protected + Auto-Delete) ----------
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

    # User Joined
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
                reply_markup=get_group_action_markup()
            )
            asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))
        except Exception as e:
            logger.error(f"Welcome message error in {chat.id}: {e}")

    # User Left
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

# ---------- Periodic Invite Reminder (Only Groups) ----------
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

# ---------- Warning / Ban ----------
async def issue_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, target, reason: str):
    chat = update.effective_chat
    warn_key = f"{chat.id}:{target.id}"
    data["warnings"][warn_key] = data["warnings"].get(warn_key, 0) + 1
    count = data["warnings"][warn_key]
    save_data(data)

    if count >= 3:
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            data["banned"][str(target.id)] = {"reason": reason, "chat_id": chat.id}
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
        await chat.send_message(warn_text, parse_mode="HTML")

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

# ---------- Anti-link / Anti-promo / Inbox Filter Auto-mod ----------
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

INBOX_KEYWORDS_PATTERN = re.compile(
    r"\b(inbox|dm|ib|pm|ইনবক্স|ইনবক্সে|ইনবক্স করো|ইনবক্স করুন|dm me|inbox me)\b",
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

    register_group(update.effective_chat.id)

    if msg.is_automatic_forward or getattr(msg, "sender_chat", None) is not None:
        return

    user = update.effective_user
    if not user or is_admin(user.id) or user.is_bot:
        return
    if await is_group_admin(update, context, user.id):
        return

    text = msg.text or msg.caption or ""

    if INBOX_KEYWORDS_PATTERN.search(text):
        try:
            await msg.delete()
        except Exception as e:
            logger.warning(f"Inbox delete failed: {e}")
        raise ApplicationHandlerStop

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
        logger.warning(f"Delete failed: {e}")

    await issue_warning(update, context, user, reason)
    raise ApplicationHandlerStop

# ---------- Multi-Channel Post System (Permanent 2 Channels) ----------
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
    rows.append([InlineKeyboardButton("✅ ২টি চ্যানেলে পোস্ট করুন", callback_data="post_publish")])
    rows.append([InlineKeyboardButton("❌ বাতিল করুন", callback_data="post_cancel")])
    return InlineKeyboardMarkup(rows)

def post_preview_text(draft):
    extra = draft.get("caption", "").strip()
    extra_txt = f"\n📝 <b>অতিরিক্ত টেক্সট:</b> {extra}" if extra else ""

    lines = [
        "📋 <b>পোস্ট প্রিভিউ (২টি চ্যানেলে পোস্ট হবে):</b>",
        f"🎯 <b>চ্যানেল ১ (-1004427297260):</b>\n<code>{PERMANENT_CHANNELS[-1004427297260]}</code>\n",
        f"🎯 <b>চ্যানেল ২ (-1004422557441):</b>\n<code>{PERMANENT_CHANNELS[-1004422557441]}</code>",
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
        "ভিডিও অথবা ছবি পাঠান যেটা ২টি চ্যানেলে পোস্ট করতে চান।\n"
        "উভয় চ্যানেলে নিজস্ব ক্যাপশন অটো চলে যাবে।\n"
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

    kb = [
        [InlineKeyboardButton("🚫 ব্যান লিস্ট দেখুন", callback_data="view_banned")],
        [InlineKeyboardButton("⚠️ ওয়ার্নিং লিস্ট দেখুন", callback_data="view_warnings")],
        [InlineKeyboardButton(f"🔗 অটো-ওয়ার্ন (লিংক): {antilink}", callback_data="toggle_antilink")],
        [InlineKeyboardButton(f"⚡ অটো জয়েন এপ্রুভ: {auto_appr}", callback_data="toggle_auto_approve")],
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

        lines.append(
            f"📍 <code>{ch_id}</code> ➔ <b>{admin_status}</b>\n"
            f"📝 <i>ক্যাপশন:</i> <code>{default_cap}</code>\n"
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

            for ch_id, base_caption in PERMANENT_CHANNELS.items():
                final_caption = f"{extra_caption}\n\n{base_caption}" if extra_caption else base_caption
                try:
                    if draft["kind"] == "video":
                        await context.bot.send_video(
                            chat_id=ch_id, video=draft["file_id"],
                            caption=final_caption, reply_markup=markup
                        )
                    else:
                        await context.bot.send_photo(
                            chat_id=ch_id, photo=draft["file_id"],
                            caption=final_caption, reply_markup=markup
                        )
                    success_count += 1
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

async def admin_text_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    user_id = update.effective_user.id
    if not awaiting or not is_admin(user_id):
        return

    # Post Extra Text Set
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

    # Post Extra Button Set
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

    # Commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("ad", ad_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("whitelist", whitelist_cmd))
    app.add_handler(CommandHandler("post", post_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # Auto Approve Member Join Requests (Channel & Group)
    app.add_handler(ChatJoinRequestHandler(auto_approve_request))

    # Real-time Chat Member Status Updates (Duplicate-safe Welcome/Goodbye)
    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER))

    # Admin Callback Queries
    app.add_handler(CallbackQueryHandler(admin_callback))

    # Admin private video/photo capture
    app.add_handler(MessageHandler(
        (filters.VIDEO | filters.PHOTO) & filters.ChatType.PRIVATE, post_video_capture
    ))

    # Private text inputs
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # Anti-link / promo / inbox automod in groups
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
        anti_link_automod
    ))

    # Periodic Friend Invite Reminder (Every 30 minutes in active groups)
    if app.job_queue:
        app.job_queue.run_repeating(periodic_invite_reminder, interval=1800, first=60)

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
