import os
import re
import json
import asyncio
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatMemberHandler,
    CallbackQueryHandler, ContextTypes, filters, ApplicationHandlerStop
)
from telegram.constants import MessageEntityType, ChatMemberStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5140546628"))

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "welcome": "ওয়েলকাম {name}! গ্রুপে স্বাগতম 🎉",
    "goodbye": "{name} গ্রুপ থেকে চলে গেলেন। বিদায় 👋",
    "warnings": {},   # user_id(str) -> count
    "banned": {},      # user_id(str) -> reason
    "antilink_enabled": True,
    "whitelist_links": [],   # domains allowed
    "button_text": "Video Channel",
    "button_url": "",        # empty = button hidden
    "rules": "",              # empty = no rules shown
    "channel_id": "",         # numeric id (e.g. -100...) or @username
}

def load_data():
    merged = dict(DEFAULT_DATA)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged.update(saved)
        except Exception as e:
            logger.error(f"Error loading data.json: {e}")
    return merged

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
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False

def get_target_chat_id(raw_id: str):
    raw = str(raw_id).strip()
    if raw.startswith("-") or raw.isdigit():
        return int(raw)
    return raw

# ---------- Welcome / Goodbye ----------
def extra_button_markup():
    url = data.get("button_url", "").strip()
    if not url:
        return None
    text = data.get("button_text", "Video Channel").strip() or "Video Channel"
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, url=url)]])

# ChatMemberHandler diye join/leave dhora (Supergroup ar Regular group sob jaygay kaj korbe)
async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    chat = update.effective_chat
    user = result.new_chat_member.user
    if user.is_bot:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    # User Joined
    if old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED) and new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
        if str(user.id) in data["banned"]:
            try:
                await context.bot.ban_chat_member(chat.id, user.id)
            except Exception:
                pass
            return
        
        text = data.get("welcome", DEFAULT_DATA["welcome"]).format(
            name=user.mention_html(), 
            group=chat.title or "গ্রুপ"
        )
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=extra_button_markup()
            )
        except Exception as e:
            logger.error(f"Welcome message error: {e}")

    # User Left / Removed
    elif old_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.RESTRICTED) and new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        text = data.get("goodbye", DEFAULT_DATA["goodbye"]).format(
            name=user.full_name or "মেম্বার", 
            group=chat.title or "গ্রুপ"
        )
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                reply_markup=extra_button_markup()
            )
        except Exception as e:
            logger.error(f"Goodbye message error: {e}")

# Fallback service message handler
async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        if str(member.id) in data["banned"]:
            try:
                await context.bot.ban_chat_member(update.effective_chat.id, member.id)
            except Exception:
                pass
            continue
        text = data.get("welcome", DEFAULT_DATA["welcome"]).format(
            name=member.mention_html(), 
            group=update.effective_chat.title or "গ্রুপ"
        )
        await update.message.reply_html(text, reply_markup=extra_button_markup())

async def farewell_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.left_chat_member:
        return
    member = update.message.left_chat_member
    if member.is_bot:
        return
    text = data.get("goodbye", DEFAULT_DATA["goodbye"]).format(
        name=member.full_name or "মেম্বার", 
        group=update.effective_chat.title or "গ্রুপ"
    )
    await update.message.reply_text(text, reply_markup=extra_button_markup())

# ---------- Warning / Ban ----------
async def issue_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, target, reason: str):
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
        warn_text = f"⚠️ {target.mention_html()} কে ওয়ার্নিং দেওয়া হলো। ({count}/3)\nকারণ: {reason}"
        rules = data.get("rules", "").strip()
        if rules:
            warn_text += f"\n\n📜 গ্রুপ রুলস:\n{rules}"
        await update.effective_chat.send_message(warn_text, parse_mode="HTML")

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
    if not user or user.id == ADMIN_ID or user.is_bot:
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
    raise ApplicationHandlerStop

# ---------- Channel Post System ----------
def _post_draft(context: ContextTypes.DEFAULT_TYPE):
    drafts = context.bot_data.setdefault("post_draft", {})
    return drafts.get(ADMIN_ID)

