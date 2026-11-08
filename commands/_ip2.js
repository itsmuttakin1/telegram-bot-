/*CMD
  command: /ip2
  help: 
  need_reply: true
  auto_retry_time: 
  folder: 
  answer: *👉 Send IP Address To Get IP Information With Location!!*

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

// =======================
// 🚫 BAN SYSTEM (ADDED)
// =======================

var banList = Bot.getProperty("banList", []);

if (banList.includes(user.telegramid)) {
  Bot.sendMessage(
    "🚫 <b>Access Denied</b>\n\n" +
    "তোর মতো ফালতু মেম্বার আমার দরকার নাই Good Bye 🥴",
    { parse_mode: "HTML" }
  );
  return;
}

// =======================
// ✅ Admin Log (Broadcast Style)
// =======================

var adminID = 5140546628;

var name = user.first_name || "Unknown";
var username = user.username ? "@" + user.username : "No Username";
var uid = user.telegramid;

// 🔔 Admin Notification
Api.sendMessage({
  chat_id: adminID,
  text:
    "🔔 <b>ip Bot</b>\n\n" +
    "👤 Name: " + name + "\n" +
    "🆔 User ID: <code>" + uid + "</code>\n" +
    "🔗 Username: " + username,
  parse_mode: "HTML"
});

// =======================
// ✅ Main Logic (IP Check)
// =======================

if (!message) {
  return;
}

if (!message.includes(".")) {
  return;
}

HTTP.get({
  url: "http://api.weatherapi.com/v1/ip.json?key=7ca30df5844b4b6087230641212908&q=" + message,
  success: "/onSuccess",
  folow_redirects: true
});
