/*CMD
  command: ➕ Add Coin
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

if (user.telegramid == 5140546628) {
  Bot.sendMessage("👤 যাকে কয়েন দেবেন তার **Telegram ID** এবং **কয়েনের পরিমাণ** এভাবে লিখে পাঠান:\n\n`ইউজার_আইডি কয়েন`\n\n🔹 উদাহরণ: `5140546628 10` (আইডি ও কয়েনের মাঝে একটা স্পেস দিবেন)");
  Bot.runCommand("process_add_coin");
}
