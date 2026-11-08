/*CMD
  command: /onLoadingSuccess
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

// API থেকে আসা JSON ডেটা পার্স করা
var data = JSON.parse(content);

// লিমিট শেষ হওয়ার চেক
if (data.message) {
  Bot.sendMessage("⚠️ এই API Key-টির লিমিট শেষ হয়েছে। দয়া করে আবার চেষ্টা করুন। (আপনার কোনো কয়েন কাটা হয়নি)");
  return;
}

// নাম্বারটি ভ্যালিড কি না চেক
if (!data.valid) {
  Bot.sendMessage("❌ দুঃখিত! এই নাম্বারটি সঠিক নয় বা এর কোনো তথ্য পাওয়া যায়নি। কান্ট্রি কোডসহ (যেমন: +880...) নাম্বার দিন। (আপনার কোনো কয়েন কাটা হয়নি)");
  return;
}

// 🪙 ডাটা সফলভাবে পাওয়া গেছে, এখন ২ কয়েন কেটে নিন
let balance = Libs.ResourcesLib.userRes("coin");
balance.remove(2);

// তথ্যগুলো ভেরিয়েবলে নেওয়া
var num = data.number || "N/A";

// 🌟 নাম্বারের মালিকের নাম (First Name ও Last Name থাকলে জোড়া লাগবে, না থাকলে N/A দেখাবে)
var firstName = data.first_name || "";
var lastName = data.last_name || "";
var fullName = (firstName + " " + lastName).trim() || "Not Found/N/A";

var country = data.country_name || "N/A";
var countryCode = data.country_code || "";
var city = data.location || "Not Found"; 
var carrier = data.carrier || "N/A";
var lineType = data.line_type || "N/A";

// সোশ্যাল মিডিয়া সার্চ লিংক জেনারেট
var cleanNumber = num.replace('?', '').replace('+', ''); 
var fbSearchLink = "https://www.facebook.com/search/top/?q=" + encodeURIComponent(num);
var waLink = "https://wa.me/" + cleanNumber;

// 🌟 সুন্দর প্রফেশনাল ও স্ট্রাকচার্ড রেজাল্ট মেসেজ 🌟
var infoText = "━━━━━━━━━━━━━━━━━━━━\n" +
               "📞 **NUMBER INFORMATION**\n" +
               "━━━━━━━━━━━━━━━━━━━━\n\n" +
               "👤 **Owner Name    :** `" + fullName + "`\n" +
               "🔹 **Phone Number  :** `" + num + "`\n" +
               "🌍 **Country Name  :** `" + country + "`\n" +
               "🆔 **Country Code  :** `" + countryCode + "`\n" +
               "🏙️ **City / Region :** `" + city + "`\n" +
               "📡 **Sim Company   :** `" + carrier + "`\n" +
               "📱 **Line Type     :** `" + lineType + "`\n\n" +
               "━━━━━━━━━━━━━━━━━━━━\n" +
               "🕵️‍♂️ **SOCIAL MEDIA TRACK**\n" +
               "💬 [Direct WhatsApp Chat](" + waLink + ")\n\n" +
               "━━━━━━━━━━━━━━━━━━━━\n" +
               "🪙 _২ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: " + balance.value() + " কয়েন।_\n" +
               "✅ *Search Completed Successfully!*";

Bot.sendMessage(infoText, { parse_mode: "Markdown", disable_web_page_preview: true });