def post_editor_markup(draft):
    rows = []
    for i, btn in enumerate(draft["buttons"]):
        rows.append([InlineKeyboardButton(f"❌ {btn['text']}", callback_data=f"post_rm_{i}")])
    if len(draft["buttons"]) < 4:
        rows.append([InlineKeyboardButton("➕ বাটন যোগ করুন", callback_data="post_add_btn")])
    rows.append([InlineKeyboardButton("✅ চ্যানেলে পোস্ট করুন", callback_data="post_publish")])
    rows.append([InlineKeyboardButton("❌ বাতিল করুন", callback_data="post_cancel")])
    return InlineKeyboardMarkup(rows)

def post_preview_text(draft):
    lines = ["📋 পোস্ট প্রিভিউ", f"ক্যাপশন: {draft['caption'] or '(খালি)'}"]
    if draft["buttons"]:
        lines.append("বাটন:")
        for b in draft["buttons"]:
            lines.append(f"  • {b['text']} → {b['url']}")
    else:
        lines.append("বাটন: এখনো যোগ করা হয়নি")
    return "\n".join(lines)

async def post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await start_post_flow(update, context)

async def start_post_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data.get("channel_id", "").strip():
        context.user_data["awaiting"] = "channel_id"
        await update.effective_message.reply_text(
            "প্রথমে পোস্ট চ্যানেল সেট করতে হবে।\nপ্রাইভেট চ্যানেলের আইডি পাঠান (যেমন: -100xxxxxxxxxx)।\n"
            "⚠️ বট কে অবশ্যই চ্যানেলে Administrator (Post messages পারমিশন সহ) বানাতে হবে।"
        )
        return
    context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = None
    context.user_data["awaiting"] = "post_video"
    await update.effective_message.reply_text(
        "ভিডিও অথবা ছবি পাঠান যেটা চ্যানেলে পোস্ট করতে চান (ক্যাপশনসহ পাঠাতে পারেন)।\nবাতিল করতে /cancel লিখুন।"
    )

async def post_video_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
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
    draft = {"kind": kind, "file_id": file_id, "caption": msg.caption or "", "buttons": []}
    context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = draft
    context.user_data["awaiting"] = None
    await update.message.reply_text(post_preview_text(draft), reply_markup=post_editor_markup(draft))
    raise ApplicationHandlerStop

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["awaiting"] = None
    context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = None
    await update.message.reply_text("❌ বাতিল করা হয়েছে।")

