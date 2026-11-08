/*CMD
  command: 📊 View Stats
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
  // বটের অলরেডি স্টার্ট করা কার্ড ও রিকোয়েস্ট ডেটা আনা হচ্ছে
  let cardList = Bot.getProperty("cards_pool", []);
  let reqList = Bot.getProperty("coin_requests_pool", []);
  
  // Bot Business এর বিল্ট-ইন মেথড দিয়ে টোটাল চ্যাট/ইউজার সংখ্যা ট্র্যাক করা
  let totalUsers = Bot.getProperty("total_users_count", 0);
  
  let msg = "📊 **বটের সামগ্রিক পরিসংখ্যান (Stats):**\n\n";
  msg += "👥 **মোট ইউজার সংখ্যা:** `" + totalUsers + "` জন\n";
  msg += "📦 **স্টকে উপলব্ধ কার্ড:** `" + cardList.length + "` টি\n";
  msg += "⏳ **পেন্ডিং কয়েন রিকোয়েস্ট:** `" + reqList.length + "` টি\n";
  
  Bot.sendMessage(msg);
} else {
  Bot.sendMessage("❌ আপনি এডমিন নন।");
}
