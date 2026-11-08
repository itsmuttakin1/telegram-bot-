/*CMD
  command: 🎁 Gen Redeem Code
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
  Bot.sendMessage("📝 নতুন রিডিম কোড বানাতে এই ফরম্যাটে পাঠান:\n\n`কোডের_নাম কয়েন লিমিট`\n\n🔹 উদাহরণ: `FREECOIN 5 10` (এর মানে কোড FREECOIN, ৫ কয়েন দিবে এবং প্রথম ১০ জন ব্যবহার করতে পারবে)");
  Bot.runCommand("process_gen_promo");
}
