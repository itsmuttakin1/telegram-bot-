/*CMD
  command: 📂 File Sharing Bot
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

/* ==========================================
   FILE SHARING REPLY KEYBOARD MENU
========================================== */

var sharePanelText = 
  "📂 *FILE SHARING SYSTEM — MR GHOST*\n" +
  "━━━━━━━━━━━━━━━━━━\n\n" +
  "⚡ এখানে আপনি যেকোনো Document, Photo বা Video আপলোড করে শেয়ার লিংক বানাতে পারবেন।\n\n" +
  "⚠️ *সতর্কবার্তা:* এই ফিচারের কোনো অপব্যবহার করলে অ্যাডমিন কোনোভাবেই দায়ী থাকবে না। সম্পূর্ণ দায়ভার ব্যবহারকারীর।\n\n" +
  "👇 নিচের বাটন থেকে নির্বাচন করুন:";

var fileMenuKeyboard = [
  [{ text: "📤 Upload File" }, { text: "📊 Stats" }],
  [{ text: "🔙 Back to Main Menu" }]
];

Api.sendMessage({
  chat_id: chat.chatid,
  text: sharePanelText,
  parse_mode: "Markdown",
  reply_markup: {
    keyboard: fileMenuKeyboard,
    resize_keyboard: true,
    one_time_keyboard: false
  }
});

