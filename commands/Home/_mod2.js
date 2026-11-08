/*CMD
  command: /mod2
  help: 
  need_reply: false
  auto_retry_time: 
  folder: Home

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

/* ========== INLINE BUTTON ========== */
var inline_keyboard = [
  [ { text: "🌐 Visit Website (Tools)", url: "https://itsmuttakin.pages.dev" } ]
];

/* ========== MESSAGE ========== */
var text =
"⚠️ *Important Notice / গুরুত্বপূর্ণ নোটিশ*\n\n" +

"━━━━━━━━━━━━━━━\n\n" +

"🇧🇩 *বাংলা:*\n" +
"এখন থেকে প্রিমিয়াম অ্যাপস (যেমন: CapCut Pro, Movie Box, YouTube Premium ইত্যাদি) বটে আপডেট করতে অনেক সময় লাগে। তাই এখন থেকে দ্রুত আপডেট এবং সুপারফাস্ট ডাউনলোড স্পিডের জন্য সব MOD APK সরাসরি ওয়েবসাইটে পাবেন। \n\n" +
"নিচের বাটনে ক্লিক করে ওয়েবসাইটের *Tools* অপশন থেকে ডাউনলোড করুন।\n\n" +

"🇺🇸 *English:*\n" +
"Updating premium apps (like CapCut Pro, Movie Box, YouTube Premium, etc.) on the bot takes a lot of time. Therefore, to ensure faster updates and high-speed downloads, all MOD APK will now be available on our website.\n\n" +
"Click the button below and go to the *Tools* section to download.\n\n" +

"━━━━━━━━━━━━━━━";

/* ========== SHOW NOTICE WITH INLINE BUTTON ========== */
Api.sendMessage({
  text: text,
  parse_mode: "Markdown",
  reply_markup: JSON.stringify({
    inline_keyboard: inline_keyboard
  })  
});
