/*CMD
  command: /b
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

var balance = Libs.ResourcesLib.userRes("coin").value();

// বাটন লেআউট (প্রতি লাইনে একটি করে)
var buttons = "💎 Buy VIP (1 Day -3 Coin)\n💰 Balance";

var msg = "👋 স্বাগতম!\n\n" +
  "💎 1 Day VIP — 10 Coin\n" +
  "💰 আপনার Balance — " + balance + " Coin\n\n" +
  "নিচের Menu থেকে একটি অপশন নির্বাচন করুন 👇";

// Bots.Business ফরম্যাট: Bot.sendKeyboard(বাটন, মেসেজ) এর জায়গায় মেসেজ আগে বা সঠিক অবজেক্ট
Bot.sendKeyboard(buttons, msg);
