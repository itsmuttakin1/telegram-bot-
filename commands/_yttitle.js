/*CMD
  command: /yttitle
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

Api.sendChatAction({
  chat_id: chat.chatid,
  action: "typing"
});

// 🪙 কয়েন ব্যালেন্স চেক (ResourcesLib)
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 1) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! এই ফিচারটি ব্যবহার করতে ১ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

Bot.sendMessage("🎥 **YouTube Data Extractor**\n\nযে ভিডিওর Title, Description ও Tags চান, তার লিংকটি পাঠান 👇");
Bot.runCommand("/yt_ext_get");
