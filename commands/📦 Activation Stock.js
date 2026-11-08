/*CMD
  command: 📦 Activation Stock
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

if (user.telegramid != 5140546628) {
  Bot.sendMessage("❌ আপনি এই বটের এডমিন নন।");
  return;
}

let activationList = Bot.getProperty(
  "activation_codes_pool",
  []
);

if (!Array.isArray(activationList)) {
  activationList = [];
}

Bot.sendMessage(
  "🎟️ *Activation Stock*\n\n" +
  "📦 মোট Activation Code: `" +
  activationList.length +
  "` টি"
);
