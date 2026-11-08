/*CMD
  command: /yt_ext_result
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

try {
  let parse = JSON.parse(content);

  // ডাটা চেক
  if (!parse || !parse.title) {
    Bot.sendMessage("❌ এই লিংক থেকে ডাটা বের করা যায়নি! (আপনার কোনো কয়েন কাটা হয়নি)");
    return;
  }

  // 🪙 ডাটা সফলভাবে পাওয়া গেছে, এখন ১ কয়েন কেটে নিন
  let balance = Libs.ResourcesLib.userRes("coin");
  balance.remove(1);

  // ডাটা কালেক্ট করা
  let title = parse.title || "No Title Found";
  let description = parse.description || "No Description Provided";
  
  // ট্যাগস যদি এপিআই লিস্ট আকারে দেয়, তবে কমা দিয়ে জোড়া লাগানো হবে
  let tags = "No Tags Found";
  if (parse.tags) {
    tags = Array.isArray(parse.tags) ? parse.tags.join(", ") : parse.tags;
  }

  // ডেসক্রিপশন অনেক বড় হলে টেলিগ্রাম মেসেজ লিমিটের জন্য কেটে ছোট করা (নিরাপত্তার জন্য)
  if (description.length > 2500) {
    description = description.substring(0, 2500) + "... (Truncated)";
  }

  // ইউজারকে মেসেজ পাঠানো
  let resText = "🎯 **YouTube Data Extracted Successfully!**\n\n" +
                "📌 **Title:**\n`" + title + "`\n\n" +
                "📝 **Description:**\n```\n" + description + "\n```\n\n" +
                "🏷️ **Tags / Keywords:**\n`" + tags + "`\n\n" +
                "🪙 _১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: " + balance.value() + " কয়েন।_";

  Bot.sendMessage(resText, { parse_mode: "Markdown" });

} catch (err) {
  Bot.sendMessage("❌ সার্ভার রেসপন্স এরর! দয়া করে আবার চেষ্টা করুন।");
}
