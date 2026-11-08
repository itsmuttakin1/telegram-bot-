/*CMD
  command: 🔴 Maintenance OFF
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

if (user.telegramid == 5140546628 || user.telegramid == 7728010216) {
  Bot.setProperty("maintenance_mode", false, "boolean");
  Bot.sendMessage("✅ Maintenance Mode turned OFF!");
  Bot.runCommand("/admin");
}
