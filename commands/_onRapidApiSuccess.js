/*CMD
  command: /onRapidApiSuccess
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

if (!content) {
    Bot.sendMessage("❌ সার্ভার থেকে কোনো সাড়া পাওয়া যায়নি।");
    return;
}

var response = JSON.parse(content);
var videoUrl = response.direct_media_url;

if (videoUrl) {
    // 🪙 সাকসেসফুল হলে ১ কয়েন কেটে নিন
    let balance = Libs.ResourcesLib.userRes("coin");
    balance.remove(1);

    // ভিডিও সেন্ড করা
    Api.sendVideo({
        video: videoUrl,
        caption: "✨ *সফলভাবে ডাউনলোড হয়েছে!*\n\n💰 ১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: " + balance.value() + "\n\n⚡ Powered by ɪᴛs ᴍᴜᴛᴛᴀᴋɪɴ",
        parse_mode: "Markdown"
    });
} else {
    Bot.sendMessage("❌ দুঃখিত! ভিডিওর মূল লিঙ্কটি পাওয়া যায়নি। ভিডিওটি প্রাইভেট হতে পারে। (আপনার কোনো কয়েন কাটা হয়নি)");
}
