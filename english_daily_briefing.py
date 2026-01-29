#!/usr/bin/env python3
"""
English Daily Briefing Bot (30-day rotating content)
- One motivational quote
- One useful "today's insight" (evergreen / modern)
- 3 tips for a better day
- 3 Astroman tips
- 3 tasks you can do today
- BM.ge top 3 news + optional NewsAPI (if NEWS_API_KEY set)

Designed to run as a *secondary* file alongside your existing briefing script.
"""

import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# === Configuration (via GitHub Secrets / env vars) ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")  # optional

# === 30-day rotating content ===
QUOTES_30 = [
    "“Discipline is choosing what you want most over what you want now.” — Abraham Lincoln",
    "“Make it easy to start. Make it hard to stop.”",
    "“Small progress, done daily, becomes massive results.”",
    "“Clarity beats motivation. Decide, then move.”",
    "“Your future is built by ordinary days used well.”",
    "“The standard you walk past is the standard you accept.”",
    "“You don’t need more time. You need fewer distractions.”",
    "“Consistency is a superpower.”",
    "“Do it scared. Do it anyway.”",
    "“You can’t edit a blank page.”",
    "“Focus is saying no to 1,000 good ideas.” — Steve Jobs",
    "“When you feel like quitting, remember why you started.”",
    "“Energy follows attention.”",
    "“Your habits are voting every day for the person you’ll become.”",
    "“The best way to predict the future is to create it.” — Peter Drucker",
    "“Action creates confidence.”",
    "“If it matters, schedule it.”",
    "“Win the morning, win the day.”",
    "“Less, but better.”",
    "“You don’t rise to goals; you fall to systems.”",
    "“Start before you’re ready.”",
    "“Make the next step obvious.”",
    "“One hard thing first.”",
    "“Your calendar is your real strategy.”",
    "“Be reliable to yourself.”",
    "“Momentum loves a small start.”",
    "“Do the work that makes the work easier tomorrow.”",
    "“A plan beats a wish.”",
    "“Trade perfection for progress.”",
    "“Today is a fresh build.”",
]

USEFUL_INFO_30 = [
    "Useful today: Use 2-factor authentication (2FA) everywhere. It’s still one of the highest ROI security habits.",
    "Useful today: If you feel overwhelmed, reduce choices. Decide your ‘Top 3’ for the day and ignore the rest.",
    "Useful today: Sleep is a performance multiplier. Even one extra hour can improve focus, mood, and decision-making.",
    "Useful today: The fastest way to learn is feedback + repetition. Ship small, get feedback, iterate.",
    "Useful today: Deep work works best in blocks. Try one 45–90 minute ‘no notifications’ session today.",
    "Useful today: A short walk after meals can improve energy and reduce afternoon crashes.",
    "Useful today: Put your most important task on the calendar—if it’s not scheduled, it’s optional.",
    "Useful today: Your phone is a slot machine. Turn off non-essential notifications for a calmer brain.",
    "Useful today: Use checklists for repeatable processes. It frees mental energy for creativity.",
    "Useful today: Write down worries. Externalizing thoughts reduces anxiety and improves clarity.",
    "Useful today: Work in sprints. 20–30 minutes focused beats 2 hours distracted.",
    "Useful today: Hydration affects cognition. A glass of water right now is a free upgrade.",
    "Useful today: Keep meetings short. Default to 15/25/50 minutes instead of 30/60.",
    "Useful today: If a task takes <2 minutes, do it now. Momentum matters.",
    "Useful today: Price perception is shaped by context—display ‘good/better/best’ options to guide buyers.",
    "Useful today: Use a single capture system for ideas (Notes/Notion). Loose ideas vanish.",
    "Useful today: Clear your workspace for 2 minutes. Visual calm helps mental calm.",
    "Useful today: Protect mornings for creation; use afternoons for admin. Your brain has a rhythm.",
    "Useful today: Decide a ‘shutdown time’ for work to prevent burnout.",
    "Useful today: If you’re stuck, lower the bar: “What’s the smallest version I can do in 5 minutes?”",
    "Useful today: Default to plain language. Clear communication beats clever communication.",
    "Useful today: Social proof sells. Show reviews, photos, and real customer outcomes whenever possible.",
    "Useful today: A simple weekly review (wins + numbers + next week plan) keeps life on track.",
    "Useful today: Reduce friction: put what you need where you need it (chargers, tools, templates).",
    "Useful today: Train your attention like a muscle—one task, one tab, one timer.",
    "Useful today: Start with a 10-minute ‘setup’ to make the next 60 minutes effortless.",
    "Useful today: Use ‘If–Then’ plans: If I feel distracted, then I do 3 deep breaths and restart.",
    "Useful today: You don’t need more content—repurpose what already worked and improve it.",
    "Useful today: Raise average order value with bundles (telescope + app guide + accessory).",
    "Useful today: Close the loop: follow up with customers 24–48h after purchase to increase loyalty.",
]

