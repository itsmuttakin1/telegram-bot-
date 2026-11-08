/*CMD
  command: /fbdownload1
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

Api.sendChatAction({
  chat_id: chat.chatid,
  action: "typing"
});

// 🪙 কয়েন ব্যালেন্স চেক: ১ কয়েন আছে কি না
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 2) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! ফেসবুক ভিডিও ডাউনলোড করতে ২ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

Bot.sendMessage("📥 **Facebook Video Downloader**\n\n আপনার ফেসবুক ভিডিও বা রিলস (Reel) লিংকটি https://www.facebook.com/reel/19634... এমন হতে হবে Share Link কাজ না করতেও পারে 👇");
// ইউজারের পরবর্তী ইনপুটটি প্রসেস করার জন্য কমান্ড সেট করা হলো
Bot.runCommand("/process_fb_download");
