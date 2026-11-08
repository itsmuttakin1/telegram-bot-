/*CMD
  command: 💳 Buy Card
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

// 🛠️ মেইনটেইন্যান্স চেক (ফিচার লক করার জন্য)
if (user.telegramid != 5140546628 && Bot.getProperty("maintenance_mode", false)) {
  Api.sendMessage({
    chat_id: user.telegramid,
    text: "⚠️ Bot is currently under maintenance. Please try again later!\n\n👨‍💻 বট এখন মেইনটেইন্যান্স মোডে আছে। দয়া করে পরে চেষ্টা করুন।"
  });
  return; // কোড এখানেই স্টপ হয়ে যাবে, নিচের মেইন কাজ রান হবে না
}
let balance = Libs.ResourcesLib.userRes("coin");

if(balance.value() < 1){
  Bot.sendMessage("❌ আপনার পর্যাপ্ত কয়েন নেই! কার্ড কিনতে ১ কয়েন লাগবে।");
} else {
  let cardList = Bot.getProperty("cards_pool", []);
  
  if(cardList.length == 0){
    Bot.sendMessage("😢 দুঃখিত! এই মুহূর্তে কোনো কার্ড স্টক এ নেই। এডমিনকে জানান।");
  } else {
    // ১ কয়েন কেটে নেওয়া হলো
    balance.add(-1);
    
    // স্টক থেকে প্রথম কার্ডটি নেওয়া হলো এবং স্টক থেকে ডিলিট করা হলো
    let textCard = cardList.shift();
    Bot.setProperty("cards_pool", cardList, "json"); // আপডেট স্টক সেভ
    
    // Random US ZIP Code জেনারেট করা (৫ ডিজিটের)
    let randomZip = Math.floor(10000 + Math.random() * 90000);
    
    // টেক্সট ব্যাকটিক ( ` ) দিয়ে ঘেরা থাকায় ক্লিক করলেই কপি হবে
    let msg = "🎁 আপনার কার্ড:\n`" + textCard + "`\n\n📌 **Random US ZIP:** `" + randomZip + "`\n\n(কার্ড ও জিপ কোডের ওপর ক্লিক করলেই কপি হয়ে যাবে।)";
    
    Bot.sendMessage(msg);
  }
}