DAY_TIPS_30 = [
    ["Start with one win (10 minutes).", "Do one deep-focus block before messages.", "End the day by planning tomorrow’s Top 3."],
    ["Move your body for 15 minutes.", "Eat protein + water early.", "Do the hardest task first."],
    ["Write your Top 3 on paper.", "Silence notifications for 60 minutes.", "Celebrate one small win."],
    ["Batch messages to 2–3 windows.", "Use a timer for focus.", "Take a short walk outside."],
    ["Say no to one distraction.", "Clean your desk for 2 minutes.", "Do one thing that future-you will thank you for."],
    ["Start with a quick review of goals.", "Break one big task into 3 steps.", "Stop work at a fixed time."],
    ["Plan your day in 5 minutes.", "Do a 25-minute sprint.", "Drink water before coffee."],
    ["Choose “one metric” to improve today.", "Do a small act of kindness.", "Make bedtime consistent."],
    ["Do one uncomfortable thing early.", "Write 3 gratitudes.", "Keep meals simple and clean."],
    ["Work on one priority before social media.", "Use ‘Do Not Disturb’ mode.", "Stretch for 3 minutes."],
    ["Set a single intention for the day.", "Protect your attention.", "Finish with a quick reflection."],
    ["Start tasks immediately (no warm-up).", "Use a checklist.", "Prepare tomorrow’s workspace tonight."],
    ["Make a micro-plan for your morning.", "Take breaks on purpose.", "Track one habit today."],
    ["Do one 45-minute deep work block.", "Avoid multitasking.", "Keep caffeine earlier in the day."],
    ["Start with learning (10 minutes).", "Do one sales outreach.", "Close your day by tidying."],
    ["Write the next action, not the whole plan.", "Stand up every hour.", "Eat slower, breathe."],
    ["Use “good enough” to ship.", "Reduce open tabs.", "Schedule your most important task."],
    ["Get sunlight in the first hour.", "Do 1 admin batch.", "Do 1 creative batch."],
    ["Delete one unnecessary commitment.", "Automate one small process.", "Send one appreciation message."],
    ["Prepare clothes/tools the night before.", "Do one thing fully (no splitting).", "Stop scrolling after 10 minutes."],
    ["Make your day visual: Top 3 + times.", "Use 2-minute rule once.", "End with a clean inbox."],
    ["Do 10 minutes of reading.", "Do 10 minutes of planning.", "Do 10 minutes of action."],
    ["Use breathing to reset (4–6 breaths).", "One task, one playlist.", "One clear finish line."],
    ["Plan your week’s priorities today.", "Review your numbers.", "Do one improvement in your system."],
    ["Start with the customer: what do they need?", "Write a simple offer.", "Follow up with one lead."],
    ["Work in a quiet environment.", "Use a short timer.", "Reward yourself after completion."],
    ["Do the ‘one call’ you’ve been avoiding.", "Keep today simple.", "Focus on output, not busywork."],
    ["Do a quick health check: water, food, movement.", "Do one meaningful conversation.", "Do one progress check."],
    ["Start with the smallest step.", "Keep attention on the process.", "Finish what you start."],
    ["Make today a ‘systems’ day: fix one routine.", "Remove one friction point.", "Document one repeatable process."],
]

