/*CMD
  command: 🖼️ Thumbnail Downloader
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

// 🪙 কয়েন ব্যালেন্স চেক (ResourcesLib)
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 1) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! থাম্বনেইল ডাউনলোড করতে ১ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

Bot.sendMessage("🖼️ **YouTube Thumbnail Downloader**\n\nদয়া করে আপনার কাঙ্ক্ষিত ইউটিউব ভিডিওর লিংকটি এখানে পাঠান:\n\n_উদাহরণ: https://youtu.be/xxxxxx_");
Bot.runCommand("process_yt_thumbnail");
