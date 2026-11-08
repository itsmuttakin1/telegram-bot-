/*CMD
  command: process_cc_gen
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

let bin = message ? message.trim() : "";
if (!bin || isNaN(bin) || bin.length < 6) {
  Bot.sendMessage("❌ ভুল BIN ফরম্যাট! দয়া করে অন্তত ৬ ডিজিটের সঠিক সংখ্যা পাঠান।");
  return;
}
if(bin.length > 8) { bin = bin.substring(0, 8); }

let total_cards = 50; // ৫০টি কার্ড
let cardsList = ""; // সব কার্ড এক বক্সে রাখার জন্য

for (let c = 0; c < total_cards; c++) {
  let ccNumber = bin;
  while (ccNumber.length < 15) {
    ccNumber += Math.floor(Math.random() * 10);
  }
  let sum = 0;
  let shouldDouble = true;
  for (let i = ccNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(ccNumber.charAt(i));
    if (shouldDouble) { digit *= 2; if (digit > 9) digit -= 9; }
    sum += digit;
    shouldDouble = !shouldDouble;
  }
  let checkSumDigit = (10 - (sum % 10)) % 10;
  ccNumber += checkSumDigit;
  
  let month = Math.floor(Math.random() * 12) + 1;
  if (month < 10) month = "0" + month;
  let year = Math.floor(Math.random() * 6) + 2026; 
  let cvc = Math.floor(Math.random() * 900) + 100;
  
  // একটার নিচে আরেকটা কার্ড যোগ হচ্ছে
  cardsList += ccNumber + "|" + month + "|" + year + "|" + cvc + "\n";
}

// পুরো ৫০টি কার্ডকে একটিমাত্র বড় কোড ব্লকের ভেতরে পাঠানো হচ্ছে
// এর ফলে বক্সের যেকোনো জায়গায় ১টি ক্লিক করলেই সম্পূর্ণ ৫০টি কার্ড একসাথে কপি হয়ে যাবে!
let responseMessage = "💳 **Generated Cards for BIN:** `" + bin + "`\n\n```\n" + cardsList + "```\n👇 ওপরের বক্সে ক্লিক করলেই **সবগুলো কার্ড একসাথে কপি** হয়ে যাবে।";

Bot.sendMessage(responseMessage);
