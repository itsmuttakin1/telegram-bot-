/*CMD
  command: check_join_for_download
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

var status = options.result.status;
var isJoined = (status == "member" || status == "administrator" || status == "creator");

var fileCode = User.getProperty("pending_file_code");

if (isJoined) {
  if (!fileCode) {
    Bot.sendMessage("❌ ফাইল কোড পাওয়া যায়নি। লিংকটি আবার চেষ্টা করুন।");
    return;
  }

  var fileData = Bot.getProperty(fileCode);

  if (!fileData) {
    Bot.sendMessage("❌ <b>ফাইল পাওয়া যায়নি!</b> ফাইলটি মুছে ফেলা হয়েছে বা লিংক ভুল।", { parse_mode: "HTML" });
    return;
  }

  Bot.sendMessage("⏳ আপনার ফাইল পাঠানো হচ্ছে...");

  // ফাইল টাইপ অনুযায়ী সেন্ড করা
  if (fileData.type == "video") {
    Api.sendVideo({
      chat_id: chat.chatid,
      video: fileData.file_id,
      caption: fileData.caption || ""
    });
  } else if (fileData.type == "photo") {
    Api.sendPhoto({
      chat_id: chat.chatid,
      photo: fileData.file_id,
      caption: fileData.caption || ""
    });
  } else {
    // ডিফল্ট হিসেবে Document
    Api.sendDocument({
      chat_id: chat.chatid,
      document: fileData.file_id,
      caption: fileData.caption || fileData.file_name || ""
    });
  }

  // কাজ শেষ হলে ক্লিয়ার করা
  User.setProperty("pending_file_code", null, "string");

} else {
  // ইউজার চ্যানেলে জয়েন না থাকলে বাটনসহ নোটিশ
  var joinText = "⚠️ <b>ফাইলটি ডাউনলোড করতে আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে!</b>\n\n" +
                 "নিচের বাটনে ক্লিক করে জয়েন করুন, তারপর আবার লিংকে চাপ দিন।";

  var keyboard = [
    [{ text: "📢 Join Channel", url: "https://t.me/mrghost_121" }],
    [{ text: "🔄 Try Again", url: "https://t.me/" + bot.name + "?start=" + fileCode }]
  ];

  Api.sendMessage({
    chat_id: chat.chatid,
    text: joinText,
    parse_mode: "HTML",
    reply_markup: { inline_keyboard: keyboard }
  });
}

