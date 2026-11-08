/*CMD
  command: /start
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
   MR GHOST BOT — START COMMAND
   Public Utility Bot
========================================== */

// ===== CONFIGURATION =====
var ADMIN_ID = 5140546628;
var isAdmin = (user.telegramid == ADMIN_ID);

// ===== FILE SHARING DEEP LINK CHECK (DIRECT DELIVERY) =====
if (params && params.trim() !== "") {
  var cleanParam = params.trim();

  // file_ অথবা f_ উভয় প্রিফিক্সই হ্যান্ডেল করবে
  if (cleanParam.indexOf("file_") === 0 || cleanParam.indexOf("f_") === 0) {
    var fileData = Bot.getProperty(cleanParam);

    if (fileData) {
      Bot.sendMessage("⏳ আপনার ফাইল পাঠানো হচ্ছে...");

      // ফাইলের নিচে যুক্ত করার ইনলাইন বাটন
      var fileKeyboard = [
        [{ text: "📢 Join Main Channel", url: "https://t.me/mrghost_121" }]
      ];

      // মিডিয়া টাইপ অনুযায়ী ফাইল ও সাথে বাটন পাঠানো
      if (fileData.type == "video") {
        Api.sendVideo({
          chat_id: chat.chatid,
          video: fileData.file_id,
          caption: fileData.caption || "",
          reply_markup: { inline_keyboard: fileKeyboard }
        });
      } else if (fileData.type == "photo") {
        Api.sendPhoto({
          chat_id: chat.chatid,
          photo: fileData.file_id,
          caption: fileData.caption || "",
          reply_markup: { inline_keyboard: fileKeyboard }
        });
      } else {
        Api.sendDocument({
          chat_id: chat.chatid,
          document: fileData.file_id,
          caption: fileData.caption || fileData.file_name || "",
          reply_markup: { inline_keyboard: fileKeyboard }
        });
      }
    } else {
      Api.sendMessage({
        chat_id: chat.chatid,
        text: "❌ <b>ফাইল পাওয়া যায়নি!</b>\nফাইলটি মুছে ফেলা হয়েছে অথবা লিংকটি মেয়াদোত্তীর্ণ।",
        parse_mode: "HTML"
      });
    }

    return; // ফাইলে আসলে নিচের মেইন মেনু মেসেজ স্কিপ করবে
  }
}

// ===== MAINTENANCE MODE =====
var maintenance = Bot.getProperty("maintenance_mode", false);

if (maintenance && !isAdmin) {
  Api.sendMessage({
    chat_id: user.telegramid,
    text:
      "⚠️ BOT UNDER MAINTENANCE\n\n" +
      "বটটি বর্তমানে মেইনটেইন্যান্সে রয়েছে।\n" +
      "অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
  });
  return;
}

// ===== USER TRACKING =====
var users = Bot.getProperty("users", []);

if (!Array.isArray(users)) {
  users = [];
}

if (!users.includes(user.telegramid)) {
  users.push(user.telegramid);
  Bot.setProperty("users", users, "json");
}

// ===== REFERRAL & FIRST JOIN BONUS =====
var ref = params;

if (!User.getProperty("joined")) {
  User.setProperty("joined", true, "boolean");

  // Welcome Bonus: 15 Coins
  var userCoin = Libs.ResourcesLib.userRes("coin");
  userCoin.add(15);

  Api.sendMessage({
    chat_id: user.telegramid,
    text:
      "🎉 অভিনন্দন!\n\n" +
      "MR GHOST BOT-এ প্রথমবার যোগ দেওয়ার জন্য আপনি ১৫টি ফ্রি কয়েন পেয়েছেন। 🪙"
  });

  // Referral Bonus: 5 Coins
  if (
    ref &&
    /^\d+$/.test(String(ref).trim()) &&
    String(ref) !== String(user.telegramid)
  ) {
    var refUserCoin = Libs.ResourcesLib.anotherUserRes("coin", parseInt(ref, 10));
    refUserCoin.add(5);

    Api.sendMessage({
      chat_id: parseInt(ref, 10),
      text:
        "🎉 *NEW REFERRAL!*\n\n" +
        "➕ Bonus: +5 Coins Added\n" +
        "💰 Total Balance: " + refUserCoin.value() + " Coins",
      parse_mode: "Markdown"
    });
  }
}

