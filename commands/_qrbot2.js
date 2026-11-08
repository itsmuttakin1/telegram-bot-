/*CMD
  command: /qrbot2
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

Bot.sendMessage("🔳 QR Code বানাতে নিচে text বা link পাঠাও 👇");
// ইউজার যখন কিছু লিখবে, তখন তা '/qr_make' কমান্ডে চলে যাবে
Bot.runCommand("/qr_make");
