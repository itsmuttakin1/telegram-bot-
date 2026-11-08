/*CMD
  command: 🔍 Check Balance
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

// 🛠️ শুধুমাত্র এডমিন চেক (আপনার আইডি: 5140546628)
if (user.telegramid != 5140546628) {
  Bot.sendMessage("❌ আপনি এই কমান্ডটি ব্যবহার করার জন্য অনুমোদিত নন!");
  return;
}

Bot.sendMessage("🔍 যে ইউজারের ব্যালেন্স দেখতে চান, তার **Telegram ID** টি পাঠান 👇");
Bot.runCommand("/view_user_balance");
