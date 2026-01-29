#!/usr/bin/env python3
"""
Telegram Morning Briefing Bot
Sends daily motivational messages with news, quotes, and productivity tips
"""

import os
import random
import requests
from datetime import datetime
import json

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWS_API_KEY_HERE')  # Get free key from newsapi.org

# Motivational quotes (mix of Georgian and English)
QUOTES = [
    "🌟 'The future belongs to those who believe in the beauty of their dreams.' - Eleanor Roosevelt",
    "💪 'Success is not final, failure is not fatal: it is the courage to continue that counts.' - Winston Churchill",
    "🚀 'The only way to do great work is to love what you do.' - Steve Jobs",
    "⭐ 'Believe you can and you're halfway there.' - Theodore Roosevelt",
    "🎯 'Don't watch the clock; do what it does. Keep going.' - Sam Levenson",
    "🌅 'Every morning is a new opportunity to be better than yesterday.'",
    "💡 'The secret of getting ahead is getting started.' - Mark Twain",
    "🔥 'Your limitation—it's only your imagination.'",
    "🎨 'Great things never come from comfort zones.'",
    "⚡ 'Success doesn't just find you. You have to go out and get it.'",
    "🌟 'დღეს არის საუკეთესო დღე რომ დავიწყოთ რაღაც ახალი!' (Today is the best day to start something new!)",
    "💪 'წარმატება მოდის მათთან, ვინც არასოდეს ანებებს!' (Success comes to those who never give up!)",
    "🚀 'შენი მომავალი იქმნება დღეს!' (Your future is created today!)",
]

# Productivity tips (mix of Georgian and English)
PRODUCTIVITY_TIPS = [
    "📝 დაწერე დღის 3 ყველაზე მნიშვნელოვანი დავალება და შეასრულე ისინი პირველ რიგში! (Write down 3 most important tasks and do them first!)",
    "⏰ გამოიყენე Pomodoro ტექნიკა - 25 წუთი მუშაობა, 5 წუთი შესვენება!",
    "🎯 Focus on ONE thing at a time - multitasking kills productivity!",
    "🌅 Start your day with the hardest task - eat that frog!",
    "📱 Turn off notifications for the first 2 hours - deep work time!",
    "💧 Drink water! Hydration = Better focus and energy!",
    "🧘 Take 5-minute breaks every hour to stretch and breathe",
    "📊 Review yesterday's wins - momentum builds confidence!",
    "🎧 Try background music or white noise for focus",
    "✅ Celebrate small wins throughout the day!",
    "🚫 Say NO to distractions - protect your energy!",
    "📖 Read for 15 minutes - invest in yourself daily!",
]

def get_motivational_quote():
    """Get a random motivational quote"""
    return random.choice(QUOTES)

def get_productivity_tip():
    """Get a random productivity tip"""
    return random.choice(PRODUCTIVITY_TIPS)

def get_news(topics, max_articles=2):
    """Fetch news from NewsAPI for specified topics"""
    if NEWS_API_KEY == 'YOUR_NEWS_API_KEY_HERE':
        return "📰 *News:*\n_Set up your NewsAPI key to get personalized news!_\nGet free API key: https://newsapi.org"
    
    news_text = "📰 *Today's News:*\n\n"
    
    topic_keywords = {
        'crypto': 'cryptocurrency OR bitcoin OR ethereum',
        'ai': 'artificial intelligence OR AI OR machine learning',
        'space': 'astronomy OR space OR NASA OR SpaceX',
        'tech': 'technology OR startup OR innovation',
        'stocks': 'stock market OR trading OR nasdaq',
        'ecommerce': 'e-commerce OR online shopping OR retail'
    }
    
    for topic, keywords in topic_keywords.items():
        try:
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': keywords,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': max_articles,
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    news_text += f"*{topic.upper()}:*\n"
                    for article in articles[:1]:  # One article per topic
                        title = article.get('title', 'No title')
                        url = article.get('url', '')
                        news_text += f"• [{title}]({url})\n"
                    news_text += "\n"
        except Exception as e:
            continue
    
    if news_text == "📰 *Today's News:*\n\n":
        news_text += "_No news available at the moment._"
    
    return news_text

def get_weather_emoji():
    """Get a random weather-appropriate emoji"""
    return random.choice(['☀️', '🌤️', '⛅', '🌈'])

def create_morning_message():
    """Create the complete morning briefing message"""
    
    now = datetime.now()
    day_name_geo = ['ორშაბათი', 'სამშაბათი', 'ოთხშაბათი', 'ხუთშაბათი', 'პარასკევი', 'შაბათი', 'კვირა'][now.weekday()]
    
    message = f"""
🌅 *დილა მშვიდობისა! Good Morning!* {get_weather_emoji()}

📅 {day_name_geo} | {now.strftime('%B %d, %Y')}

━━━━━━━━━━━━━━━━━━━━

{get_motivational_quote()}

━━━━━━━━━━━━━━━━━━━━

💡 *Today's Productivity Tip:*
{get_productivity_tip()}

━━━━━━━━━━━━━━━━━━━━

{get_news(['crypto', 'ai', 'space', 'tech', 'stocks', 'ecommerce'])}

━━━━━━━━━━━━━━━━━━━━

✨ *Quick Daily Checklist:*
□ Review your top 3 priorities
□ Check Astroman.ge orders
□ 10 minutes learning something new
□ Exercise or walk
□ Connect with someone meaningful

━━━━━━━━━━━━━━━━━━━━

🚀 *დღეს შენი დღეა! Make it count!* 💪
    """
    
    return message.strip()

def send_telegram_message(message):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Message sent successfully at {datetime.now()}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    """Main function to run the morning briefing"""
    print("🌅 Generating morning briefing...")
    
    message = create_morning_message()
    
    # For testing, print the message
    print("\n" + "="*50)
    print(message)
    print("="*50 + "\n")
    
    # Send via Telegram
    if TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
        send_telegram_message(message)
    else:
        print("⚠️  Set up your Telegram bot token to send messages!")
        print("See setup instructions in README.md")

if __name__ == "__main__":
    main()
