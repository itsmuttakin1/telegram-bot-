/*CMD
  command: show2
  help: 
  need_reply: true
  auto_retry_time: 
  folder: Admin 

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

Bot.setProperty(

"hide_"+message,

false,

"boolean"

);

Bot.sendMessage(
"✅ Added to leaderboard"
);
