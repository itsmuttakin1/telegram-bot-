/*CMD
  command: 📢 Broadcast
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
  Bot.sendMessage("📢 বটের সকল ইউজারকে যে নোটিফিকেশন বা মেসেজটি পাঠাতে চান তা লিখে পাঠান:");
  Bot.runCommand("process_broadcast");
}
