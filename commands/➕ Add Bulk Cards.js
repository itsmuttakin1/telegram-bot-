/*CMD
  command: ➕ Add Bulk Cards
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

if (user.telegramid == 5140546628) {
  // ইউজারের পরবর্তী মেসেজটি ক্যাচ করার জন্য 'import_cards' কমান্ডে পাঠানো হচ্ছে
  Bot.sendMessage("📝 আপনার কার্ডগুলো নিচের ফরম্যাটে একটার নিচে একটা দিয়ে পেস্ট করুন:\n\n`5598880395051834|08|2030|038`\n`5598880395051834|08|2030|038`\n\n👇 এখন কার্ডের লিস্টটি পাঠান:");
  Bot.runCommand("import_cards");
}
