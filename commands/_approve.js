/*CMD
  command: /approve
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
  let params = message.split(" ");
  let targetUserId = params[0] ? params[0].trim() : null;
  let amount = parseInt(params[1]);

  if (!targetUserId || !amount || isNaN(amount)) {
    Bot.sendMessage("❌ সঠিক ফরম্যাট ব্যবহার করুন। উদাহরণ: `/approve 5140546628 2` ");
    return;
  }

  // সরাসরি ইউজারের রিকোয়েস্ট স্ট্যাটাস চেক করা হচ্ছে
  let requestStatus = Bot.getProperty("req_" + targetUserId);

  if (requestStatus == "pending") {
    // ১. রিকোয়েস্ট স্ট্যাটাস ক্লিয়ার করা
    Bot.setProperty("req_" + targetUserId, "approved", "string");
    
    // ২. রিকোয়েস্ট লিস্ট (পুলের) দৃশ্যমান তালিকা থেকে রিমুভ করা
    let reqList = Bot.getProperty("coin_requests_pool", []);
    let updatedList = [];
    for (let i = 0; i < reqList.length; i++) {
      if (String(reqList[i]) != String(targetUserId)) {
        updatedList.push(String(reqList[i]));
      }
    }
    Bot.setProperty("coin_requests_pool", updatedList, "json");

    // ৩. ইউজারের রিকোয়েস্ট বাটন আনলক করার সিগন্যাল
    Bot.run({
      command: "unlock_user_request",
      options: { tg_id: targetUserId }
    });

    // ৪. কয়েন যোগ করা
    let userBalance = Libs.ResourcesLib.anotherUserRes("coin", targetUserId);
    userBalance.add(amount);

    Bot.sendMessage("✅ User `" + targetUserId + "` এর রিকোয়েস্ট সফলভাবে অ্যাপ্রুভ হয়েছে এবং তাকে **" + amount + "** কয়েন দেওয়া হয়েছে।");
    Bot.sendMessageToChatWithId(targetUserId, "🎉 এডমিন আপনার কয়েন রিকোয়েস্ট অ্যাপ্রুভ করেছেন এবং আপনার অ্যাকাউন্টে **" + amount + "** কয়েন যোগ করেছেন!");

  } else {
    Bot.sendMessage("❌ এই আইডিটি (`" + targetUserId + "`) রিকোয়েস্ট লিস্টে পাওয়া যায়নি বা অলরেডি অ্যাপ্রুভ হয়ে গেছে।");
  }
} else {
  Bot.sendMessage("❌ আপনি এডমিন নন।");
}
