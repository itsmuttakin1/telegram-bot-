/*CMD
  command: /tik_result
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

var tikData = User.getProperty("tik_data");
if (!tikData) return;

var data = null;
var isValidJson = true;

// 🛡️ সেফ পার্সিং (Ratelimit বা টেক্সট মেসেজ আসলে যেন কোড ক্র্যাশ না করে)
try {
  data = JSON.parse(content);
} catch(e) {
  isValidJson = false;
}

var videoUrl = null;
var title = "TikTok Video";
var index = tikData.index;

// 🔍 API রেসপন্স চেক করা
if (isValidJson && data) {
  if (index === 0 && data.video) { 
    // API 1: TiklyDown
    videoUrl = data.video.noWatermark || data.video.noWatermark_hd || data.video.watermark;
    title = data.title || title;
  } 
  else if (index === 1 && data.data && data.data.play) { 
    // API 2: TikWM
    videoUrl = data.data.play;
    title = data.data.title || title;
  } 
  else if (index === 2 && data.result) { 
    // API 3: Maher-Zubair
    videoUrl = data.result.url || data.result.noWatermark;
    title = data.result.title || title;
  }
}

// ✅ ভিডিও পাওয়া গেলে সেন্ড করা হবে
if (videoUrl) {
  Api.sendVideo({
    video: videoUrl,
    caption:
      "🎵 *TikTok Video Downloaded*\n\n" +
      "📌 " + title,
    parse_mode: "Markdown"
  });

  // 🪙 ভিডিও সফলভাবে যাওয়ার পর ২ কয়েন কেটে নেওয়া হবে
  let balance = Libs.ResourcesLib.userRes("coin");
  balance.remove(2);
  Bot.sendMessage("🪙 আপনার ব্যালেন্স থেকে ২ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: *" + balance.value() + "* কয়েন।");

  // সেভ করা ডাটা ক্লিয়ার করা
  User.setProperty("tik_data", null, "json");
  return;
}

// 🔄 বর্তমান API ফেল করলে বা Limit খেলে পরবর্তী API ট্রাই করার লজিক
var nextIndex = index + 1;

if (nextIndex < tikData.apis.length) {
  tikData.index = nextIndex;
  User.setProperty("tik_data", tikData, "json");

  // পরবর্তী API-তে রিকোয়েস্ট
  HTTP.get({
    url: tikData.apis[nextIndex],
    success: "/tik_result"
  });
} else {
  // ❌ সবকটি API ব্যর্থ হলে
  Bot.sendMessage("❌ সকল ডাউনলোড সার্ভার এখন ব্যস্ত আছে! কিছুক্ষণ পর আবার চেষ্টা করুন।");
  User.setProperty("tik_data", null, "json");
}
