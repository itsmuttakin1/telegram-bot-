/*CMD
  command: /bdnid2
  help: 
  need_reply: false
  auto_retry_time: 
  folder: 

  <<ANSWER
https://t.me/mrghostdataserver/15
https://t.me/mrghostdataserver/16
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
      "🚧 <b>Bot Maintenance চলছে!</b>\n\n" +
      "🔧 কিছু আপডেট করা হচ্ছে...\n" +
      "⏳ একটু পরে আবার চেষ্টা করো।",
    parse_mode: "html"
  });
  return;
}


/* ========== BAN SYSTEM ========== */

var banList = Bot.getProperty("banList", []);

if (banList.includes(user.telegramid)) {
  Bot.sendMessage(
    "🚫 তুমি এই বট থেকে ব্যান করা আছো!\n" +
    "Unban করতে এডমিন এর সাথে যোগাযোগ করো।"
  );
  return;
}


/* ========== BOT MAIN MESSAGE ========== */

Bot.sendMessage("👋 Welcome to the bot!");

/* ===== ADMIN NOTIFY ===== */
var adminID = 5140546628; // Admin Telegram ID

var mentionUser = "[" + user.first_name + "](tg://user?id=" + user.telegramid + ")";

Api.sendMessage({
  chat_id: adminID,
  text:
    "🚀 *NID*\n\n" +
    "👤 User: " + mentionUser + "\n" +
    "🆔 ID: `" + user.telegramid + "`\n" +
    "🔗 Username: @" + (user.username ? user.username : "N/A"),
  parse_mode: "Markdown"
});

/* ===== FORCE JOIN VIDEO MESSAGE ===== */