# ---------- Admin Panel ----------
def admin_panel_markup():
    kb = [
        [InlineKeyboardButton("✏️ Welcome মেসেজ সেট", callback_data="set_welcome")],
        [InlineKeyboardButton("✏️ Goodbye মেসেজ সেট", callback_data="set_goodbye")],
        [InlineKeyboardButton("🚫 ব্যান লিস্ট দেখুন", callback_data="view_banned")],
        [InlineKeyboardButton("⚠️ ওয়ার্নিং লিস্ট দেখুন", callback_data="view_warnings")],
        [InlineKeyboardButton(
            "🔗 লিংক/প্রোমো অটো-ওয়ার্ন: " + ("ON ✅" if data.get("antilink_enabled", True) else "OFF ❌"),
            callback_data="toggle_antilink"
        )],
        [InlineKeyboardButton("🔘 Welcome/Goodbye বাটন সেট", callback_data="set_button")],
        [InlineKeyboardButton("📜 গ্রুপ রুলস সেট", callback_data="set_rules")],
        [InlineKeyboardButton("📢 চ্যানেলে নতুন পোস্ট বানান", callback_data="new_post")],
        [InlineKeyboardButton("🎯 পোস্ট চ্যানেল পরিবর্তন", callback_data="set_channel")],
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
    elif action == "toggle_antilink":
        data["antilink_enabled"] = not data.get("antilink_enabled", True)
        save_data(data)
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "set_button":
        context.user_data["awaiting"] = "button"
        cur_text = data.get("button_text", "Video Channel")
        cur_url = data.get("button_url", "") or "(সেট করা নেই — বাটন হাইড থাকবে)"
        await query.edit_message_text(
            "নতুন বাটন সেট করতে এই ফরম্যাটে পাঠান:\n\n"
            "বাটন নাম | লিংক\n\n"
            "উদাহরণ:\nVideo Channel | https://t.me/yourchannel\n\n"
            f"বর্তমান বাটন নাম: {cur_text}\nবর্তমান লিংক: {cur_url}\n\n"
            "বাটন বন্ধ করতে শুধু লিখুন: off"
        )
    elif action == "set_rules":
        context.user_data["awaiting"] = "rules"
        cur_rules = data.get("rules", "") or "(সেট করা নেই)"
        await query.edit_message_text(
            "নতুন গ্রুপ রুলস পাঠান — কেউ ওয়ার্নিং খেলে এই টেক্সট মেসেজের নিচে দেখানো হবে।\n\n"
            f"বর্তমান রুলস:\n{cur_rules}\n\n"
            "রুলস বন্ধ করতে শুধু লিখুন: off"
        )
    elif action == "set_channel":
        context.user_data["awaiting"] = "channel_id"
        cur = data.get("channel_id", "") or "(সেট করা নেই)"
        await query.edit_message_text(
            "প্রাইভেট চ্যানেলের আইডি পাঠান (যেমন: -100xxxxxxxxxx)।\n"
            "⚠️️ বট কে অবশ্যই চ্যানেলে Post Messages পারমিশন সহ Admin বানাতে হবে।\n\n"
            f"বর্তমান চ্যানেল: {cur}"
        )
    elif action == "new_post":
        if not data.get("channel_id", "").strip():
            context.user_data["awaiting"] = "channel_id"
            await query.edit_message_text(
                "প্রথমে পোস্ট চ্যানেল সেট করতে হবে।\nপ্রাইভেট চ্যানেলের আইডি পাঠান (যেমন: -100xxxxxxxxxx)।\n"
                "⚠️ বট কে অবশ্যই চ্যানেলে Admin বানাতে হবে।"
            )
            return
        context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = None
        context.user_data["awaiting"] = "post_video"
        await query.edit_message_text(
            "ভিডিও অথবা ছবি পাঠান যেটা চ্যানেলে পোস্ট করতে চান (ক্যাপশনসহ পাঠাতে পারেন)।\nবাতিল করতে /cancel লিখুন।"
        )
    elif action == "post_add_btn":
        draft = _post_draft(context)
        if not draft:
            await query.edit_message_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            return
        if len(draft["buttons"]) >= 4:
            await query.answer("সর্বোচ্চ ৪টা বাটন যোগ করা যাবে।", show_alert=True)
            return
        context.user_data["awaiting"] = "post_button"
        await query.edit_message_text(
            post_preview_text(draft) + "\n\nনতুন বাটন এই ফরম্যাটে পাঠান:\nবাটন নাম | লিংক\n\nউদাহরণ:\nWatch Now | https://t.me/yourchannel"
        )
    elif action.startswith("post_rm_"):
        draft = _post_draft(context)
        if not draft:
            await query.edit_message_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            return
        idx = int(action.replace("post_rm_", ""))
        if 0 <= idx < len(draft["buttons"]):
            draft["buttons"].pop(idx)
        await query.edit_message_text(post_preview_text(draft), reply_markup=post_editor_markup(draft))
    elif action == "post_cancel":
        context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = None
        context.user_data["awaiting"] = None
        await query.edit_message_text("❌ পোস্ট বাতিল করা হয়েছে।")
    elif action == "post_publish":
        draft = _post_draft(context)
        if not draft:
            await query.edit_message_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            return
        channel = data.get("channel_id", "").strip()
        if not channel:
            await query.edit_message_text("চ্যানেল সেট করা নেই।")
            return

        chat_target = get_target_chat_id(channel)
        markup = None
        if draft["buttons"]:
            rows = [[InlineKeyboardButton(b["text"], url=b["url"])] for b in draft["buttons"]]
            markup = InlineKeyboardMarkup(rows)
        try:
            if draft["kind"] == "video":
                await context.bot.send_video(
                    chat_id=chat_target, video=draft["file_id"],
                    caption=draft["caption"] or None, reply_markup=markup
                )
            else:
                await context.bot.send_photo(
                    chat_id=chat_target, photo=draft["file_id"],
                    caption=draft["caption"] or None, reply_markup=markup
                )
            context.bot_data.setdefault("post_draft", {})[ADMIN_ID] = None
            await query.edit_message_text(f"✅ চ্যানেলে ({channel}) পোস্ট সফলভাবে হয়ে গেছে।")
        except Exception as e:
            await query.edit_message_text(
                f"❌ পোস্ট করতে সমস্যা হয়েছে: {e}\n\n"
                f"লক্ষ্য করুন:\n"
                f"১. চ্যানেলের আইডি ঠিক আছে কিনা (প্রাইভেট চ্যানেলে অবশ্যই -100 দিয়ে শুরু হয়)।\n"
                f"২. বট ওই প্রাইভেট চ্যানেলে Admin এবং 'Post Messages' পারমিশন অন আছে কিনা।"
            )

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
    elif awaiting == "button":
        raw = update.message.text.strip()
        if raw.lower() == "off":
            data["button_url"] = ""
            save_data(data)
            await update.message.reply_text("✅ বাটন বন্ধ করা হয়েছে।")
        elif "|" in raw:
            btn_text, btn_url = raw.split("|", 1)
            btn_text, btn_url = btn_text.strip(), btn_url.strip()
            if not (btn_url.startswith("http://") or btn_url.startswith("https://") or btn_url.startswith("t.me/") or btn_url.startswith("tg://")):
                await update.message.reply_text("❌ লিংক সঠিক ফরম্যাটে দিন (http:// বা https:// দিয়ে শুরু)। আবার চেষ্টা করুন।")
                context.user_data["awaiting"] = "button"
                return
            if btn_url.startswith("t.me/"):
                btn_url = "https://" + btn_url
            data["button_text"] = btn_text or "Video Channel"
            data["button_url"] = btn_url
            save_data(data)
            await update.message.reply_text(f"✅ বাটন সেট হয়েছে: {data['button_text']} → {data['button_url']}")
        else:
            await update.message.reply_text("❌ ফরম্যাট ভুল। এভাবে পাঠান: বাটন নাম | লিংক")
            context.user_data["awaiting"] = "button"
            return
    elif awaiting == "rules":
        raw = update.message.text.strip()
        if raw.lower() == "off":
            data["rules"] = ""
            save_data(data)
            await update.message.reply_text("✅ গ্রুপ রুলস বন্ধ করা হয়েছে।")
        else:
            data["rules"] = update.message.text
            save_data(data)
            await update.message.reply_text("✅ গ্রুপ রুলস সেট হয়েছে। এখন থেকে ওয়ার্নিং এর নিচে এটা দেখাবে।")
    elif awaiting == "channel_id":
        raw = update.message.text.strip()
        # Auto-format for negative id if user forgets -100
        if raw.isdigit():
            raw = f"-100{raw}"
        data["channel_id"] = raw
        save_data(data)
        await update.message.reply_text(
            f"✅ পোস্ট চ্যানেল আইডি সেট হয়েছে: {raw}\n\nএখন /post কমান্ড দিয়ে পোস্ট করা শুরু করতে পারেন।"
        )
    elif awaiting == "post_button":
        draft = _post_draft(context)
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
            await update.message.reply_text("❌ লিংক সঠিক ফরম্যাটে দিন (http:// বা https:// দিয়ে শুরু)। আবার চেষ্টা করুন।")
            context.user_data["awaiting"] = "post_button"
            return
        if btn_url.startswith("t.me/"):
            btn_url = "https://" + btn_url
        if len(draft["buttons"]) >= 4:
            await update.message.reply_text("সর্বোচ্চ ৪টা বাটন যোগ করা যাবে।")
        else:
            draft["buttons"].append({"text": btn_text or "Button", "url": btn_url})
        await update.message.reply_text(post_preview_text(draft), reply_markup=post_editor_markup(draft))
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

    # Real-time Chat Member Status Updates (Welcome & Goodbye for Supergroups/Groups)
    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER))

    # Fallback status updates
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, farewell_member))

    # Admin Callback Queries
    app.add_handler(CallbackQueryHandler(admin_callback))

    # Admin private video/photo capture
    app.add_handler(MessageHandler(
        (filters.VIDEO | filters.PHOTO) & filters.ChatType.PRIVATE, post_video_capture
    ))

    # Admin private text inputs
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # Anti-link/promo automod in groups
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
        anti_link_automod
    ))

    logger.info("Bot starting...")
    # Chat member updates receive korte Update.ALL_TYPES obosshoi thakte hobe
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
