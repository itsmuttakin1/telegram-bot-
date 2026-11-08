/*CMD
  command: process_yt_thumbnail
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

let url = message ? message.trim() : "";

if (!url || url == "🖼️ Thumbnail Downloader") {
  Bot.sendMessage("❌ কোনো লিংক পাওয়া যায়নি। আবার চেষ্টা করুন।");
  return;
}

// আবার ব্যালেন্স চেক (ডাবল সিকিউরিটি)
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 1) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! ১ কয়েন লাগবে।");
  return;
}

let videoId = "";

// ১. যদি Shorts বা মোবাইল/শেয়ার লিংক হয়
if (url.indexOf("shorts/") > -1) {
  let temp = url.split("shorts/")[1];
  videoId = temp ? temp.split(/[?#&]/)[0] : "";
} else if (url.indexOf("youtu.be/") > -1) {
  let temp = url.split("youtu.be/")[1];
  videoId = temp ? temp.split(/[?#&]/)[0] : "";
} else if (url.indexOf("watch?v=") > -1) {
  let temp = url.split("watch?v=")[1];
  videoId = temp ? temp.split("&")[0] : "";
} else if (url.indexOf("embed/") > -1) {
  let temp = url.split("embed/")[1];
  videoId = temp ? temp.split(/[?#&]/)[0] : "";
}

// ভিডিও আইডি ১১ ডিজিটের কি না তা নিশ্চিত করা
if (videoId && videoId.length == 11) {
  // হাই-কোয়ালিটি থাম্বনেইল ইমেজের লিংক
  let thumbnailUrl = "https://img.youtube.com/vi/" + videoId + "/maxresdefault.jpg";

  // ইউজারকে সরাসরি ছবি হিসেবে পাঠানো
  Api.sendPhoto({
    chat_id: user.telegramid,
    photo: thumbnailUrl,
    caption: "🎯 **আপনার ইউটিউব ভিডিওর থাম্বনেইল!**\n\n🔥 *Quality:* Ultra HD (Max Resolution)\n\n🪙 ১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: *" + (balance.value() - 1) + "* কয়েন।",
    parse_mode: "Markdown"
  });

  // 🪙 থাম্বনেইল সফলভাবে পাঠানোর পর ১ কয়েন কেটে নিন
  balance.remove(1);

} else {
  Bot.sendMessage("❌ এটি সঠিক ইউটিউব লিংক নয়!\n\n💡 দয়া করে ইউটিউব অ্যাপ থেকে সরাসরি Share বাটনে ক্লিক করে লিংক কপি করে পাঠান।\n(আপনার কোনো কয়েন কাটা হয়নি)");
}
