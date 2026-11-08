/*CMD
  command: /visa1
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


// 🛠️ মেইনটেইন্যান্স চেক (ফিচার লক করার জন্য)
if (user.telegramid != 5140546628 && Bot.getProperty("maintenance_mode", false)) {
  Api.sendMessage({
    chat_id: user.telegramid,
    text: "⚠️ Bot is currently under maintenance. Please try again later!\n\n👨‍💻 বট এখন মেইনটেইন্যান্স মোডে আছে। দয়া করে পরে চেষ্টা করুন।"
  });
  return; // কোড এখানেই স্টপ হয়ে যাবে, নিচের মেইন কাজ রান হবে না
}// ১. টোটাল ইউজার কাউন্ট ট্র্যাকিং (Stats এর জন্য)
let totalUsers = Bot.getProperty("total_users_count", 0);
let alreadyStarted = User.getProperty("already_started");

if (!alreadyStarted) {
  // নতুন ইউজার প্রথমবার আসলে টোটাল ইউজার ১ জন বাড়বে
  Bot.setProperty("total_users_count", totalUsers + 1, "integer");
  
  // নতুন ইউজার নিজে জয়েন করার কারণে ৩টি কয়েন পাবে
  let balance = Libs.ResourcesLib.userRes("coin");
  balance.add(3);
  User.setProperty("already_started", true, "boolean");
  Bot.sendMessage("👋 স্বাগতম! আপনি বটের পক্ষ থেকে ৩টি ফ্রি কয়েন পেয়েছেন।");

  // ২. রেফারেল বোনাস লজিক (৩ কয়েন)
  if (params) {
    let referrerId = params.trim();
    
    // ইউজার যাতে নিজের লিংকে নিজে ক্লিক করে কয়েন না নিতে পারে
    if (referrerId != user.telegramid) {
      let refBalance = Libs.ResourcesLib.anotherUserRes("coin", referrerId);
      refBalance.add(3); // রেফারকারীকে ৩ কয়েন দেওয়া হলো
      
      // রেফারকারীর কাছে নোটিফিকেশন পাঠানো (ইউজার মেনশন সহ)
      let newUserMention = "[" + user.first_name + "](tg://user?id=" + user.telegramid + ")";
      let refMsg = "🎉 আপনার রেফারেল লিংকে নতুন ইউজার " + newUserMention + " জয়েন করেছে! আপনি **৩ কয়েন** পেয়েছেন।";
      Bot.sendMessageToChatWithId(referrerId, refMsg);
    }
  }
} else {
  Bot.sendMessage("👋 আবার স্বাগতম আমাদের বটে!");
}

// ৩. হোম কিবোর্ড বাটন শো করা (এখানে নিচে নতুন করে 🏠 Home বাটনটি যুক্ত করা হয়েছে)
Bot.sendKeyboard("💳 Buy Card, 🔗 Refer\n💰 My Balance,💳 CC Generator, 🎁 Redeem Code\n🏠 Home", "👇 নিচের বাটনগুলো ব্যবহার করুন:");
