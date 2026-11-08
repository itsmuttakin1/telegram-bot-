/*CMD
  command: /banlist
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

var adminID = 5140546628;
var banList = Bot.getProperty("banList", []);

// 🔔 Notify admin when banlist is used
Api.sendMessage({
  chat_id: adminID,
  text:
    "📢 *Banlist Viewed*\n\n" +
    "👤 Name: " + user.first_name + "\n" +
    "🆔 ID: `" + user.telegramid + "`",
  parse_mode: "Markdown"
});

// 📄 If no banned users
if (banList.length == 0) {
  Bot.sendMessage("✅ No banned users");
  return;
}

// 🧱 Build clickable ban list with ID
var text = "☠️ *Channel Rule Break*\n\n";

banList.forEach(function(id, index){
  text +=
    (index + 1) + ". " +
    "`" + id + "` → " +
    "[User](tg://user?id=" + id + ")\n";
});

// 📤 Send to user
Bot.sendMessage(text, { parse_mode: "Markdown" });
