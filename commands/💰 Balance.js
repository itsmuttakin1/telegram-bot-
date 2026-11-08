/*CMD
  command: 💰 Balance
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

var ADMIN_ID = 5140546628;
var maintenance = Bot.getProperty("maintenance_mode", false);

if (maintenance && user.telegramid != ADMIN_ID) {
  Bot.sendMessage("🛠️ Bot বর্তমানে Maintenance Mode-এ আছে।");
  return;
}

var coin = Libs.ResourcesLib.userRes("coin").value();

var purchased = User.getProperty(
  "my_purchased_codes",
  []
);

if (!Array.isArray(purchased)) {
  purchased = [];
}

var msg =
  "💰 আপনার Balance\n\n" +
  "👤 User ID: `" + user.telegramid + "`\n" +
  "🪙 Coin: " + coin + "\n" +
  "🎟️ Purchased VIP: " + purchased.length + "\n\n";

if (purchased.length === 0) {

  msg += "📭 এখনো কোনো VIP Code Purchase করেননি।";

} else {

  msg += "📋 Purchase History:\n\n";

  for (var i = 0; i < purchased.length; i++) {

    var p = purchased[i];

    msg +=
      "━━━━━━━━━━━━━━\n" +
      "💎 Plan: " + (p.plan || "1 Day") + "\n" +
      "🔑 Code: `" + (p.code || "N/A") + "`\n" +
      "📅 Date: " + (p.date || "N/A") + "\n";
  }

  msg += "━━━━━━━━━━━━━━";
}

Bot.sendMessage(msg);
