# 🧠 Robin & 🌊 Nami — Discord Bots with LLM + API Power

Welcome to your custom two-bot Discord system!

- **Robin** handles natural language queries via your local LLM (Ollama).
- **Nami** fetches real-time news, weather, crypto updates, and daily briefings using public APIs.

Built with 💻 Python, 🐋 Docker, and ⚡️ Discord.py

---

## 🧩 Bot Overview

### 🤖 Robin (LLM-Powered)
>
> Access your local Ollama model via Discord

**Commands**

```
.ask <question>         # Chat with your LLM
.models                 # Show available Ollama models
.summarize <text>       # Summarize any input
```

**Slash Commands**

```
/stats [time_period]    # Show command usage statistics
/userstats [user]       # Show user-specific stats
/errorstats            # Show command error statistics
```

> Prefix: `.` (dot)

---

### 🌤 Nami (API Specialist)
>
> News, weather, crypto — your command center bot

**Commands**

```
!news                   # Latest headlines (NewsAPI)
!weather <city>         # Current conditions (OpenWeather)
!crypto <symbol>        # Crypto price via CoinGecko
!dailybrief [city]      # News + Weather + Crypto
```

**Slash Commands**

```
/games <league> [days]  # Show upcoming games
/scores <league>        # Show live scores
/subscribe <league> [team]  # Subscribe to game alerts

/schedule <channel> <time> [timezone] [type]  # Schedule briefings
/unschedule <channel>   # Remove scheduled briefing
/briefings             # List all scheduled briefings
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
```

### nami/.env

```
DISCORD_TOKEN=your_nami_token
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key
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

## ✨ Features To Implement

- [ ] Voice transcription with Whisper
- [ ] Private DM sessions
- [ ] Dictionary lookup command
- [ ] Anime info command
- [ ] Personal reminders system

## ✅ Implemented Features

- [x] Slash command support (including `/stats`, `/userstats`, `/serverstats`, `/games`, `/scores`, `/subscribe`, `/schedule`, `/unschedule`, `/briefings`)
- [x] Command usage analytics and statistics (track usage, errors, trends per user/server)
- [x] Game + sports alerts (MLB, NBA, NFL) with live score subscriptions and notifications
- [x] Scheduled briefings (daily/weekly/monthly) with rich card formatting
- [x] Embedded summaries for news, weather, crypto, and sports
- [x] Advanced help system with paginated embeds and dynamic help for commands/categories
- [x] Robust error handling and logging (user-facing and internal)
- [x] LLM integration via Ollama API (local model chat, summarization, model selection)
- [x] Modular API integrations: NewsAPI, OpenWeatherMap, CoinGecko, OddsAPI
- [x] Rate limiting and user preferences
- [x] Docker-based deployment for both bots
- [x] Extensible architecture for adding new commands and APIs

---

## 📚 Command Reference

### Robin (LLM-Powered)

| Command                  | Description                                |
|-------------------------|--------------------------------------------|
| `.ask <question>`       | Chat with your local LLM                   |
| `.models`               | Show available Ollama models               |
| `.summarize <text>`     | Summarize any input                        |
| `/stats [time_period]`  | Show command usage statistics              |
| `/userstats [user]`     | Show user-specific stats                   |
| `/errorstats`           | Show command error statistics              |
| `/games <league> [days]`| Show upcoming games                        |
| `/scores <league>`      | Show live scores                           |
| `/subscribe <league> [team]` | Subscribe to game alerts           |
| `/schedule <channel> <time> [timezone] [type]` | Schedule briefings |
| `/unschedule <channel>` | Remove scheduled briefing                   |
| `/briefings`            | List all scheduled briefings                |

### Nami (API Specialist)

| Command                  | Description                                |
|-------------------------|--------------------------------------------|
| `!news`                 | Latest headlines (NewsAPI)                 |
| `!weather <city>`       | Current conditions (OpenWeather)           |
| `!crypto <symbol>`      | Crypto price via CoinGecko                 |
| `!dailybrief [city]`    | News + Weather + Crypto                    |

---

## 🛠 Advanced Architecture & Features

- **Analytics & Statistics:**
  - Tracks command usage, errors, and trends per user/server
  - View stats with `/stats`, `/userstats`, `/serverstats`, `/errorstats`
- **Briefings System:**
  - Automated daily, weekly, and monthly briefings with top commands, trends, and error rates
  - Schedule/unschedule briefings via slash commands
- **Sports/Game Alerts:**
  - Subscribe to live score notifications for major leagues
  - Custom channel subscriptions and notifications
- **Help System:**
  - Paginated help embeds, dynamic command/category help, and command discovery
- **Error Handling:**
  - User-facing error messages and detailed logging for debugging
- **Modular APIs:**
  - Easily extend with new APIs for news, weather, crypto, sports, and LLMs
- **Dockerized:**
  - Production-ready Docker Compose setup for both bots

---

## 🛡 .gitignore

`.env` files and local caches are excluded. See `.gitignore` for details.

---

## 🧠 Credits

- [discord.py](https://github.com/Rapptz/discord.py)
- [Ollama](https://ollama.com/)
- [NewsAPI](https://newsapi.org/)
- [OpenWeatherMap](https://openweathermap.org/)
- [CoinGecko API](https://www.coingecko.com/en/api)

---

## 📸 Preview

> _"You're not just running bots. You're commanding a crew."_ – You, probably
