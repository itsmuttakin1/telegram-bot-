/*CMD
  command: /ytx
  help: 
  need_reply: false
  auto_retry_time: 
  folder: 

  <<ANSWER

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

/* ========== ADMIN LOG ========== */
var name = user.first_name;
var username = user.username ? "@" + user.username : "No username";

Api.sendMessage({
  chat_id: adminID,
  text:
    "🚀 *User Started YT Bot!*\n\n" +
    "👤 Name: *" + name + "*\n" +
    "🔗 Username: *" + username + "*\n" +
    "🆔 ID: `" + user.telegramid + "`\n\n" +
    "🕒 Time: " + new Date().toLocaleString(),
  parse_mode: "Markdown"
});

/* ========== SAVE USER (BROADCAST) ========== */
var users = Bot.getProperty("Broadcast") || [];
if (!users.includes(user.telegramid)) {
  users.push(user.telegramid);
  Bot.setProperty("Broadcast", users, "json");
}

/* ========== YT START ========== */
Bot.sendMessage("🎥 Give Me Video Link👇");
Bot.runCommand("/yt3");
