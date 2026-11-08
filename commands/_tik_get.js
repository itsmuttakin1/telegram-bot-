/*CMD
  command: /tik_get
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

var link = message;

if (!link || !link.includes("tiktok.com")) {
  Bot.sendMessage("❌ Please send a valid TikTok link!");
  return;
}

// 🪙 ব্যালেন্স চেক (২ কয়েন)
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 2) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! ভিডিও ডাউনলোড করতে ২ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

// ⏳ Processing Message
Bot.sendMessage("Please Wait Send Your Video 🥺...");

// 🔥 ৩টি ব্যাকআপ ফ্রি API-এর তালিকা
var apis = [
  "https://api.tiklydown.eu.org/api/download?url=" + encodeURIComponent(link),
  "https://www.tikwm.com/api/?url=" + encodeURIComponent(link),
  "https://api.maher-zubair.tech/download/tiktok?url=" + encodeURIComponent(link)
];

// বটের স্টেট সেভ রাখা
User.setProperty("tik_data", {
  link: link,
  apis: apis,
  index: 0
}, "json");

// ১ম API-তে রিকোয়েস্ট পাঠানো
HTTP.get({
  url: apis[0],
  success: "/tik_result"
});
