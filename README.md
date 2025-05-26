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

- [ ] Slash command support
- [ ] Game + sports alerts (MLB, NBA, NFL)
- [ ] Embedded summaries + rich card formatting
- [ ] Scheduled briefings (every morning)
- [ ] Voice transcription with Whisper
- [ ] Private DM sessions

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

> _“You’re not just running bots. You’re commanding a crew.”_ – You, probably
