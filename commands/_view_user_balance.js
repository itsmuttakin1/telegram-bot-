/*CMD
  command: /view_user_balance
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

// 🛠️ সিকিউরিটি চেক (নিশ্চিত করা যে অন্য কেউ এটি রান করছে না)
if (user.telegramid != 5140546628) {
  return;
}

let targetUserId = message ? message.trim() : "";

// ইনপুট ভ্যালিডেশন
if (!targetUserId || isNaN(targetUserId)) {
  Bot.sendMessage("❌ দয়া করে একটি সঠিক সংখ্যাবাচক টেলিগ্রাম আইডি (Telegram ID) দিন।");
  return;
}

// 🪙 ResourcesLib ব্যবহার করে টার্গেট ইউজারের কয়েন ব্যালেন্স বের করা
let userCoin = Libs.ResourcesLib.anotherUserRes("coin", targetUserId);

// টার্গেট ইউজারের প্রোফাইল ইনফো (যদি আপনার /start কমান্ডের মাধ্যমে সেভ হয়ে থাকে)
let userInfo = Bot.getProperty("user_" + targetUserId);
let userName = userInfo ? userInfo.name : "Unknown User";
let userUsername = userInfo && userInfo.username ? "@" + userInfo.username : "N/A";

// এডমিনকে রেজাল্ট পাঠানো
Bot.sendMessage(
  "📊 **User Balance Details:**\n\n" +
  "🆔 **User ID:** `" + targetUserId + "`\n" +
  "👤 **Name:** " + userName + "\n" +
  "🔗 **Username:** " + userUsername + "\n\n" +
  "💰 **Current Balance:** *" + userCoin.value() + "* Coins",
  { parse_mode: "Markdown" }
);
