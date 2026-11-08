/*CMD
  command: 📊 View Stock
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

if (user.telegramid == 5140546628) {
  let cardList = Bot.getProperty("cards_pool", []);
  Bot.sendMessage("📦 **Current Stock Info:**\n\n💵 মোট উপলব্ধ কার্ড আছে: `" + cardList.length + "` টি।");
}
