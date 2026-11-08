/*CMD
  command: /daily1
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

/* ===== DAILY BONUS SYSTEM ===== */
let lastBonus = User.getProperty("last_bonus_date");
// বাংলাদেশ টাইমজোনের সাথে মিল রেখে নিখুঁত তারিখ ফরম্যাট
let today = new Date().toLocaleDateString("en-US", {timeZone: "Asia/Dhaka"});

if (lastBonus == today) {
  Bot.sendMessage("❌ আপনি আজ অলরেডি বোনাস নিয়েছেন! আগামী ২৪ ঘণ্টা পর আবার চেষ্টা করুন।");
} else {
  // 🪙 ফিক্সড ৫ কয়েন বোনাস সেট করা হলো
  let bonusCoin = 3;
  
  // বোনাস কয়েন মূল ব্যালেন্সে যোগ করুন
  let balance = Libs.ResourcesLib.userRes("coin");
  balance.add(bonusCoin);
  
  // আজকের তারিখ সেট করুন যাতে আজকের দিনে আর নিতে না পারে
  User.setProperty("last_bonus_date", today, "string");
  
  // ইউজারকে মেসেজ পাঠান
  Bot.sendMessage("🎉 অভিনন্দন! আপনি **" + bonusCoin + "** কয়েন ডেইলি বোনাস পেয়েছেন।\n\n💰 বর্তমান ব্যালেন্স: *" + balance.value() + "* কয়েন।");

  /* 📢 ADMIN NOTIFICATION */
  let adminID = 5140546628; // আপনার এডমিন আইডি
  let name = user.first_name;
  let username = user.username ? "@" + user.username : "No username";

  Api.sendMessage({
    chat_id: adminID,
    text: "🎁 *Daily Bonus Claimed!*\n\n" +
          "👤 Name: *" + name + "*\n" +
          "🔗 Username: " + username + "\n" +
          "🆔 ID: `" + user.telegramid + "`\n" +
          "💰 Claimed: *" + bonusCoin + " Coins*\n" +
          "📈 Total Balance: " + balance.value() + " Coins",
    parse_mode: "Markdown"
  });
}
