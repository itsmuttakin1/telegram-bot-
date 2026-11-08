/*CMD
  command: /bg2
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

/* ========== MAINTENANCE CHECK ========== */

var adminID = 5140546628;
var maintenance = Bot.getProperty("maintenance", false);

if (maintenance && user.telegramid != adminID) {
  Api.sendMessage({
    text:
      "🚧 <b>Bot Under Maintenance</b>\n\n" +
      "🔧 We are currently updating the system.\n" +
      "⏳ Please try again later.",
    parse_mode: "HTML"
  });
  return;
}

/* ========== MAIN BUTTON ========== */

var buttons = [
  [
    { title: "🌐 Open Background Remover", url: "https://itsmuttakin.pages.dev/bgremove" }
  ]
];

// Send button to user
Bot.sendInlineKeyboard(
  buttons,
  "👇 Click the button below to remove background instantly"
);

/* ========== ADMIN LOG ========== */

var name = user.first_name;
var username = user.username ? "@" + user.username : "No username";
var uid = user.telegramid;

Api.sendMessage({
  chat_id: adminID,
  text:
    "🎨 *Background Remover Used*\n\n" +
    "👤 Name: *" + name + "*\n" +
    "🔗 Username: *" + username + "*\n" +
    "🆔 ID: `" + uid + "`",
  parse_mode: "Markdown"
});
