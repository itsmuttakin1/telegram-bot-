/*CMD
  command: /unban
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

if (user.telegramid != adminID) {
  Bot.sendMessage("❌ Admin only command");
  return;
}

var unbanID = parseInt(message.split(" ")[1]);

if (!unbanID) {
  Bot.sendMessage("⚠️ Use like: /unban 123456789");
  return;
}

var banList = Bot.getProperty("banList", []);
banList = banList.filter(id => id != unbanID);

Bot.setProperty("banList", banList, "json");

Bot.sendMessage("✅ User unbanned successfully");
