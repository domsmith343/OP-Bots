# 🧠 Robin & 🌊 Nami — Discord Bots with LLM + API Power

A two-bot Discord system:

- **Robin** answers natural-language questions via a local LLM (Ollama) and a few handy lookups.
- **Nami** fetches real-time news, weather, and crypto, and posts scheduled daily briefs.

Built with 💻 Python, 🐋 Docker, and ⚡️ [discord.py](https://github.com/Rapptz/discord.py).

Both bots use classic **prefix commands** (not slash commands). Robin listens on `.`, Nami on `!`.

---

## 🧩 Bot Overview

### 🤖 Robin (LLM-Powered) — prefix `.`

> Talk to your local Ollama model from Discord.

| Command            | Description                                         |
|--------------------|-----------------------------------------------------|
| `.ask <question>`  | Ask the LLM a question (long replies are chunked).  |
| `.summarize <text>`| Summarize any block of text with the LLM.           |
| `.models`          | List the models installed in your Ollama instance.  |
| `.define <term>`   | Dictionary lookup (dictionaryapi.dev).              |
| `.anime <title>`   | Anime info lookup (Jikan / MyAnimeList).            |
| `.schedule [entry]`| List the in-memory schedule, or add an entry.       |
| `.help`            | Show Robin's command list.                          |

> Note: `.schedule` is stored in memory and is cleared when the bot restarts.

### 🌊 Nami (API Specialist) — prefix `!`

> News, weather, and crypto — plus an automatic daily brief.

| Command                       | Description                                                  |
|-------------------------------|--------------------------------------------------------------|
| `!news [category] [keyword]`  | US headlines (NewsAPI). Categories: general, sports, business, technology, entertainment, health, science. |
| `!weather <city>`             | Current conditions (OpenWeather). Defaults to your preference/`DEFAULT_CITY`. |
| `!crypto <symbol>`            | Price + 24h change (CoinGecko). Supported: btc, eth, sol, doge, ada, dot, ltc. |
| `!dailybrief`                 | Combined news + weather + BTC update.                        |
| `!setprefs`                   | Configure preferred news source, crypto, and location.       |
| `!togglebrief`                | Toggle your daily-brief notifications on/off.                |
| `!stats`                      | Usage/error analytics (**bot owner only**).                  |
| `!help`                       | Show Nami's command list.                                    |

> **Scheduled brief:** Nami automatically posts a daily brief at **08:00, 14:00, and 20:00** (server local time) to the channel set by `DAILYBRIEF_CHANNEL_ID`.

---

## 🚀 Getting Started

### 1. Clone

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create `.env` files

These are gitignored and required for Docker to run.

**`bots/robin/.env`**

```
DISCORD_TOKEN=your_robin_token
OLLAMA_API=http://host.docker.internal:11434   # reach Ollama on the host from inside Docker
OLLAMA_DEFAULT_MODEL=llama3                     # optional, default: llama3
COMMAND_PREFIX=.                                # optional, default: .
```

**`bots/nami/.env`**

```
DISCORD_TOKEN=your_nami_token
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key
DAILYBRIEF_CHANNEL_ID=123456789012345678        # channel for scheduled briefs
DEFAULT_CITY=los angeles                         # optional, default: los angeles
DEFAULT_CRYPTO=btc                               # optional, default: btc
```

> CoinGecko needs no API key.

### 3. Run with Docker Compose

```bash
docker-compose down
docker-compose up -d --build
```

Both bots launch in the background and connect to your server.

---

## 🗂 Project Layout

```
bots/
  robin/
    ollama_discord_bot.py   # Robin entrypoint (the bot that runs)
    requirements.txt
    Dockerfile
  nami/
    nami_bot.py             # Nami entrypoint (the bot that runs)
    api/                    # news, weather, crypto clients
    db/                     # user preferences (JSON-backed)
    analytics.py            # command/error usage tracking
    requirements.txt
    Dockerfile
docker-compose.yml
```

---

## 🧠 Credits

- [discord.py](https://github.com/Rapptz/discord.py)
- [Ollama](https://ollama.com/)
- [NewsAPI](https://newsapi.org/)
- [OpenWeatherMap](https://openweathermap.org/)
- [CoinGecko API](https://www.coingecko.com/en/api)

---

## 📸 Preview

> _"You're not just running bots. You're commanding a crew."_
