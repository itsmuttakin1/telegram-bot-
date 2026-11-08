/*CMD
  command: /numbertoinfo
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

// ইউজার যে নাম্বারটি পাঠিয়েছে তা নেওয়া হলো
var phoneNumber = message ? message.trim() : "";

// যদি ইউজার ভুল করে আবার বাটনে চাপ দেয় বা খালি মেসেজ দেয়
if (!phoneNumber || phoneNumber.includes("📞")) {
  Bot.sendMessage("❌ দয়া করে একটি সঠিক ফোন নাম্বার লিখে পাঠান।");
  return;
}

// 🪙 কয়েন ব্যালেন্স চেক: ২ কয়েন আছে কি না
let balance = Libs.ResourcesLib.userRes("coin");
if (balance.value() < 2) {
  Bot.sendMessage("❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! ফোন নাম্বারের তথ্য দেখতে ২ কয়েন লাগবে।\n\n🔗 রেফার করে কয়েন আর্ন করুন।");
  return;
}

// ওয়েটিং মেসেজ
Bot.sendMessage("⏳ তথ্য খোঁজা হচ্ছে, দয়া করে অপেক্ষা করুন...");

// আপনার দেওয়া দুটি API Key
var apiKeys = [
  "num_live_mneEFIScOsKerA8d3hXBMPHiF4HkZ3dEFqtIvHFv", 
  "num_live_nTrhy606oIdTtY38in7aAqRgEJNKgKBqwTlhbtEE"  
];

// র‍্যান্ডমলি যেকোনো একটি API Key সিলেক্ট করা
var randomIndex = Math.floor(Math.random() * apiKeys.length);
var selectedApiKey = apiKeys[randomIndex];

var apiUrl = "https://api.numlookupapi.com/v1/validate/" + encodeURIComponent(phoneNumber);

// HTTP GET রিকোয়েস্ট পাঠানো
HTTP.get({
  url: apiUrl,
  headers: {
    "apikey": selectedApiKey
  },
  success: "/onLoadingSuccess", 
  error: "/onLoadingError"      
});
