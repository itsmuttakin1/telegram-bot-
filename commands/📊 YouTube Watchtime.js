/*CMD
  command: 📊 YouTube Watchtime
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

let channel = "@mrghost_121";

Api.getChatMember({
  chat_id: channel,
  user_id: user.telegramid,
  on_result: "/watchtime1"
});

