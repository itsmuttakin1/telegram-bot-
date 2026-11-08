/*CMD
  command: 📤 Upload File
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

Bot.sendMessage("📤 <b>যেকোনো ফাইল পাঠান:</b>\n\nআপনি Document, Video বা Photo পাঠাতে পারেন। বট স্বয়ংক্রিয়ভাবে একটি ইউনিক শেয়ার লিংক বানিয়ে দেবে।", { parse_mode: "HTML" });

// পরের মেসেজ হ্যান্ডেল করতে 'save_file' কমান্ডে পাঠাবে
Bot.runCommand("save_file");

