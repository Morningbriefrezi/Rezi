#!/usr/bin/env python3
"""
Rezi Morning Brief v2.0 — AI-Summarized, Bilingual (Georgian + English)
Sectors: AI & Tech | Crypto & Finance | Space & Astronomy | E-commerce | Georgian Business News
Delivery: Telegram Bot via GitHub Actions
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")

# ── RSS Feeds per Sector ───────────────────────────────────────────────────────
SECTORS = {
    "🤖 AI & Tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    ],
    "₿ Crypto & Finance": [
        "https://feeds.feedburner.com/CoinDesk",
        "https://cointelegraph.com/rss",
    ],
    "🚀 Space & Astronomy": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://www.space.com/feeds/all",
    ],
    "🛍️ E-commerce & Retail": [
        "https://feeds.feedburner.com/practicalecommerce",
        "https://techcrunch.com/tag/e-commerce/feed/",
    ],
    "🇬🇪 Georgian Business": [
        "https://bm.ge/rss",
        "https://tabula.ge/geo/rss.xml",
    ],
}

ARTICLES_PER_SECTOR = 3

# ── 30-day rotating Astroman tasks ────────────────────────────────────────────
ASTROMAN_TASKS_30 = [
    ["Show one best-seller with real use-case photo.", "Post one astronomy fact.", "Create a bundle offer."],
    ["Ask customers: 'Which product next?'", "Pin top reviews.", "Add a 'today only' flash deal."],
    ["Message 3 schools/hotels about telescope experiences.", "Post a quick unboxing clip.", "Highlight premium item with payment options."],
    ["Create a 'Beginner Telescope Guide' post.", "Offer free 10-min consultation.", "Collect emails for follow-up."],
    ["Make a 'Kids Space Corner' bundle.", "Run a 24h story Q&A.", "Show behind-the-scenes store life."],
    ["Post 'before/after' (with/without accessory).", "Feature one customer photo.", "Add a small upsell at checkout."],
    ["Promote binoculars + stargazing spots near Tbilisi.", "Post weekend stargazing reminder.", "Offer a mini workshop signup."],
    ["Do a simple giveaway: comment + share.", "Show 3 price tiers: good/better/best.", "Create a 'gift finder' post."],
    ["Push one hero product with clear CTA.", "Add a 'what's included' graphic.", "Highlight warranty/after-sales support."],
    ["Post one 'myth vs fact' about space.", "Cross-post to TikTok/IG Reels.", "Boost best-performing post with small budget."],
    ["Create a 'Back to school' STEM angle post.", "Offer school package PDF.", "Call 3 B2B leads."],
    ["Make a 'Top 5 gifts under X GEL' post.", "Add urgency: limited stock.", "Track daily sales target in story."],
    ["Show store location + quick map.", "Share staff pick of the week.", "Offer free delivery threshold."],
    ["Post a 15-sec telescope demo clip.", "Invite customers to Astronomy Night.", "Start a loyalty stamp card."],
    ["Feature one new arrival with price & benefits.", "Ask customers for feedback poll.", "Offer bundle discount for 2+ items."],
    ["Create a 'How to use star projector' tip.", "Sell with benefits, not specs.", "Add a cross-sell: batteries/stand/tripod."],
    ["Show 'setup time' (easy install) video.", "Make a 'gift for couples' carousel.", "Offer personalization if available."],
    ["Post a customer story: why they bought it.", "Promote your website & delivery options.", "Retarget website visitors."],
    ["Make a 'Night Sky Tonight' post.", "Link to one product matching a sky event.", "Encourage in-store test."],
    ["Offer a 'starter kit' for beginners.", "Add a quick FAQ post.", "Follow up with past buyers."],
    ["Promote a school partnership offer.", "Create a monthly event calendar.", "Collect testimonials from institutions."],
    ["Do a short live video demo.", "Offer a limited-time coupon code.", "Highlight installment/payment methods."],
    ["Post 'Top 3 mistakes beginners make' + solutions.", "Sell accessories with solution framing.", "Use strong product photos."],
    ["Create a 'Cosmic gift wrapping' upsell.", "Show packaging quality.", "Use scarcity: only X left."],
    ["Push one premium telescope weekly.", "Show comparison chart.", "Offer free setup help."],
    ["Offer a weekend 'Try before you buy' slot.", "Promote family-friendly experience.", "Show store cosmic ambience."],
    ["Share 3 reviews in one post.", "Ask customers to tag friends.", "Run a micro-influencer collab."],
    ["Do a 'Deal of the Day' story.", "Drive foot traffic with simple CTA.", "Track conversions by channel."],
    ["Promote B2B wholesale inquiries.", "Post a corporate gift offer.", "Reach out to 3 companies."],
    ["Do a recap: wins + bestsellers.", "Announce next week's focus.", "Set a clear sales target and CTA."],
]

# ── RSS Fetcher ────────────────────────────────────────────────────────────────
def fetch_rss(url: str, max_items: int = ARTICLES_PER_SECTOR) -> list:
    """Fetch RSS/Atom feed and return list of {title, link, summary} dicts."""
    headers = {"User-Agent": "MorningBriefBot/2.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        ns = ""
        if "atom" in root.tag.lower() or root.tag.startswith("{http://www.w3.org/2005/Atom}"):
            ns = "{http://www.w3.org/2005/Atom}"

        items = []
        if ns:
            for entry in root.findall(f"{ns}entry")[:max_items]:
                title = (entry.findtext(f"{ns}title") or "").strip()
                link_el = entry.find(f"{ns}link")
                link = link_el.get("href", "") if link_el is not None else ""
                summary = (entry.findtext(f"{ns}summary") or entry.findtext(f"{ns}content") or "").strip()[:200]
                if title:
                    items.append({"title": title, "link": link, "summary": summary})
        else:
            channel = root.find("channel") or root
            for item in channel.findall("item")[:max_items]:
                title = (item.findtext("title") or "").strip()
                link  = (item.findtext("link") or "").strip()
                desc  = (item.findtext("description") or "").strip()[:200]
                if title:
                    items.append({"title": title, "link": link, "summary": desc})

        return items
    except Exception as e:
        print(f"  WARNING: RSS fetch failed for {url}: {e}")
        return []

def get_all_news() -> dict:
    """Fetch news for all sectors."""
    all_news = {}
    for sector, feeds in SECTORS.items():
        articles = []
        for feed_url in feeds:
            fetched = fetch_rss(feed_url)
            for a in fetched:
                if a not in articles:
                    articles.append(a)
            if len(articles) >= ARTICLES_PER_SECTOR:
                break
        all_news[sector] = articles[:ARTICLES_PER_SECTOR]
        print(f"  OK {sector}: {len(all_news[sector])} articles")
    return all_news

# ── BM.ge Scraper (Georgian Business fallback) ────────────────────────────────
def scrape_bmge(max_items: int = 3) -> list:
    """Scrape BM.ge top news as backup."""
    try:
        r = requests.get("https://bm.ge/rss", headers={"User-Agent": "MorningBriefBot/2.0"}, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        channel = root.find("channel") or root
        for item in channel.findall("item")[:max_items]:
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link") or "").strip()
            if title:
                items.append({"title": title, "link": link, "summary": ""})
        if items:
            return items
    except Exception:
        pass

    try:
        import re
        r = requests.get("https://bm.ge/category/all", headers={"User-Agent": "MorningBriefBot/2.0"}, timeout=12)
        items = []
        seen = set()
        matches = re.findall(r'href="(/news/[^"]+)"[^>]*>([^<]{10,})', r.text)
        for href, text in matches:
            url = "https://bm.ge" + href
            title = text.strip()
            if url not in seen and title:
                seen.add(url)
                items.append({"title": title, "link": url, "summary": ""})
            if len(items) >= max_items:
                break
        return items
    except Exception as e:
        print(f"  WARNING: BM.ge scrape failed: {e}")
        return []

# ── AI Summarizer ─────────────────────────────────────────────────────────────
def summarize_with_openai(all_news: dict) -> str:
    """Send headlines to OpenAI, get bilingual digest."""
    if not OPENAI_API_KEY:
        return format_raw_headlines(all_news)

    news_block = ""
    for sector, articles in all_news.items():
        news_block += f"\n## {sector}\n"
        if articles:
            for i, a in enumerate(articles, 1):
                news_block += f"{i}. {a['title']}\n"
                if a.get("summary"):
                    news_block += f"   Context: {a['summary'][:150]}\n"
        else:
            news_block += "No articles available.\n"

    prompt = f"""You are a sharp morning news editor writing a daily brief for Rezi — a Georgian entrepreneur who runs a telescope shop (Astroman.ge) and follows tech, crypto, space, e-commerce, and Georgian business news.

