/*CMD
  command: 👥 Total Users
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

/* ========= STATISTICS ========= */

var users = Bot.getProperty("users", []);
var totalUsers = users.length;

Bot.sendMessage(
  "📊 <b>Bot Statistics</b>\n\n" +
  "🟢 Bot Status : Alive\n\n" +
  "👥 <b>Total Users :</b> " + totalUsers,
  { parse_mode: "html" }
);
