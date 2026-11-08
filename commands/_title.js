/*CMD
  command: /title
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
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! টিকটক টাইটেল এক্সট্রাক্ট করতে ১ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

Bot.sendMessage("🎵 Send TikTok video link to extract Title👇");
Bot.runCommand("/tik_title_get");
