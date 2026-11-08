/*CMD
  command: process_redeem
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

let inputCode = message ? message.trim() : "";
let codeData = Bot.getProperty("promo_" + inputCode);

if (!codeData) {
  Bot.sendMessage("❌ দুঃখিত! এই রিডিম কোডটি সঠিক নয় বা এটি এক্সপায়ার হয়ে গেছে।");
  return;
}

// চেক করা হচ্ছে ইউজার এই কোড আগে একবার ব্যবহার করেছে কি না
let alreadyUsed = User.getProperty("used_code_" + inputCode);
if (alreadyUsed) {
  Bot.sendMessage("⚠️ আপনি এই রিডিম কোডটি ইতিমধ্যে একবার ব্যবহার করে ফেলেছেন!");
  return;
}

if (codeData.used_count >= codeData.limit) {
  Bot.sendMessage("😢 দুঃখিত! এই কোডটির ব্যবহারের সর্বোচ্চ সীমা (Limit) শেষ হয়ে গেছে।");
  Bot.setProperty("promo_" + inputCode, null); // কোড ডিলিট
  return;
}

// কয়েন যোগ করা
let balance = Libs.ResourcesLib.userRes("coin");
balance.add(codeData.reward);

// ইউজারের জন্য কোডটি লক করা
User.setProperty("used_code_" + inputCode, true, "boolean");

// কোডের ব্যবহার সংখ্যা ১ বাড়ানো
codeData.used_count += 1;
Bot.setProperty("promo_" + inputCode, codeData, "json");

Bot.sendMessage("🎉 অভিনন্দন! রিডিম কোডটি সফল হয়েছে। আপনি **" + codeData.reward + "** কয়েন পেয়েছেন।");

// এডমিনকে নোটিফিকেশন পাঠানো
let userMention = "[" + user.first_name + "](tg://user?id=" + user.telegramid + ")";
let adminMsg = "📢 **রিডিম কোড নোটিফিকেশন!**\n\nইউজার: " + userMention + "\nকোড ব্যবহার করেছে: `" + inputCode + "`\nস্ট্যাটাস: (" + codeData.used_count + "/" + codeData.limit + " বার ব্যবহৃত)";
Bot.sendMessageToChatWithId(5140546628, adminMsg);

// যদি লিমিট শেষ হয়ে যায়
if (codeData.used_count >= codeData.limit) {
  Bot.sendMessageToChatWithId(5140546628, "🛑 কোড: `" + inputCode + "` এর লিমিট শেষ হওয়ায় এটি অটো-ডিলিট করা হয়েছে।");
}
