/*CMD
  command: /yt_v2
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

// Uploading animation
Api.sendChatAction({
  chat_id: chat.chatid,
  action: "upload_video"
});

// Parse API
let parse = JSON.parse(content);

if (!parse || !parse.video_with_audio || parse.video_with_audio.length == 0) {
  Bot.sendMessage("❌ Video download failed or link invalid!");
  return;
}

let video = parse.video_with_audio[0].url;
let audio = parse.audio && parse.audio[0] ? parse.audio[0].url : "";
let title = parse.title;

// Save audio
User.setProperty("audio", audio, "string");

// DIRECT TITLE
Api.sendMessage({
  text: title,
  parse_mode: "HTML"
});

// Buttons (আপনার আগের বাটনগুলো)
let button = [
  [
    { text: "🎥 Full HD Video Download", url: video }
  ],
  [
    { text: "🎵 High-Quality Audio (MP3)", url: audio }
  ],
  [
    { text: "Download Tutorial", callback_data: "/how_download" }
  ]
];

// Send download options
Api.sendMessage({
  text: " Choose Your Format",
  parse_mode: "HTML",
  reply_markup: { inline_keyboard: button }
});

// 🪙 সফলভাবে বাটন দেওয়ার পর ১ কয়েন কেটে নিন
let balance = Libs.ResourcesLib.userRes("coin");
balance.remove(1);

Bot.sendMessage("🪙 আপনার ব্যালেন্স থেকে ১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: *" + balance.value() + "* কয়েন।");
