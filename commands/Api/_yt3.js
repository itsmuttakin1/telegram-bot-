/*CMD
  command: /yt3
  help: 
  need_reply: true
  auto_retry_time: 
  folder: Api

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

var link = message;

// 🪙 কয়েন ব্যালেন্স চেক (ResourcesLib)
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 1) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! ইউটিউব ভিডিও ডাউনলোড করতে ১ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

User.setProperty("vurl", link, "string");
Bot.sendMessage("Please Wait Jan🤫");

HTTP.get({
  url: "https://yt-vid.hazex.workers.dev/?url=" + encodeURIComponent(link),
  success: "/yt_v2",
  error: "error"
});
