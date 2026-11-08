/*CMD
  command: 🎟️ M Box Activation Code
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
}
let channel = "@mrghost_121";

Api.getChatMember({
  chat_id: channel,
  user_id: user.telegramid,
  on_result: "/b1"
});
