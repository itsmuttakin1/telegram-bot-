/*CMD
  command: 🎓 Tutorials Hub
  help: 
  need_reply: false
  auto_retry_time: 
  folder: Tutural

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

/* ========== MAINTENANCE CHECK ========== */

var adminID = 5140546628;
var maintenance = Bot.getProperty("maintenance", false);

if (maintenance && user.telegramid != adminID) {
  Api.sendMessage({
    text:
      "🚧 <b>Bot Maintenance চলতেছে!</b>\n\n" +
      "🔧 কিছু আপডেট করা হচ্ছে…\n" +
      "⏳ একটু পরে আবার চেষ্টা করো।",
    parse_mode: "HTML"
  });
  return;
}

/* ========== /start MENU ========== */

var buttons = [
  [ { title: "🤖 BOT Create", command: "/bot" } ],
  [ { title: "📂 File Share Bot Make", command: "/file" } ],
  [ { title: "🤖 AI Trend", command: "/aitrend" } ],
  [ { title: "📈 Unlimited Follower", command: "/unlimitedfollwer" } ],
  [ { title: "🌐 Cyber Website Make", command: "/cyber" } ],
  [ { title: "🎮 VPN / Game Crack", command: "/vpn" } ],

  // 🔜 Coming Soon
  [ { title: "💎 ChatGPT Plus", command: "/chatgpt" } ],
  [ { title: "🔥Free Hosting+ Giveaway", command: "/hosting" } ],
  [ { title: "🚧 Coming Soon", command: "/coming3" } ]
];

// ✅ Menu Show
if (user.telegramid == adminID) {
  Bot.sendInlineKeyboard(
    buttons,
    "🔐 *Welcome Admin!*\nMr Ghost Bot Control Panel:"
  );
} else {
  Bot.sendInlineKeyboard(
    buttons,
    "👋 *Welcome!*\n📚 এখানে সব টিউটোরিয়াল ভিডিও পাবা 👇"
  );
}

// ✅ Admin Log
var name = user.first_name;
var username = user.username ? "@" + user.username : "No username";
var uid = user.telegramid;

Api.sendMessage({
  chat_id: adminID,
  text:
    "📢 *Tutorial Access*\n\n" +
    "👤 Name: *" + name + "*\n" +
    "🔗 Username: *" + username + "*\n" +
    "🆔 ID: `" + uid + "`",
  parse_mode: "Markdown"
});
