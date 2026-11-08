/*CMD
  command: /thumbnail2
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

Bot.sendMessage("🖼️ **YouTube Thumbnail Downloader**\n\nদয়া করে আপনার কাঙ্ক্ষিত ইউটিউব ভিডিওর লিংকটি এখানে পাঠান:\n\n_উদাহরণ: https://youtu.be/xxxxxx_");
Bot.runCommand("process_yt_thumbnail");
