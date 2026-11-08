/*CMD
  command: /tik_title_result
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

var data = JSON.parse(content);

if (!data || !data.data) {
  Bot.sendMessage("❌ Failed to fetch video data! (আপনার কোনো কয়েন কাটা হয়নি)");
  return;
}

// 🪙 ডাটা সফলভাবে পাওয়া গেছে, এখন ১ কয়েন কেটে নিন
let balance = Libs.ResourcesLib.userRes("coin");
balance.remove(1);

// টাইটেল বা ক্যাপশন এক্সট্রাক্ট করা
var title = data.data.title || "No Title Found Provided by Creator!";

// ইউজারকে টাইটেল পাঠানো (যাতে সহজে কপি করতে পারে)
Bot.sendMessage(
  "🎵 **TikTok Video Title Extracted Successfully!**\n\n" +
  "📝 **Title:**\n`" + title + "`\n\n" +
  "🪙 ১ কয়েন কেটে নেওয়া হয়েছে। বর্তমান ব্যালেন্স: *" + balance.value() + "* কয়েন।",
  { parse_mode: "Markdown" }
);
