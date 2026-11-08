/*CMD
  command: 🎨 PicsArt
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

let channel = "@mrghost_121";

Api.getChatMember({
  chat_id: channel,
  user_id: user.telegramid,
  on_result: "/PicsArt1"
});

