/*CMD
  command: /wink1
  help: 
  need_reply: false
  auto_retry_time: 
  folder: Mod Hub

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
    "
  );
  
  Bot.runCommand("/wink2"); // Main menu

} else {
  // FAILED
  Bot.sendMessage(
    "⛔ Access Denied!\n\n" +
    "❌ আগে channel join করতে হবে\n" +
    "❌ You must join the channel first\n\n" +
    "👉 Join: @mrghost_121\n" +
    "" +
    ""
  );
}
