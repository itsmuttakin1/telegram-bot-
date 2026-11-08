/*CMD
  command: check_join_for_upload
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

/* ==========================================
   COMMAND: check_join_for_upload
========================================== */

var status = (options && options.result) ? options.result.status : "";
var isJoined = (status == "member" || status == "administrator" || status == "creator");

var savedMsgId = User.getProperty("temp_upload_msg_id");
var fileName = User.getProperty("temp_upload_file_name") || "Shared File";
var userId = user ? user.telegramid : chat.chatid;

// 1. Channel join check
if (!isJoined) {
  var joinMsg = "⚠️ *You must join our channel to upload files!*\n\n" +
                "👉 Please join @mrghost_121 and try uploading again.\n\n" +
                "⚠️ *ফাইল আপলোড করতে আপনাকে অবশ্যই চ্যানেলে জয়েন থাকতে হবে!*\n\n" +
                "👉 দয়া করে @mrghost_121 চ্যানেলে জয়েন করে আবার ফাইলটি পাঠান।";
  
  Bot.sendMessage(joinMsg);
  return;
}

// 2. Coin balance check & Link generate
if (savedMsgId) {
  var balance = Libs.ResourcesLib.userRes("coin");
  if (balance.value() < 2) {
    Bot.sendMessage("⚠️ *Insufficient coins!*\n\nফাইল আপলোড করতে আপনার ২ কয়েন প্রয়োজন। বর্তমান ব্যালেন্স: " + balance.value() + " Coins");
    return;
  }

  var fileCode = "file_" + new Date().getTime();

  // Save in Bot Properties
  Bot.setProperty(fileCode + "_msg_id", savedMsgId, "integer");
  Bot.setProperty(fileCode + "_file_name", fileName, "string");
  Bot.setProperty(fileCode + "_chat_id", chat.chatid, "integer");

  // Deduct 2 coins
  balance.remove(2);

  var shareLink = "https://t.me/" + bot.name + "?start=" + fileCode;

  var responseMsg = "✅ *Upload Successful! (2 Coins Deducted)*\n" +
                    "👤 Your Balance: *" + balance.value() + "* Coins\n\n" +
                    "📁 *File Name:* " + fileName + "\n" +
                    "📂 *File Code (Click to Copy):*\n`" + fileCode + "`\n\n" +
                    "🔗 *Share Link:*\n" + shareLink + "\n\n" +
                    "✅ *আপলোড সফল হয়েছে! (২ কয়েন কাটা হয়েছে)*\n\n" +
                    "⚠️ *MISUSE DISCLAIMER*: কোনো ফাইলের অপব্যবহারের জন্য অ্যাডমিন দায়ী থাকবে না।";

  Api.sendMessage({
    chat_id: userId,
    text: responseMsg,
    parse_mode: "Markdown"
  });

  // Clear temp storage
  User.setProperty("temp_upload_msg_id", null);
  User.setProperty("temp_upload_file_name", null);
} else {
  Bot.sendMessage("⚠️ কোনো ফাইল খুঁজে পাওয়া যায়নি! দয়া করে আবার ফাইল পাঠান।");
}

