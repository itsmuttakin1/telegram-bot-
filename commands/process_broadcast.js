/*CMD
  command: process_broadcast
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

if (user.telegramid == 5140546628 || user.telegramid == 7728010216) {
  if (!message) {
    Bot.sendMessage("❌ খালি মেসেজ ব্রডকাস্ট করা যাবে না।");
    return;
  }
  
  // আপনার কাস্টম ইউজার লিস্ট ডাটাবেজ থেকে আইডিগুলো আনা হচ্ছে
  let userList = Bot.getProperty("users", []);
  
  if (userList.length == 0) {
    Bot.sendMessage("❌ বটে কোনো ইউজার ডাটা পাওয়া যায়নি।");
    return;
  }

  // লুপ চালিয়ে প্রত্যেক ইউজারকে পার্সোনালি মেসেজ পাঠানো
  for (let i = 0; i < userList.length; i++) {
    Api.sendMessage({
      chat_id: userList[i],
      text: "📢 **Important Notice:**\n\n" + message
    });
  }
  
  Bot.sendMessage("✅ সফলভাবে " + userList.length + " জন ইউজারের ইনবক্সে ব্রডকাস্ট মেসেজ পাঠানো হয়েছে।");
}
