/*CMD
  command: handle_upload
  help: 
  need_reply: true
  auto_retry_time: 
  folder: 

  <<ANSWER

  ANSWER

  <<KEYBOARD

  KEYBOARD
  aliases: 
  group: 
CMD*/

// ১. ফাইল চেক
if (!request.message_id) {
    Bot.sendMessage("❌ Invalid file! Please upload or forward a file.");
    return;
}

// আপলোডের ফাইল ডাটা সাময়িকভাবে সেভ করে রাখা হচ্ছে যাতে জয়েন থাকলে রান করা যায়
User.setProperty("temp_upload_msg_id", request.message_id, "integer");

// মেম্বারশিপ চেক রান করা হচ্ছে
Api.getChatMember({
    chat_id: "@mrghost_121",
    user_id: user.telegramid,
    on_result: "check_join_for_upload"
});
