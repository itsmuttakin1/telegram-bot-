/*CMD
  command: /nu
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

// Get user input
var raw = message;

// Remove everything except digits
var number = raw.replace(/[^0-9]/g, "");

// Auto fix common formats

// 🇧🇩 Bangladesh
if (number.startsWith("01") && number.length == 11) {
  number = "880" + number.slice(1);
}

// 🇮🇳 India
else if (number.length == 10 && number.startsWith("6") || number.startsWith("7") || number.startsWith("8") || number.startsWith("9")) {
  number = "91" + number;
}

// 🇺🇸 USA
else if (number.length == 10) {
  number = "1" + number;
}

// If already international (10–15 digits), keep it

// Validation (WhatsApp standard)
if (number.length < 10 || number.length > 15) {
  Bot.sendMessage("❌ Invalid number!\n\nSend a valid WhatsApp number with country code.");
  return;
}

// Generate link
var link = "https://wa.me/" + number;

// Send button
Bot.sendInlineKeyboard(
  [[{ title: "💬 Open WhatsApp Chat", url: link }]],
  "🌍 Ready for all countries!\nClick below to start chat 👇"
);
