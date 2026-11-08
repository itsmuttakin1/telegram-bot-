/*CMD
  command: 📊 Stats
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

/* ==========================================
   MR GHOST BOT — STATS COMMAND
========================================== */

// মোট ইউজার সংখ্যা বের করা
var usersList = Bot.getProperty("users", []);
var totalBotUsers = Array.isArray(usersList) ? usersList.length : 0;

// ইউজারের কয়েন ব্যালেন্স
var userCoin = Libs.ResourcesLib.userRes("coin");
var currentBalance = userCoin ? userCoin.value() : 0;

// ইউজারের আপলোড সংখ্যা
var userUploads = User.getProperty("total_uploads") || 0;

var statsMessage = 
  "📊 <b>MR GHOST BOT — পরিসংখ্যান</b>\n" +
  "━━━━━━━━━━━━━━━━━━\n\n" +
  "👤 <b>ব্যবহারকারীর তথ্য:</b>\n" +
  "• নাম: " + (user.first_name || "User") + "\n" +
  "• আইডি: <code>" + user.telegramid + "</code>\n" +
  "• ইউজারনেম: @" + (user.username || "N/A") + "\n\n" +
  "📈 <b>অ্যাক্টিভিটি ও ব্যালেন্স:</b>\n" +
  "• মোট কয়েন: <b>" + currentBalance + "</b> 🪙\n" +
  "• মোট ফাইল আপলোড: <b>" + userUploads + "</b> টি\n" +
  "• বটের মোট ব্যবহারকারী: <b>" + totalBotUsers + "</b> জন\n\n" +
  "━━━━━━━━━━━━━━━━━━\n" +
  "⚠️ <b>সতর্কবার্তা ও ডিসক্লেইমার:</b>\n" +
  "বটের যেকোনো টুলস ও ফাইল শেয়ারিং সার্ভিস সম্পূর্ণ নিজ দায়িত্বে ব্যবহার করবেন। এর কোনো প্রকার অপব্যবহার, প্রতারণা, অবৈধ কার্যকলাপ বা স্প্যামিংয়ের জন্য <b>অ্যাডমিন কোনোভাবেই দায়ী থাকবে না</b>। অপব্যবহারকারীর অ্যাকাউন্ট যেকোনো সময় ব্যান করা হতে পারে।\n\n" +
  "👨‍💻 <b>Powered by Mr Ghost</b>";

var statsKeyboard = [
  [{ text: "📢 Join Main Channel", url: "https://t.me/mrghost_121" }],
  [{ text: "📂 File Sharing Bot", callback_data: "/upload_file" }]
];

Api.sendMessage({
  chat_id: chat.chatid,
  text: statsMessage,
  parse_mode: "HTML",
  disable_web_page_preview: true,
  reply_markup: {
    inline_keyboard: statsKeyboard
  }
});

