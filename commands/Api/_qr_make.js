/*CMD
  command: /qr_make
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

var text = message;

// ১. ইনপুট চেক
if (!text || text == "/qrbot") {
  Bot.sendMessage("❌ কিছু লিখো বা link দাও!");
  return;
}

// ২. কয়েন ব্যালেন্স চেক
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 1) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! QR Code বানাতে ১ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

// ৩. QR API
var qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + encodeURIComponent(text);

// ৪. QR Code পাঠানো
Api.sendPhoto({
  photo: qrUrl,
  caption:
    "✅ *QR Code Ready!*\n\n" +
    "📌 Data: `" + text + "`\n\n" +
    "🪙 ১ কয়েন কেটে নেওয়া হয়েছে।",
  parse_mode: "Markdown"
});

// ৫. ব্যালেন্স থেকে ১ কয়েন কাটা
balance.remove(1);