ASTROMAN_TIPS_30 = [
    ["Show one best-selling item with a real use-case photo.", "Post one short educational fact about astronomy.", "Create a bundle offer (telescope + accessory)."],
    ["Ask customers to vote: “Which product next?”", "Pin top reviews to your profile.", "Add a limited-time ‘today only’ deal."],
    ["Message 3 schools/hotels about telescope experiences.", "Post a quick “unboxing” clip.", "Highlight one premium item with payment options."],
    ["Create a ‘Beginner Telescope Guide’ post.", "Offer free 10-min consultation in-store.", "Collect emails/phones for follow-ups."],
    ["Make a ‘Kids Space Corner’ product bundle.", "Run a 24-hour story Q&A.", "Show behind-the-scenes store life."],
    ["Post ‘before/after’ (with/without accessory).", "Feature one customer photo (with permission).", "Add a small upsell at checkout."],
    ["Promote binoculars + stargazing spots near Tbilisi.", "Create a weekend stargazing reminder post.", "Offer a mini workshop signup."],
    ["Do a simple giveaway: comment + share.", "Show 3 price tiers: good/better/best.", "Create a “gift finder” post."],
    ["Push one hero product with a clear CTA.", "Add a ‘what’s included’ graphic.", "Highlight warranty/after-sales support."],
    ["Post one ‘myth vs fact’ about space.", "Cross-post to TikTok/IG Reels.", "Boost the best-performing post with small budget."],
    ["Create a ‘Back to school’ STEM angle post.", "Offer school package PDF.", "Call 3 B2B leads."],
    ["Make a “Top 5 gifts under X GEL” post.", "Add urgency: limited stock.", "Track daily sales target publicly (story)."],
    ["Show store location + quick map.", "Share staff pick of the week.", "Offer free delivery threshold."],
    ["Post a 15-sec telescope demo clip.", "Invite customers to Astronomy Night.", "Start a loyalty stamp card idea."],
    ["Feature one new arrival with price & benefits.", "Ask customers for feedback poll.", "Offer bundle discount for 2+ items."],
    ["Create a “How to use star projector” tip post.", "Sell with benefits, not specs.", "Add a cross-sell: batteries/stand/tripod."],
    ["Show “setup time” (easy install) video.", "Make a “gift for couples” carousel.", "Offer engraving/personalization if available."],
    ["Post a customer story: why they bought it.", "Promote your website & delivery options.", "Retarget website visitors."],
    ["Make a “Night Sky Today” post.", "Link to one product that matches the sky event.", "Encourage in-store test."],
    ["Offer a “starter kit” for beginners.", "Add a quick FAQ post.", "Follow up with past buyers."],
    ["Promote a school partnership offer.", "Create a monthly event calendar.", "Collect testimonials from institutions."],
    ["Do a short live video demo.", "Offer a limited-time coupon code.", "Highlight installment/payment methods."],
    ["Post “Top 3 mistakes beginners make” and solutions.", "Sell accessories with solution framing.", "Use strong product photos (not busy)."],
    ["Create a “Cosmic gift wrapping” upsell.", "Show packaging quality.", "Use scarcity: only X left."],
    ["Push one premium telescope weekly.", "Show comparison chart.", "Offer free setup help."],
    ["Offer a weekend ‘Try before you buy’ slot.", "Promote family-friendly experience.", "Show store ambience with cosmic vibe."],
    ["Share 3 reviews in one post.", "Ask customers to tag friends.", "Run a micro-influencer collab."],
    ["Do a “Deal of the day” story.", "Drive foot traffic with simple CTA.", "Track conversions by channel."],
    ["Promote B2B wholesale inquiries.", "Post a corporate gift offer.", "Reach out to 3 companies."],
    ["Do a recap post: wins + bestsellers.", "Announce next week’s focus.", "Set a clear sales target and CTA."],
]

