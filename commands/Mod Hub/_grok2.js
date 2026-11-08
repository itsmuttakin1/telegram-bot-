/*CMD
  command: /grok2
  help: 
  need_reply: false
  auto_retry_time: 
  folder: Mod Hub

  <<ANSWER
Grok Now Working 
⏳You can use this method anytime..
https://youtu.be/kNirZj_NTYU
  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

/* ========== MAINTENANCE CHECK ========== */

var adminID = 5140546628;
var maintenance = Bot.getProperty("maintenance", false);

if (maintenance && user.telegramid != adminID) {
  Api.sendMessage({
    text:
      "🚧 <b>Bot Maintenance চলতেছে!</b>\n\n" +
      "🔧 কিছু আপডেট করা হচ্ছে…\n" +
      "⏳ একটু পরে আবার চেষ্টা করো।",
    parse_mode: "HTML"
  });
  return;
}

/* ===== ADMIN NOTIFY ===== */
var adminID = 5140546628; // Admin Telegram ID

var mentionUser = "[" + user.first_name + "](tg://user?id=" + user.telegramid + ")";

Api.sendMessage({
  chat_id: adminID,
  text:
    "🚀 *Grok mod apk*\n\n" +
    "👤 User: " + mentionUser + "\n" +
    "🆔 ID: `" + user.telegramid + "`\n" +
    "🔗 Username: @" + (user.username ? user.username : "N/A"),
  parse_mode: "Markdown"
});

/* ===== FORCE JOIN VIDEO MESSAGE ===== */
/* ===== FORCE JOIN VIDEO MESSAGE ===== */

Api.sendMessage({
  text:
    "⚠️ <b>Notice</b>\n\n" +
    "🚫 Old Version Not Working!\n" +
    "🆕 New Version Adding Soon...\n\n" +
    "⏳You can use this method anytime..",
  parse_mode: "HTML"
});
