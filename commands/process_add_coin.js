/*CMD
  command: process_add_coin
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

if (user.telegramid == 5140546628) {
  let params = message.split(" ");
  let userId = params[0];
  let amount = parseInt(params[1]);

  if (!userId || !amount || isNaN(amount)) {
    Bot.sendMessage("❌ ভুল ফরম্যাট! আবার `➕ Add Coin` বাটনে চাপ দিয়ে সঠিক নিয়মে পাঠান।");
    return;
  }

  // ResourcesLib দিয়ে কয়েন অ্যাড করা
  let userBalance = Libs.ResourcesLib.anotherUserRes("coin", userId);
  userBalance.add(amount);

  Bot.sendMessage("✅ User `" + userId + "` কে সফলভাবে **" + amount + "** কয়েন দেওয়া হয়েছে।");
  Bot.sendMessageToChatWithId(userId, "💰 এডমিন আপনার অ্যাকাউন্টে **" + amount + "** কয়েন যোগ করেছেন!");
}
