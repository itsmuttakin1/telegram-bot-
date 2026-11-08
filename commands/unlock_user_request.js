/*CMD
  command: unlock_user_request
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

// এটি ইউজারের নিজস্ব প্রোপার্টি ক্লিয়ার করার জন্য রান হয়
User.setProperty("pending_coin_request", false, "boolean");
