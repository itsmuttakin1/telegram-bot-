/*CMD
  command: /onSuccess
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

if (!content) {
  return
}
var result = JSON.parse(content)
if (result.status == "fail") {
  Bot.sendMessage("*Error*\n\n_" + result.message + "_", {
    parse_mode: "Markdown"
  })
  return
}

var txt = "*🔻 IP Information Extracted*\n\n"
var resultKeys = Object.keys(result)
for (var i in resultKeys) {
  txt += `*${resultKeys[i]}* : ${result[resultKeys[i]]}\n`
}
Bot.sendMessage(txt, { parse_mode: "Markdown" })
Api.sendLocation({ latitude: result.lat, longitude: result.lon })

