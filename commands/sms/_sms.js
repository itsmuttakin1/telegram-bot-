/*CMD
  command: /sms
  help: 
  need_reply: false
  auto_retry_time: 
  folder: sms
  answer: https://t.me/mrghostdataserver/43

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
    "🚀 *Sms Bomber*\n\n" +
    "👤 User: " + mentionUser + "\n" +
    "🆔 ID: `" + user.telegramid + "`\n" +
    "🔗 Username: @" + (user.username ? user.username : "N/A"),
  parse_mode: "Markdown"
});

/* ===== FORCE JOIN VIDEO MESSAGE ===== */

