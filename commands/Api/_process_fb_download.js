/*CMD
  command: /process_fb_download
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

var msg = message ? message.trim() : "";

// ইনপুট চেক (যদি ইউজার আবার ভুল করে কমান্ড টেক্সট পাঠায়)
if (!msg || msg == "/fb_downloader") {
  Bot.sendMessage("❌ কোনো লিংক পাওয়া যায়নি। আবার চেষ্টা করুন।");
  return;
}

if (msg.includes("facebook.com") || msg.includes("fb.watch") || msg.includes("fb.gg") || msg.includes("fb.me")) {
    
    // 🪙 ডাবল সিকিউরিটি ব্যালেন্স চেক
    let balance = Libs.ResourcesLib.userRes("coin");
    if (balance.value() < 2) {
        Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই!");
        return;
    }

    Bot.sendMessage("⏳ *লিঙ্ক প্রসেস হচ্ছে... অনুগ্রহ করে একটু অপেক্ষা করুন।*");
    
    // ইউআরএল ক্লিন করা
    var cleanUrl = msg.split("?")[0]; 
    if (cleanUrl.includes("/share/r/")) {
        cleanUrl = cleanUrl.replace("/share/r/", "/reel/");
    }
    
    var apiUrl = "https://facebook-media-downloader1.p.rapidapi.com/get_media";
    
    var headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "facebook-media-downloader1.p.rapidapi.com",
        "x-rapidapi-key": "cf592df3e7msh30db0359b677defp17cc2bjsn0c3386203b12"
    };
    
    var body = {
        url: cleanUrl
    };
    
    HTTP.post({
        url: apiUrl,
        headers: headers,
        body: body,
        success: "/onRapidApiSuccess" 
    });
    
} else {
    Bot.sendMessage("⚠️ এটি সঠিক ফেসবুক লিঙ্ক নয়। আপনার কোনো কয়েন কাটা হয়নি।");
}
