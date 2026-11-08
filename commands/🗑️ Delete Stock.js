/*CMD
  command: 🗑️ Delete Stock
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
  // ডাটাবেজের কার্ড পুলে খালি অ্যারে (Empty Array) সেট করে দেওয়া হলো
  Bot.setProperty("cards_pool", [], "json");
  Bot.sendMessage("🗑️ **স্টক সফলভাবে খালি করা হয়েছে!**\nবর্তমানে বটের স্টকে কোনো কার্ড নেই।");
}
