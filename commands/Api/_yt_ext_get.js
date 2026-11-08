/*CMD
  command: /yt_ext_get
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

if (!link || link == "/yt_extract") {
  Bot.sendMessage("❌ দয়া করে একটি সঠিক ইউটিউব ভিডিও লিংক দিন!");
  return;
}

Bot.sendMessage("Extracting Data from YouTube...");

// API Request
HTTP.get({
  url: "https://yt-vid.hazex.workers.dev/?url=" + encodeURIComponent(link),
  success: "/yt_ext_result",
  error: "/yt_ext_error",
  timeout: 6000 // ৬ সেকেন্ড টাইমআউট
});