TASKS_30 = [
    ["Do one 45-min deep work block.", "Send 3 follow-up messages to leads.", "Prepare tomorrow’s Top 3."],
    ["Post one product story + CTA.", "Call 2 B2B prospects (school/hotel).", "Review yesterday’s sales numbers."],
    ["Update one product page or description.", "Create one bundle offer.", "Walk for 20 minutes."],
    ["Write a short script for 1 Reel/TikTok.", "Message 3 customers for reviews.", "Clean/organize one shelf area."],
    ["Plan 3 posts for the next 3 days.", "Run a 10 GEL boost to best post.", "Do 10 minutes learning."],
    ["Check inventory: top sellers + low stock.", "Create a ‘Top 5 gifts’ post draft.", "Do one admin batch (invoices)."],
    ["Reach out to one influencer.", "Prepare one in-store demo setup.", "Do one exercise session."],
    ["Write a 1-page B2B offer outline.", "Send it to 2 prospects.", "Do a short evening review."],
    ["Improve your checkout upsell message.", "Post one astronomy fact.", "Walk outside before noon."],
    ["Call 3 warm leads.", "Create a customer photo post.", "Prepare a mini weekly plan."],
    ["Audit your ad: keep only best creative.", "Update one banner/copy.", "Do a 25-min focus sprint."],
    ["Create a “Good/Better/Best” pricing post.", "Share 1 testimonial.", "Drink 2 extra glasses of water."],
    ["Organize product categories on site.", "Post one unboxing clip.", "Do a 10-min stretch."],
    ["DM 5 potential partners.", "Draft Astronomy Night idea.", "Review expenses quickly."],
    ["Make a 3-slide offer image.", "Post it.", "Reply to all messages in one batch."],
    ["Follow up with yesterday’s buyers.", "Ask for feedback.", "Do a short walk after meal."],
    ["Plan weekend stargazing promo.", "Bundle binoculars + map.", "Do 10 mins reading."],
    ["Clean photos for 5 products.", "Upload 1 to site.", "Do 1 deep work block."],
    ["Create “Deal of the Day” template.", "Use it today.", "Track result."],
    ["Write 3 short captions for products.", "Schedule posts.", "Do a mini review."],
    ["Call 2 schools.", "Offer demo session.", "Do 15 mins learning."],
    ["Create a FAQ post.", "Pin it.", "Do a short stretch."],
    ["Set a weekly sales target.", "Share it in story.", "Follow up 3 leads."],
    ["Create a premium telescope spotlight.", "Offer free setup.", "Do a walk."],
    ["Collect 3 testimonials.", "Turn into 1 post.", "Do one admin batch."],
    ["Optimize product bundle pricing.", "Update post/offer.", "Do a 45-min focus."],
    ["Plan next week content.", "Pick hero product.", "Review best seller margins."],
    ["DM 5 customers for user content.", "Post one astronomy tip.", "Do a short review."],
    ["Prepare B2B corporate gift pitch.", "Send to 2 companies.", "Do one exercise."],
    ["Summarize your week: wins + numbers.", "Choose next week focus.", "Reset workspace."],
]

def _idx_30() -> int:
    # stable daily rotation: day-of-year modulo 30
    return (datetime.now().timetuple().tm_yday - 1) % 30

def _safe_md(text: str) -> str:
    # Telegram Markdown can break on special characters, so we sanitize titles.
    if not text:
        return ""
    return (text.replace('[', ' ')
                .replace(']', ' ')
                .replace('(', ' ')
                .replace(')', ' ')
                .replace('*', ' ')
                .replace('_', ' ')
                .replace('`', ' ')
                .strip())

