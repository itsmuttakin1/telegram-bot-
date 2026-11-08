/*CMD
  command: verify_and_generate_link
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
   COMMAND: verify_and_generate_link
========================================== */

// লোডিং আইকন বন্ধ করতে অ্যানসার কলব্যাক কুয়েরি পাঠানো
if (request && request.id) {
  Api.answerCallbackQuery({
    callback_query_id: request.id
  });
}

// চ্যানেল জয়েন চেক শুরু
Api.getChatMember({
  chat_id: "@mrghost_121",
  user_id: user.telegramid,
  on_result: "check_join_for_upload"
});