// ===== SAVE USER INFORMATION =====
Bot.setProperty(
  "user_" + user.telegramid,
  {
    name: user.first_name,
    username: user.username || "N/A"
  },
  "json"
);

// ===== ADMIN NOTIFICATION =====
var name = user.first_name || "Unknown";
var username = user.username ? "@" + user.username : "N/A";

Api.sendMessage({
  chat_id: ADMIN_ID,
  text:
    "🚀 *MR GHOST BOT STARTED*\n\n" +
    "👤 Name: " + name + "\n" +
    "🆔 User ID: `" + user.telegramid + "`\n" +
    "🔗 Username: " + username,
  parse_mode: "Markdown"
});

// ===== MAIN REPLY KEYBOARD =====
var replyKeyboard = [
  [{ text: "📂 File Sharing Bot" }],
  [
    { text: "💰 Balance" },
    { text: "🎁 Daily Bonus" },
    { text: "🔗 Refer Link" }
  ],
  [
    { text: "🪪 Visa / Master Card Maker" },
    { text: "📹 Facebook Download" }
  ],
  [
    { text: "🎁 Redeem Code" },
    { text: "📝 Yt Title Tags Extract" }
  ],
  [
    { text: "🎥 YouTube Downloader" },
    { text: "📝 TikTok Title Extract" }
  ],
  [
    { text: "🎵 TikTok Download" },
    { text: "📞 Number to Info" }
  ],
  [
    { text: "🔳 Qr Maker" },
    { text: "🖼️ Thumbnail Downloader" }
  ],
  [
    { text: "🧩 Mod APK Apps" },
    { text: "🖼️ Background Remover" }
  ],
  [
    { text: "🆔 BD NID Tools" },
    { text: "⚠️ SMS BOMBER" }
  ],
  [
    { text: "🔐 Encode & Decode" },
    { text: "🛡️ Link Checker" }
  ],
  [
    { text: "🎓 Tutorials Hub" },
    { text: "📊 YouTube Watchtime" }
  ],
  [
    { text: "🌍 IP Tracker" },
    { text: "💫 Whatsapp Opener" }
  ],
  [
    { text: "🪪 Aadhaar Tools" }
  ]
];

// ===== PUBLIC BOT NOTICE =====
var welcomeText =
  "👋 *WELCOME TO MR GHOST BOT!*\n" +
  "━━━━━━━━━━━━━━━━━━\n\n" +
  "🌐 আমাদের বটটি একটি Public Utility Bot।\n" +
  "যে কেউ বটটি ব্যবহার করতে পারবেন।\n\n" +
  "⚠️ *IMPORTANT NOTICE | গুরুত্বপূর্ণ সতর্কবার্তা*\n\n" +
  "✅ বটটি বৈধ ও দায়িত্বশীল কাজে ব্যবহার করুন।\n" +
  "❌ প্রতারণা, স্প্যাম, অবৈধ কার্যকলাপ অথবা অন্যের ক্ষতি হয় এমন কাজে বট ব্যবহার করবেন না।\n\n" +
  "🚫 *MISUSE DISCLAIMER*\n" +
  "বটের কোনো ফিচার অপব্যবহার করলে তার দায়ভার সম্পূর্ণ ব্যবহারকারীর নিজের।\n" +
  "অপব্যবহারের জন্য অ্যাডমিন দায়ী থাকবেন না।\n\n" +
  "🛡️ *USE RESPONSIBLY • STAY SAFE*\n" +
  "👨‍💻 Powered by Mr Ghost";

Api.sendMessage({
  chat_id: user.telegramid,
  text: welcomeText,
  parse_mode: "Markdown",
  reply_markup: {
    keyboard: replyKeyboard,
    resize_keyboard: true,
    one_time_keyboard: false
  }
});