def get_bmge_top_news(max_items: int = 3) -> str:
    url = "https://bm.ge/category/all"
    headers = {"User-Agent": "Mozilla/5.0 (MorningBriefBot)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        items = []
        seen = set()

        for a in soup.select('a[href^="/news/"]'):
            href = (a.get("href") or "").strip()
            title = _safe_md(a.get_text(" ", strip=True))

            if not href or not title or len(title) < 10:
                continue

            full_url = "https://bm.ge" + href
            if full_url.lower() in seen:
                continue
            seen.add(full_url.lower())

            items.append((title, full_url))
            if len(items) >= max_items:
                break

        if not items:
            return "📰 *BM.ge Top News:*\n_No BM.ge news available right now._"

        lines = ["📰 *BM.ge Top News:*", ""]
        for t, u in items:
            lines.append(f"• [{t}]({u})")
        return "\n".join(lines).strip()

    except Exception:
        return "📰 *BM.ge Top News:*\n_No BM.ge news available right now._"

def get_newsapi_news(max_topics: int = 4, max_articles_per_topic: int = 1) -> str:
    """
    Optional extra global news via NewsAPI (if NEWS_API_KEY is configured).
    """
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE" or not NEWS_API_KEY:
        return ""  # silent if not configured

    topic_keywords = {
        "crypto": "cryptocurrency OR bitcoin OR ethereum",
        "ai": "artificial intelligence OR AI OR machine learning",
        "space": "astronomy OR space OR NASA OR SpaceX",
        "tech": "technology OR startup OR innovation",
        "stocks": "stock market OR trading OR nasdaq",
        "ecommerce": "e-commerce OR online shopping OR retail",
    }

    lines = ["🗞️ *Global Headlines (NewsAPI):*", ""]
    added = 0

    for topic, q in topic_keywords.items():
        if added >= max_topics:
            break
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": q,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_articles_per_topic,
                "apiKey": NEWS_API_KEY,
            }
            resp = requests.get(url, params=params, timeout=12)
            if resp.status_code != 200:
                continue
            data = resp.json()
            arts = data.get("articles", [])
            if not arts:
                continue
            a = arts[0]
            title = _safe_md(a.get("title", "No title"))
            link = a.get("url", "")
            lines.append(f"*{topic.upper()}:*")
            lines.append(f"• [{title}]({link})")
            lines.append("")
            added += 1
        except Exception:
            continue

    if added == 0:
        return ""
    return "\n".join(lines).strip()

def create_english_message() -> str:
    i = _idx_30()
    now = datetime.now()

    quote = QUOTES_30[i]
    useful = USEFUL_INFO_30[i]
    day_tips = DAY_TIPS_30[i]
    astro_tips = ASTROMAN_TIPS_30[i]
    tasks = TASKS_30[i]

    bm_news = get_bmge_top_news(3)
    global_news = get_newsapi_news(max_topics=4, max_articles_per_topic=1)

    message = f"""
☀️ *Good Morning, Rezi!*

📅 {now.strftime('%A, %B %d, %Y')}

━━━━━━━━━━━━━━━━━━━━

💬 *Motivational Quote:*
{quote}

━━━━━━━━━━━━━━━━━━━━

🧠 *Useful Today:*
{useful}

━━━━━━━━━━━━━━━━━━━━

✅ *3 Tips for a Better Day:*
1) {day_tips[0]}
2) {day_tips[1]}
3) {day_tips[2]}

━━━━━━━━━━━━━━━━━━━━

🪐 *3 Tips for ASTROMAN:*
1) {astro_tips[0]}
2) {astro_tips[1]}
3) {astro_tips[2]}

━━━━━━━━━━━━━━━━━━━━

🧾 *3 Tasks to Do Today:*
1) {tasks[0]}
2) {tasks[1]}
3) {tasks[2]}

━━━━━━━━━━━━━━━━━━━━

{bm_news}
{("\n\n" + global_news) if global_news else ""}

━━━━━━━━━━━━━━━━━━━━

🚀 *Win the day. One clean action at a time.*
""".strip()

    return message

def send_telegram_message(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            print(f"✅ English brief sent at {datetime.now()}")
            return True
        print(f"❌ Telegram send failed: {resp.status_code} | {resp.text}")
        return False
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def main():
    print("☀️ Generating English daily briefing...")
    msg = create_english_message()

    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60 + "\n")

    if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        send_telegram_message(msg)
    else:
        print("⚠️ Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as secrets/env vars.")

if __name__ == "__main__":
    main()
