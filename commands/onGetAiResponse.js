/*CMD
  command: onGetAiResponse
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

if (content) {
  try {
    var responseData = JSON.parse(content);
    
    // সফলভাবে উত্তর আসলে
    if (responseData && responseData.choices && responseData.choices[0] && responseData.choices[0].message) {
      var aiReply = responseData.choices[0].message.content;
      Bot.sendMessage(aiReply);
    } 
    // OpenAI যদি কোনো এরর কোড বা মেসেজ পাঠায়
    else if (responseData && responseData.error) {
      Bot.sendMessage("❌ OpenAI API Error:\n" + responseData.error.message);
    } 
    else {
      Bot.sendMessage("⚠️ ডাটা ফরম্যাটে সমস্যা। Raw Content: " + content);
    }
  } catch (err) {
    Bot.sendMessage("❌ JSON পার্সিং এরর। সার্ভার থেকে ভুল রেসপন্স এসেছে।");
  }
} else {
  Bot.sendMessage("❌ খালি রেসপন্স (Null Content) এসেছে।");
}
