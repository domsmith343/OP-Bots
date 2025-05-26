# 🧠 Robin & 🌊 Nami — Discord Bots with LLM + API Power

Welcome to your custom two-bot Discord system!

- **Robin** handles natural language queries via your local LLM (Ollama).
- **Nami** fetches real-time news, weather, crypto updates, and daily briefings using public APIs.

Built with 💻 Python, 🐋 Docker, and ⚡️ Discord.py

---

## 🧩 Bot Overview

### 🤖 Robin (LLM-Powered)
> Access your local Ollama model via Discord

**Commands**
```
.ask <question>         # Chat with your LLM
.models                 # Show available Ollama models
.summarize <text>       # Summarize any input
.define <term>          # Quick dictionary lookup
.anime <title>          # Get anime info (Jikan API)
.schedule [event]       # Add/view personal reminders
```

> Prefix: `.` (dot)

---

### 🌤 Nami (API Specialist)
> News, weather, crypto — your command center bot

**Commands**
```
!news                   # Latest headlines (NewsAPI)
!weather <city>         # Current conditions (OpenWeather)
!crypto <symbol>        # Crypto price via CoinGecko
!dailybrief             # News + Weather + Crypto
```

> Prefix: `!` (bang)

---

## 🚀 Getting Started

1. **Clone the repo**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. **Create `.env` files**

### robin/.env
```
DISCORD_TOKEN=your_robin_token
OLLAMA_API=http://host.docker.internal:11434
OLLAMA_DEFAULT_MODEL=llama3
```

### nami/.env
```
DISCORD_TOKEN=your_nami_token
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key
DEFAULT_CITY=los angeles
DEFAULT_CRYPTO=btc
```

> These files are gitignored and required for Docker to run correctly.

---

## 🐳 Running the Bots (Docker Compose)

```bash
docker-compose down
docker-compose up -d --build
```

Both bots will launch in the background and connect to your Discord server.

---

## ✨ Features To Expand

### ✅ Implemented Features
- [x] Slash command support
- [x] Game + sports alerts (MLB, NBA, NFL, NHL)
- [x] Embedded summaries + rich card formatting
- [x] Scheduled briefings (daily/weekly/monthly)
- [x] Private DM sessions

### 🚀 Future Features
- [ ] Voice transcription with Whisper
- [ ] AI-powered command suggestions
- [ ] Custom command aliases
- [ ] User-defined command shortcuts
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Role-based command access
- [ ] Automated moderation tools
- [ ] Integration with external calendars
- [ ] Custom notification preferences
- [ ] Command usage heatmaps
- [ ] Server activity reports
- [ ] User engagement metrics
- [ ] Automated backup system
- [ ] Plugin system for custom extensions

---

## 🛡 .gitignore

`.env` files and local caches are excluded. See `.gitignore` for details.

---

## 🧠 Credits

- [discord.py](https://github.com/Rapptz/discord.py)
- [Ollama](https://ollama.com/)
- [Jikan API (MyAnimeList)](https://jikan.moe/)
- [NewsAPI](https://newsapi.org/)
- [OpenWeatherMap](https://openweathermap.org/)
- [CoinGecko API](https://www.coingecko.com/en/api)

---

## 📸 Preview

> _"You're not just running bots. You're commanding a crew."_ – You, probably

# Robin Discord Bot

A feature-rich Discord bot with command usage tracking, sports alerts, and private DM sessions.

## Features

### Command Usage Tracking
- Tracks command usage statistics
- Monitors success/failure rates
- Records execution times
- Provides usage trends over time
- Supports time-based filtering (1h, 1d, 1w, 1m)

### Briefings System
- Automated usage statistics reports
- Multiple briefing types:
  - Daily briefings
  - Weekly summaries
  - Monthly reports
- Customizable scheduling with timezone support
- Includes:
  - Top commands by usage
  - Error statistics
  - Success rates
  - Usage trends

### Sports Alerts
- Real-time game updates
- League support:
  - NBA
  - NFL
  - MLB
  - NHL
- Features:
  - Live score updates
  - Upcoming game notifications
  - Betting odds integration
  - Team-specific subscriptions
  - League-wide alerts

### Private DM Sessions
- Secure private interactions
- Session management:
  - Automatic timeout
  - Activity tracking
  - Command history
- Available commands:
  - `!help` - Show available commands
  - `!stats` - View personal usage statistics
  - `!end` - End DM session

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with:
   ```
   DISCORD_TOKEN=your_bot_token
   ODDS_API_KEY=your_odds_api_key
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

### Briefings
- `/schedule` - Schedule a briefing (daily/weekly/monthly)
- `/unschedule` - Remove a scheduled briefing
- `/briefings` - List all scheduled briefings

### Sports
- `/games` - Show upcoming games
- `/scores` - Show live scores
- `/subscribe` - Subscribe to game alerts
- `/unsubscribe` - Remove game subscriptions
- `/subscriptions` - List current subscriptions

### DM Session
- `/dm` - Start a private DM session

## Dependencies
- discord.py>=2.0.0
- matplotlib>=3.5.0
- pytz>=2021.3
- python-dotenv>=0.19.0
- aiohttp>=3.8.0

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