Here are today's top headlines from 5 sectors:
{news_block}

Write a clean morning digest with these exact rules:
1. For each sector with news, write 2-3 sentences summarizing the key stories — first in ENGLISH, then the same summary in GEORGIAN (ქართული).
2. Keep each sector summary tight: what happened + why it matters to an entrepreneur like Rezi.
3. Use Telegram Markdown: *bold* for sector names, plain text for summaries.
4. Skip sectors with no news gracefully.
5. Add one sentence at the end (in both languages) with a practical "so what?" for Rezi's business or mindset.

Format:
*🤖 AI & Tech*
[English summary]
[Georgian summary]

*₿ Crypto & Finance*
[English summary]
[Georgian summary]

... and so on.

End with:
*💡 Today's Takeaway:*
[English]
[Georgian]"""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
                "temperature": 0.7,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  WARNING: OpenAI call failed: {e}")
        return format_raw_headlines(all_news)

def format_raw_headlines(all_news: dict) -> str:
    """Fallback: list raw headlines without AI summarization."""
    lines = []
    for sector, articles in all_news.items():
        lines.append(f"*{sector}*")
        if articles:
            for a in articles:
                title = a["title"][:100]
                link  = a.get("link", "")
                if link:
                    lines.append(f"• [{title}]({link})")
                else:
                    lines.append(f"• {title}")
        else:
            lines.append("_No news available._")
        lines.append("")
    return "\n".join(lines).strip()

# ── Message Builder ────────────────────────────────────────────────────────────
def build_message(ai_digest: str, tasks: list) -> str:
    now = datetime.now()
    day_names_geo = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]
    day_geo = day_names_geo[now.weekday()]
    date_en = now.strftime("%B %d, %Y")

    t1, t2, t3 = tasks

    message = (
        f"🌅 *დილა მშვიდობისა! Good Morning, Rezi!*\n"
        f"📅 {day_geo} | {date_en}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📰 *TODAY'S INTEL:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ai_digest}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🪐 *ASTROMAN — Top 3 Tasks Today:*\n"
        f"1️⃣ {t1}\n"
        f"2️⃣ {t2}\n"
        f"3️⃣ {t3}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 *დღეს შენი დღეა — Make it count!* 💪"
    )

    return message.strip()

# ── Telegram Sender ───────────────────────────────────────────────────────────
def send_telegram(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("WARNING: Telegram credentials not set.")
        return False

    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]

    for chunk in chunks:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code != 200:
                print(f"ERROR: Telegram {r.status_code} | {r.text}")
                return False
        except Exception as e:
            print(f"ERROR: Telegram exception: {e}")
            return False

    print(f"SUCCESS: Brief sent at {datetime.now().strftime('%H:%M')}")
    return True

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("🌅 Rezi Morning Brief v2.0 starting...\n")

    print("📡 Fetching news feeds...")
    all_news = get_all_news()

    if not all_news.get("🇬🇪 Georgian Business"):
        print("  Trying BM.ge scrape...")
        all_news["🇬🇪 Georgian Business"] = scrape_bmge()

    print("\n🤖 Summarizing with OpenAI...")
    ai_digest = summarize_with_openai(all_news)

    day_idx = (datetime.now().timetuple().tm_yday - 1) % 30
    tasks = ASTROMAN_TASKS_30[day_idx]

    message = build_message(ai_digest, tasks)

    print("\n" + "=" * 60)
    print(message)
    print("=" * 60 + "\n")

    send_telegram(message)

if __name__ == "__main__":
    main()
