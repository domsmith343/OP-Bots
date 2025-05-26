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

> _"You're not just running bots. You're commanding a crew."_ – You, probably

# Robin - Discord Bot

A versatile Discord bot with advanced command tracking and statistics capabilities.

## Features

### Command Tracking
- Tracks command usage, success rates, and execution times
- Monitors user engagement and command popularity
- Provides detailed error tracking and analysis
- Supports time-based filtering for all statistics

### Statistics Commands
- `/stats` - View overall command usage statistics
- `/userstats` - Check command usage for specific users
- `/errorstats` - Analyze command error patterns
- `/serverstats` - View server-wide command usage statistics
  - Overall server statistics
  - Command-specific usage
  - Top users by command usage
  - Channel usage statistics
- `/trends` - Visualize command usage trends over time
  - Hourly usage graphs
  - Command-specific trends
  - Customizable time periods
- `/timeofday` - Analyze command usage patterns by time of day
  - Hour-by-hour usage breakdown
  - Peak usage hours identification
  - Visual representation with bar charts

### Data Visualization
- Interactive graphs for usage trends
- Bar charts for time-of-day analysis
- Success rate visualizations
- Error distribution charts

### Time-based Analysis
- Filter statistics by time periods (1h, 1d, 1w, 1m)
- Track usage patterns over time
- Identify peak usage hours
- Monitor command popularity trends

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/robin.git
cd robin
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the bot:
```bash
python main.py
```

## Configuration

Create a `.env` file with the following variables:
```
DISCORD_TOKEN=your_bot_token
```

## Usage

1. Invite the bot to your server using the OAuth2 URL
2. Use `/help` to see available commands
3. Start tracking command usage with `/stats`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Discord.py for the bot framework
- Matplotlib for data visualization
- SQLite for data storage
