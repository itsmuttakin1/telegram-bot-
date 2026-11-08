/*CMD
  command: /Whatsapp2
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

Bot.sendMessage(
  "📱 <b>Direct WhatsApp Chat Bot</b>\n\n" +
  "🌍 All country supported\n" +
  "📌 Contact save করা লাগবে না\n(No need to save number)\n\n" +
  "👉 শুধু নাম্বার পাঠাও\n(Send any WhatsApp number)\n" +
  "👉 Button এ click করলেই chat open হবে\n(Tap button to start chat instantly)\n\n" +
  "<b>Examples:</b>\n" +
  "• 017XXXXXXXX (BD)\n" +
  "• +919876543210 (India)\n" +
  "• 1234567890 (USA)\n\n" +
  "🚀 Send a number now 👇\n\n" +
  "📥 <b>Enter your WhatsApp number...</b>",
  { parse_mode: "html" }
);

Bot.runCommand("/nu");
