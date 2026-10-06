import os
import re
import json
import asyncio
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatMemberHandler,
    CallbackQueryHandler, ContextTypes, filters, ApplicationHandlerStop
)
from telegram.constants import MessageEntityType, ChatMemberStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Dui jon admin access pabe
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

DEFAULT_DATA = {
    "welcome": "ওয়েলকাম {name}! গ্রুপে স্বাগতম 🎉",
    "goodbye": "{name} গ্রুপ থেকে চলে গেলেন। বিদায় 👋",
    "warnings": {},          # "chat_id:user_id" -> count
    "banned": {},            # user_id(str) -> {"reason": str, "chat_id": int/str}
    "antilink_enabled": True,
    "whitelist_links": [],   # domains allowed
    "button_text": "Video Channel",
    "button_url": "",        # empty = button hidden
    "channels": [],          # Multiple channel IDs/Usernames list
}

def load_data():
    merged = dict(DEFAULT_DATA)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Migration from single channel_id to channels list
            if "channel_id" in saved and saved["channel_id"]:
                merged["channels"] = [saved["channel_id"]]
            merged.update(saved)
            if not isinstance(merged.get("channels"), list):
                merged["channels"] = [merged["channels"]] if merged.get("channels") else []
        except Exception as e:
            logger.error(f"Error loading data.json: {e}")
    return merged

def save_data(data_obj):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_obj, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------- Helper Functions ----------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False

def format_target_chat(raw_id: str):
    raw = str(raw_id).strip()
    if raw.startswith("-") or raw.isdigit():
        return int(raw)
    return raw

async def delete_message_after_delay(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE, delay_seconds: int = 60):
    try:
        await asyncio.sleep(delay_seconds)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.debug(f"Auto delete message failed or already deleted: {e}")

# ---------- Welcome / Goodbye (Groups Only + 1-Min Auto-Delete) ----------
def extra_button_markup():
    url = data.get("button_url", "").strip()
    if not url:
        return None
    text = data.get("button_text", "Video Channel").strip() or "Video Channel"
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, url=url)]])

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return

    result = update.chat_member
    if not result:
        return

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
            sent_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=extra_button_markup()
            )
            asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))
        except Exception as e:
            logger.error(f"Welcome message error in {chat.id}: {e}")

    # User Left
    elif old_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.RESTRICTED) and new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        text = data.get("goodbye", DEFAULT_DATA["goodbye"]).format(
            name=user.full_name or "মেম্বার", 
            group=chat.title or "গ্রুপ"
        )
        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                reply_markup=extra_button_markup()
            )
            asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))
        except Exception as e:
            logger.error(f"Goodbye message error in {chat.id}: {e}")

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        if str(member.id) in data["banned"]:
            try:
                await context.bot.ban_chat_member(chat.id, member.id)
            except Exception:
                pass
            continue
        text = data.get("welcome", DEFAULT_DATA["welcome"]).format(
            name=member.mention_html(), 
            group=chat.title or "গ্রুপ"
        )
        sent_msg = await update.message.reply_html(text, reply_markup=extra_button_markup())
        asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))

async def farewell_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return
    if not update.message or not update.message.left_chat_member:
        return
    member = update.message.left_chat_member
    if member.is_bot:
        return
    text = data.get("goodbye", DEFAULT_DATA["goodbye"]).format(
        name=member.full_name or "মেম্বার", 
        group=chat.title or "গ্রুপ"
    )
    sent_msg = await update.message.reply_text(text, reply_markup=extra_button_markup())
    asyncio.create_task(delete_message_after_delay(chat.id, sent_msg.message_id, context, 60))

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

# ---------- Anti-link / Anti-promo Auto-mod ----------
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
    if not user or is_admin(user.id) or user.is_bot:
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

