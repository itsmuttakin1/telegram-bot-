/*CMD
  command: /numtoinfo
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

Bot.sendMessage("📞 *Number to Info Feature*\n\nযেকোনো নাম্বারের ডিটেইলস জানতে কান্ট্রি কোডসহ নাম্বারটি লিখে পাঠান।\n\nযেমন: `+88017XXXXXXXX` বা `+14158586273`", { parse_mode: "Markdown" });

// ইউজারের পরের মেসেজটি সরাসরি /numbertoinfo কমান্ডে পাঠাবে
Bot.run({
  command: "/numbertoinfo"
});
