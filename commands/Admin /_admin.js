/*CMD
  command: /admin
  help: 
  need_reply: false
  auto_retry_time: 
  folder: Admin 

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

if (user.telegramid == 5140546628) {

  let maintenance = Bot.getProperty("maintenance_mode", false);

  let maintnBtn = maintenance
    ? "🔴 Maintenance OFF"
    : "🟢 Maintenance ON";

  let adminTxt =
    "⚙️ ADMIN PANEL\n\n" +
    "Maintenance Status: " +
    (maintenance ? "🔧 ON" : "✅ OFF");

  Bot.sendKeyboard(
    "🎟️ Add Activation Codes, ➕ Add Bulk Cards\n" +
    "📦 Activation Stock, 💳 Card Stock\n" +
    "🗑️ Delete Activation Stock, 🗑️ Delete Stock\n" +
    "🪙 Manage Coins, 🔍 Check Balance\n" +
    "📋 Request List, 🧹 Clear Request List\n" +
    "🎁 Gen Redeem Code, 📢 Broadcast\n" +
    maintnBtn + ", 🏠 Home",
    adminTxt
  );

} else {
  Bot.sendMessage("❌ আপনি এই বটের এডমিন নন।");
}
