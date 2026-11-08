/*CMD
  command: 🧹 Clear Request List
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
  let reqList = Bot.getProperty("coin_requests_pool", []);
  
  // লুপ চালিয়ে সব আইডির ইন্টারনাল রিকোয়েস্ট মেমোরি ডিলিট করা হচ্ছে
  for (let i = 0; i < reqList.length; i++) {
    Bot.setProperty("req_" + reqList[i], null);
  }
  
  // মেইন পুুল খালি করা
  Bot.setProperty("coin_requests_pool", [], "json");
  Bot.sendMessage("🧹 **কয়েন রিকোয়েস্ট লিস্ট ও মেমোরি ডাটা সফলভাবে সম্পূর্ণ রিসেট করা হয়েছে!**");
}
