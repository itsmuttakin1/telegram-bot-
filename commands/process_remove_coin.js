/*CMD
  command: process_remove_coin
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
    Bot.sendMessage("❌ ভুল ফরম্যাট! আবার `➖ Remove Coin` বাটনে চাপ দিয়ে সঠিক নিয়মে পাঠান।");
    return;
  }

  let userBalance = Libs.ResourcesLib.anotherUserRes("coin", userId);
  
  // চেক করা হচ্ছে ইউজারের ততটুকু কয়েন আছে কিনা
  if (userBalance.value() < amount) {
    Bot.sendMessage("⚠️ ইউজারের বর্তমান ব্যালেন্স (" + userBalance.value() + " কয়েন) আপনার দেওয়া পরিমাণের চেয়ে কম। তবে তার ব্যালেন্স এখন ০ করে দেওয়া হচ্ছে।");
    userBalance.set(0);
  } else {
    userBalance.add(-amount); // মাইনাস করা হলো
    Bot.sendMessage("✅ User `" + userId + "` এর অ্যাকাউন্ট থেকে **" + amount + "** কয়েন কেটে নেওয়া হয়েছে।");
    Bot.sendMessageToChatWithId(userId, "📉 এডমিন আপনার অ্যাকাউন্ট থেকে **" + amount + "** কয়েন কেটে নিয়েছেন।");
  }
}
