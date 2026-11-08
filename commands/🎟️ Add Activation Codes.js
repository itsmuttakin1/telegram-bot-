/*CMD
  command: 🎟️ Add Activation Codes
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

Bot.sendMessage(
  "🎟️ *Add Activation Codes*\n\n" +
  "এখন আপনার Activation Code গুলো পাঠান।\n\n" +
  "প্রতিটি Code নতুন লাইনে দিন:\n\n" +
  "`ACT-001`\n" +
  "`ACT-002`\n" +
  "`ACT-003`\n" +
  "`ACT-004`\n\n" +
  "একসাথে অনেক Code পাঠাতে পারবেন।"
);

Bot.runCommand("process_activation_codes");
