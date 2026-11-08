/*CMD
  command: save_file
  help: 
  need_reply: true
  auto_retry_time: 
  folder: 

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

/* ==========================================
   FILE UPLOAD & SHARE LINK GENERATOR
========================================== */

var fileId = null;
var fileType = null;
var fileName = "";
var caption = request.caption || "";

// টেলিগ্রাম ফাইল টাইপ ডিটেকশন
if (request.document) {
  fileId = request.document.file_id;
  fileType = "document";
  fileName = request.document.file_name || "Document";
} else if (request.video) {
  fileId = request.video.file_id;
  fileType = "video";
  fileName = "Video";
} else if (request.photo && request.photo.length > 0) {
  fileId = request.photo[request.photo.length - 1].file_id;
  fileType = "photo";
  fileName = "Photo";
}

if (fileId) {
  // ইউনিক আইডি তৈরি
  var uniqueCode = "file_" + Math.random().toString(36).substring(2, 9);

  // ডাটাবেসে সেভ করা
  Bot.setProperty(uniqueCode, {
    file_id: fileId,
    file_name: fileName,
    caption: caption,
    type: fileType
  }, "json");

  // লিংক এক লাইনে প্রস্তুত করা
  var shareLink = "https://t.me/" + bot.name + "?start=" + uniqueCode;

  var msg = "✅ <b>ফাইল সফলভাবে আপলোড হয়েছে!</b>\n\n" +
            "📁 <b>নাম:</b> " + fileName + "\n\n" +
            "🔗 <b>শেয়ার লিংক:</b>\n" +
            shareLink + "\n\n" +
            "<i>এই লিংকে ক্লিক করলে যে কেউ ফাইলটি পেয়ে যাবে।</i>";

  var keyboard = [
    [{ text: "📤 আরও আপলোড করুন", callback_data: "/upload" }],
    [{ text: "🔙 মেইন মেনু", callback_data: "/start" }]
  ];

  Api.sendMessage({
    chat_id: chat.chatid,
    text: msg,
    parse_mode: "HTML",
    disable_web_page_preview: true,
    reply_markup: { inline_keyboard: keyboard }
  });

} else {
  Bot.sendMessage("⚠️ অনুগ্রহ করে কোনো Document, Photo অথবা Video পাঠান।");
}

