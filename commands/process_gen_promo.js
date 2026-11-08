/*CMD
  command: process_gen_promo
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
  let codeName = params[0];
  let rewardAmount = parseInt(params[1]);
  let userLimit = parseInt(params[2]);

  if (!codeName || !rewardAmount || !userLimit || isNaN(rewardAmount) || isNaN(userLimit)) {
    Bot.sendMessage("❌ ভুল ফরম্যাট! আবার বাটনে চাপ দিয়ে সঠিক নিয়মে পাঠান।");
    return;
  }

  let promoData = {
    reward: rewardAmount,
    limit: userLimit,
    used_count: 0
  };

  Bot.setProperty("promo_" + codeName, promoData, "json");
  Bot.sendMessage("✅ **রিডিম কোড তৈরি হয়েছে!**\n\n🎫 কোড: `" + codeName + "`\n💰 কয়েন রিওয়ার্ড: " + rewardAmount + "\n👥 ব্যবহারের লিমিট: " + userLimit + " জন");
}
