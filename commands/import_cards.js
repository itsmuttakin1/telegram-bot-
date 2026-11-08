/*CMD
  command: import_cards
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

if (user.telegramid != 5140546628) {
  Bot.sendMessage("❌ আপনি এই বটের এডমিন নন।");
  return;
}

if (!params || params.trim() == "") {

  Bot.sendMessage(
    "➕ *Add Bulk Cards*\n\n" +
    "প্রতিটি Card Code নতুন লাইনে লিখুন।\n\n" +
    "Example:\n\n" +
    "`CARD-001`\n" +
    "`CARD-002`\n" +
    "`CARD-003`\n" +
    "`CARD-004`"
  );

  return;
}

let cardList = Bot.getProperty(
  "cards_pool",
  []
);

if (!Array.isArray(cardList)) {
  cardList = [];
}

let cards = params
  .split(/[\r\n,\s]+/)
  .map(function(card) {
    return card.trim();
  })
  .filter(function(card) {
    return card.length > 0;
  });

let added = 0;
let duplicate = 0;

for (let i = 0; i < cards.length; i++) {

  let card = cards[i];

  if (cardList.indexOf(card) != -1) {
    duplicate++;
    continue;
  }

  cardList.push(card);
  added++;
}

Bot.setProperty(
  "cards_pool",
  cardList,
  "json"
);

Bot.sendMessage(
  "✅ *Cards Added Successfully!*\n\n" +
  "➕ Added: `" + added + "`\n" +
  "♻️ Duplicate: `" + duplicate + "`\n" +
  "💳 Total Card Stock: `" +
  cardList.length +
  "`"
);
