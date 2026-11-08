/*CMD
  command: 🔗 Refer
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

// 🛠️ মেইনটেইন্যান্স চেক
if (user.telegramid != 5140546628 && Bot.getProperty("maintenance_mode", false)) {
  Api.sendMessage({
    chat_id: user.telegramid,
    text: "⚠️ Bot is currently under maintenance. Please try again later!\n\n👨‍💻 বট এখন মেইনটেইন্যান্স মোডে আছে। দয়া করে পরে চেষ্টা করুন।"
  });
  return;
}

let bot_name = bot.name; 
// Bots.business-এর স্ট্যান্ডার্ড রেফার লিংক ফরম্যাট
let reflink = "https://t.me/" + bot_name + "?start=r" + user.telegramid;

Bot.sendMessage("🔗 **আপনার রেফারেল লিংক:**\n\n" + reflink + "\n\n🎯 এই লিংকে কেউ প্রথমবার জয়েন করলে আপনি পাবেন 5 কয়েন**!");
