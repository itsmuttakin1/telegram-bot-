/*CMD
  command: /get_yt_link
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

let videoUrl = parse.video_with_audio[0].url;
let audioUrl = parse.audio && parse.audio[0] ? parse.audio[0].url : null;
let title = parse.title || "YouTube Video";

// 🎥 সরাসরি ভিডিও ফাইল টেলিগ্রামে পাঠানো
Api.sendVideo({
  chat_id: user.telegramid,
  video: videoUrl,
  caption: "🎥 **" + title + "**\n\n📥 _Downloaded via @"+bot.name+"_",
  parse_mode: "Markdown"
});

// 🎵 অডিও ফাইল থাকলে সেটিও সরাসরি পাঠানো (অপশনাল, চাইলে কোডটি রাখতে পারেন)
if (audioUrl) {
  Api.sendChatAction({
    chat_id: chat.chatid,
    action: "upload_audio"
  });
  
  Api.sendAudio({
    chat_id: user.telegramid,
    audio: audioUrl,
    title: title,
    caption: "🎵 **" + title + " (Audio)**",
    parse_mode: "Markdown"
  });
}

// 🪙 কাজ সফলভাবে শেষ হওয়ার পর ব্যালেন্স থেকে ১ কয়েন কেটে নিন
let balance = Libs.ResourcesLib.userRes("coin");
balance.remove(1);

Bot.sendMessage("🪙 আপনার ব্যালেন্স থেকে ১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: *" + balance.value() + "* কয়েন।");