# ---------- Multi-Channel Post System ----------
def _post_draft(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    drafts = context.bot_data.setdefault("post_draft", {})
    return drafts.get(user_id)

def post_editor_markup(draft):
    rows = []
    for i, btn in enumerate(draft["buttons"]):
        rows.append([InlineKeyboardButton(f"❌ {btn['text']}", callback_data=f"post_rm_{i}")])
    if len(draft["buttons"]) < 4:
        rows.append([InlineKeyboardButton("➕ বাটন যোগ করুন", callback_data="post_add_btn")])
    rows.append([InlineKeyboardButton("✅ সব চ্যানেলে পোস্ট করুন", callback_data="post_publish")])
    rows.append([InlineKeyboardButton("❌ বাতিল করুন", callback_data="post_cancel")])
    return InlineKeyboardMarkup(rows)

def post_preview_text(draft):
    channels_count = len(data.get("channels", []))
    lines = [
        "📋 পোস্ট প্রিভিউ",
        f"🎯 টার্গেট চ্যানেল সংখ্যা: {channels_count} টি",
        f"ক্যাপশন: {draft['caption'] or '(খালি)'}"
    ]
    if draft["buttons"]:
        lines.append("বাটন:")
        for b in draft["buttons"]:
            lines.append(f"  • {b['text']} → {b['url']}")
    else:
        lines.append("বাটন: এখনো যোগ করা হয়নি")
    return "\n".join(lines)

async def post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    await start_post_flow(update, context)

async def start_post_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not data.get("channels"):
        await update.effective_message.reply_text(
            "⚠️️ কোনো চ্যানেল যোগ করা নেই!\n/ad প্যানেল থেকে '🎯 চ্যানেল ম্যানেজ করুন' চাপুন এবং চ্যানেল আইডি যোগ করুন।"
        )
        return
    context.bot_data.setdefault("post_draft", {})[user_id] = None
    context.user_data["awaiting"] = "post_video"
    await update.effective_message.reply_text(
        "ভিডিও অথবা ছবি পাঠান যেটা সব চ্যানেলে পোস্ট করতে চান (ক্যাপশনসহ পাঠাতে পারেন)।\nবাতিল করতে /cancel লিখুন।"
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
    draft = {"kind": kind, "file_id": file_id, "caption": msg.caption or "", "buttons": []}
    context.bot_data.setdefault("post_draft", {})[user_id] = draft
    context.user_data["awaiting"] = None
    await update.message.reply_text(post_preview_text(draft), reply_markup=post_editor_markup(draft))
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
    channel_count = len(data.get("channels", []))
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
        [InlineKeyboardButton(f"🎯 চ্যানেল ম্যানেজ করুন ({channel_count} টি)", callback_data="manage_channels")],
        [InlineKeyboardButton("📢 চ্যানেলে নতুন পোস্ট বানান", callback_data="new_post")],
    ]
    return InlineKeyboardMarkup(kb)

def get_channels_markup():
    channels = data.get("channels", [])
    kb = []
    if channels:
        for idx, ch in enumerate(channels):
            kb.append([InlineKeyboardButton(f"❌ সরান: {ch}", callback_data=f"rm_channel_{idx}")])
    kb.append([InlineKeyboardButton("➕ নতুন চ্যানেল যোগ করুন", callback_data="add_channel")])
    kb.append([InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")])
    
    text = (
        "🎯 **টার্গেট চ্যানেল লিস্ট:**\n\n"
        + ("\n".join(f"{i+1}. `{ch}`" for i, ch in enumerate(channels)) if channels else "কোনো চ্যানেল যোগ করা নেই।")
        + "\n\n⚠️ বটকে অবশ্যই প্রতিটা চ্যানেলে Administrator (Post messages পারমিশন সহ) বানাতে হবে।"
    )
    return text, InlineKeyboardMarkup(kb)

def get_banned_list_markup():
    banned_items = data.get("banned", {})
    if not banned_items:
        text = "🚫 ব্যান লিস্ট:\nকোনো ব্যান করা ইউজার নেই।"
        kb = [[InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_panel")]]
        return text, InlineKeyboardMarkup(kb)

    lines = ["🚫 ব্যান লিস্ট (আনব্যান করতে বাটনে চাপুন):\n"]
    kb = []
    for uid, info in banned_items.items():
        reason = info.get("reason", "unknown") if isinstance(info, dict) else str(info)
        lines.append(f"• ID: `{uid}`\n  কারণ: {reason}")
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

    # Post creation flow actions
    if action in ("new_post", "post_add_btn", "post_cancel", "post_publish") or action.startswith("post_rm_"):
        if action == "new_post":
            await start_post_flow(update, context)
            return

        draft = _post_draft(context, user_id)
        if not draft and action != "post_cancel":
            await query.edit_message_text("পোস্ট খুঁজে পাওয়া যায়নি, আবার /post দিয়ে শুরু করুন।")
            return

        if action == "post_add_btn":
            if len(draft["buttons"]) >= 4:
                await query.answer("সর্বোচ্চ ৪টা বাটন যোগ করা যাবে।", show_alert=True)
                return
            context.user_data["awaiting"] = "post_button"
            await query.edit_message_text(
                post_preview_text(draft) + "\n\nনতুন বাটন এই ফরম্যাটে পাঠান:\nবাটন নাম | লিংক\n\nউদাহরণ:\nWatch Now | https://t.me/yourchannel"
            )
        elif action.startswith("post_rm_"):
            idx = int(action.replace("post_rm_", ""))
            if 0 <= idx < len(draft["buttons"]):
                draft["buttons"].pop(idx)
            await query.edit_message_text(post_preview_text(draft), reply_markup=post_editor_markup(draft))
        elif action == "post_cancel":
            context.bot_data.setdefault("post_draft", {})[user_id] = None
            context.user_data["awaiting"] = None
            await query.edit_message_text("❌ পোস্ট বাতিল করা হয়েছে।")
        elif action == "post_publish":
            channels = data.get("channels", [])
            if not channels:
                await query.edit_message_text("কোনো চ্যানেল সেট করা নেই।")
                return

            markup = None
            if draft["buttons"]:
                rows = [[InlineKeyboardButton(b["text"], url=b["url"])] for b in draft["buttons"]]
                markup = InlineKeyboardMarkup(rows)

            success_count, fail_count = 0, 0
            for ch in channels:
                chat_target = format_target_chat(ch)
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
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to post in {ch}: {e}")
                    fail_count += 1

            context.bot_data.setdefault("post_draft", {})[user_id] = None
            await query.edit_message_text(
                f"✅ পোস্ট প্রক্রিয়া সম্পন্ন!\n\n"
                f"সফল হয়েছে: {success_count} টি চ্যানেলে\n"
                f"ব্যর্থ হয়েছে: {fail_count} টি চ্যানেলে"
            )
        return

    # Panel Navigation & Settings
    if action == "back_to_panel":
        await query.edit_message_text("🛠 অ্যাডমিন প্যানেল", reply_markup=admin_panel_markup())
    elif action == "manage_channels":
        text, markup = get_channels_markup()
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    elif action == "add_channel":
        context.user_data["awaiting"] = "add_channel"
        await query.edit_message_text(
            "চ্যানেলের আইডি বা ইউজারনেম পাঠান (প্রাইভেট চ্যানেল হলে -100 দিয়ে শুরু আইডি দিন):\n\n"
            "উদাহরণ: `-1002345678901` অথবা `@mychannel`"
        )
    elif action.startswith("rm_channel_"):
        idx = int(action.replace("rm_channel_", ""))
        channels = data.get("channels", [])
        if 0 <= idx < len(channels):
            removed = channels.pop(idx)
            save_data(data)
            await query.answer(f"❌ চ্যানেল {removed} সরানো হয়েছে!", show_alert=True)
        text, markup = get_channels_markup()
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    elif action == "view_banned":
        text, markup = get_banned_list_markup()
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
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
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    elif action == "set_welcome":
        context.user_data["awaiting"] = "welcome"
        await query.edit_message_text(
            "নতুন Welcome মেসেজ পাঠান। {name} আর {group} ব্যবহার করতে পারবেন।\n\nবর্তমান:\n" + data["welcome"]
        )
    elif action == "set_goodbye":
        context.user_data["awaiting"] = "goodbye"
        await query.edit_message_text(
            "নতুন Goodbye মেসেজ পাঠান। {name} আর {group} ব্যবহার করতে পারবেন।\n\nবর্তমান:\n" + data["goodbye"]
        )
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

async def admin_text_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    user_id = update.effective_user.id
    if not awaiting or not is_admin(user_id):
        return

    if awaiting == "post_button":
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

    elif awaiting == "add_channel":
        raw = update.message.text.strip()
        if raw.isdigit():
            raw = f"-100{raw}"
        channels = data.setdefault("channels", [])
        if raw in channels:
            await update.message.reply_text("⚠️ এই চ্যানেল আগে থেকেই লিস্টে আছে!")
        else:
            channels.append(raw)
            save_data(data)
            await update.message.reply_text(f"✅ নতুন চ্যানেল যোগ হয়েছে: `{raw}`", parse_mode="Markdown")

    elif awaiting == "welcome":
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

    # Real-time Chat Member Status Updates
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

    # Private text inputs
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, admin_text_capture))

    # Anti-link/promo automod in groups
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
        anti_link_automod
    ))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
