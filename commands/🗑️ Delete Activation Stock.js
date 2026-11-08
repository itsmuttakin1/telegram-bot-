/*CMD
  command: 🗑️ Delete Activation Stock
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

// আপনি যে প্রপার্টি নামে স্টক রাখেন (vip_codes_1day অথবা activation_codes_pool)
let currentStock = Bot.getProperty("vip_codes_1day", []);
let stockCount = Array.isArray(currentStock) ? currentStock.length : 0;

if (stockCount === 0) {
  Bot.sendMessage("⚠️ Activation Code স্টকে ইতিমধ্যে কোনো কোড নেই (স্টক খালি)!");
  return;
}

// স্টক সম্পূর্ণ খালি বা রিসেট করা
Bot.setProperty("vip_codes_1day", [], "json");

Bot.sendMessage(
  "🗑️ *Activation Code Stock Cleared!*\n\n" +
  "স্টক থেকে মোট *" + stockCount + "* টি কোড সফলভাবে মুছে ফেলা হয়েছে।\n" +
  "📦 বর্তমান অবশিষ্ট স্টক: *0* টি।",
  { parse_mode: "Markdown" }
);
