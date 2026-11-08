/*CMD
  command: /maintenance
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

var text =
"🚧 <b>Bot Maintenance in Progress</b>\n\n" +
"🔧 System upgrade চলছে...\n" +
"✨ Adding new features & improving performance.\n\n" +
"⏳ Bot টি আগামী <b>2 hours</b> unavailable থাকবে।\n" +
"⏰ Please try again later.\n\n" +
"🙏 আপনার ধৈর্যের জন্য ধন্যবাদ!\n" +
"💙 Thank you for your patience!";

Bot.sendMessage({
  text: text,
  parse_mode: "HTML"
});
