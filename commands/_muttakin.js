/*CMD
  command: /muttakin
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

var email = message
var jon = "" + email.slice(0, 4) + "****@gmail.com"

if (!email.includes("@")) {
  var notEmailText = "<i>⚠️ Please send a valid email address!</i>"

  Api.sendMessage({
    text: notEmailText,
    parse_mode: "html",
    on_result: "/give"
  })
} else {
  BBAdmin.installBot({
    email: email,
    bot_id: bot.id
  })

  var userText =
    "<b>✅ Bot Claimed Successfully 🥳\n\n👉 Sent To " +
    email +
    "\n\n❤️ Developer : @itsmuttakin\n🔥 Don't share without credit 😊</b>"

  Api.sendMessage({
    text: userText,
    parse_mode: "html",
    disable_web_page_preview: true
  })

  var adminText =
    "<b>✅ New User Claimed Bot\n\n👤 User : <a href='tg://user?id=" +
    user.telegramid +
    "'>" +
    user.first_name +
    "</a>\n👉 Email : " +
    email +
    "</b>"

  Api.sendMessage({
    chat_id: "5140546628",
    text: adminText,
    parse_mode: "html",
    disable_web_page_preview: true
  })

  var channelText =
    "<b>✅ New User Claimed Bot\n\n👤 User : <a href='tg://user?id=" +
    user.telegramid +
    "'>" +
    user.first_name +
    "</a>\n💌 Email 👉 " +
    jon +
    "\n😍 To Claim The Bot, Just Send</b> <code>/give</code> <b> here 👉 @" +
    bot.name +
    "\n\n👑 Developer: ITS MUTTAKIN\n📞 Telegram: @itsmuttakin\n📢 Channel: https://t.me/Mr_ghost121\n🔥 Don't share without credit 😊</b>"

  Api.sendMessage({
    chat_id: "5140546628",
    text: channelText,
    parse_mode: "html",
    disable_web_page_preview: true
  })
}
