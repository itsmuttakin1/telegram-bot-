/*CMD
  command: process_activation_codes
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

if (user.telegramid != 5140546628) {
  return;
}

if (!message || message.trim() === "") {
  Bot.sendMessage("⚠️ কোনো কোড পাওয়া যায়নি। আবার চেষ্টা করুন।");
  return;
}

// লাইন ব্রেক ও স্পেস দিয়ে কোডগুলো আলাদা করা
var rawCodes = message.trim().split(/[\r\n]+/);
var validCodes = [];

for (var i = 0; i < rawCodes.length; i++) {
  var cleanCode = rawCodes[i].trim();
  if (cleanCode.length > 0) {
    validCodes.push(cleanCode);
  }
}

if (validCodes.length === 0) {
  Bot.sendMessage("❌ কোনো সঠিক কোড পাওয়া যায়নি!");
  return;
}

// বিদ্যমান স্টকে কোড যুক্ত করা
var currentStock = Bot.getProperty("vip_codes_1day", []);
var updatedStock = currentStock.concat(validCodes);

Bot.setProperty("vip_codes_1day", updatedStock, "json");

Bot.sendMessage(
  "✅ সফলভাবে *" + validCodes.length + "* টি নতুন কোড স্টকে যোগ হয়েছে!\n\n" +
  "📦 মোট বর্তমান স্টক: *" + updatedStock.length + "* টি।",
  { parse_mode: "Markdown" }
);
