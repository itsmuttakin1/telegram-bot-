# টেলিগ্রাম গ্রুপ বট

## ফিচার
- Welcome / Goodbye মেসেজ (কাস্টমাইজযোগ্য)
- /warn → ৩ বার হলে অটো ব্যান
- /ban, /unban (গ্রুপ এডমিনদের জন্য)
- /ad → শুধু ADMIN_ID (5140546628) এর জন্য অ্যাডমিন প্যানেল খুলবে (ইনলাইন বাটন)
- Gemini AI দিয়ে অটো রিপ্লাই (বট কে মেনশন করলে বা রিপ্লাই দিলে)

## ⚠️ জরুরি — আগে এটা করুন
আপনি যে Gemini API key আমাকে পাঠিয়েছেন সেটা এই চ্যাটে পাবলিকলি শেয়ার হয়ে গেছে।
**Render এ ডিপ্লয় করার আগে Google AI Studio তে গিয়ে এই key টা Revoke করে নতুন একটা key বানান।**
লিংক: https://aistudio.google.com/app/apikey
নতুন key টা কাউকে কখনো চ্যাটে/কোডে না বসিয়ে শুধু Render এর Environment Variable এ বসান।

## GitHub এ আপলোড
```bash
git init
git add .
git commit -m "telegram group bot"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Render এ ডিপ্লয়
1. render.com এ লগইন করুন
2. New → Blueprint → আপনার GitHub রিপো সিলেক্ট করুন (render.yaml অটো ডিটেক্ট হবে)
   বা New → Background Worker → রিপো কানেক্ট করুন
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
3. Environment ভ্যারিয়েবল সেট করুন:
   - `BOT_TOKEN` → @BotFather থেকে পাওয়া টোকেন
   - `GEMINI_API_KEY` → নতুন (revoke করার পর জেনারেট করা) key
   - `ADMIN_ID` → 5140546628 (আগে থেকেই render.yaml এ আছে)
4. Deploy চাপুন

## BotFather এ সেটিংস
- বট কে গ্রুপে অ্যাড করুন
- বট কে গ্রুপ Admin বানান (ব্যান/মেসেজ ডিলিট পারমিশন সহ)
- Privacy Mode অফ করতে হবে যাতে বট সব মেসেজ দেখতে পারে:
  @BotFather → /mybots → বট সিলেক্ট → Bot Settings → Group Privacy → Turn off

## লিংক/ফরোয়ার্ড/প্রোমো অটো-মড
গ্রুপে কেউ লিংক, ফরোয়ার্ড মেসেজ, বা প্রোমোশনাল কিওয়ার্ড (join channel, earn money, প্রমো কোড ইত্যাদি) পাঠালে:
1. মেসেজ সাথে সাথে ডিলিট হবে
2. ইউজার একটা ওয়ার্নিং পাবে (reason সহ)
3. ৩টা ওয়ার্নিং হলে অটো ব্যান

গ্রুপ এডমিন ও মেইন ADMIN_ID এর মেসেজে এটা কাজ করবে না।
নির্দিষ্ট ডোমেইন (যেমন নিজের চ্যানেল লিংক) বাদ দিতে: `/whitelist t.me/yourchannel`
`/ad` প্যানেল থেকে পুরো ফিচারটা ON/OFF করা যাবে ("লিংক/প্রোমো অটো-ওয়ার্ন" বাটন)।

⚠️ বট কে অবশ্যই গ্রুপে **Delete Messages** permission সহ Admin বানাতে হবে, নাহলে মেসেজ ডিলিট হবে না (ওয়ার্নিং তবুও দেবে)।

## ব্যবহার
- গ্রুপে: `/warn` (রিপ্লাই দিয়ে), `/ban` (রিপ্লাই দিয়ে)
- প্রাইভেট চ্যাটে বট কে (ADMIN_ID দিয়ে): `/ad` → প্যানেল খুলবে
- AI রিপ্লাই পেতে বট কে মেনশন করুন বা বটের মেসেজে রিপ্লাই দিন

## ডেটা স্টোরেজ নোট
এখন `data.json` ফাইলে সেভ হয় — Render এর ফ্রি প্ল্যানে ডিস্ক পার্সিস্টেন্ট না, রিডিপ্লয়ে ডেটা মুছে যেতে পারে।
পার্মানেন্ট রাখতে চাইলে Render Disk অ্যাড করুন বা future এ SQLite/Postgres এ মাইগ্রেট করা যাবে — বললে করে দিব।
