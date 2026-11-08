/*CMD
  command: /about
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

var aboutText = "ℹ️ <b>File Store Bot</b>\n\n" +
                "এই বট দিয়ে আনলিমিটেড ফাইল শেয়ারিং লিংক তৈরি করা যায়।\n" +
                "⚡ <i>Fast & Cloud Storage Supported</i>";

var keyboard = [[{ text: "🔙 মেইন মেনু", callback_data: "/start" }]];

Api.sendMessage({
  chat_id: chat.chatid,
  text: aboutText,
  parse_mode: "HTML",
  reply_markup: { inline_keyboard: keyboard }
});

