/*CMD
  command: /buy
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

var ADMIN_ID = 5140546628;

var maintenance = Bot.getProperty("maintenance_mode", false);

if (maintenance && user.telegramid != ADMIN_ID) {
  Bot.sendMessage("🛠️ Bot বর্তমানে Maintenance Mode-এ আছে।");
  return;
}

var coin = Libs.ResourcesLib.userRes("coin");

if (coin.value() < 3) {
  Bot.sendMessage(
    "❌ পর্যাপ্ত Coin নেই!\n\n" +
    "💰 আপনার Balance: " + coin.value() + " Coin\n" +
    "💎 প্রয়োজন: 3 Coin"
  );
  return;
}

// প্রপার্টির নাম অবশ্যই কোড অ্যাড করার নামের সাথে মিল থাকতে হবে
var activationList = Bot.getProperty("vip_codes_1day", []);

if (!Array.isArray(activationList)) {
  activationList = [];
}

if (activationList.length < 1) {
  Bot.sendMessage(
    "❌ *Activation Code Out of Stock!*\n\n" +
    "পরে আবার চেষ্টা করুন।"
  );
  return;
}

// স্টক থেকে কোড বের করা ও ব্যালেন্স কাটা
var activationCode = activationList.shift();
coin.remove(10);

Bot.setProperty("vip_codes_1day", activationList, "json");

var date = new Date().toISOString();

// ইউজারের পার্সোনাল হিস্ট্রিতে সেভ করা
var myCodes = User.getProperty("my_purchased_codes", []);
if (!Array.isArray(myCodes)) {
  myCodes = [];
}
myCodes.push(activationCode);
User.setProperty("my_purchased_codes", myCodes, "json");

// ইউজারকে মেসেজ পাঠানো
Bot.sendMessage(
  "🎉 *Activation Code Purchased!*\n\n" +
  "🎟️ *Activation Code:*\n\n" +
  "`" + activationCode + "`\n\n" +
  "💰 Used: 3 Coin\n" +
  "💰 Remaining: " + coin.value() + " Coin\n" +
  "📅 Date: " + date
);

// অ্যাডমিনকে নোটিফিকেশন পাঠানো
Bot.sendMessageToChatWithId(
  ADMIN_ID,
  "🔔 *NEW ACTIVATION PURCHASE*\n\n" +
  "👤 User: " + (user.first_name || "Unknown") + "\n" +
  "🆔 User ID: `" + user.telegramid + "`\n\n" +
  "🎟️ Activation Code: `" + activationCode + "`\n" +
  "💰 Price: 3 Coin\n" +
  "💰 User Balance: " + coin.value() + " Coin\n" +
  "📦 Remaining Stock: " + activationList.length + "\n\n" +
  "📅 Date: " + date
);
