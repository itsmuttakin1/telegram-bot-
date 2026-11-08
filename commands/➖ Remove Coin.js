/*CMD
  command: ➖ Remove Coin
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
  Bot.sendMessage("👤 যার অ্যাকাউন্ট থেকে কয়েন কাটবেন তার **Telegram ID** এবং **কয়েনের পরিমাণ** এভাবে লিখে পাঠান:\n\n`ইউজার_আইডি কয়েন`\n\n🔹 উদাহরণ: `5140546628 5` ");
  Bot.runCommand("process_remove_coin");
}
