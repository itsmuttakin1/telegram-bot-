/*CMD
  command: /how_download
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

var mes = "📥 How to Download:\n\n" +
"1️⃣ Click on the Video or Audio button\n" +
"2️⃣ A new page will open with the link\n" +
"3️⃣ Download from there ✅";

Api.sendVideo({
  video: "https://t.me/profilecoverbot4/4",  // replace with your video link
  caption: mes,
  parse_mode: "Markdown",
  protect_content: true
});
