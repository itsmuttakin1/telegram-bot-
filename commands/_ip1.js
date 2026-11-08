/*CMD
  command: /ip1
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

let status = options.result.status;

if (status == "member" || status == "administrator" || status == "creator") {
  // SUCCESS
  Bot.sendMessage(
    ""
  );
  
  Bot.runCommand("/ip2"); // Main menu

} else {
  // FAILED
  Bot.sendMessage(
    "⛔ Access Denied!\n\n" +
    "❌ আগে channel join করতে হবে\n" +
    "❌ You must join the channel first\n\n" +
    "" +
    "" +
    ""
  );
}
