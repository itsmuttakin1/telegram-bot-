/*CMD
  command: 🪙 Manage Coins
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
  Bot.sendKeyboard("➕ Add Coin, ➖ Remove Coin\n🔙 Back to Admin", "🪙 **Coin Management**\n\nআপনি কি ইউজারের কয়েন বাড়াতে চান নাকি কমাতে চান? নিচের বাটন চাপুন:");
}
