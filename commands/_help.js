/*CMD
  command: /help
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

var helpText =
"MR GHOST — Cyber Security Bot\n\n" +

"About This Bot:\n" +
"MR GHOST is a professional cyber security bot providing multiple digital tools & resources.\n\n" +

"Available Tools:\n" +
"- Free Like / Comment Tools\n" +
"- Downloder\n" +
"- NID Maker\n" +
"- Hacking Tools & Tutorials\n" +
"- Mod APK\n" +
"- Free Income Methods\n" +
"- More Useful Tools\n\n" +

"Commands:\n" +
"/start - Start or restart the bot\n" +
"/help - Show this help menu\n" +
"/banlist - Channel rule break\n\n" +

"Channel Rules (Bangla):\n" +
"- আমাদের অফিসিয়াল চ্যানেলে অবশ্যই Join থাকতে হবে।\n" +
"- চ্যানেল Leave করলে Auto Ban হবে।\n" +
"- Ban হলে সব Tool ব্যবহার বন্ধ হবে।\n\n" +

"Channel Rules (English):\n" +
"- You must stay joined in our official channel.\n" +
"- Leaving the channel will result in auto ban.\n" +
"- Banned users lose access to all tools.\n\n" +

"Support:\n" +
"Developer: @helpghotsteam";

Api.sendMessage({
  text: helpText,
  reply_markup: {
    inline_keyboard: [
      [{ text: "📢 Join Channel", url: "https://t.me/mrghost_121" }],
      [{ text: "💬 Contact Admin", url: "https://t.me/helpghotsteam" }]
    ]
  },
  disable_web_page_preview: true
});
