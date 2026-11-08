/*CMD
  command: onAiError
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

Bot.sendMessage("❌ HTTP Request Failed! আপনার বটের রিকোয়েস্ট OpenAI সার্ভারে পৌঁছায়নি অথবা Bots.business-এ আইপি ব্লক আছে।");
