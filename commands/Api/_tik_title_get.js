/*CMD
  command: /tik_title_get
  help: 
  need_reply: true
  auto_retry_time: 
  folder: Api

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

var link = message;

if (!link) {
  Bot.sendMessage("❌ Please send a valid TikTok link!");
  return;
}

Bot.sendMessage("Extracting Title...");

// 🔥 TikWM API
var api = "https://tikwm.com/api/?url=" + encodeURIComponent(link);

HTTP.get({
  url: api,
  success: "/tik_title_result"
});
